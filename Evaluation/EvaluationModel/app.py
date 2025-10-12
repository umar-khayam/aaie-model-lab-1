# streamlit_app.py
import torch
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from transformers import AutoTokenizer, AutoModelForCausalLM
import google.generativeai as genai
from evaluateModel import EvaluateModel
import os
import openai
from huggingface_hub import login
from sklearn.metrics import confusion_matrix
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

# =============================================================================
# MODEL CONFIGURATIONS - modify for future models
# =============================================================================

device = torch.device(
                "cuda" if torch.cuda.is_available() else
                "cpu")

AVAILABLE_MODELS = {
    "gemini-1.5-flash": {
        "type": "api",
        "provider": "google",
        "api_key_required": True,
        "description": "Google's Gemini 1.5 Flash model"
    },
    "gemini-1.5-pro": {
        "type": "api",
        "provider": "google", 
        "api_key_required": True,
        "description": "Google's Gemini 1.5 Pro model"
    },
    "mistral-7b": {
        "type": "local",
        "provider": "huggingface",
        "model_name": "mistralai/Mistral-7B-Instruct-v0.1",
        "api_key_required": True,
        "description": "Mistral 7B Instruct model"
    },
    "phi-2": {
        "type": "local",
        "provider": "huggingface",
        "model_name": "microsoft/phi-2",
        "api_key_required": False,
        "description": "Microsoft's Phi-2 language model"
    },
    "llama-7b": {
        "type": "local",
        "provider": "huggingface",
        "model_name": "meta-llama/Llama-2-7b-chat-hf",
        "api_key_required": True,
        "description": "Llama 2 7B Chat model"
    },
    "gpt-3.5-turbo": {
        "type": "api",
        "provider": "openai",
        "api_key_required": True,
        "description": "OpenAI's GPT-3.5 Turbo model"
    }
}

EVALUATION_METRICS = {
    "classification": ["accuracy", "precision", "recall", "f1_score"],
    "generative": ["bleu", "rouge", "bertscore"]
}

MODEL_TYPES = ["ai_detection", "feedback_generation"]

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def initialize_api_model(api_key: str, model_name: str, provider: str) -> bool:
    """Initialize API-based model with API key"""
    try:
        if provider == "google":
            genai.configure(api_key=api_key)
            # Test connection
            model = genai.GenerativeModel(model_name)
            test_response = model.generate_content("Hello")
            return True
        elif provider == "openai":
            # Add OpenAI initialization logic here
            openai.api_key = api_key
            # Test connection with a simple call
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        else:
            st.error(f"Unsupported API provider: {provider}")
            return False
    except Exception as e:
        st.error(f"Failed to connect to {model_name}: {str(e)}")
        return False

def initialize_local_model(api_key: Optional[str], model_name: str) -> Tuple[Optional[Any], Optional[Any]]:
    """Initialize local model from HuggingFace"""
    try:
        with st.spinner(f"Loading {model_name}..."):
            if api_key:
                login(api_key)
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Add padding token if it doesn't exist
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map= 'automap' if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True
            )
        st.success(f"{model_name} loaded successfully!")
        return model, tokenizer
    except Exception as e:
        st.error(f"Failed to load {model_name}: {str(e)}")
        return None, None

def generate_response_api(message: Dict[str, str], model_name: str, provider: str) -> str:
    """Generate response using API-based model"""
    try:
        if provider == "google":
            model = genai.GenerativeModel(model_name, system_instruction=message['system'])
            chat = model.start_chat()
            response = chat.send_message(message['user'])
            return response.text
        elif provider == "openai":
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": message['system']},
                    {"role": "user", "content": message['user']}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        else:
            return f"Unsupported API provider: {provider}"
    except Exception as e:
        return f"Error generating response: {str(e)}"

def generate_response_local(message: Dict[str, str], model, tokenizer) -> str:
    """Generate response using local model"""
    try:
        full_prompt = f"System: {message['system']}\nUser: {message['user']}\nAssistant:"
        # Move inputs to the same device as the model
        inputs = tokenizer(
            full_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(device)

        with torch.no_grad():
            print("Loading the generate")
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Cut off the prompt part, keep only model’s answer
        return response[len(full_prompt):].strip()

    except Exception as e:
        return f"Error generating response: {str(e)}"

def validate_dataframe(df: pd.DataFrame, model_type: str) -> List[str]:
    """Validate dataframe has required columns for the selected model type"""
    errors = []
    
    required_columns = {
        "ai_detection": ["text", "labels", "predictions"],
        "feedback_generation": ["text", "domain", "generated_texts", "references"]
    }
    
    if model_type in required_columns:
        for col in required_columns[model_type]:
            if col not in df.columns:
                errors.append(f"Missing required column: '{col}'")
    
    return errors

def is_model_supports_attention(model_config: Dict[str, Any]) -> bool:
    """Check if model supports attention visualization"""
    return (model_config["type"] == "local" and 
            model_config.get("provider", "") == "huggingface")

# =============================================================================
# STREAMLIT APP
# =============================================================================

st.set_page_config(
    page_title="Advanced Model Evaluation Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">Advanced Model Evaluation Dashboard</h1>', unsafe_allow_html=True)

# =============================================================================
# SIDEBAR CONFIGURATION
# =============================================================================

with st.sidebar:
    st.markdown("## Configuration")
    
    # Model Selection
    st.markdown("### Model Selection")
    selected_model_key = st.selectbox(
        "Choose Model:",
        list(AVAILABLE_MODELS.keys()),
        help="Select the model you want to use for evaluation"
    )
    
    selected_model_config = AVAILABLE_MODELS[selected_model_key]
    
    # API Key input (if required)
    api_key = None
    if selected_model_config["api_key_required"]:
        api_key_label = f"API Key for {selected_model_key}:"
        if selected_model_config.get("provider") == "google":
            api_key_label += " (Google AI Studio)"
        elif selected_model_config.get("provider") == "openai":
            api_key_label += " (OpenAI)"
        elif selected_model_config.get("provider") == "huggingface":
            api_key_label += " (HuggingFace)"
            
        api_key = st.text_input(
            api_key_label,
            type="password",
            help="Enter your API key to use this model"
        )
    
    # Model Type Selection
    st.markdown("### Evaluation Type")
    model_type = st.selectbox(
        "Model Type:",
        MODEL_TYPES,
        help="Select the type of model evaluation you want to perform"
    )
    
    # Metrics Selection
    st.markdown("### Metrics Configuration")
    if model_type in ["classification", "ai_detection"]:
        avg_type = st.selectbox(
            "Average Type:",
            ["macro", "micro", "weighted", "binary"],
            help="Choose averaging method for multi-class metrics"
        )
        
        selected_metrics = st.multiselect(
            "Classification Metrics:",
            EVALUATION_METRICS["classification"],
            default=EVALUATION_METRICS["classification"]
        )
    else:
        selected_metrics = st.multiselect(
            "Generative Metrics:",
            EVALUATION_METRICS["generative"],
            default=["bleu", "rouge", "bertscore"]
        )
    
    # Attention Visualization Options (only for local HuggingFace models)
    st.markdown("### Attention Visualization")
    
    if is_model_supports_attention(selected_model_config):
        show_attention_rollout = st.checkbox("Show Attention Rollout", value=True)
        show_attention_weights = st.checkbox("Show Attention Weights", value=True)
        
        if show_attention_weights:
            attention_layer = st.slider("Attention Layer", 0, 11, 2)
            attention_head = st.slider("Attention Head", 0, 11, 0)
    else:
        show_attention_rollout = False
        show_attention_weights = False
        model_type_name = selected_model_config["type"].capitalize()
        provider_name = selected_model_config.get("provider", "").capitalize()
        st.info(f"Attention visualization is only available for local HuggingFace models. Current model is {model_type_name} ({provider_name})")
        attention_layer = 2
        attention_head = 0

# =============================================================================
# MAIN CONTENT AREA
# =============================================================================

# Create columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("## Data Upload")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your dataset (CSV format):",
        type=['csv'],
        help="Upload a CSV file containing your evaluation data"
    )
    
    # Sample data preview
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            
            st.markdown("### Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            st.markdown("### Dataset Info")
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("Rows", len(df))
            with col_info2:
                st.metric("Columns", len(df.columns))
            with col_info3:
                st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
            
            # Validate dataframe
            validation_errors = validate_dataframe(df, model_type)
            if validation_errors:
                st.error("Data Validation Errors:")
                for error in validation_errors:
                    st.error(f"• {error}")
            else:
                st.success("Data validation passed!")
                
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")

with col2:
    st.markdown("## Model Status")
    
    # Model connection status
    model_connected = False
    model_instance = None
    tokenizer_instance = None
    
    # Dynamic button text based on model type
    if selected_model_config["type"] == "api":
        button_text = f"Test {selected_model_config.get('provider', 'API').title()} Connection"
    else:
        button_text = f"Load {selected_model_key.title()} Model"
    
    if selected_model_config["api_key_required"] and not api_key:
        st.warning("Please enter API key to proceed")
    elif not selected_model_config["api_key_required"] or api_key:
        if st.button(button_text):
            if selected_model_config["type"] == "api":
                model_connected = initialize_api_model(
                    api_key, 
                    selected_model_key, 
                    selected_model_config.get("provider", "")
                )
                if model_connected:
                    st.success(f"Successfully connected to {selected_model_key}")
                    st.session_state.model_connected = True
                else:
                    st.error(f"Failed to connect to {selected_model_key}")
                    st.session_state.model_connected = False
            
            elif selected_model_config["type"] == "local":
                model_instance, tokenizer_instance = initialize_local_model(
                    api_key,
                    selected_model_config["model_name"]
                )
                if model_instance and tokenizer_instance:
                    model_connected = True
                    st.session_state.model_instance = model_instance
                    st.session_state.tokenizer_instance = tokenizer_instance
                    st.session_state.model_connected = True
                else:
                    st.session_state.model_connected = False
    
    # Check session state for model connection status
    if hasattr(st.session_state, 'model_connected'):
        model_connected = st.session_state.model_connected
    
    # Display model info
    st.markdown("### Current Configuration")
    st.info(f"""
    **Selected Model:** {selected_model_key}  
    **Model Type:** {selected_model_config["type"]}  
    **Provider:** {selected_model_config.get("provider", "N/A")}  
    **Connection Status:** {'Connected' if model_connected else 'Not Connected'}  
    **Description:** {selected_model_config['description']}
    """)

# =============================================================================
# EVALUATION SECTION
# =============================================================================

st.markdown('<h2 class="section-header">Model Evaluation</h2>', unsafe_allow_html=True)

# Action buttons
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    run_evaluation_btn = st.button("Run Evaluation", type="primary")

with col_btn2:
    visualize_attention_btn = st.button("Visualize Attention", disabled=not is_model_supports_attention(selected_model_config))

with col_btn3:
    generate_responses_btn = st.button("Generate Responses")

# =============================================================================
# EVALUATION EXECUTION
# =============================================================================

if 'df' in st.session_state and not st.session_state.df.empty:
    
    if run_evaluation_btn:
        st.markdown("### Evaluation Results")
        
        try:
            # Initialize evaluator
            evaluator = EvaluateModel(
                dataset=st.session_state.df,
                model_type=model_type
            )
            
            # Run evaluation based on model type
            if model_type in ["classification", "ai_detection"]:
                evaluator.evaluate_classification_model(
                    average=avg_type,
                    print_result=False
                )
                
                # Display metrics
                results_df = pd.DataFrame([evaluator.results])
                st.dataframe(results_df, use_container_width=True)
                
                # Create confusion matrix if possible
                if "labels" in st.session_state.df.columns and "predictions" in st.session_state.df.columns:
                    labels = st.session_state.df["labels"]
                    preds = st.session_state.df["predictions"]
                    
                    # Create confusion matrix
                    cm = confusion_matrix(labels, preds)
                    
                    fig = px.imshow(
                        cm,
                        color_continuous_scale="Blues",
                        title="Confusion Matrix",
                        labels=dict(x="Predicted", y="Actual", color="Count")
                    )
                    fig.update_layout(
                        xaxis_title="Predicted Labels",
                        yaxis_title="Actual Labels"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            else:  # generative models
                evaluator.evaluate_generative_model(
                    metrics=selected_metrics,
                    print_result=False
                )
                
                # Display metrics
                results_df = pd.DataFrame([evaluator.results])
                st.dataframe(results_df, use_container_width=True)
                
                # Create metrics comparison chart
                metrics_data = []
                for metric, value in evaluator.results.items():
                    metrics_data.append({"Metric": metric.upper(), "Score": value})
                
                metrics_df = pd.DataFrame(metrics_data)
                fig = px.bar(
                    metrics_df,
                    x="Metric",
                    y="Score",
                    title="Generative Model Metrics Comparison",
                    color="Score",
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Evaluation failed: {str(e)}")
    
    # Attention Visualization
    if visualize_attention_btn and (show_attention_rollout or show_attention_weights):
        st.markdown("### Attention Visualization")
        
        # Check if we have a local HuggingFace model loaded
        if (is_model_supports_attention(selected_model_config) and 
            hasattr(st.session_state, 'model_instance') and 
            hasattr(st.session_state, 'tokenizer_instance') and
            st.session_state.model_instance is not None):
            
            try:
                # Initialize evaluator for attention visualization
                evaluator = EvaluateModel(
                    dataset=st.session_state.df,
                    model_type=model_type,
                    model=st.session_state.model_instance,
                    tokenizer=st.session_state.tokenizer_instance
                )
                evaluator.construct_data_messages()
                # Get sample text for attention visualization
                sample_text = st.session_state.df.iloc[0]['text']
                sample_prompt = f"Analyze this text: {evaluator.dataset_prompt[0]}"
                
                if show_attention_rollout:
                    st.markdown("#### Attention Rollout")
                    with st.spinner("Computing attention rollout..."):
                        try:
                            # Call the static method from EvaluateModel
                            attn_values, tokens_segment = evaluator.visualize_rollout(
                                model=st.session_state.model_instance,
                                tokenizer=st.session_state.tokenizer_instance,
                                text=sample_text,
                                prompt=sample_prompt,
                                title="Attention Rollout Visualization", plot = False
                            )
                            
                            fig = px.bar(
                                x=tokens_segment,
                                y=attn_values,
                                labels={"x": "Tokens", "y": "Attention Value"},
                                title="Attention Rollout Visualization",
                                color=attn_values,  # color intensity by value
                                color_continuous_scale="Reds"
                            )
                            fig.update_layout(
                                xaxis_tickangle=-45,
                                bargap=0.3,
                                height=400,
                                width=max(600, len(tokens_segment) * 40)  # auto-scale width for many tokens
                            )

                            # Show in Streamlit
                            st.plotly_chart(fig, use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"Attention rollout failed: {str(e)}")
                            st.info("This feature requires the AttentionRollout class to be properly implemented in your EvaluateModel")
                
                if show_attention_weights:
                    st.markdown("#### Attention Weights Heatmap")
                    with st.spinner(f"Computing attention weights (Layer {attention_layer}, Head {attention_head})..."):
                        try:
                            # Call the static method from EvaluateModel
                            attn_segment, tokens_segment = evaluator.visualize_attention_weights(
                                st.session_state.model_instance,
                                st.session_state.tokenizer_instance,
                                sample_text,
                                sample_prompt,
                                title=f"Attention Weights - Layer {attention_layer}, Head {attention_head}", plot = False
                            )
                            
                             # Convert tensor to numpy
                            attn_data = attn_segment.detach().cpu().numpy()

                            # Create interactive heatmap
                            fig = px.imshow(
                                attn_data,
                                x=tokens_segment,
                                y=tokens_segment,
                                color_continuous_scale="viridis",
                                text_auto=True,
                                aspect="auto"
                            )
                            fig.update_layout(
                                title=f"Attention Weights - Layer {attention_layer}, Head {attention_head}",
                                xaxis_title="Tokens (to)",
                                yaxis_title="Tokens (from)"
                            )

                            # Show in Streamlit
                            st.plotly_chart(fig, use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"Attention weights visualization failed: {str(e)}")
                            st.info("This feature requires the AttentionWeight class to be properly implemented in your EvaluateModel")
                    
            except Exception as e:
                st.error(f"Attention visualization failed: {str(e)}")
                
        elif selected_model_config["type"] == "api":
            st.warning("Attention visualization is not available for API-based models (they don't expose attention weights)")
            st.info("Try using a local HuggingFace model for attention visualization features")
            
        else:
            st.warning("Please load the local model first to visualize attention")
            st.info("Click the 'Load Model' button in the Model Status section")
    # =============================================================================
    # Response Generation
    # =============================================================================
    if generate_responses_btn and model_connected:
        st.markdown("### Generate Sample Responses")
        
        try:
            evaluator = EvaluateModel(
                dataset=st.session_state.df,
                model_type=model_type
            )
            
            # Construct prompts
            evaluator.construct_data_messages()
            
            if evaluator.dataset_prompt:
                sample_message = evaluator.dataset_prompt[0]
                
                with st.spinner("Generating response..."):
                    if selected_model_config["type"] == "api":
                        response = generate_response_api(
                            sample_message, 
                            selected_model_key,
                            selected_model_config.get("provider", "")
                        )
                    elif selected_model_config["type"] == "local":
                        response = generate_response_local(
                            sample_message, 
                            st.session_state.model_instance, 
                            st.session_state.tokenizer_instance
                        )
                    else:
                        response = "Unsupported model type"
                
                st.markdown("#### System Prompt:")
                st.code(sample_message["system"])
                
                st.markdown("#### User Prompt:")
                st.code(sample_message["user"])
                
                st.markdown("#### Model Response:")
                st.write(response)
                
        except Exception as e:
            st.error(f"Response generation failed: {str(e)}")

else:
    st.warning("Please upload a CSV file to proceed with evaluation")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("### Usage Tips")
st.markdown("""
- **Data Requirements**: Make sure your CSV has the required columns for your selected model type
- **Model Connection**: Test your connection before running evaluations
- **Metrics Selection**: Choose appropriate metrics for your evaluation type
- **Attention Visualization**: Works with local HuggingFace transformer models only
- **API Keys**: Keep your API keys secure and don't share them
- **Model Types**: API models are faster but don't support attention visualization, local models support all features but require more resources
""")

# Add session state info for debugging
with st.expander("Debug Information"):
    st.write("Session State Keys:", list(st.session_state.keys()))
    if 'df' in st.session_state:
        st.write("DataFrame shape:", st.session_state.df.shape)
        st.write("DataFrame columns:", list(st.session_state.df.columns))
    st.write("Selected Model Config:", selected_model_config)
    st.write("Model Connected:", model_connected)
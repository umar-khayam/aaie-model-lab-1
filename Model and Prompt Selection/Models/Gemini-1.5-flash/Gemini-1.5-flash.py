# %%
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

# %%
import json
import os

data = {}

# %%
for file_name in os.listdir('/content'):
    if file_name.endswith('.json') and os.path.isfile(os.path.join('/content', file_name)):
        with open(os.path.join('/content', file_name), 'r') as f:
            key = os.path.splitext(file_name)[0]
            data[key] = json.load(f)

display(data)

# %%
for domain, domain_data in data.items():
    prompt = domain_data['prompt']
    rubric = domain_data['rubric']

    for submission in domain_data['submissions']:
        submission_text = submission['final_submission']

        # Construct the prompt for OpenRouter using the chat format
        messages = [
            {"role": "system", "content": f"Domain: {domain_data['domain']}\nPrompt given to student: {prompt}\nRubric: {rubric}"},
            {"role": "user", "content": f"Student Submission: {submission_text}\n\nGenerate feedback for the student submission based on the provided rubric."}
        ]

        try:
            # Use the OpenAI client initialized for OpenRouter
            response = client.chat.completions.create(
                model="google/gemini-flash-1.5",  # Specify the model you want to use via OpenRouter
                messages=messages
            )
            feedback = response.choices[0].message.content
            print(f"Generated feedback for {domain} submission:")
            print(feedback)
            submission['zsl_feedback'] = feedback
        except Exception as e:
            print(f"Error generating feedback for {domain} submission: {e}")
            submission['zsl_feedback'] = f"Error generating feedback: {e}"

display(data)

# %%
if data: # Check if data is loaded
    # Generate synthetic examples for FSL outside the dataset
    fsl_examples = [
        {"final_submission": "I found a Hand written letter in my grandmother's attic. It's a bit faded but you can still read most of it. The letter consists of the memories she made with our family and how much she loves me as her only grandchild.", "label_type": "Human"},
        {"final_submission": "Yesterday I went to Queen Victoria Market with my roommates. We tried Turkish delight, and I bought some groceries for my room. It was such a good day, i enjoyed alot.", "label_type": "Human"},
        {"final_submission": "I missed my train this morning because I did'nt heard the alarm, and then it started raining as I walked to uni. Honestly, Mondays are annoying.", "label_type": "Human"},
        {"final_submission": "Artificial intelligence has transformed multiple industries, including healthcare, finance, and education, by enabling automation, predictive analytics, and personalized recommendations.", "label_type": "AI"},
        {"final_submission": "The rapid advancement of machine learning models highlights the importance of ethical considerations, including bias mitigation, explainability, and fairness across diverse populations.", "label_type": "AI"},
        {"final_submission": "The impact of climate change on global ecosystems is a complex issue with far-reaching consequences. Scientific models predict a significant increase in average global temperatures, leading to rising sea levels, more frequent extreme weather events, and disruptions to biodiversity. While some argue for immediate, drastic measures to reduce carbon emissions, others emphasize the need for technological innovation and adaptation strategies.", "label_type": "AI"},
        {"final_submission": "I was so nervous before my job interview, but once I started talking it went smoothly. Communication is a fundamental skill that helps establish trust and credibility in professional environments.", "label_type": "Hybrid"},
        {"final_submission": "Last night I cooked pasta for the first time and it actually turned out delicious. Cooking at home is also an effective way to save money and improve overall nutritional health.", "label_type": "Hybrid"},
        {"final_submission": "I love playing cricket with my friends on weekends. Team sports are widely recognized for fostering collaboration, leadership, and strategic thinking.", "label_type": "Hybrid"}
    ]


    # Shuffle examples to avoid bias based on order
    import random
    random.shuffle(fsl_examples)

    # Iterate through all domains and their submissions
    all_submissions = []
    for domain_data in data.values():
        all_submissions.extend(domain_data.get('submissions', []))

    for submission in all_submissions:
        submission_text = submission['final_submission']

        messages = [{"role": "system", "content": "You are an AI that classifies text as either Human, Hybrid, or AI generated. Respond only with 'Human', 'Hybrid', or 'AI'."}]

        # Add FSL examples to the prompt
        for example in fsl_examples:
            messages.append({"role": "user", "content": f"Text: {example['final_submission']}\nIs this text Human, Hybrid, or AI?"})
            messages.append({"role": "assistant", "content": example['label_type']})

        messages.append({"role": "user", "content": f"Text: {submission_text}\nIs this text Human, Hybrid, or AI?"})

        try:
            # Use the OpenAI client initialized for OpenRouter
            response = client.chat.completions.create(
                model="google/gemini-flash-1.5",  # Specify the model you want to use via OpenRouter
                messages=messages
            )
            classification = response.choices[0].message.content
            submission['fsl_ai_detection'] = classification
        except Exception as e:
            print(f"Error classifying AI detection submission: {e}")
            submission['fsl_ai_detection'] = f"Error classifying: {e}"

display(data)

# %%
import json

output_data = []

if data:
    for domain, domain_data in data.items():
        if 'submissions' in domain_data:
            # Initialize submission_id counter for the current domain
            submission_id_counter = 1
            for submission in domain_data['submissions']:
                output_entry = {
                    'domain': domain,
                    'original_submission': submission.get('final_submission'),
                    'ground_truth_label': submission.get('label_type'), # Added ground truth label
                    'zsl_feedback': submission.get('zsl_feedback'),
                    'fsl_ai_detection': submission.get('fsl_ai_detection'),
                    'submission_id': submission_id_counter
                }
                output_data.append(output_entry)
                submission_id_counter += 1 # Increment counter for the current domain


output_filename = "gemini-1.5-flash_outputs.json"

with open(output_filename, 'w') as f:
    json.dump(output_data, f, indent=4)

print(f"Outputs saved to {output_filename}")

# %%


# %%


# %%


# %% [markdown]
# # Task
# Adapt the provided Python code to use the OpenRouter API for generating ZSL feedback and performing few-shot AI detection, utilizing the `.json` data provided previously.

# %% [markdown]
# ## Initialize openai client for openrouter
# 
# ### Subtask:
# Uncomment and modify cell `c6a5c3d7` to initialize the `openai.OpenAI` client with the OpenRouter base URL and your OpenRouter API key.
# 

# %% [markdown]
# **Reasoning**:
# The subtask requires modifying cell `c6a5c3d7` to use the OpenRouter API. This involves uncommenting the existing code, setting the correct base URL, and providing the API key.
# 
# 

# %%
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

# The following code for image processing is not needed for the current task and remains commented.
# completion = client.chat.completions.create(
#   extra_body={},
#   model="google/gemini-flash-1.5",
#   messages=[
#     {
#       "role": "user",
#       "content": [
#         {
#           "type": "text",
#           "text": "What is in this image?"
#         },
#         {
#           "type": "image_url",
#           "image_url": {
#             "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
#           }
#         }
#       ]
#     }
#   ]
# )
# print(completion.choices[0].message.content)



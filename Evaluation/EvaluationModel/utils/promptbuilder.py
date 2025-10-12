import json
import pandas as pd
class PromptBuilder:
    def __init__(self, model_type, prompt_path="ultis/genai_prompt.json"):
        self.model_type = model_type
        self.prompt_path = prompt_path
        with open(prompt_path, "r") as f:
            self.templates = json.load(f)[model_type]

    def structure_input_data(self, **kwargs):
        if self.model_type == "feedback_generation":
            return {
                "submission": kwargs.get("text"),
                "Feedback": kwargs.get("generated_texts"),
                "domain": kwargs.get("domain")
            }
        elif self.model_type == "ai_detection":
            return {
                "submission": kwargs.get("text"),
                "label": kwargs.get("label"),
                "prediction": kwargs.get("prediction")
            }
        
    def load_example_format(self):
        example_str = "Example Input:\n"
        for key, value in self.templates.get("example1", {}).get("input", {}).items():
            example_str += f"  {key}: {value}\n"

        example_str += "\nExample Output:\n"
        for key, value in self.templates.get("example1", {}).get("output", {}).items():
            if key != "Reasoning":
                example_str += f"  {key}: {value}\n"
            else:
                example_str += "  Reasoning:\n"
                for crit, reason in value.items():
                    example_str += f"    - {crit}: {reason}\n"
        return example_str
    
    def construct_prompt(self, **kwargs):
        template = self.templates
        input_data = self.structure_input_data(**kwargs)

        # Build criteria string
        criteria_str = "\n".join([f"- {c}: {v}" for c,v in template.get("criteria", {}).items()])
        # Output structure string
        output_structure = json.dumps(template.get("output_structure", {}), indent=2)

        # Example string
        example_str = self.load_example_format()
        sys_prompt = f""" [SYSTEM]
        Given that {template.get('system')} you must strictly follow the criteria: \n
        {criteria_str}
        {example_str}
        """

        user_prompt = f"""[USER] Input data: {input_data} \n Output structure: \n {output_structure}"""
        return sys_prompt, user_prompt
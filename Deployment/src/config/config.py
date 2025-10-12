"""Configuration handler for the application."""
from pathlib import Path
import yaml

class Config:
    def __init__(self):
        self.config_path = Path(__file__).parent / "prompts.yaml"
        self.load_config()

    def load_config(self):
        """Load configuration from YAML file."""
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def get_system_prompt(self, prompt_type: str) -> str:
        """Get system prompt by type.
        
        Args:
            prompt_type: Type of prompt to retrieve (classify, rubric, or feedback)
            
        Returns:
            The system prompt string
        """
        return self.config["system_prompts"].get(prompt_type, "")

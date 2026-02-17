"""
app/core/config.py - Configuration management
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. "
        "Add it to your .env file or set it as an environment variable."
    )
import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "./data")
MOCK = os.getenv("MOCK", "0") == "1"
PROVIDER = os.getenv("PROVIDER", "gemini")
FEWSHOT_MAX = int(os.getenv("FEWSHOT_MAX", "6"))

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "1024"))

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

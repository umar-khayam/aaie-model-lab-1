# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "default_api_key")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

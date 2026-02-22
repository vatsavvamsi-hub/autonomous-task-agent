"""
Configuration for the Autonomous Task Agent.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# ─── LLM Settings ────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ─── Agent Settings ──────────────────────────────────────────────
MAX_STEPS = 10  # Maximum reasoning steps before the agent stops

# ─── Paths ───────────────────────────────────────────────────────
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DATA_DIR = os.path.join(PROJECT_DIR, "sample_data")

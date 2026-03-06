"""Configuration management for ClawCut."""
import os
from dotenv import load_dotenv

load_dotenv()

# Vertex AI
VERTEX_PROJECT = os.getenv("VERTEX_PROJECT")
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")

# Models
MODEL_SCRIPT = "gemini-3-pro-preview"
MODEL_IMAGE = "gemini-3-pro-image-preview"
MODEL_VIDEO = "veo-3.1-generate-001"
MODEL_VIDEO_FAST = "veo-3.1-fast-generate-001"

# ffmpeg
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "/tmp/ffmpeg")
if not os.path.exists(FFMPEG_BIN):
    # fallback to system ffmpeg
    FFMPEG_BIN = "ffmpeg"

# Output
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

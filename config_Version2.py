import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# V2Ray Configuration
SUPPORTED_PROTOCOLS = ["vless", "vmess", "trojan", "shadowsocks", "hysteria", "hysteria2"]

# Rate limiting (requests per minute per user)
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "30"))

# Render deployment settings
PORT = int(os.getenv("PORT", 8000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")  # For Render deployment

# API timeout
API_REQUEST_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", "20"))
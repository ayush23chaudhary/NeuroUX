# Backend configuration file (for future use)
import os
from dotenv import load_dotenv

load_dotenv()

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False") == "True"

# Database Configuration (for Phase 2)
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "neuroux")

# Socket.io Configuration
SOCKET_TIMEOUT = int(os.getenv("SOCKET_TIMEOUT", 60))
SOCKET_PING_INTERVAL = int(os.getenv("SOCKET_PING_INTERVAL", 25))

# Fraud Detection Thresholds
BOT_VELOCITY_THRESHOLD_MS = int(os.getenv("BOT_VELOCITY_THRESHOLD_MS", 200))
SUSPICION_SCORE_THRESHOLD = float(os.getenv("SUSPICION_SCORE_THRESHOLD", 0.7))

# UI Adaptation Thresholds
HIGH_RISK_DENSITY_THRESHOLD = float(os.getenv("HIGH_RISK_DENSITY_THRESHOLD", 0.7))
LOW_RISK_DENSITY_THRESHOLD = float(os.getenv("LOW_RISK_DENSITY_THRESHOLD", 0.2))

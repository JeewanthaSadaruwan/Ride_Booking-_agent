"""Constants and configuration for the vehicle dispatch agent."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Session ID for AWS Strands tracing
SESSION_ID = "vehicle-dispatch-agent-session"

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/ride_booking"
)

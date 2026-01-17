"""OpenAI model configuration for the vehicle dispatch agent."""

import os
from dotenv import load_dotenv
from strands.models.openai import OpenAIModel

# Load environment variables
load_dotenv()

# Create OpenAI model instance
model = OpenAIModel(
    client_args={
        "api_key": os.getenv("OPENAI_API_KEY"),
    },
    model_id="gpt-4o",
    params={
        "max_tokens": 1000,
        "temperature": 0.7,
    }
)

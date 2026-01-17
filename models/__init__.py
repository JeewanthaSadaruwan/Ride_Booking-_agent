"""Models module for the vehicle dispatch agent."""

from .openai_model import create_openai_model, get_model

__all__ = ["create_openai_model", "get_model"]

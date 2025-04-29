"""
Frontegg AI SDK

A Python SDK for interacting with Frontegg AI Agents.
"""

# Re-export components from the core package
from .core import (
    FronteggAiClient,
    FronteggAiClientConfig,
    Environment,
    setup_logger
)

__version__ = "1.0.0"

__all__ = [
    "FronteggAiClient",
    "FronteggAiClientConfig",
    "Environment",
    "setup_logger",
] 
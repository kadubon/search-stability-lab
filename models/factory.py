"""Factory for model adapters."""

from __future__ import annotations

from core.config import ModelConfig
from models.base import ModelAdapter
from models.gemini_adapter import GeminiAdapter
from models.local_endpoint_adapter import LocalEndpointAdapter
from models.mock_adapter import MockAdapter


def build_model_adapter(config: ModelConfig) -> ModelAdapter:
    if config.provider == "mock":
        return MockAdapter(config)
    if config.provider == "gemini":
        return GeminiAdapter(config)
    return LocalEndpointAdapter(config)

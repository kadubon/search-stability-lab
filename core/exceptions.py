"""Structured exceptions used across the repository."""

from __future__ import annotations


class SearchStabilityError(Exception):
    """Base exception for repository-specific failures."""


class ConfigError(SearchStabilityError):
    """Raised when configuration files are malformed or incomplete."""


class MissingAssetError(SearchStabilityError):
    """Raised when a required external asset or task slice is unavailable."""


class TaskAssetError(SearchStabilityError):
    """Raised when a task asset bundle exists but is malformed or incomplete."""


class StructuredOutputError(SearchStabilityError):
    """Raised when model output cannot be parsed into the required schema."""


class RetryExhaustedError(StructuredOutputError):
    """Raised after bounded structured-output retries are exhausted."""

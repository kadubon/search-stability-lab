"""Prompt loading helpers."""

from __future__ import annotations

from pathlib import Path


PROMPT_DIR = Path("prompts")


def load_prompt_text(prompt_name: str, version: str) -> str:
    path = PROMPT_DIR / version / f"{prompt_name}.txt"
    return path.read_text(encoding="utf-8").strip()


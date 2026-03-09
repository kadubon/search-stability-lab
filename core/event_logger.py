"""JSONL event logging."""

from __future__ import annotations

import json
from pathlib import Path

from core.structured_models import EventRecord


class EventLogger:
    """Write structured JSONL events."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: EventRecord) -> None:
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.model_dump(mode="json"), sort_keys=True))
            handle.write("\n")

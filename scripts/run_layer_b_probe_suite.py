"""Run one or more Layer B probe configs sequentially."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

DEFAULT_CONFIGS = [
    "configs/experiments/real_tasks_gemini_substitution_probe.yaml",
    "configs/experiments/real_tasks_gemini_compression_probe.yaml",
    "configs/experiments/real_tasks_gemini_reset_probe.yaml",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="*", default=DEFAULT_CONFIGS)
    parser.add_argument("--max-tasks", type=int, default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    for config in args.configs:
        command = [sys.executable, "scripts/run_real_tasks.py", "--config", config]
        if args.max_tasks is not None:
            command.extend(["--max-tasks", str(args.max_tasks)])
        subprocess.run(command, cwd=repo_root, check=True)


if __name__ == "__main__":
    main()

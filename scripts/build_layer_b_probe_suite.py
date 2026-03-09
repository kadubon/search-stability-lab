"""Merge analyzed Layer B final outcomes into a probe-suite bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--final-outcomes", nargs="+", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = [pd.read_csv(path) for path in args.final_outcomes]
    merged = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    merged.to_csv(output_dir / "final_outcomes.csv", index=False)

    manifest = {
        "suite": args.suite,
        "final_outcomes": args.final_outcomes,
        "row_count": int(len(merged)),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

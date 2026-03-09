"""Validate a Layer B task manifest and all referenced bundled assets."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.config import load_task_manifest
from tasks.asset_bundle import load_task_asset_bundle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="tasks/manifests/frozen_task_slice_v3.yaml")
    args = parser.parse_args()

    manifest = load_task_manifest(args.manifest)
    for task in manifest.tasks:
        bundle = load_task_asset_bundle(task)
        print(f"{task.task_id}: OK ({bundle.bundle_id})")


if __name__ == "__main__":
    main()

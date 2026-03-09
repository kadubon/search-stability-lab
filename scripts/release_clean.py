"""Remove disposable caches and local runtime leftovers before packaging."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


CACHE_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
CACHE_FILE_SUFFIXES = {".pyc", ".pyo"}
OPTIONAL_TEMP_DIR_NAMES = {"tmp", "temp", "logs", "local_logs"}


def collect_cleanup_targets(root: Path, *, include_optional_temps: bool = False) -> list[Path]:
    targets: list[Path] = []
    for path in root.rglob("*"):
        if path.name in CACHE_DIR_NAMES and path.is_dir():
            targets.append(path)
            continue
        if path.suffix.lower() in CACHE_FILE_SUFFIXES and path.is_file():
            targets.append(path)
            continue
        if include_optional_temps and path.name in OPTIONAL_TEMP_DIR_NAMES and path.is_dir():
            targets.append(path)
    return sorted(set(targets))


def release_clean(root: Path, *, dry_run: bool = False, include_optional_temps: bool = False) -> list[str]:
    targets = collect_cleanup_targets(root, include_optional_temps=include_optional_temps)
    actions: list[str] = []
    for target in targets:
        relative = target.relative_to(root).as_posix()
        if dry_run:
            actions.append(f"would_remove:{relative}")
            continue
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        elif target.exists():
            target.unlink()
        actions.append(f"removed:{relative}")
    return actions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-optional-temps", action="store_true")
    args = parser.parse_args()

    actions = release_clean(
        Path(args.root),
        dry_run=args.dry_run,
        include_optional_temps=args.include_optional_temps,
    )
    for action in actions:
        print(action)
    if not actions:
        print("nothing_to_clean")


if __name__ == "__main__":
    main()

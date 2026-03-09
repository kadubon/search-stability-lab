"""Scan the working tree for common public-release safety problems."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


LOCAL_PATH_PATTERN = re.compile(r"C:/Users/|C:\\Users\\|/Users/|/home/")
SECRET_PATTERN = re.compile(r"(AIza[0-9A-Za-z\-_]{20,}|sk-[0-9A-Za-z]{20,})")
USERNAME_PATH_PATTERN = re.compile(r"(Users[/\\][A-Za-z0-9._-]+|home/[A-Za-z0-9._-]+)")
IGNORED_DIR_PARTS_DEV = {"__pycache__", ".git", "artifacts"}
IGNORED_DIR_PARTS_RELEASE = {"__pycache__", ".git"}
IGNORED_FILES = {"scripts/check_public_safety.py"}


def is_public_text_file(path: Path) -> bool:
    return path.suffix.lower() in {
        ".md",
        ".txt",
        ".py",
        ".yaml",
        ".yml",
        ".json",
        ".jsonl",
        ".csv",
        ".toml",
        ".cff",
        ".tex",
        ".sh",
        ".ps1",
    }


def scan_repo(root: Path, *, mode: str = "dev") -> list[str]:
    findings: list[str] = []
    ignored_dir_parts = IGNORED_DIR_PARTS_RELEASE if mode == "release" else IGNORED_DIR_PARTS_DEV
    if (root / ".env").exists():
        findings.append("Real .env file is present in the working tree.")
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_dir_parts for part in path.parts):
            continue
        if path.as_posix() in IGNORED_FILES:
            continue
        if path.name.startswith(".env") and path.name != ".env.example":
            findings.append(f"Unsafe env-style file present: {path.as_posix()}")
            continue
        if not is_public_text_file(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if LOCAL_PATH_PATTERN.search(text):
            findings.append(f"Local absolute path found: {path.as_posix()}")
        if USERNAME_PATH_PATTERN.search(text):
            findings.append(f"User or machine path fragment found: {path.as_posix()}")
        if SECRET_PATTERN.search(text):
            findings.append(f"Secret-like token found: {path.as_posix()}")
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--mode", choices=["dev", "release"], default="dev")
    args = parser.parse_args()
    findings = scan_repo(Path(args.root), mode=args.mode)
    if findings:
        for item in findings:
            print(item)
        sys.exit(1)
    print(f"OK ({args.mode})")


if __name__ == "__main__":
    main()

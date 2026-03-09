"""Deterministic family proxy construction for Layer B."""

from __future__ import annotations

from collections import OrderedDict

from core.config import TaskManifestEntry


def family_proxy_key(task: TaskManifestEntry) -> str:
    if task.proxy_family_hint:
        return task.proxy_family_hint.strip().lower()
    if task.target_files:
        return "|".join(sorted(path.strip().lower() for path in task.target_files))
    first_sentence = task.issue_summary.split(".", maxsplit=1)[0].strip().lower()
    return first_sentence.replace(" ", "-")


def derived_family_candidates(task: TaskManifestEntry) -> list[str]:
    ordered = OrderedDict[str, None]()
    ordered[family_proxy_key(task)] = None
    for path in task.target_files:
        ordered[path.split("/")[-1].split(".")[0].lower()] = None
    for token in task.issue_summary.lower().replace(",", " ").split():
        if len(token) >= 5:
            ordered[token.strip(".")] = None
        if len(ordered) >= 4:
            break
    return list(ordered.keys())[:4]


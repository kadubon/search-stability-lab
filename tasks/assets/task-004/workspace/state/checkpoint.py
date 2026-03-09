"""Checkpoint resume logic for the bundled Layer B micro-task."""


def choose_resume_path(has_clean_resume: bool, has_legacy_chain: bool) -> str:
    if has_clean_resume:
        return "resume-clean"
    if has_legacy_chain:
        return "resume-legacy"
    return "bootstrap"

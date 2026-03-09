from state.checkpoint import choose_resume_path


def test_choose_resume_path_prefers_clean_resume() -> None:
    assert choose_resume_path(has_clean_resume=True, has_legacy_chain=True) == "resume-clean"

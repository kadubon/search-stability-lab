from __future__ import annotations

from pathlib import Path

from scripts.check_public_safety import scan_repo
from scripts.release_clean import collect_cleanup_targets, release_clean


def test_release_clean_dry_run_and_cleanup(tmp_path: Path) -> None:
    cache_dir = tmp_path / "pkg" / "__pycache__"
    cache_dir.mkdir(parents=True)
    cache_file = cache_dir / "module.pyc"
    cache_file.write_text("x", encoding="utf-8")

    dry_run_actions = release_clean(tmp_path, dry_run=True)
    assert any("__pycache__" in action for action in dry_run_actions)
    assert cache_dir.exists()

    release_clean(tmp_path, dry_run=False)
    assert not cache_dir.exists()


def test_release_scan_includes_artifacts(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    unsafe_path = "C:" + "/" + "Users" + "/example/secret"
    (artifact_dir / "unsafe.md").write_text(unsafe_path, encoding="utf-8")

    dev_findings = scan_repo(tmp_path, mode="dev")
    release_findings = scan_repo(tmp_path, mode="release")

    assert dev_findings == []
    assert any("artifacts/unsafe.md" in finding or "artifacts\\unsafe.md" in finding for finding in release_findings)


def test_collect_cleanup_targets_can_include_optional_temps(tmp_path: Path) -> None:
    (tmp_path / "local_logs").mkdir()
    targets = collect_cleanup_targets(tmp_path, include_optional_temps=True)
    assert any(path.name == "local_logs" for path in targets)

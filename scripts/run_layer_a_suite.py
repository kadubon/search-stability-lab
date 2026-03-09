"""Run the Layer A hypothesis suite reproducibly."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_CONFIGS = [
    "configs/experiments/layer_a_h1_budget_threshold_gemini.yaml",
    "configs/experiments/layer_a_h2_substitution_gemini.yaml",
    "configs/experiments/layer_a_h3_h4_compression_gemini.yaml",
    "configs/experiments/layer_a_h5_reset_gemini.yaml",
]


def _run_command(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip().splitlines()[-1].strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="*", default=DEFAULT_CONFIGS)
    parser.add_argument("--max-conditions", type=int, default=None)
    parser.add_argument("--max-episodes", type=int, default=None)
    parser.add_argument("--output", default="artifacts/layer_a_suite")
    args = parser.parse_args()

    suite_dir = REPO_ROOT / args.output
    suite_dir.mkdir(parents=True, exist_ok=True)
    suite_records: list[dict[str, object]] = []
    for config in args.configs:
        run_command = [sys.executable, "scripts/run_simulator.py", "--config", config]
        if args.max_conditions is not None:
            run_command += ["--max-conditions", str(args.max_conditions)]
        if args.max_episodes is not None:
            run_command += ["--max-episodes", str(args.max_episodes)]
        run_output_dir = _run_command(run_command, REPO_ROOT)
        analysis_output_dir = f"{run_output_dir}/analysis"
        _run_command(
            [
                sys.executable,
                "scripts/analyze_results.py",
                "--input-dir",
                run_output_dir,
                "--output-dir",
                analysis_output_dir,
            ],
            REPO_ROOT,
        )
        suite_records.append(
            {
                "config": config,
                "run_output_dir": run_output_dir,
                "analysis_output_dir": analysis_output_dir,
            }
        )

    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "configs": args.configs,
        "max_conditions": args.max_conditions,
        "max_episodes": args.max_episodes,
        "runs": suite_records,
    }
    manifest_path = suite_dir / "suite_manifest.json"
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()

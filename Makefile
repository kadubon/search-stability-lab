PYTHON ?= python

.PHONY: smoke-sim smoke-mock analyze status assets safety release-safety release-clean-dry release-clean test

smoke-sim:
	$(PYTHON) scripts/run_simulator.py --config configs/experiments/pilot.yaml --max-conditions 1 --max-episodes 1 --controllers C0

smoke-mock:
	$(PYTHON) scripts/run_real_tasks.py --config configs/experiments/real_tasks.yaml --max-tasks 1 --controllers C0

analyze:
	$(PYTHON) scripts/analyze_results.py --input-dir artifacts --output-dir artifacts/analysis

status:
	$(PYTHON) scripts/generate_status_summary.py

assets:
	$(PYTHON) scripts/validate_task_assets.py --manifest tasks/manifests/frozen_task_slice_v3.yaml

safety:
	$(PYTHON) scripts/check_public_safety.py --mode dev

release-safety:
	$(PYTHON) scripts/check_public_safety.py --mode release

release-clean-dry:
	$(PYTHON) scripts/release_clean.py --dry-run

release-clean:
	$(PYTHON) scripts/release_clean.py

test:
	$(PYTHON) -m pytest -q

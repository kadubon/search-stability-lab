# Reproducibility Checklist

## Freeze the comparison block

- fix one backbone model ID per comparison block
- freeze controller configs
- freeze the experiment config file
- freeze the task manifest or simulator grid

## Record run identity

- log the seed
- log the prompt version
- log the model ID
- log the controller ID
- log the layer
- log the code revision

## Preserve scope distinctions

- keep exact (simulator) and proxy (task harness) quantities separate
- do not rewrite Layer B proxies as exact truths
- preserve negative and mixed results

## Environment setup

- use `.env.example` only as a template
- keep secrets in local `.env`, never in tracked files
- run `python -m pip install -r requirements.txt`

## Safe reruns

- simulator smoke:
  `python scripts/run_simulator.py --config configs/experiments/pilot.yaml --max-conditions 1 --max-episodes 1 --controllers C0`
- local mock e2e:
  `python scripts/run_real_tasks.py --config configs/experiments/real_tasks.yaml --max-tasks 1 --controllers C0`
- public-safety scan:
  `python scripts/check_public_safety.py --mode dev`
- release-safety scan:
  `python scripts/check_public_safety.py --mode release`
- release-clean dry run:
  `python scripts/release_clean.py --dry-run`
- release-clean apply:
  `python scripts/release_clean.py`
- current status regeneration:
  `python scripts/generate_status_summary.py`

## Before zipping or publishing

- run release cleanup to remove caches and bytecode
- run the release safety scan so `artifacts/` are checked too
- preserve scientific artifacts unless they are clearly disposable local smoke outputs

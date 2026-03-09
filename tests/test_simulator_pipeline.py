from __future__ import annotations

import json

from controllers.factory import build_controller
from core.config import load_controller_config, load_model_config, load_simulator_experiment
from core.event_logger import EventLogger
from simulator.engine import run_episode
from simulator.scenarios import expand_conditions


def test_simulator_episode_smoke(tmp_path) -> None:
    experiment = load_simulator_experiment("configs/experiments/pilot.yaml")
    model_config = load_model_config(experiment.model_path)
    controller = build_controller(load_controller_config("configs/controllers/c5.yaml"))
    condition = expand_conditions(experiment)[0]
    logger = EventLogger(tmp_path / "events.jsonl")

    outcome = run_episode(
        run_id="test-run",
        seed=123,
        episode_id="episode-1",
        condition=condition,
        controller=controller,
        model_config=model_config,
        logger=logger,
        families_range=experiment.families_range,
        routes_per_family_range=experiment.routes_per_family_range,
        prompt_version=model_config.prompt_version,
    )

    assert "success_final" in outcome
    assert outcome["controller_id"] == "C5"
    lines = (tmp_path / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 2
    first_event = json.loads(lines[0])
    last_event = json.loads(lines[-1])
    assert first_event["event_type"] == "episode_start"
    assert last_event["event_type"] == "episode_end"
    assert last_event["adequate_family_ids_true"]


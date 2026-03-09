"""Episode generation utilities."""

from __future__ import annotations

from typing import Iterable

import numpy as np

from simulator.types import EpisodeState, FamilyState, RouteState, SimulatorCondition


def _sample_adequate_families(
    family_ids: list[str], rng: np.random.Generator
) -> list[str]:
    adequate_count = int(rng.integers(1, max(2, len(family_ids) // 2 + 1)))
    selected = sorted(rng.choice(family_ids, size=adequate_count, replace=False).tolist())
    return selected


def _initial_active_set(
    route_ids: Iterable[str],
    routes: dict[str, RouteState],
    budget_cap: float,
) -> tuple[list[str], list[str]]:
    ranked = sorted(route_ids, key=lambda route_id: routes[route_id].local_promise, reverse=True)
    active: list[str] = []
    used = 0.0
    for route_id in ranked:
        cost = routes[route_id].retention_cost
        if used + cost <= budget_cap or not active:
            active.append(route_id)
            used += cost
    archived = [route_id for route_id in ranked if route_id not in active]
    return active, archived


def _family_style(adequate: bool, rng: np.random.Generator) -> str:
    if adequate:
        return rng.choice(["buried", "balanced"], p=[0.65, 0.35]).item()
    return rng.choice(["lure", "balanced"], p=[0.65, 0.35]).item()


def generate_episode(
    episode_id: str,
    rng: np.random.Generator,
    condition: SimulatorCondition,
    families_range: tuple[int, int],
    routes_per_family_range: tuple[int, int],
    decision_noise: float,
) -> EpisodeState:
    family_count = int(rng.integers(families_range[0], families_range[1] + 1))
    family_ids = [f"family-{index}" for index in range(family_count)]
    adequate_family_ids = _sample_adequate_families(family_ids, rng)
    families: dict[str, FamilyState] = {}
    routes: dict[str, RouteState] = {}
    route_ids: list[str] = []
    for family_index, family_id in enumerate(family_ids):
        route_count = int(rng.integers(routes_per_family_range[0], routes_per_family_range[1] + 1))
        family_routes: list[str] = []
        adequate = family_id in adequate_family_ids
        style = _family_style(adequate, rng)
        threshold = 0.72 if adequate else 0.9
        for route_index in range(route_count):
            route_id = f"{family_id}-route-{route_index}"
            family_routes.append(route_id)
            route_ids.append(route_id)
            if adequate:
                promise_base = 0.34 if style == "buried" else 0.46
                verification_gain = float(rng.uniform(0.42, 0.62))
                evidence_base = 0.12 if style == "buried" else 0.22
            else:
                promise_base = 0.62 if style == "lure" else 0.44
                verification_gain = float(rng.uniform(0.06, 0.24))
                evidence_base = 0.18 if style == "lure" else 0.2
            local_promise = float(
                np.clip(
                    promise_base - 0.045 * route_index + rng.normal(0.0, 0.08 + decision_noise),
                    0.05,
                    0.99,
                )
            )
            route_cost = float(np.clip(1.45 - 0.22 * route_index + rng.normal(0.0, 0.08), 0.55, 1.6))
            route_verification_gain = float(
                np.clip(
                    verification_gain - 0.03 * route_index + rng.normal(0.0, 0.025),
                    0.04,
                    0.75,
                )
            )
            routes[route_id] = RouteState(
                route_id=route_id,
                family_id=family_id,
                local_promise=local_promise,
                latent_verification_gain=route_verification_gain,
                retention_cost=route_cost,
                overlap_burden=float(rng.uniform(0.2, 1.0) * condition.overlap_scale),
                staleness=0.0,
                inertia=float(rng.uniform(0.0, 0.2)),
                compression_sensitivity=float(rng.uniform(0.28, 0.95)),
                evidence=float(np.clip(evidence_base + rng.normal(0.0, 0.06), 0.02, 0.5)),
                utility_shadow=local_promise,
            )
        families[family_id] = FamilyState(
            family_id=family_id,
            adequate=adequate,
            route_ids=family_routes,
            verification_threshold=threshold,
        )
    active_route_ids, archived_route_ids = _initial_active_set(route_ids, routes, condition.budget_cap)
    for route_id in active_route_ids:
        routes[route_id].active = True
        routes[route_id].recoverable = True
        routes[route_id].ever_active = True
        families[routes[route_id].family_id].represented_once = True
    for route_id in archived_route_ids:
        routes[route_id].recoverable = False
    return EpisodeState(
        episode_id=episode_id,
        step_index=0,
        condition=condition,
        families=families,
        routes=routes,
        adequate_family_ids_true=adequate_family_ids,
        active_route_ids=active_route_ids,
        archived_route_ids=archived_route_ids,
    )

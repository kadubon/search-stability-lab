"""Controller factory."""

from __future__ import annotations

from controllers.base import BaseController
from controllers.policies import CONTROLLER_REGISTRY
from core.config import ControllerConfig


def build_controller(config: ControllerConfig) -> BaseController:
    controller_cls = CONTROLLER_REGISTRY[config.controller_id]
    return controller_cls(config)

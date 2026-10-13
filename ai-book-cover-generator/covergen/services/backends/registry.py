"""Backend registry — maps config name to a constructed backend instance.

Lazy-imports heavy backends so the GUI can start without torch installed.
"""
from __future__ import annotations

import logging

from covergen.config.schema import AppConfig
from covergen.services.backends.base import BaseBackend

log = logging.getLogger(__name__)


def build_backend(config: AppConfig) -> BaseBackend:
    name = config.backend.name

    if name == "mock":
        from covergen.services.backends.mock_backend import MockBackend

        return MockBackend()

    if name in {"sd_local", "sdxl_local"}:
        from covergen.services.backends.diffusers_backend import DiffusersBackend

        return DiffusersBackend(config.backend)

    if name == "onnx_local":
        from covergen.services.backends.onnx_backend import OnnxBackend

        return OnnxBackend(config.backend)

    if name == "remote":
        from covergen.services.backends.remote_backend import RemoteBackend

        return RemoteBackend(config.backend)

    raise ValueError(f"unknown backend: {name!r}")
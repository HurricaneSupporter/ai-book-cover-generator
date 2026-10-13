"""Config loader — merges defaults, user config, and environment overrides."""
from __future__ import annotations

import os
from pathlib import Path

import yaml

from covergen.config.schema import AppConfig

_DEFAULT = Path(__file__).with_name("default.yaml")


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(user_path: Path | None = None) -> AppConfig:
    """Load config: defaults <- user file <- env vars. Validated by schema."""
    data = yaml.safe_load(_DEFAULT.read_text(encoding="utf-8")) or {}

    if user_path is not None:
        if not user_path.exists():
            raise FileNotFoundError(f"config not found: {user_path}")
        user_data = yaml.safe_load(user_path.read_text(encoding="utf-8")) or {}
        data = _deep_merge(data, user_data)

    if env_level := os.environ.get("COVERGEN_LOG_LEVEL"):
        data["log_level"] = env_level
    if env_out := os.environ.get("COVERGEN_OUTPUT_DIR"):
        data["output_dir"] = env_out

    return AppConfig.model_validate(data)
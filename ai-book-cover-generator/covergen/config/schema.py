"""Pydantic schema for covergen configuration.

The schema is the single source of truth for what a valid config looks
like. Loader validates against it; the GUI reads it to populate fields.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class BackendConfig(BaseModel):
    name: Literal["mock", "sd_local", "sdxl_local", "onnx_local", "remote"] = "mock"
    model_path: Path | None = None
    endpoint: HttpUrl | None = None
    api_key_env: str = "COVERGEN_API_KEY"
    steps: int = Field(default=28, ge=1, le=150)
    guidance: float = Field(default=7.0, ge=0.0, le=30.0)
    width: int = Field(default=1024, ge=256, le=4096)
    height: int = Field(default=1536, ge=256, le=4096)
    allow_remote_fetch: bool = False


class LayoutConfig(BaseModel):
    title_font: str = "Cinzel-Bold.ttf"
    author_font: str = "EBGaramond-Regular.ttf"
    title_pt: int = Field(default=96, ge=12, le=400)
    author_pt: int = Field(default=48, ge=8, le=200)
    margin_pct: float = Field(default=0.08, ge=0.0, le=0.4)
    spine_safe_pct: float = Field(default=0.04, ge=0.0, le=0.2)
    title_color: str = "#F5EFE0"
    author_color: str = "#E8DCC0"


class PromptConfig(BaseModel):
    genre: str = "fantasy"
    preset_dir: Path = Path("covergen/models/presets")
    negative: str = "text, watermark, signature, blurry, lowres, deformed hands"


class AppConfig(BaseModel):
    backend: BackendConfig = BackendConfig()
    layout: LayoutConfig = LayoutConfig()
    prompt: PromptConfig = PromptConfig()
    output_dir: Path = Path("outputs")
    cache_dir: Path = Path(".covers-cache")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
"""Prompt builder — merges genre preset with job-specific overrides."""
from __future__ import annotations

from covergen.config.schema import AppConfig
from covergen.models.preset_loader import load_preset


def build_prompt(config: AppConfig, job: "object") -> str:
    """Compose a positive prompt from genre preset + job title/author/extra.

    ``job`` is a ``CoverJob``; typed loosely here to keep core free of the
    dataclass import cycle.
    """
    title = getattr(job, "title", "")
    author = getattr(job, "author", "")
    genre = getattr(job, "genre", config.prompt.genre)
    extra = getattr(job, "extra_prompt", "")

    preset = load_preset(config.prompt.preset_dir, genre)

    parts = [
        preset.style_prefix,
        f"book cover artwork for \"{title}\" by {author}",
        preset.composition,
        preset.lighting,
        preset.palette,
    ]
    if extra:
        parts.append(extra.strip())
    return ", ".join(p for p in parts if p)
"""End-to-end cover pipeline: prompt -> hero image -> composited cover.

The pipeline is backend-agnostic. It calls ``BaseBackend.generate`` for the
artwork, then hands off to the renderer for typography and spine-safe
compositing.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from covergen.config.schema import AppConfig
from covergen.core.prompt_builder import build_prompt
from covergen.core.renderer import composite_cover
from covergen.services.backends.base import BaseBackend, GenerationRequest

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CoverJob:
    title: str
    author: str
    genre: str
    seed: int | None = None
    extra_prompt: str = ""


@dataclass(frozen=True, slots=True)
class CoverResult:
    hero_path: Path
    cover_path: Path
    seed_used: int
    elapsed_ms: int


def run_pipeline(config: AppConfig, backend: BaseBackend, job: CoverJob) -> CoverResult:
    """Generate a hero image and composite a finished cover. Blocking."""
    started = time.perf_counter()

    prompt = build_prompt(config, job)
    seed = job.seed if job.seed is not None else backend.suggest_seed()

    request = GenerationRequest(
        prompt=prompt,
        negative=config.prompt.negative,
        width=config.backend.width,
        height=config.backend.height,
        steps=config.backend.steps,
        guidance=config.backend.guidance,
        seed=seed,
    )

    log.info("generating hero image seed=%s backend=%s", seed, backend.name)
    hero: Image.Image = backend.generate(request)

    hero_path = config.output_dir / f"hero_{seed}.png"
    hero_path.parent.mkdir(parents=True, exist_ok=True)
    hero.save(hero_path, format="PNG")

    cover = composite_cover(hero, config.layout, title=job.title, author=job.author)
    cover_path = config.output_dir / f"cover_{_slug(job.title)}_{seed}.png"
    cover.save(cover_path, format="PNG")

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    log.info("cover written %s in %dms", cover_path, elapsed_ms)

    return CoverResult(hero_path=hero_path, cover_path=cover_path, seed_used=seed, elapsed_ms=elapsed_ms)


def _slug(text: str) -> str:
    keep = [c.lower() if c.isalnum() else "_" for c in text]
    return "".join(keep).strip("_")[:48] or "untitled"
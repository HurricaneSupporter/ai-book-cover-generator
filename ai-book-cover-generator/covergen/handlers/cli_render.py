"""Headless render path — used by ``covergen --cli --prompt ...``."""
from __future__ import annotations

import logging
from pathlib import Path

from covergen.config.schema import AppConfig
from covergen.core.pipeline import CoverJob, run_pipeline
from covergen.services.backends.base import BaseBackend

log = logging.getLogger(__name__)


def run_cli_render(
    config: AppConfig,
    backend: BaseBackend,
    *,
    prompt: str,
    out_dir: Path,
    seed: int | None,
) -> int:
    """Render a single cover from a raw prompt and exit code."""
    config = config.model_copy(update={"output_dir": out_dir})
    job = CoverJob(
        title=prompt[:64] or "Untitled",
        author="covergen",
        genre=config.prompt.genre,
        seed=seed,
        extra_prompt=prompt,
    )
    result = run_pipeline(config, backend, job)
    log.info("cover: %s", result.cover_path)
    return 0
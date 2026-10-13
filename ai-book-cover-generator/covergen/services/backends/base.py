"""Abstract backend contract for covergen.

Every backend implements ``generate(request) -> PIL.Image``. Backends are
responsible for their own model loading and unload; the pipeline only
cares about the returned image.
"""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass

from PIL import Image


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    prompt: str
    negative: str
    width: int
    height: int
    steps: int
    guidance: float
    seed: int


class BaseBackend(ABC):
    """Base class for all covergen generation backends."""

    name: str = "base"

    @abstractmethod
    def generate(self, request: GenerationRequest) -> Image.Image:
        """Return a single RGB image matching ``request`` dimensions."""

    def suggest_seed(self) -> int:
        """Default seed source. Override for deterministic backends."""
        return random.randint(0, 2**31 - 1)

    def close(self) -> None:
        """Release model / device resources. No-op by default."""
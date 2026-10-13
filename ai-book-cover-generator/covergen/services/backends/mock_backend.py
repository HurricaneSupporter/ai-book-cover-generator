"""Deterministic mock backend — no model, no GPU, always available.

Produces a gradient + noise hero image seeded by the request seed. Useful
for CI, for GUI smoke tests, and for developing the layout layer without
a diffusion model installed.
"""
from __future__ import annotations

import hashlib

import numpy as np
from PIL import Image

from covergen.services.backends.base import BaseBackend, GenerationRequest


class MockBackend(BaseBackend):
    name = "mock"

    def generate(self, request: GenerationRequest) -> Image.Image:
        rng = np.random.default_rng(request.seed)
        h, w = request.height, request.width

        # Vertical gradient, palette derived from the prompt hash.
        digest = hashlib.sha256(request.prompt.encode("utf-8")).digest()
        top = np.array([digest[0], digest[1], digest[2]], dtype=np.float32)
        bottom = np.array([digest[3], digest[4], digest[5]], dtype=np.float32)

        ramp = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
        gradient = top[None, None, :] * (1 - ramp) + bottom[None, None, :] * ramp
        image = np.repeat(gradient, w, axis=1)

        noise = rng.normal(0.0, 18.0, size=(h, w, 3)).astype(np.float32)
        image = np.clip(image + noise, 0, 255).astype(np.uint8)

        return Image.fromarray(image, mode="RGB")
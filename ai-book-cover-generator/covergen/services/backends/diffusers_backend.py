"""Local Stable Diffusion / SDXL backend via diffusers.

Loads weights lazily on first call. On CUDA, uses fp16 + attention slicing
to fit SDXL at 1024x1536 on 12GB VRAM. On CPU, forces float32 and warns.
"""
from __future__ import annotations

import logging

from PIL import Image

from covergen.config.schema import BackendConfig
from covergen.services.backends.base import BaseBackend, GenerationRequest

log = logging.getLogger(__name__)


class DiffusersBackend(BaseBackend):
    name = "sdxl_local"

    def __init__(self, cfg: BackendConfig) -> None:
        self.cfg = cfg
        self._pipe = None

    def _load(self):
        import torch
        from diffusers import StableDiffusionXLPipeline

        if self.cfg.model_path is None:
            raise ValueError("backend.model_path is required for sdxl_local")

        use_cuda = torch.cuda.is_available()
        dtype = torch.float16 if use_cuda else torch.float32
        log.info("loading SDXL from %s (cuda=%s, dtype=%s)", self.cfg.model_path, use_cuda, dtype)

        pipe = StableDiffusionXLPipeline.from_pretrained(
            str(self.cfg.model_path), torch_dtype=dtype, variant="fp16" if use_cuda else None
        )
        pipe = pipe.to("cuda" if use_cuda else "cpu")
        if use_cuda:
            pipe.enable_attention_slicing()
            pipe.enable_vae_slicing()
        self._pipe = pipe

    def generate(self, request: GenerationRequest) -> Image.Image:
        if self._pipe is None:
            self._load()
        assert
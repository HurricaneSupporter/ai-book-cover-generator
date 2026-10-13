"""Cover compositor — typography, scrim, spine-safe margins.

Takes a hero image and produces a finished cover with title block and
author line. Fonts are resolved from the system font dir; missing fonts
fall back to Pillow's bundled default so the pipeline never hard-fails.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from covergen.config.schema import LayoutConfig
from covergen.utils.paths import font_search_dirs

log = logging.getLogger(__name__)


def composite_cover(hero: Image.Image, layout: LayoutConfig, *, title: str, author: str) -> Image.Image:
    """Overlay typography on the hero image. Returns a new RGB image."""
    base = hero.convert("RGB")
    width, height = base.size
    margin_x = int(width * layout.margin_pct)
    spine = int(width * layout.spine_safe_pct)

    scrim = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_scrim = ImageDraw.Draw(scrim)
    band_top = int(height * 0.58)
    for y in range(band_top, height):
        alpha = int(180 * ((y - band_top) / max(1, height - band_top)) ** 1.4)
        draw_scrim.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    base = Image.alpha_composite(base.convert("RGBA"), scrim).convert("RGB")

    draw = ImageDraw.Draw(base)
    title_font = _load_font(layout.title_font, layout.title_pt)
    author_font = _load_font(layout.author_font, layout.author_pt)

    title_lines = _wrap(title, draw, title_font, width - 2 * margin_x - spine)
    line_h = _line_height(title_font)
    block_h = line_h * len(title_lines) + int(layout.author_pt * 1.6)
    y = height - int(height * 0.10) - block_h

    for line in title_lines:
        w = draw.textlength(line, font=title_font)
        x = margin_x + spine + max(0, (width - 2 * margin_x - spine - w) // 2)
        draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0))
        draw.text((x, y), line, font=title_font, fill=layout.title_color)
        y += line_h

    y += int(layout.author_pt * 0.4)
    author_w = draw.textlength(author, font=author_font)
    ax = margin_x + spine + max(0, (width - 2 * margin_x - spine - author_w) // 2)
    draw.text((ax + 2, y + 2), author, font=author_font, fill=(0, 0, 0))
    draw.text((ax, y), author, font=author_font, fill=layout.author_color)

    return base


def _load_font(name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for directory in font_search_dirs():
        candidate = Path(directory) / name
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except OSError:
                continue
    log.warning("font %s not found, using default", name)
    return ImageFont.load_default()


def _wrap(text: str, draw: ImageDraw.ImageDraw, font, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _line_height(font) -> int:
    try:
        ascent, descent = font.getmetrics()
        return ascent + descent
    except AttributeError:
        return getattr(font, "size", 24) + 6
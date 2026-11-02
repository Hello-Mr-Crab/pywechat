"""Conservative image views for tiny contact-panel text."""

from __future__ import annotations

from PIL import Image, ImageEnhance, ImageOps


def recognition_views(image: Image.Image) -> tuple[Image.Image, Image.Image]:
    """Return independent 2x source and 2x grayscale/contrast views.

    No thresholding or morphology is used: thin underscores, hyphens and
    glyph strokes must survive preprocessing.
    """
    rgb = image.convert("RGB")
    size = (max(1, rgb.width * 2), max(1, rgb.height * 2))
    view_a = rgb.resize(size, Image.Resampling.LANCZOS)
    view_b = ImageEnhance.Contrast(ImageOps.grayscale(rgb)).enhance(1.35)
    return view_a, view_b.resize(size, Image.Resampling.LANCZOS)

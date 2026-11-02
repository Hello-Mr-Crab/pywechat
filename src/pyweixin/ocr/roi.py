"""Window-relative fallback profile ROI calculations."""

from __future__ import annotations

from .config import DEFAULT_CONFIG, WeChatIdOcrConfig


def fallback_profile_roi(
    rect, config: WeChatIdOcrConfig | None = None
) -> tuple[int, int, int, int] | None:
    """Map normalized panel bounds onto a window rectangle; return None if empty."""
    cfg = config or DEFAULT_CONFIG
    width, height = rect.right - rect.left, rect.bottom - rect.top
    if width <= 0 or height <= 0:
        return None
    return (
        rect.left + int(width * cfg.roi_fallback_left_ratio),
        rect.top + int(height * cfg.roi_fallback_top_ratio),
        rect.left + int(width * cfg.roi_fallback_right_ratio),
        rect.top + int(height * cfg.roi_fallback_bottom_ratio),
    )

"""PII masking for WeChat IDs.

A WeChat ID is a durable personal identifier. Nothing in this package logs
one in full: every diagnostic, every review row and every smoke-test line
goes through :func:`mask_wechat_id` first. Full values are written only to
the export files the user explicitly asked for, or to an opt-in debug dump.
"""

from __future__ import annotations

_MASK = "***"


def mask_wechat_id(value: str | None) -> str:
    """Return a masked form safe for logs, e.g. ``abc_123`` -> ``ab***23``.

    Values short enough that revealing the ends would reveal the whole are
    masked entirely. Empty/None becomes an empty string so callers can log
    the result unconditionally.
    """
    if not value:
        return ""
    text = str(value)
    if len(text) <= 4:
        return "*" * len(text)
    return f"{text[:2]}{_MASK}{text[-2:]}"

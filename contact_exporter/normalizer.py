"""Normalize raw pyweixin contact dicts into Contact models.

Responsibilities:
  - map Chinese keys -> canonical English fields
  - coerce upstream '无'/None/'' sentinels to empty string
  - optionally deduplicate (by wechat_id, falling back to nickname+region)
  - never fail on a single missing field (PRD: leave empty, do not terminate)
"""
from __future__ import annotations

from typing import Any

from .models import Contact, EMPTY_SENTINELS, EXPORT_FIELDS, KEY_MAP


def _clean(value: Any) -> str:
    """Coerce a raw upstream value to a clean string; sentinels -> ''."""
    if value is None:
        return ""
    text = str(value).strip()
    if text in EMPTY_SENTINELS:
        return ""
    return text


def normalize_one(raw: dict[str, Any], exported_at: str) -> Contact:
    """Map a single raw dict to a Contact (no dedup)."""
    fields: dict[str, str] = {en: "" for en in EXPORT_FIELDS if en != "exported_at"}
    fields["exported_at"] = exported_at
    for cn_key, en_key in KEY_MAP.items():
        if cn_key in raw:
            fields[en_key] = _clean(raw[cn_key])
    return Contact(**fields)


def _dedup_key(c: Contact) -> tuple:
    """Build a stable identity for dedup; prefer wechat_id over name."""
    if c.wechat_id:
        return ("wx", c.wechat_id)
    return ("name", c.nickname, c.remark, c.region)


def normalize(
    raw_contacts: list[dict[str, Any]],
    exported_at: str,
    deduplicate: bool = True,
) -> list[Contact]:
    """Normalize a list of raw contact dicts into Contact models.

    Args:
        raw_contacts: list of dicts as returned by pyweixin get_friends_detail.
        exported_at: timestamp string stamped onto every contact.
        deduplicate: when True, drop later duplicates (default True).

    Returns:
        Ordered list of normalized Contact objects.
    """
    out: list[Contact] = []
    seen: set[tuple] = set()
    for raw in raw_contacts:
        if not isinstance(raw, dict):
            continue
        contact = normalize_one(raw, exported_at)
        if deduplicate:
            key = _dedup_key(contact)
            if key in seen:
                continue
            seen.add(key)
        out.append(contact)
    return out

"""Contact data model and export field definitions.

Field set is the PRD baseline (PRD_WECHAT_CONTACT_EXPORTER.md §4):
nickname, remark, wechat_id, phone, region, tags, source, exported_at.
New fields must be append-only to keep CSV header stability.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Canonical export field order. Stable; extend only by appending.
EXPORT_FIELDS: list[str] = [
    "nickname",
    "remark",
    "wechat_id",
    "phone",
    "region",
    "tags",
    "source",
    "exported_at",
]

# Mapping from pyweixin get_friends_detail Chinese keys -> export fields.
# Only fields we actually export are mapped; extra upstream keys are ignored.
KEY_MAP: dict[str, str] = {
    "昵称": "nickname",
    "备注": "remark",
    "微信号": "wechat_id",
    "电话": "phone",
    "地区": "region",
    "标签": "tags",
    "来源": "source",
}

# Sentinels the upstream uses for "missing" values; normalized to empty string.
EMPTY_SENTINELS: set = {"无", "", None}


@dataclass
class Contact:
    """A normalized contact record ready for export."""

    nickname: str = ""
    remark: str = ""
    wechat_id: str = ""
    phone: str = ""
    region: str = ""
    tags: str = ""
    source: str = ""
    exported_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        """Return an ordered dict aligned with EXPORT_FIELDS."""
        return {f: getattr(self, f) for f in EXPORT_FIELDS}

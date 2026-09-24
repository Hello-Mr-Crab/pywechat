"""The outcome of one WeChat-ID extraction attempt.

``value`` and ``status`` are deliberately separate. A syntactically valid
string is not the same thing as a confirmed reading, and only a CONFIRMED
result may ever reach the canonical ``wechat_id`` export field.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Status = Literal["CONFIRMED", "NEED_REVIEW", "NOT_FOUND", "OCR_FAILED"]
Source = Literal["ocr", "ocr+uia", "uia", "none"]


@dataclass
class WeChatIdResult:
    """Result of extracting a WeChat ID from one contact profile.

    Attributes:
        value: the candidate string, or None. Present for NEED_REVIEW too,
            so a human reviewer has something to check -- callers must not
            treat a non-None value as trustworthy on its own.
        status: CONFIRMED / NEED_REVIEW / NOT_FOUND / OCR_FAILED.
        source: which path produced the value.
        confidence: lowest per-view confidence among agreeing views, or None.
        ocr_candidates: one entry per OCR view (None where a view found
            nothing), so disagreements are auditable.
        ui_candidate: the UIA-tree candidate, if one was read.
        reason: short machine-ish explanation, e.g. "view_disagreement".
        risky_chars: confusable characters present in ``value``.
        diagnostics: ordered trace of what the extractor did.
    """

    value: str | None = None
    status: Status = "NOT_FOUND"
    source: Source = "none"
    confidence: float | None = None
    ocr_candidates: list[str | None] = field(default_factory=list)
    ui_candidate: str | None = None
    reason: str | None = None
    risky_chars: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)

    @property
    def is_confirmed(self) -> bool:
        """True only for CONFIRMED. The single gate for writing wechat_id."""
        return self.status == "CONFIRMED"

    def to_metadata(self) -> dict[str, object]:
        """Flat dict for CSV/TXT metadata columns. Contains no full ID."""
        return {
            "status": self.status,
            "source": self.source,
            "confidence": "" if self.confidence is None else f"{self.confidence:.3f}",
            "reason": self.reason or "",
        }

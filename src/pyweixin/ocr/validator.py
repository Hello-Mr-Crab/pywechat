"""Syntactic validation and confusable-character detection for WeChat IDs.

Two rules govern this module:

1. **No guessing.** There is deliberately no code here that rewrites
   ``O``->``0``, ``l``->``1``, ``S``->``5`` or ``-``->``_``. A reading is
   either accepted as-is or refused. Silently "fixing" a character is how a
   wrong ID gets written into an export with full confidence.

2. **Valid is not the same as confirmed.** :func:`validate_wechat_id` only
   answers "could this string be a WeChat ID at all?". Whether a reading is
   *correct* is decided by multi-view consensus in ``wechat_id.py``. Keeping
   the two apart is what stops a plausible-looking misread from being
   promoted to CONFIRMED.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .config import RISKY_CHARS, RISKY_SEQUENCES, WeChatIdOcrConfig

# Whitespace and line breaks that OCR may introduce around a value.
_EDGE_WHITESPACE = re.compile(r"^[\s　]+|[\s　]+$")
# Any whitespace left in the middle of a candidate is a refusal, not a join.
_INNER_WHITESPACE = re.compile(r"[\s　]")
# Zero-width and bidirectional-control characters: never legitimate in an ID.
_INVISIBLE = re.compile(r"[​-‏‪-‮⁠-⁤﻿]")


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of syntactic validation, with a reason when it fails."""

    valid: bool
    reason: str | None = None
    value: str | None = None


def strip_label(raw: str, labels: tuple[str, ...]) -> str:
    """Remove a leading WeChat-ID label from a merged OCR token.

    Detectors sometimes return ``微信号：abc_123`` as a single token rather
    than as label and value separately. Only a *leading* label is removed;
    a label appearing mid-string is left alone so that the validator can
    reject the token rather than have us guess at a split point.
    """
    text = raw.strip()
    for label in labels:
        if text.startswith(label):
            return text[len(label) :]
    return text


def normalize_candidate(raw: str | None, labels: tuple[str, ...] = ()) -> str:
    """Trim a raw OCR token into candidate form without altering characters.

    Only removes surrounding whitespace/newlines and an optional leading
    label. Every interior character is preserved exactly as the recogniser
    produced it -- including fullwidth forms and confusable characters,
    which the validator will then reject rather than repair.
    """
    if not raw:
        return ""
    text = _EDGE_WHITESPACE.sub("", str(raw))
    if labels:
        text = strip_label(text, labels)
        text = _EDGE_WHITESPACE.sub("", text)
    return text


def risky_characters(value: str) -> list[str]:
    """Return the confusable characters present in ``value``, deduplicated.

    Detection only. The caller records these for audit; nothing rewrites them.
    """
    if not value:
        return []
    found = [ch for ch in dict.fromkeys(value) if ch in RISKY_CHARS]
    for seq in RISKY_SEQUENCES:
        if seq in value:
            found.append(seq)
    return found


def validate_wechat_id(
    value: str | None, config: WeChatIdOcrConfig | None = None
) -> ValidationResult:
    """Check whether ``value`` could syntactically be a WeChat ID.

    Deliberately conservative. A WeChat ID is 6-20 characters, starts with a
    letter, and contains only ASCII letters, digits, underscore and hyphen.
    Requiring a leading letter is what makes an 11-digit phone number
    impossible to accept, which matters because phone numbers are the most
    likely lookalike elsewhere on the same profile panel.

    Refusals are returned with a reason rather than raising, so that the
    caller can record why a candidate was dropped.
    """
    cfg = config or WeChatIdOcrConfig()
    if value is None:
        return ValidationResult(False, "empty")

    text = value
    if not text:
        return ValidationResult(False, "empty")

    if _INVISIBLE.search(text):
        return ValidationResult(False, "invisible_characters")

    if _INNER_WHITESPACE.search(text):
        # Two tokens joined by a space is not one ID. Refuse rather than
        # concatenate: joining would invent a string that was never seen.
        return ValidationResult(False, "embedded_whitespace")

    if any(ord(ch) > 127 for ch in text):
        # Fullwidth Latin, CJK, or any other non-ASCII. Real WeChat IDs are
        # ASCII; a fullwidth reading is an OCR artifact, so refuse it here
        # instead of normalising it into a plausible-looking value.
        return ValidationResult(False, "non_ascii")

    if not (cfg.wechat_id_min_len <= len(text) <= cfg.wechat_id_max_len):
        return ValidationResult(False, "length_out_of_range")

    if cfg.require_letter_start and not text[0].isascii():
        return ValidationResult(False, "not_ascii_start")
    if cfg.require_letter_start and not text[0].isalpha():
        return ValidationResult(False, "does_not_start_with_letter")

    if not all(ch.isascii() and (ch.isalnum() or ch in "_-") for ch in text):
        return ValidationResult(False, "illegal_character")

    # Reject strings that are all separators or otherwise degenerate.
    if not any(ch.isalnum() for ch in text):
        return ValidationResult(False, "no_alphanumeric")

    return ValidationResult(True, None, text)


def is_normalized_form(value: str) -> bool:
    """True when ``value`` is already in NFKC form.

    Used only for diagnostics: a non-NFKC reading is a hint that the
    recogniser emitted a compatibility character, which is worth surfacing
    even though the validator rejects such values outright.
    """
    return unicodedata.normalize("NFKC", value) == value

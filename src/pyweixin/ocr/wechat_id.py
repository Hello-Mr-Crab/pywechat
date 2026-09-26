"""Spatially anchored, OCR-primary WeChat ID extraction."""

from __future__ import annotations

import re
from typing import Iterable, Sequence

from .config import DEFAULT_CONFIG, WeChatIdOcrConfig
from .engine import OcrToken, get_ocr_engine
from .errors import OcrError
from .preprocess import recognition_views
from .result import WeChatIdResult
from .validator import normalize_candidate, risky_characters, validate_wechat_id

_LABEL = re.compile(
    r"^(?:微信号|微信\s*ID|WeChat\s*ID|Weixin\s*ID)\s*[:：]?\s*(.*)$", re.I
)


def _label_token(text: str) -> tuple[bool, str]:
    match = _LABEL.match(text.strip())
    if not match:
        return False, ""
    return True, match.group(1).strip()


def candidate_near_label(
    tokens: Sequence[OcrToken], config: WeChatIdOcrConfig | None = None
) -> tuple[str | None, float | None]:
    """Choose only the nearest same-line right token, or a nearby next-line token."""
    cfg = config or DEFAULT_CONFIG
    choices: list[tuple[int, float, str, float]] = []
    for label in tokens:
        is_label, inline = _label_token(label.text)
        if not is_label:
            continue
        if inline:
            value = normalize_candidate(inline, cfg.labels)
            if value:
                choices.append((0, 0.0, value, label.confidence))
        for value_token in tokens:
            if value_token is label:
                continue
            value = normalize_candidate(value_token.text, cfg.labels)
            if not value:
                continue
            vertical = abs(value_token.center_y - label.center_y)
            if (
                value_token.left >= label.right
                and vertical
                <= max(label.height, value_token.height) * cfg.line_tolerance_ratio
            ):
                gap = value_token.left - label.right
                if gap <= label.height * cfg.max_horizontal_gap_ratio:
                    choices.append(
                        (0, gap, value, min(label.confidence, value_token.confidence))
                    )
            elif value_token.top >= label.bottom:
                gap = value_token.top - label.bottom
                if (
                    gap <= label.height * cfg.max_line_gap_ratio
                    and abs(value_token.left - label.left) <= label.width * 1.5
                ):
                    choices.append(
                        (1, gap, value, min(label.confidence, value_token.confidence))
                    )
    if not choices:
        return None, None
    choices.sort(key=lambda item: (item[0], item[1]))
    # Multiple equally placed values are ambiguous; never concatenate them.
    best = choices[0]
    tied = [item for item in choices if item[:2] == best[:2]]
    if len({item[2] for item in tied}) > 1:
        return None, None
    return best[2], best[3]


def extract_wechat_id_from_uia(
    texts: Iterable[str], config: WeChatIdOcrConfig | None = None
) -> str | None:
    """Read a UIA label/value pair for secondary verification only."""
    values = list(texts)
    cfg = config or DEFAULT_CONFIG
    for index, text in enumerate(values):
        is_label, inline = _label_token(str(text))
        if is_label:
            candidate = inline or (
                str(values[index + 1]).strip() if index + 1 < len(values) else ""
            )
            candidate = normalize_candidate(candidate, cfg.labels)
            if validate_wechat_id(candidate, cfg).valid:
                return candidate
    return None


class WeChatIdExtractor:
    def __init__(self, engine=None, config: WeChatIdOcrConfig | None = None):
        self.config = config or DEFAULT_CONFIG
        self._engine = engine

    def extract(self, image, *, ui_candidate: str | None = None) -> WeChatIdResult:
        if not self.config.ocr_enabled or not self.config.ocr_primary:
            return WeChatIdResult(status="OCR_FAILED", reason="ocr_primary_disabled")
        candidates: list[str | None] = []
        scores: list[float | None] = []
        try:
            engine = self._engine or get_ocr_engine(self.config)
            for view in recognition_views(image):
                value, score = candidate_near_label(engine.recognize(view), self.config)
                if value and not validate_wechat_id(value, self.config).valid:
                    value = None
                candidates.append(value)
                scores.append(score)
        except OcrError as exc:
            return WeChatIdResult(
                status="OCR_FAILED",
                source="none",
                ui_candidate=ui_candidate,
                reason=exc.code,
                diagnostics=["OCR_FAILED"],
            )
        except Exception:
            return WeChatIdResult(
                status="OCR_FAILED",
                source="none",
                ui_candidate=ui_candidate,
                reason="OCR_INFERENCE_FAILED",
                diagnostics=["OCR_FAILED"],
            )
        return reconcile_ocr_result(
            WeChatIdResult(
                ocr_candidates=candidates,
                confidence=min(
                    (score for score in scores if score is not None), default=None
                ),
            ),
            ui_candidate,
            self.config,
        )


def reconcile_ocr_result(
    ocr_result: WeChatIdResult,
    ui_candidate: str | None,
    config: WeChatIdOcrConfig | None = None,
) -> WeChatIdResult:
    """Apply UIA only after the OCR-first result has been computed."""
    cfg = config or DEFAULT_CONFIG
    if ocr_result.status == "OCR_FAILED":
        return WeChatIdResult(
            status="OCR_FAILED",
            source="uia" if ui_candidate else "none",
            ui_candidate=ui_candidate,
            reason=ocr_result.reason,
            diagnostics=["OCR_FAILED"],
        )
    candidates = ocr_result.ocr_candidates
    if len(candidates) != 2:
        return WeChatIdResult(
            status="OCR_FAILED",
            source="none",
            reason="OCR_INFERENCE_FAILED",
            diagnostics=["OCR_FAILED"],
        )
    scores = [ocr_result.confidence]
    if not any(candidates):
        if ui_candidate:
            return WeChatIdResult(
                value=ui_candidate,
                status="NEED_REVIEW",
                source="uia",
                ui_candidate=ui_candidate,
                reason="uia_only",
                diagnostics=["UIA_CANDIDATE", "NEED_REVIEW"],
            )
        return WeChatIdResult(status="NOT_FOUND", reason="label_or_value_not_found")
    if candidates[0] != candidates[1]:
        return WeChatIdResult(
            value=None,
            status="NEED_REVIEW",
            source="ocr+uia" if ui_candidate else "ocr",
            confidence=None,
            ocr_candidates=candidates,
            ui_candidate=ui_candidate,
            reason="view_disagreement",
            diagnostics=["OCR_DISAGREEMENT", "NEED_REVIEW"],
        )
    value = candidates[0]
    assert value is not None
    confidence = min((score for score in scores if score is not None), default=None)
    if ui_candidate and ui_candidate != value:
        return WeChatIdResult(
            value=None,
            status="NEED_REVIEW",
            source="ocr+uia",
            confidence=confidence,
            ocr_candidates=candidates,
            ui_candidate=ui_candidate,
            reason="uia_mismatch",
            diagnostics=["CROSS_CHECK_MISMATCH", "NEED_REVIEW"],
        )
    if confidence is not None and confidence >= cfg.min_confidence_confirm:
        return WeChatIdResult(
            value=value,
            status="CONFIRMED",
            source="ocr+uia" if ui_candidate else "ocr",
            confidence=confidence,
            ocr_candidates=candidates,
            ui_candidate=ui_candidate,
            risky_chars=risky_characters(value),
            reason="multi_view_consensus",
            diagnostics=["CROSS_CHECK_MATCH"] if ui_candidate else ["OCR_CANDIDATE"],
        )
    if confidence is not None and ui_candidate == value:
        return WeChatIdResult(
            value=value,
            status="CONFIRMED",
            source="ocr+uia",
            confidence=confidence,
            ocr_candidates=candidates,
            ui_candidate=ui_candidate,
            risky_chars=risky_characters(value),
            reason="low_confidence_uia_match",
            diagnostics=["CROSS_CHECK_MATCH"],
        )
    return WeChatIdResult(
        value=None,
        status="NEED_REVIEW",
        source="ocr",
        confidence=confidence,
        ocr_candidates=candidates,
        ui_candidate=ui_candidate,
        reason="low_confidence",
        diagnostics=["NEED_REVIEW"],
    )

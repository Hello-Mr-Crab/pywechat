"""Central configuration for WeChat-ID OCR extraction.

Every threshold lives here so that none of them are magic numbers buried in
the extraction logic.

Initial threshold basis: the local synthetic two-view smoke read the known
candidate at 0.9998. The 0.99 threshold leaves margin below that one reading,
but is not calibrated against a representative real-profile dataset.
Confidence alone never confirms a value; both views must agree and syntax
must pass. Retest before changing this threshold.

The default is PP-OCRv6 medium detection and recognition, as the target is a
small, high-value identifier. Do not silently change to a smaller model to
improve speed; measure the target Windows workload and make any tradeoff
explicit.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Labels as they appear in the WeChat profile panel. Mirrors
# pyweixin.Uielements.Special_Labels.WxNum for all three shipped UI
# languages, with the trailing colon optional so that a detector which
# drops the punctuation still anchors correctly.
DEFAULT_LABELS: tuple[str, ...] = (
    "微信号：",
    "微信号:",
    "微信号",
    "WeChat ID:",
    "WeChat ID",
    "Weixin ID:",
    "Weixin ID",
    "微信 ID:",
    "微信 ID",
)

# Characters OCR routinely confuses with one another. Presence of any of
# these does not by itself invalidate a reading -- it marks the reading as
# one where a systematic (multi-view-stable) misread is plausible, so the
# result carries the flag for audit. The code never rewrites these
# characters; see ocr/validator.py.
RISKY_CHARS: frozenset[str] = frozenset("0Oo1Iil5Ss8B2ZG6G9gq-_")

# Multi-character sequences that are visually confusable as a unit.
RISKY_SEQUENCES: tuple[str, ...] = ("rn", "vv", "cl")


@dataclass
class WeChatIdOcrConfig:
    """Configuration for the OCR-primary WeChat-ID extraction path."""

    # --- enablement -------------------------------------------------------
    ocr_enabled: bool = True
    # OCR is the primary source; UIA is only ever a secondary cross-check.
    # Setting this False restores the legacy UIA-only behaviour.
    ocr_primary: bool = True
    uia_secondary: bool = True
    # When True, a value that is not CONFIRMED is never written to the
    # canonical wechat_id field; it is diverted to the review file instead.

    # --- model ------------------------------------------------------------
    ocr_version: str = "PP-OCRv6"
    det_model_type: str = "medium"
    rec_model_type: str = "medium"
    # ONNX Runtime defaults to one thread per core, which on a many-core
    # machine thrashes on small inputs: the medium detector took 91s with
    # defaults vs 12s pinned to 4 threads for identical input.
    intra_op_num_threads: int = 4
    inter_op_num_threads: int = 1
    # Where the .onnx files are cached. None -> RapidOCR's own default,
    # which is inside site-packages; a project-local cache is preferred so
    # the models survive a reinstall and can be pre-seeded for offline use.
    model_root_dir: Path | None = None
    # Run the detector at all. With a tightly cropped ROI this can be
    # disabled to run the recogniser directly on a known text band.
    use_det: bool = True

    # --- multi-pass -------------------------------------------------------
    multi_pass: bool = True

    # --- confidence -------------------------------------------------------
    min_confidence_confirm: float = 0.99

    # --- label anchoring --------------------------------------------------
    labels: tuple[str, ...] = DEFAULT_LABELS
    # Vertical tolerance for "same line", as a fraction of the taller box.
    line_tolerance_ratio: float = 0.6
    # How far below the label a next-line value may sit, in label heights.
    max_line_gap_ratio: float = 2.0
    # How far right of the label a same-line value may start, in label heights.
    max_horizontal_gap_ratio: float = 6.0

    # --- syntactic validation --------------------------------------------
    wechat_id_min_len: int = 6
    wechat_id_max_len: int = 20
    # WeChat IDs must begin with a letter. Requiring it is the conservative
    # choice: it is what keeps an 11-digit phone number from ever validating.
    require_letter_start: bool = True

    # --- ROI --------------------------------------------------------------
    # Level-2 fallback geometry, as fractions of the WeChat window rect.
    # Used only when the UIA profile panel is unavailable. Ratios, never
    # absolute pixels, so the same values hold at 100%/125%/150% DPI and
    # for windowed or maximised windows.
    roi_fallback_left_ratio: float = 0.50
    roi_fallback_right_ratio: float = 0.99
    roi_fallback_top_ratio: float = 0.06
    roi_fallback_bottom_ratio: float = 0.60

    def model_label(self) -> str:
        """Human-readable model identifier for logs and reports."""
        return f"{self.ocr_version}-det:{self.det_model_type}/rec:{self.rec_model_type}"

    def cache_key(self) -> tuple:
        """Identity of everything that requires a distinct engine instance."""
        return (
            self.ocr_version,
            self.det_model_type,
            self.rec_model_type,
            self.intra_op_num_threads,
            self.inter_op_num_threads,
            str(self.model_root_dir) if self.model_root_dir else None,
            self.use_det,
        )


DEFAULT_CONFIG = WeChatIdOcrConfig()

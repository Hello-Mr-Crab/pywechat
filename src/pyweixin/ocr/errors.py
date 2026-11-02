"""Explicit OCR failure modes.

The WeChat-ID path must never fail silently. A caller has to be able to tell
"OCR ran and found nothing" apart from "OCR never ran at all", so every
failure raises a typed error carrying a stable ``code`` that logs and callers
can branch on without parsing human-readable messages.

Codes are part of the public contract (see docs/wechat-id-ocr.md):
    OCR_RUNTIME_UNAVAILABLE   rapidocr/onnxruntime missing or unimportable
    OCR_MODEL_LOAD_FAILED     engine could not be constructed
    OCR_INFERENCE_FAILED      engine built, but a recognize() call raised
"""

from __future__ import annotations


class OcrError(RuntimeError):
    """Base class for OCR failures; ``code`` is stable and machine-readable."""

    code = "OCR_ERROR"

    def __init__(self, message: str, *, detail: str | None = None) -> None:
        super().__init__(message)
        self.detail = detail


class OcrRuntimeUnavailable(OcrError):
    """rapidocr or onnxruntime is not installed, or cannot be imported."""

    code = "OCR_RUNTIME_UNAVAILABLE"


class OcrModelLoadFailed(OcrError):
    """The engine could not be constructed (missing or corrupt model files).

    Also raised when the requested model combination is not published, e.g.
    a model_type that PP-OCRv6 does not ship.
    """

    code = "OCR_MODEL_LOAD_FAILED"


class OcrInferenceFailed(OcrError):
    """The engine was constructed but a recognize() call raised.

    Includes malformed engine output (e.g. txts/scores/boxes of differing
    length), which is treated as a failure rather than as partial data.
    """

    code = "OCR_INFERENCE_FAILED"

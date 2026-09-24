"""RapidOCR engine wrapper: lazy, cached, and explicit about failure.

Loading PP-OCRv6 costs real time and ~140 MB of resident memory, so the
engine is built once per process and reused for every contact. Exporting
1000 contacts must not load the model 1000 times.

This module is the only place that imports ``rapidocr``. Keeping the import
inside the factory means the exporter, the normalizer and the test suite all
work on machines without the OCR runtime installed -- they simply get an
``OcrRuntimeUnavailable`` if they actually ask for OCR.
"""

from __future__ import annotations

import threading
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from .config import DEFAULT_CONFIG, WeChatIdOcrConfig
from .errors import (
    OcrInferenceFailed,
    OcrModelLoadFailed,
    OcrRuntimeUnavailable,
)

Point = tuple[float, float]


@dataclass(frozen=True)
class OcrToken:
    """One recognised text region, with its confidence and geometry.

    Geometry is what makes label anchoring possible: without the box we
    could only regex over the concatenated page text, which is exactly the
    failure mode this package exists to avoid.
    """

    text: str
    confidence: float
    box: tuple[Point, Point, Point, Point]

    @property
    def left(self) -> float:
        return min(p[0] for p in self.box)

    @property
    def right(self) -> float:
        return max(p[0] for p in self.box)

    @property
    def top(self) -> float:
        return min(p[1] for p in self.box)

    @property
    def bottom(self) -> float:
        return max(p[1] for p in self.box)

    @property
    def center_y(self) -> float:
        return (self.top + self.bottom) / 2.0

    @property
    def height(self) -> float:
        return max(1.0, self.bottom - self.top)

    @property
    def width(self) -> float:
        return max(1.0, self.right - self.left)


def _build_params(config: WeChatIdOcrConfig) -> dict[str, Any]:
    """Translate our config into RapidOCR params.

    RapidOCR requires *Enum* values for the version/model keys -- passing
    plain strings raises ``TypeError: The value of Det.ocr_version must be
    Enum Type.`` The enums are imported here rather than at module scope so
    that the dependency stays optional.
    """
    from rapidocr import EngineType, ModelType, OCRVersion

    def enum_of(enum_cls: Any, value: str, what: str) -> Any:
        try:
            return enum_cls(value)
        except ValueError as exc:
            valid = ", ".join(m.value for m in enum_cls)
            raise OcrModelLoadFailed(
                f"不支持的 OCR {what}：{value!r}（可选：{valid}）",
                detail=str(exc),
            ) from exc

    params: dict[str, Any] = {
        "Det.engine_type": EngineType.ONNXRUNTIME,
        "Rec.engine_type": EngineType.ONNXRUNTIME,
        "Cls.engine_type": EngineType.ONNXRUNTIME,
        "Det.ocr_version": enum_of(OCRVersion, config.ocr_version, "ocr_version"),
        "Rec.ocr_version": enum_of(OCRVersion, config.ocr_version, "ocr_version"),
        "Det.model_type": enum_of(ModelType, config.det_model_type, "det_model_type"),
        "Rec.model_type": enum_of(ModelType, config.rec_model_type, "rec_model_type"),
        "EngineConfig.onnxruntime.intra_op_num_threads": config.intra_op_num_threads,
        "EngineConfig.onnxruntime.inter_op_num_threads": config.inter_op_num_threads,
        "EngineConfig.onnxruntime.use_cuda": False,
        "Global.use_det": config.use_det,
    }
    if config.model_root_dir is not None:
        params["Global.model_root_dir"] = str(config.model_root_dir)
    return params


class OcrEngine:
    """Thin wrapper over RapidOCR that returns geometry-bearing tokens."""

    def __init__(self, config: WeChatIdOcrConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self._engine = self._construct()

    def _construct(self) -> Any:
        try:
            from rapidocr import RapidOCR
        except ImportError as exc:
            raise OcrRuntimeUnavailable(
                "未安装 OCR 运行时（rapidocr / onnxruntime）。"
                "请执行：pip install -r src/requirements-ocr.txt",
                detail=str(exc),
            ) from exc

        params = _build_params(self.config)
        try:
            return RapidOCR(params=params)
        except OcrModelLoadFailed:
            raise
        except (ImportError, ModuleNotFoundError) as exc:
            raise OcrRuntimeUnavailable(
                "ONNX Runtime OCR 后端不可用。请确认 src/requirements-ocr.txt 已安装。",
                detail=str(exc),
            ) from exc
        except Exception as exc:
            # Model download failure, corrupt cache, unsupported combination,
            # or an ONNX Runtime that cannot start. All are load failures.
            raise OcrModelLoadFailed(
                f"OCR 模型加载失败（{self.config.model_label()}）：{exc}",
                detail=str(exc),
            ) from exc

    def recognize(self, image: Any) -> list[OcrToken]:
        """Run OCR on a PIL image and return tokens with geometry.

        Args:
            image: a ``PIL.Image.Image``. Passing PIL directly (rather than a
                numpy array) matters: RapidOCR treats a raw ndarray as BGR and
                a PIL image as RGB, so handing it an array would silently
                swap the red and blue channels.

        Raises:
            OcrInferenceFailed: the call raised, or returned output whose
                text/score/box arrays disagree in length.
        """
        try:
            result = self._engine(image)
        except Exception as exc:
            raise OcrInferenceFailed(f"OCR 推理失败：{exc}", detail=str(exc)) from exc
        try:
            return self._to_tokens(result)
        except OcrInferenceFailed:
            raise
        except Exception as exc:
            raise OcrInferenceFailed(
                "OCR 返回 malformed result", detail=str(exc)
            ) from exc

    @staticmethod
    def _to_tokens(result: Any) -> list[OcrToken]:
        """Convert a RapidOCROutput into tokens, rejecting malformed output.

        RapidOCR returns an empty ``RapidOCROutput`` (all fields None) when
        it finds nothing, which is a legitimate empty result, not an error.
        Anything else that is ragged is treated as a failure.
        """
        texts: Sequence[Any] | None = getattr(result, "txts", None)
        scores = getattr(result, "scores", None)
        boxes = getattr(result, "boxes", None)
        if texts is None and scores is None and boxes is None:
            return []
        if texts is None or scores is None or boxes is None:
            raise OcrInferenceFailed(
                "OCR 返回结果不完整（malformed OCR result）",
                detail=f"txts={texts is not None} scores={scores is not None} boxes={boxes is not None}",
            )

        try:
            n = len(texts)
            if len(scores) != n or len(boxes) != n:
                raise OcrInferenceFailed(
                    "OCR 返回结果长度不一致（malformed OCR result）",
                    detail=f"txts={len(texts)} scores={len(scores)} boxes={len(boxes)}",
                )
        except TypeError as exc:
            raise OcrInferenceFailed(
                "OCR 返回结果不可索引（malformed OCR result）", detail=str(exc)
            ) from exc

        tokens: list[OcrToken] = []
        for text, score, box in zip(texts, scores, boxes):
            try:
                points = tuple((float(p[0]), float(p[1])) for p in box)
            except (TypeError, IndexError, ValueError) as exc:
                raise OcrInferenceFailed(
                    "OCR 返回的 bbox 无法解析（malformed OCR result）",
                    detail=str(exc),
                ) from exc
            if len(points) != 4:
                raise OcrInferenceFailed(
                    "OCR 返回的 bbox 不是四点多边形（malformed OCR result）",
                    detail=f"points={len(points)}",
                )
            if text is None or any(
                not math.isfinite(coord) for point in points for coord in point
            ):
                raise OcrInferenceFailed("OCR 返回无效 text 或非有限坐标")
            try:
                confidence = float(score)
            except (TypeError, ValueError) as exc:
                raise OcrInferenceFailed(
                    "OCR 返回的 score 无法解析", detail=str(exc)
                ) from exc
            if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
                raise OcrInferenceFailed("OCR 返回的 confidence 超出 0..1 范围")
            tokens.append(OcrToken(text=str(text), confidence=confidence, box=points))  # type: ignore[arg-type]
        return tokens


# --- process-wide cache ---------------------------------------------------

_CACHE: dict[tuple, OcrEngine] = {}
_LOCK = threading.Lock()


def get_ocr_engine(config: WeChatIdOcrConfig | None = None) -> OcrEngine:
    """Return the shared engine, building it on first use.

    Keyed on the settings that actually change the loaded model, so a caller
    asking for a different model gets its own engine rather than a
    silently-wrong shared one.
    """
    cfg = config or DEFAULT_CONFIG
    key = cfg.cache_key()
    with _LOCK:
        engine = _CACHE.get(key)
        if engine is None:
            engine = OcrEngine(cfg)
            _CACHE[key] = engine
        return engine


def reset_ocr_engine_cache() -> None:
    """Drop cached engines. For tests and for changing models at runtime."""
    with _LOCK:
        _CACHE.clear()


def default_model_root_dir() -> Path:
    """Where RapidOCR caches models when we do not override the location."""
    try:
        import rapidocr

        return Path(rapidocr.__file__).resolve().parent / "models"
    except Exception:  # pragma: no cover - only on a broken install
        return Path()

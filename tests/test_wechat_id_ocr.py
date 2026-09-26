from __future__ import annotations

from PIL import Image

from pyweixin.ocr.config import WeChatIdOcrConfig
from pyweixin.ocr.engine import (
    OcrEngine,
    OcrToken,
    get_ocr_engine,
    reset_ocr_engine_cache,
)
from pyweixin.ocr.errors import OcrModelLoadFailed
from pyweixin.ocr.result import WeChatIdResult
from pyweixin.ocr.wechat_id import (
    WeChatIdExtractor,
    candidate_near_label,
    extract_wechat_id_from_uia,
    reconcile_ocr_result,
)
from pyweixin.ocr.validator import normalize_candidate, validate_wechat_id
from pyweixin.ocr.roi import fallback_profile_roi


def token(text, x, y=10, confidence=0.99, width=60, height=16):
    return OcrToken(
        text,
        confidence,
        ((x, y), (x + width, y), (x + width, y + height), (x, y + height)),
    )


def good_view(value="wechat123", score=0.99):
    return [
        token("微信号：", 0, width=58),
        token(value, 65, confidence=score, width=85),
    ]


class FakeEngine:
    def __init__(self, views):
        self.views, self.calls = list(views), 0

    def recognize(self, _image):
        value = self.views[self.calls]
        self.calls += 1
        return value


def extractor(views, confidence=0.95):
    return WeChatIdExtractor(
        FakeEngine(views), WeChatIdOcrConfig(min_confidence_confirm=confidence)
    )


def test_spatial_anchor_uses_nearest_right_value_not_other_id():
    tokens = [
        token("昵称", 0),
        token("random123", 100, 60),
        token("微信号：", 0, 100, width=58),
        token("wxid_abc123", 65, 100, width=100),
        token("phone123", 300, 100),
    ]
    assert candidate_near_label(tokens)[0] == "wxid_abc123"


def test_supported_ids_and_ambiguous_glyphs_are_never_rewritten():
    for value in (
        "wechat123",
        "wxid_abc123",
        "abc-def",
        "abc_def",
        "a0O1Il",
        "test-S5",
    ):
        assert validate_wechat_id(value).valid
        assert normalize_candidate(value) == value


def test_high_confidence_two_view_consensus_confirms():
    result = extractor([good_view(), good_view()]).extract(Image.new("RGB", (200, 60)))
    assert (result.value, result.status, result.source) == (
        "wechat123",
        "CONFIRMED",
        "ocr",
    )


def test_ocr_disagreement_is_review_even_if_uia_agrees_with_one():
    result = extractor([good_view("abcO123"), good_view("abc0123")]).extract(
        Image.new("RGB", (200, 60))
    )
    result = reconcile_ocr_result(result, "abc0123")
    assert result.status == "NEED_REVIEW" and result.reason == "view_disagreement"


def test_low_confidence_matching_uia_confirms():
    result = extractor([good_view(score=0.83), good_view(score=0.86)]).extract(
        Image.new("RGB", (200, 60))
    )
    result = reconcile_ocr_result(result, "wechat123")
    assert result.status == "CONFIRMED" and result.source == "ocr+uia"


def test_low_confidence_mismatching_uia_needs_review():
    result = extractor([good_view(score=0.83), good_view(score=0.86)]).extract(
        Image.new("RGB", (200, 60))
    )
    result = reconcile_ocr_result(result, "wechat124")
    assert result.status == "NEED_REVIEW" and result.reason == "uia_mismatch"


def test_high_confidence_mismatching_uia_still_needs_review():
    result = extractor([good_view(), good_view()]).extract(Image.new("RGB", (200, 60)))
    result = reconcile_ocr_result(result, "wechat124")
    assert result.status == "NEED_REVIEW" and result.reason == "uia_mismatch"


def test_ocr_absent_uia_only_needs_review_and_empty_is_not_found():
    absent = WeChatIdResult(ocr_candidates=[None, None])
    assert reconcile_ocr_result(absent, "wechat123").status == "NEED_REVIEW"
    assert reconcile_ocr_result(absent, None).status == "NOT_FOUND"


def test_label_without_value_and_multiple_ids_never_guess():
    assert candidate_near_label([token("微信号：", 0, width=58)]) == (None, None)
    tokens = [
        token("微信号：", 0, width=58),
        token("first123", 65),
        token("other123", 65),
    ]
    assert candidate_near_label(tokens) == (None, None)


def test_uia_helper_is_label_anchored():
    assert (
        extract_wechat_id_from_uia(["other123", "微信号：", "wxid_abc123"])
        == "wxid_abc123"
    )
    assert extract_wechat_id_from_uia(["other123"]) is None


def test_engine_cache_builds_once_per_config(monkeypatch):
    from pyweixin.ocr import engine

    reset_ocr_engine_cache()
    made = []

    class Stub:
        def __init__(self, config):
            made.append(config)

    monkeypatch.setattr(engine, "OcrEngine", Stub)
    cfg = WeChatIdOcrConfig()
    assert get_ocr_engine(cfg) is get_ocr_engine(cfg)
    assert len(made) == 1
    reset_ocr_engine_cache()


def test_rapidocr_output_malformed_is_explicit_failure():
    class Broken:
        txts = ["id"]
        scores = []
        boxes = []

    try:
        OcrEngine._to_tokens(Broken())
    except Exception as exc:
        assert getattr(exc, "code", None) == "OCR_INFERENCE_FAILED"
    else:
        raise AssertionError("malformed result must fail closed")


def test_rapidocr_partial_empty_output_is_not_silently_accepted():
    class Broken:
        txts = None
        scores = [0.9]
        boxes = []

    try:
        OcrEngine._to_tokens(Broken())
    except Exception as exc:
        assert getattr(exc, "code", None) == "OCR_INFERENCE_FAILED"
    else:
        raise AssertionError("partial result must fail closed")


def test_model_load_error_has_explicit_ocr_failed_status(monkeypatch):
    from pyweixin.ocr import wechat_id

    def fail(_config):
        raise OcrModelLoadFailed("load failed")

    monkeypatch.setattr(wechat_id, "get_ocr_engine", fail)
    result = WeChatIdExtractor().extract(Image.new("RGB", (120, 40)))
    assert result.status == "OCR_FAILED"
    assert result.reason == "OCR_MODEL_LOAD_FAILED"


def test_preprocessing_produces_two_non_destructive_views():
    from pyweixin.ocr.preprocess import recognition_views

    source = Image.new("RGB", (40, 20), (120, 120, 120))
    first, second = recognition_views(source)
    assert first.size == second.size == (80, 40)
    assert first.mode == "RGB" and second.mode == "L"


def test_roi_geometry_and_model_load_errors_are_fail_closed():
    failed = WeChatIdResult(status="OCR_FAILED", reason="OCR_MODEL_LOAD_FAILED")
    assert reconcile_ocr_result(failed, "wechat123").status == "OCR_FAILED"
    # Typical 100%, 125%, 150%, windowed and maximised rectangles all keep
    # normalized relative coordinates identical by construction.
    for left, top, w, h in (
        (0, 0, 1200, 800),
        (120, 80, 1500, 1000),
        (0, 0, 2880, 1800),
    ):

        class Rect:
            pass

        rect = Rect()
        rect.left = left
        rect.top = top
        rect.right = left + w
        rect.bottom = top + h
        roi = fallback_profile_roi(rect)
        assert roi is not None
        assert roi[0] >= left and roi[2] <= left + w and roi[3] <= top + h

    class Empty:
        left = 0
        top = 0
        right = 0
        bottom = 0

    assert fallback_profile_roi(Empty()) is None

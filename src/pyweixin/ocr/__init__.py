"""WeChat-ID-specific OCR pipeline (not a general OCR API)."""

from .wechat_id import WeChatIdExtractor, extract_wechat_id_from_uia
from .result import WeChatIdResult

__all__ = ["WeChatIdExtractor", "WeChatIdResult", "extract_wechat_id_from_uia"]

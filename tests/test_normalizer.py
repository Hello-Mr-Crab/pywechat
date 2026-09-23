"""Unit tests for contact_exporter.normalizer."""
from __future__ import annotations

import json
from pathlib import Path

from contact_exporter.normalizer import _clean, normalize, normalize_one
from contact_exporter.models import EXPORT_FIELDS

FIXTURE = Path(__file__).parent / "fixtures" / "sample_contacts.json"
EXPORTED_AT = "2026-09-23 15:30:00"


def _load_fixture() -> list[dict]:
    with FIXTURE.open(encoding="utf-8") as fp:
        return json.load(fp)


def test_basic_key_mapping():
    raw = {
        "昵称": "张三", "微信号": "zs", "地区": "北京", "备注": "老张",
        "电话": "13800138000", "标签": "同事", "来源": "群聊",
    }
    c = normalize_one(raw, EXPORTED_AT)
    assert c.nickname == "张三"
    assert c.wechat_id == "zs"
    assert c.region == "北京"
    assert c.remark == "老张"
    assert c.phone == "13800138000"
    assert c.tags == "同事"
    assert c.source == "群聊"
    assert c.exported_at == EXPORTED_AT


def test_none_and_sentinel_fields_become_empty():
    raw = {
        "昵称": "李四", "微信号": "无", "备注": None,
        "电话": "", "地区": "  无  ", "标签": "无", "来源": "无",
    }
    c = normalize_one(raw, EXPORTED_AT)
    assert c.nickname == "李四"
    assert c.wechat_id == ""
    assert c.remark == ""
    assert c.phone == ""
    assert c.region == ""
    assert c.tags == ""
    assert c.source == ""


def test_missing_keys_default_empty():
    c = normalize_one({"昵称": "王五"}, EXPORTED_AT)
    assert c.nickname == "王五"
    assert c.wechat_id == ""
    assert c.phone == ""
    assert c.source == ""


def test_clean_helper():
    assert _clean(None) == ""
    assert _clean("无") == ""
    assert _clean("") == ""
    assert _clean("  无  ") == ""
    assert _clean("北京") == "北京"
    assert _clean(123) == "123"


def test_chinese_values_preserved():
    raw = {"昵称": "繁體中文測試", "地区": "香港中環", "标签": "重要客戶"}
    c = normalize_one(raw, EXPORTED_AT)
    assert c.nickname == "繁體中文測試"
    assert c.region == "香港中環"
    assert c.tags == "重要客戶"


def test_special_characters_do_not_break_structure():
    # Outer whitespace is stripped; inner comma/quote/newline/tab preserved.
    raw = {
        "昵称": '逗号,引号"换行\n制表\t中',
        "备注": 'Alice "A", Inc.',
        "微信号": "weird,id",
    }
    c = normalize_one(raw, EXPORTED_AT)
    assert c.nickname == '逗号,引号"换行\n制表\t中'
    assert c.remark == 'Alice "A", Inc.'
    assert c.wechat_id == "weird,id"


def test_deduplicate_default_drops_duplicates():
    contacts = normalize(_load_fixture(), EXPORTED_AT, deduplicate=True)
    # fixture has 5 entries; entries 0 and 4 are identical (same wechat_id).
    assert len(contacts) == 4
    ids = [c.wechat_id for c in contacts]
    assert ids.count("zhangsan1989") == 1


def test_no_deduplicate_keeps_all():
    contacts = normalize(_load_fixture(), EXPORTED_AT, deduplicate=False)
    assert len(contacts) == 5


def test_deduplicate_by_nickname_when_no_wechat_id():
    raw = [
        {"昵称": "小明", "备注": "无", "地区": "杭州"},
        {"昵称": "小明", "备注": "无", "地区": "杭州"},
        {"昵称": "小明", "备注": "无", "地区": "成都"},
    ]
    contacts = normalize(raw, EXPORTED_AT, deduplicate=True)
    # first and second identical -> dedup; third differs by region -> kept
    assert len(contacts) == 2


def test_export_fields_order_stable():
    raw = [{"昵称": "x", "来源": "s", "微信号": "w"}]
    c = normalize_one(raw, EXPORTED_AT)
    assert list(c.as_dict().keys()) == EXPORT_FIELDS


def test_non_dict_entries_skipped():
    raw = [{"昵称": "ok"}, "garbage", None, 42, ["list"]]
    contacts = normalize(raw, EXPORTED_AT, deduplicate=True)
    assert len(contacts) == 1
    assert contacts[0].nickname == "ok"


def test_empty_input():
    assert normalize([], EXPORTED_AT) == []


def test_mock_reader_feeds_normalizer():
    from contact_exporter.reader import MockContactReader

    reader = MockContactReader(_load_fixture())
    raw = reader.read_contacts()
    contacts = normalize(raw, EXPORTED_AT, deduplicate=True)
    assert len(contacts) == 4
    assert all(c.exported_at == EXPORTED_AT for c in contacts)

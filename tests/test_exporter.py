"""Unit tests for contact_exporter.exporter (CSV + TXT)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from contact_exporter.exporter import export_all, export_csv, export_txt
from contact_exporter.models import Contact, EXPORT_FIELDS
from contact_exporter.normalizer import normalize

FIXTURE = Path(__file__).parent / "fixtures" / "sample_contacts.json"
EXPORTED_AT = "2026-09-23 15:30:00"


def _contacts(dedup: bool = True) -> list[Contact]:
    with FIXTURE.open(encoding="utf-8") as fp:
        raw = json.load(fp)
    return normalize(raw, exported_at=EXPORTED_AT, deduplicate=dedup)


# ---------- CSV ----------


def test_csv_has_utf8_bom(tmp_path):
    path = export_csv(_contacts(), tmp_path, filename="out.csv")
    raw = path.read_bytes()
    assert raw[:3] == b"\xef\xbb\xbf", "CSV must start with UTF-8 BOM"


def test_csv_header_row(tmp_path):
    path = export_csv(_contacts(), tmp_path, filename="out.csv")
    with path.open(encoding="utf-8-sig", newline="") as fp:
        reader = csv.reader(fp)
        header = next(reader)
    assert header == EXPORT_FIELDS


def test_csv_row_content(tmp_path):
    path = export_csv(_contacts(), tmp_path, filename="out.csv")
    with path.open(encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))
    assert rows[0]["nickname"] == "张三"
    assert rows[0]["wechat_id"] == "zhangsan1989"
    assert rows[0]["wechat_id_status"] == "CONFIRMED"
    assert rows[0]["phone"] == "13800138000"
    assert rows[0]["exported_at"] == EXPORTED_AT


def test_csv_chinese_values(tmp_path):
    path = export_csv(_contacts(), tmp_path, filename="out.csv")
    text = path.read_text(encoding="utf-8-sig")
    assert "繁體中文測試" not in text  # not in fixture; sanity
    assert "北京海淀" in text


def test_csv_special_characters_safe(tmp_path):
    contacts = _contacts()
    path = export_csv(contacts, tmp_path, filename="out.csv")
    with path.open(encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))
    # newline in nickname must be quoted by csv module (single cell)
    nl_row = next(r for r in rows if r["wechat_id"] == "nl_test")
    assert "换行\n测试" in nl_row["nickname"]
    # nickname has a comma; remark has quotes -> csv quoting round-trips both
    alice = next(r for r in rows if r["wechat_id"] == "alice_wx")
    assert alice["nickname"] == "Alice, Inc."
    assert alice["remark"] == 'Alice "A"'


def test_csv_empty_contacts_still_has_header(tmp_path):
    path = export_csv([], tmp_path, filename="empty.csv")
    with path.open(encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.reader(fp))
    assert rows == [EXPORT_FIELDS]


# ---------- TXT ----------


def test_txt_has_utf8_bom(tmp_path):
    path = export_txt(_contacts(), tmp_path, filename="out.txt")
    assert path.read_bytes()[:3] == b"\xef\xbb\xbf"


def test_txt_header_and_format(tmp_path):
    path = export_txt(_contacts(), tmp_path, filename="out.txt")
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    assert lines[0].startswith(
        "备注 | 昵称 | 微信号 | 手机号 | 地区 | 标签 | 微信号状态"
    )
    first_data = lines[1]
    assert first_data.startswith(
        "张三(公司) | 张三 | zhangsan1989 | 13800138000 | 北京海淀 | 同事 | CONFIRMED"
    )


def test_txt_empty_contacts_has_header_only(tmp_path):
    path = export_txt([], tmp_path, filename="empty.txt")
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    assert lines == [
        "备注 | 昵称 | 微信号 | 手机号 | 地区 | 标签 | 微信号状态 | 来源 | 置信度 | 原因 | 微信号候选"
    ]


def test_txt_keeps_review_candidate_outside_canonical_id_column(tmp_path):
    contact = Contact(
        nickname="示例",
        wechat_id="",
        wechat_id_status="NEED_REVIEW",
        wechat_id_candidate="abcO123",
        wechat_id_source="ocr",
    )
    path = export_txt([contact], tmp_path, filename="review.txt")
    row = path.read_text(encoding="utf-8-sig").splitlines()[1].split(" | ")
    assert row[2] == ""
    assert row[-1] == "abcO123"


# ---------- non-overwrite ----------


def test_csv_does_not_overwrite_existing(tmp_path):
    a = export_csv(_contacts(), tmp_path, filename="dup.csv")
    original = a.read_bytes()
    b = export_csv(_contacts(), tmp_path, filename="dup.csv")
    assert b != a
    assert a.read_bytes() == original  # original untouched
    assert b.name.startswith("dup_") and b.suffix == ".csv"


def test_txt_does_not_overwrite_existing(tmp_path):
    a = export_txt(_contacts(), tmp_path, filename="dup.txt")
    original = a.read_bytes()
    b = export_txt(_contacts(), tmp_path, filename="dup.txt")
    assert b != a
    assert a.read_bytes() == original
    assert b.name.startswith("dup_") and b.suffix == ".txt"


def test_export_all_timestamps_match(tmp_path):
    paths = export_all(_contacts(), tmp_path)
    assert paths["csv"].stem.rsplit("_", 1)[0] == paths["txt"].stem.rsplit("_", 1)[0]
    assert paths["csv"].exists()
    assert paths["txt"].exists()


def test_none_fields_render_as_empty_in_csv(tmp_path):
    contacts = [Contact(nickname="x", exported_at=EXPORTED_AT)]
    path = export_csv(contacts, tmp_path, filename="none.csv")
    with path.open(encoding="utf-8-sig", newline="") as fp:
        row = next(csv.DictReader(fp))
    assert row["phone"] == ""
    assert row["wechat_id"] == ""
    assert row["region"] == ""


def test_output_dir_created(tmp_path):
    nested = tmp_path / "deep" / "nested" / "dir"
    path = export_csv(_contacts(), nested, filename="out.csv")
    assert path.exists()
    assert path.parent == nested

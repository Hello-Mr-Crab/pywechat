"""CSV / TXT exporters with timestamped, non-overwriting filenames.

Output rules (PRD §5):
  - CSV: UTF-8 BOM, header row first, Excel/WPS friendly.
  - TXT: UTF-8 BOM, line format "备注 | 昵称 | 微信号 | 手机号 | 地区 | 标签".
  - Filename: wechat_contacts_YYYYMMDD_HHMMSS.{csv,txt}
  - Never overwrite an existing file: append _1/_2/... suffix instead.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import Contact, EXPORT_FIELDS


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _next_available_path(path: Path) -> Path:
    """Return a path that does not exist; append _1/_2/... to avoid overwrite."""
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 1
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def export_csv(
    contacts: Iterable[Contact],
    output_dir: str | Path,
    *,
    filename: str | None = None,
    timestamp: str | None = None,
) -> Path:
    """Write contacts to a UTF-8-BOM CSV with a header row. Returns the path."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = timestamp or _timestamp()
    name = filename or f"wechat_contacts_{ts}.csv"
    path = _next_available_path(out_dir / name)

    # utf-8-sig prepends BOM (EF BB BF) -> Excel/WPS display Chinese correctly.
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(
            fp, fieldnames=EXPORT_FIELDS, extrasaction="ignore"
        )
        writer.writeheader()
        for contact in contacts:
            writer.writerow(contact.as_dict())
    return path


def export_txt(
    contacts: Iterable[Contact],
    output_dir: str | Path,
    *,
    filename: str | None = None,
    timestamp: str | None = None,
) -> Path:
    """Write contacts to a UTF-8-BOM TXT. Returns the path."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = timestamp or _timestamp()
    name = filename or f"wechat_contacts_{ts}.txt"
    path = _next_available_path(out_dir / name)

    cols = ["remark", "nickname", "wechat_id", "phone", "region", "tags"]
    header = "备注 | 昵称 | 微信号 | 手机号 | 地区 | 标签"
    with path.open("w", encoding="utf-8-sig") as fp:
        fp.write(header + "\n")
        for contact in contacts:
            d = contact.as_dict()
            fp.write(" | ".join(str(d[col]) for col in cols) + "\n")
    return path


def export_all(
    contacts: list[Contact], output_dir: str | Path
) -> dict[str, Path]:
    """Export both CSV and TXT sharing one timestamp. Returns paths."""
    ts = _timestamp()
    return {
        "csv": export_csv(contacts, output_dir, timestamp=ts),
        "txt": export_txt(contacts, output_dir, timestamp=ts),
    }

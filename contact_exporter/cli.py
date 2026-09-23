"""Command-line interface for the WeChat contact exporter.

MVP surface (PRD §3):
    python export_contacts.py --format csv|txt|all
        [--output-dir ./output] [--deduplicate|--no-deduplicate] [--verbose]
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import Optional, Sequence

from .exporter import export_all, export_csv, export_txt
from .logging_config import setup_logging
from .normalizer import normalize
from .reader import ContactReadError, reader_factory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="export_contacts.py",
        description=(
            "导出当前登录微信账号的联系人到 CSV/TXT（只读，不修改微信）。"
        ),
    )
    parser.add_argument(
        "--format", choices=["csv", "txt", "all"], default="csv",
        help="输出格式（默认 csv）",
    )
    parser.add_argument(
        "--output-dir", default="./output", help="输出目录（默认 ./output）",
    )
    parser.add_argument(
        "--deduplicate", action=argparse.BooleanOptionalAction, default=True,
        help="按微信号去重（默认开启；--no-deduplicate 关闭）",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="详细日志（注意：可能打印手机号/微信号）",
    )
    parser.add_argument(
        "--backend", choices=["pyweixin", "mock"], default="pyweixin",
        help="联系人读取后端（mock 用于无微信环境的冒烟测试）",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logger = setup_logging(verbose=args.verbose)
    exported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        reader = reader_factory(args.backend)
        raw = reader.read_contacts()
    except ContactReadError as e:
        logger.error(str(e))
        return 2
    except Exception as e:  # pragma: no cover - defensive
        logger.error("读取联系人时发生未预期错误：%s", e)
        return 1

    contacts = normalize(
        raw, exported_at=exported_at, deduplicate=args.deduplicate
    )
    logger.info(
        "规范化后共 %d 条联系人（去重=%s）", len(contacts), args.deduplicate
    )
    if not contacts:
        logger.warning("没有联系人可导出，将仅生成含表头的空文件")

    try:
        if args.format == "csv":
            path = export_csv(contacts, args.output_dir)
            logger.info("CSV 已导出：%s", path)
        elif args.format == "txt":
            path = export_txt(contacts, args.output_dir)
            logger.info("TXT 已导出：%s", path)
        else:
            paths = export_all(contacts, args.output_dir)
            for kind, path in paths.items():
                logger.info("%s 已导出：%s", kind.upper(), path)
    except Exception as e:  # pragma: no cover - defensive
        logger.error("导出失败：%s", e)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

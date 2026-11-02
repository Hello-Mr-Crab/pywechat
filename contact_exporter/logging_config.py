"""Logging setup with PII redaction by default.

By default (non-verbose) phone numbers are masked and full contact objects
are not dumped. Use --verbose to enable detailed logging (may include PII).
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import re
from pathlib import Path

# Chinese mainland mobile numbers.
_PHONE_RE = re.compile(r"\b1[3-9]\d{9}\b")
# Full contact dict/list dumps produced by repr()/str() of raw data.
_CONTACT_DUMP_RE = re.compile(r"\{[^{}]*昵称[^{}]*\}|\[[^\[\]]*\{[^{}]*\}[^\[\]]*\]")


class _RedactingFormatter(logging.Formatter):
    """Formatter that masks PII unless verbose is enabled."""

    def __init__(self, fmt: str, datefmt: str, verbose: bool = False) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.verbose = verbose

    def format(self, record: logging.LogRecord) -> str:
        text = super().format(record)
        if not self.verbose:
            text = _PHONE_RE.sub("1**********", text)
            text = _CONTACT_DUMP_RE.sub("<redacted contact>", text)
        return text


def setup_logging(
    verbose: bool = False, log_dir: str | os.PathLike = "logs"
) -> logging.Logger:
    """Configure the contact_exporter logger (console + rotating file)."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("contact_exporter")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    fmt = _RedactingFormatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        verbose=verbose,
    )

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    console.setFormatter(fmt)
    logger.addHandler(console)

    file_h = logging.handlers.RotatingFileHandler(
        log_path / "contact_exporter.log",
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_h.setLevel(logging.DEBUG)
    file_h.setFormatter(fmt)
    logger.addHandler(file_h)

    return logger

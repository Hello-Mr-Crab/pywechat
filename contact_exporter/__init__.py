"""WeChat contact exporter — local, read-only CSV/TXT export tool.

Additive module over pyweixin; does not modify upstream core logic.
Only reads contacts via the public API Contacts.get_friends_detail() and
writes local files. No messaging, no mutation, no hooks, no DB access.
"""
from __future__ import annotations

__version__ = "0.1.0"

from .models import Contact, EXPORT_FIELDS
from .normalizer import normalize
from .exporter import export_csv, export_txt, export_all

__all__ = [
    "Contact",
    "EXPORT_FIELDS",
    "normalize",
    "export_csv",
    "export_txt",
    "export_all",
]

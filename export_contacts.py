#!/usr/bin/env python3
"""Entry point: export WeChat contacts to CSV/TXT (read-only, local files).

Usage:
    python export_contacts.py --format csv
    python export_contacts.py --format txt
    python export_contacts.py --format all
"""
import sys

from contact_exporter.cli import main

if __name__ == "__main__":
    sys.exit(main())

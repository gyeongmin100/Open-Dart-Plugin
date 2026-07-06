# -*- coding: utf-8 -*-
"""bs4/lxml/openpyxl 미설치 시 requirements.txt로 자동 설치."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def ensure_deps() -> None:
    try:
        import bs4  # noqa: F401
        import lxml  # noqa: F401
        import openpyxl  # noqa: F401
    except ImportError:
        req = Path(__file__).parent.parent / "requirements.txt"
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(req)])

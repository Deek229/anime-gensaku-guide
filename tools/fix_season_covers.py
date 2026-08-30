"""2026秋・2027冬の誤ISBN/表紙を修正して再取得（fix_season_metadata.py へ委譲）"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fix_season_metadata import main

if __name__ == '__main__':
    raise SystemExit(main())

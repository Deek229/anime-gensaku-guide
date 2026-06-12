"""Annict からシーズン作品を同期"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

from annict_client import fetch_season_works

sys.stdout.reconfigure(encoding='utf-8')

season = sys.argv[1] if len(sys.argv) > 1 else '2026-summer'
works = fetch_season_works(season)
print(f'{season}: {len(works)}件を取り込みました')

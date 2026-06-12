"""Annict API からシーズン作品を取得（要 ANNICT_ACCESS_TOKEN）"""
from __future__ import annotations

import time
from typing import Any

import requests

from config import ANNICT_ACCESS_TOKEN, ANNICT_API_URL
from store import slugify, upsert_work

# Annict media -> source_type 推定は手動補完が必要
_SOURCE_GUESS_KEYWORDS = {
    'light_novel': ['無職転生', 'Re:ゼロ', '幼女戦記', '骸骨騎士', '乙女ゲー世界はモブ'],
    'manga': ['ぐらんぶる', 'BLEACH', '100人の彼女', '逃げ上手', 'マジルミエ'],
}


def _guess_source_type(title: str) -> str:
    for st, keys in _SOURCE_GUESS_KEYWORDS.items():
        if any(k in title for k in keys):
            return st
    return 'other'


def fetch_season_works(season: str) -> list[dict[str, Any]]:
    if not ANNICT_ACCESS_TOKEN:
        raise RuntimeError('ANNICT_ACCESS_TOKEN が未設定です（.env または環境変数）')

    session = requests.Session()
    session.headers['Authorization'] = f'Bearer {ANNICT_ACCESS_TOKEN}'
    page = 1
    imported: list[dict[str, Any]] = []

    while True:
        r = session.get(
            ANNICT_API_URL,
            params={
                'filter_season': season,
                'sort_watchers_count': 'desc',
                'per_page': 50,
                'page': page,
            },
            timeout=30,
        )
        r.raise_for_status()
        payload = r.json()
        batch = payload.get('works', [])
        if not batch:
            break
        for row in batch:
            title = row.get('title', '')
            work = upsert_work({
                'id': slugify(title),
                'annict_id': row.get('id'),
                'season': season,
                'title': title,
                'title_kana': row.get('title_kana', ''),
                'media': row.get('media', 'tv'),
                'status': 'upcoming',
                'watchers_count': row.get('watchers_count', 0),
                'official_url': row.get('official_site_url', ''),
                'wikipedia_url': row.get('wikipedia_url', ''),
                'episodes_count': row.get('episodes_count'),
                'source_type': _guess_source_type(title),
                'source_title': '',
                'volumes_anime': '',
                'read_order': '',
                'amazon_search': f'{title} 原作',
                'tags': [],
                'memo': '',
            })
            imported.append(work)
        if len(batch) < 50:
            break
        page += 1
        time.sleep(0.5)
    return imported

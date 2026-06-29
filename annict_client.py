"""Annict API からシーズン作品を取得（要 ANNICT_ACCESS_TOKEN）"""
from __future__ import annotations

import re
import time
import urllib.request
from typing import Any

import requests

from config import ANNICT_ACCESS_TOKEN, ANNICT_API_URL
from store import slugify, upsert_work

_OG_IMAGE_PATTERNS = (
    re.compile(r'property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', re.I),
    re.compile(r'content=["\']([^"\']+)["\']\s+property=["\']og:image["\']', re.I),
    re.compile(r'name=["\']twitter:image["\']\s+content=["\']([^"\']+)["\']', re.I),
)

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


def _annict_session() -> requests.Session:
    if not ANNICT_ACCESS_TOKEN:
        raise RuntimeError('ANNICT_ACCESS_TOKEN が未設定です（.env または環境変数）')
    session = requests.Session()
    session.headers['Authorization'] = f'Bearer {ANNICT_ACCESS_TOKEN}'
    return session


def _extract_recommended_image(row: dict[str, Any]) -> str:
    images = row.get('images') or {}
    return (images.get('recommended_url') or '').strip()


def fetch_work_images(title: str, annict_id: int | None = None) -> tuple[str, int | None]:
    """Annict からキービジュアル URL を取得。(url, annict_id)"""
    if not ANNICT_ACCESS_TOKEN:
        return '', annict_id

    session = _annict_session()
    rows: list[dict[str, Any]] = []
    if annict_id:
        r = session.get(f'{ANNICT_API_URL}/{annict_id}', timeout=30)
        if r.status_code == 200:
            rows = [r.json()]
    else:
        r = session.get(
            ANNICT_API_URL,
            params={'filter_title': title, 'per_page': 10},
            timeout=30,
        )
        r.raise_for_status()
        rows = r.json().get('works', [])

    needle = title.strip()
    for row in rows:
        if annict_id or row.get('title', '').strip() == needle:
            url = _extract_recommended_image(row)
            return url, row.get('id') or annict_id
    return '', annict_id


def fetch_official_og_image(official_url: str) -> str:
    """公式サイトの og:image をキービジュアル候補として取得"""
    url = (official_url or '').strip()
    if not url:
        return ''
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; AnimeGensakuGuide/1.0)'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except (urllib.error.URLError, TimeoutError):
        return ''
    for pattern in _OG_IMAGE_PATTERNS:
        m = pattern.search(html)
        if m:
            candidate = m.group(1).strip()
            if candidate.startswith('http'):
                return candidate
    return ''


def fetch_season_works(season: str) -> list[dict[str, Any]]:
    session = _annict_session()
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
            key_visual_url = _extract_recommended_image(row)
            payload: dict[str, Any] = {
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
            }
            if key_visual_url:
                payload['key_visual_url'] = key_visual_url
            work = upsert_work(payload)
            imported.append(work)
        if len(batch) < 50:
            break
        page += 1
        time.sleep(0.5)
    return imported

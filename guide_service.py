"""シーズンまとめ（SEO）ページ用"""
from __future__ import annotations

from typing import Any

from anime_service import list_works
from config import SEASON_LABELS


MATOME_PAGES: dict[str, dict[str, Any]] = {
    '2026-spring': {
        'season': '2026-spring',
        'slug': '2026-spring',
        'title': '2026年春アニメ 原作おすすめ10選',
        'lead': '2026年4月放送の春アニメから、原作を読む価値が高い作品を10本厳選。ラノベ・漫画の読み始め巻と、アニメ化範囲の目安をまとめました。',
        'limit': 10,
    },
    '2026-summer': {
        'season': '2026-summer',
        'slug': '2026-summer',
        'title': '2026年夏アニメ 原作おすすめ10選',
        'lead': '2026年7月放送の夏アニメから、原作チェックにおすすめの人気作10選。続編ものの「何巻から読むか」もひと目でわかります。',
        'limit': 10,
    },
    '2026-autumn': {
        'season': '2026-autumn',
        'slug': '2026-autumn',
        'title': '2026年秋アニメ 原作おすすめ10選',
        'lead': '2026年10月放送の秋アニメから、原作ファン・これから読み始める人向けのおすすめ10作品をピックアップしました。',
        'limit': 10,
    },
    '2026-winter': {
        'season': '2026-winter',
        'slug': '2026-winter',
        'title': '2026年冬アニメ 原作おすすめ10選',
        'lead': '2027年1月放送の冬アニメ（2026年冬クール）から、原作を押さえておきたい注目作10選を紹介します。',
        'limit': 10,
    },
}


def list_matome_pages() -> list[dict[str, Any]]:
    return [
        {
            'slug': meta['slug'],
            'path': f'/matome/{meta["slug"]}',
            'title': meta['title'],
            'season': meta['season'],
            'season_label': SEASON_LABELS.get(meta['season'], meta['season']),
        }
        for meta in MATOME_PAGES.values()
    ]


def get_matome(slug: str) -> dict[str, Any] | None:
    meta = MATOME_PAGES.get(slug)
    if not meta:
        return None
    season = meta['season']
    limit = meta['limit']
    picks = list_works(season=season, has_source_only=True)[:limit]
    return {
        **meta,
        'season_label': SEASON_LABELS.get(season, season),
        'path': f'/matome/{slug}',
        'picks': picks,
        'seo_description': meta['lead'][:155],
    }

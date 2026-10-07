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
        'page_kind': 'picks',
    },
    '2026-summer': {
        'season': '2026-summer',
        'slug': '2026-summer',
        'title': '2026年夏アニメ 原作おすすめ10選',
        'lead': '2026年7月放送の夏アニメから、原作チェックにおすすめの人気作10選。続編ものの「何巻から読むか」もひと目でわかります。',
        'limit': 10,
        'page_kind': 'picks',
    },
    '2026-autumn': {
        'season': '2026-autumn',
        'slug': '2026-autumn',
        'title': '2026年秋アニメ 原作おすすめ10選',
        'lead': '2026年9〜12月（10月クール）の秋アニメから、原作ファン・これから読み始める人向けのおすすめ10作品をピックアップしました。',
        'limit': 10,
        'page_kind': 'picks',
    },
    '2027-winter': {
        'season': '2027-winter',
        'slug': '2027-winter',
        'title': '2027年冬アニメ 原作おすすめ10選',
        'lead': '2027年1〜3月放送の冬アニメから、原作を押さえておきたい注目作10選を紹介します。',
        'limit': 10,
        'page_kind': 'picks',
    },
    '2027-spring': {
        'season': '2027-spring',
        'slug': '2027-spring',
        'title': '2027年春アニメ 原作おすすめ10選',
        'lead': '2027年4〜6月放送の春アニメから、原作を読む価値が高い作品を10本厳選。ラノベ・漫画の読み始め巻と、アニメ化範囲の目安をまとめました。',
        'limit': 10,
        'page_kind': 'picks',
    },
    # SEO: 「何巻から」検索向け（シーズン全作品の巻対応表）
    '2026-autumn-nankan': {
        'season': '2026-autumn',
        'slug': '2026-autumn-nankan',
        'title': '2026年秋アニメ 原作は何巻から？対応一覧',
        'lead': '2026年秋（10月クール）アニメの原作漫画・ラノベを「何巻から読むか」が一覧でわかる対応表です。続編は続き巻、新作は1巻からの目安をまとめています。',
        'limit': None,
        'page_kind': 'nankan',
        'related_matome': '2026-autumn',
    },
    '2027-winter-nankan': {
        'season': '2027-winter',
        'slug': '2027-winter-nankan',
        'title': '2027年冬アニメ 原作は何巻から？対応一覧',
        'lead': '2027年冬（1月クール）アニメの原作漫画・ラノベを「何巻から読むか」が一覧でわかる対応表です。続編は続き巻、新作は1巻からの目安をまとめています。',
        'limit': None,
        'page_kind': 'nankan',
        'related_matome': '2027-winter',
    },
    '2027-spring-nankan': {
        'season': '2027-spring',
        'slug': '2027-spring-nankan',
        'title': '2027年春アニメ 原作は何巻から？対応一覧',
        'lead': '2027年春（4月クール）アニメの原作漫画・ラノベを「何巻から読むか」が一覧でわかる対応表です。続編は続き巻、新作は1巻からの目安をまとめています。',
        'limit': None,
        'page_kind': 'nankan',
        'related_matome': '2027-spring',
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
    limit = meta.get('limit')
    picks = list_works(season=season, has_source_only=True)
    if limit is not None:
        picks = picks[:limit]
    related_slug = meta.get('related_matome')
    related = None
    if related_slug and related_slug in MATOME_PAGES:
        related_meta = MATOME_PAGES[related_slug]
        related = {
            'slug': related_slug,
            'path': f'/matome/{related_slug}',
            'title': related_meta['title'],
        }
    elif meta.get('page_kind', 'picks') == 'picks':
        for other_slug, other_meta in MATOME_PAGES.items():
            if other_meta.get('related_matome') == slug:
                related = {
                    'slug': other_slug,
                    'path': f'/matome/{other_slug}',
                    'title': other_meta['title'],
                }
                break
    return {
        **meta,
        'page_kind': meta.get('page_kind', 'picks'),
        'season_label': SEASON_LABELS.get(season, season),
        'path': f'/matome/{slug}',
        'picks': picks,
        'related': related,
        'seo_description': meta['lead'][:155],
    }

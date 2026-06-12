"""アニメ作品の検索・フィルタ"""
from __future__ import annotations

from typing import Any

from amazon_links import buy_url
from config import (
    DEFAULT_SEASON,
    SEASON_LABELS,
    SOURCE_TYPE_LABELS,
    STATUS_LABELS,
)
from store import find_work, load_works


def enrich_work(work: dict[str, Any]) -> dict[str, Any]:
    url, buy_label = buy_url(work)
    st = work.get('source_type', 'other')
    return {
        **work,
        'source_type_label': SOURCE_TYPE_LABELS.get(st, st),
        'status_label': STATUS_LABELS.get(work.get('status', ''), ''),
        'season_label': SEASON_LABELS.get(work.get('season', ''), work.get('season', '')),
        'buy_url': url,
        'buy_label': buy_label,
        'has_source': st not in ('original', 'other', ''),
    }


def list_works(
    season: str | None = None,
    source_type: str | None = None,
    status: str | None = None,
    q: str | None = None,
    has_source_only: bool = False,
) -> list[dict[str, Any]]:
    items = [enrich_work(w) for w in load_works()]
    if season:
        items = [w for w in items if w.get('season') == season]
    if source_type:
        items = [w for w in items if w.get('source_type') == source_type]
    if status:
        items = [w for w in items if w.get('status') == status]
    if has_source_only:
        items = [w for w in items if w.get('has_source')]
    if q:
        needle = q.lower()
        items = [
            w for w in items
            if needle in f"{w.get('title','')} {w.get('source_title','')} {w.get('tags',[])}".lower()
        ]
    items.sort(key=lambda w: (-(w.get('watchers_count') or 0), w.get('title', '')))
    return items


def get_work(work_id: str) -> dict[str, Any] | None:
    w = find_work(work_id)
    return enrich_work(w) if w else None


def list_meta() -> dict[str, Any]:
    works = load_works()
    seasons = sorted({w.get('season', '') for w in works if w.get('season')}, reverse=True)
    return {
        'app_title': 'アニメ原作ガイド',
        'default_season': DEFAULT_SEASON,
        'seasons': [
            {'id': s, 'label': SEASON_LABELS.get(s, s), 'count': sum(1 for w in works if w.get('season') == s)}
            for s in seasons
        ],
        'source_types': [{'id': k, 'label': v} for k, v in SOURCE_TYPE_LABELS.items()],
        'statuses': [{'id': k, 'label': v} for k, v in STATUS_LABELS.items()],
        'affiliate_disclosure': 'Amazonのリンクにはアフィリエイトを使用する場合があります。',
        'has_amazon_tag': bool(__import__('config').AMAZON_ASSOCIATE_TAG),
    }

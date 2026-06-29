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
from seo import (
    absolute_url,
    build_faq,
    build_intro,
    build_share_text,
    line_share_url,
    twitter_share_url,
    work_meta_description,
    work_page_title,
)
from store import find_work, load_works, resolve_share_slug
from volume_utils import enrich_volume_fields


def enrich_work(work: dict[str, Any]) -> dict[str, Any]:
    url, buy_label = buy_url(work)
    work = enrich_volume_fields(work)
    st = work.get('source_type', 'other')
    base = {
        **work,
        'source_type_label': SOURCE_TYPE_LABELS.get(st, st),
        'status_label': STATUS_LABELS.get(work.get('status', ''), ''),
        'season_label': SEASON_LABELS.get(work.get('season', ''), work.get('season', '')),
        'buy_url': url,
        'buy_label': buy_label,
        'has_source': st not in ('original', 'other', ''),
    }
    page_path = f'/works/{work["id"]}'
    page_url = absolute_url(page_path)
    share_slug = resolve_share_slug(work)
    share_path = f'/works/{share_slug}'
    share_url = absolute_url(share_path)
    share_text = build_share_text(base)
    return {
        **base,
        'page_path': page_path,
        'page_url': page_url,
        'share_slug': share_slug,
        'share_path': share_path,
        'share_url': share_url,
        'seo_title': work_page_title(base),
        'seo_description': work_meta_description(base),
        'intro': build_intro(base),
        'faq': build_faq(base),
        'share_text': share_text,
        'twitter_share_url': twitter_share_url(share_text, share_url),
        'line_share_url': line_share_url(share_text, share_url),
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


def related_works(work_id: str, limit: int = 4) -> list[dict[str, Any]]:
    target = find_work(work_id)
    if not target:
        return []
    tags = set(target.get('tags') or [])
    season = target.get('season')
    scored: list[tuple[int, dict[str, Any]]] = []
    for work in load_works():
        if work.get('id') == work_id:
            continue
        score = len(tags & set(work.get('tags') or []))
        if season and work.get('season') == season:
            score += 1
        if score > 0:
            scored.append((score, work))
    scored.sort(key=lambda x: (-x[0], -(x[1].get('watchers_count') or 0)))
    return [enrich_work(w) for _, w in scored[:limit]]


def popular_works(season: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
    items = list_works(season=season, has_source_only=True)
    return items[:limit]


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

"""ランキング取得・キャッシュ・作品情報マージ"""
from __future__ import annotations

import json
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from config import BIGGENRE_LABELS, CACHE_DIR, END_LABELS, RANK_CACHE_TTL_SEC
from narou_client import fetch_novels, fetch_ranking, novel_url, rank_rtype

PERIOD_LABELS = {
    'd': '日間',
    'w': '週間',
    'm': '月間',
    'q': '四半期',
}


def _cache_path(period: str, target: date) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    rtype = rank_rtype(target, period)
    return CACHE_DIR / f'rank_{rtype}.json'


def _load_cache(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
        if time.time() - payload.get('fetched_at', 0) > RANK_CACHE_TTL_SEC:
            return None
        return payload
    except (json.JSONDecodeError, OSError):
        return None


def _save_cache(path: Path, payload: dict[str, Any]):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def _enrich_row(rank_row: dict[str, Any], novel: dict[str, Any] | None) -> dict[str, Any]:
    novel = novel or {}
    biggenre = int(novel.get('biggenre') or 0)
    end = int(novel.get('end') or 0)
    isstop = int(novel.get('isstop') or 0)
    ncode = rank_row['ncode']
    return {
        'rank': rank_row.get('rank'),
        'pt': rank_row.get('pt'),
        'ncode': ncode,
        'title': novel.get('title', '（情報取得中）'),
        'writer': novel.get('writer', ''),
        'story': novel.get('story', ''),
        'biggenre': biggenre,
        'biggenre_label': BIGGENRE_LABELS.get(biggenre, '不明'),
        'genre': novel.get('genre'),
        'keyword': novel.get('keyword', ''),
        'general_lastup': novel.get('general_lastup', ''),
        'general_all_no': novel.get('general_all_no'),
        'end': end,
        'end_label': END_LABELS.get(end, '不明'),
        'isstop': isstop,
        'isstop_label': '休載中' if isstop else '',
        'url': novel_url(ncode),
    }


def get_ranking(period: str = 'd', target: date | None = None) -> dict[str, Any]:
    if period not in PERIOD_LABELS:
        period = 'd'
    target = target or date.today()
    cache_path = _cache_path(period, target)
    cached = _load_cache(cache_path)
    if cached:
        return cached

    rank_rows = fetch_ranking(target, period)
    ncodes = [r['ncode'] for r in rank_rows]
    novels = fetch_novels(ncodes)
    items = [_enrich_row(r, novels.get(r['ncode'])) for r in rank_rows]

    payload = {
        'period': period,
        'period_label': PERIOD_LABELS[period],
        'rtype': rank_rtype(target, period),
        'target_date': target.isoformat(),
        'fetched_at': time.time(),
        'fetched_at_iso': datetime.now().isoformat(timespec='seconds'),
        'count': len(items),
        'items': items,
    }
    _save_cache(cache_path, payload)
    return payload


def default_target_date(period: str) -> date:
    d = date.today()
    if period == 'w':
        while d.weekday() != 1:
            d -= timedelta(days=1)
    elif period in ('m', 'q'):
        d = d.replace(day=1)
    return d


def list_meta() -> dict[str, Any]:
    return {
        'periods': [{'id': k, 'label': v} for k, v in PERIOD_LABELS.items()],
        'biggenres': [{'id': k, 'label': v} for k, v in sorted(BIGGENRE_LABELS.items())],
        'end_status': [{'id': k, 'label': v} for k, v in END_LABELS.items()],
        'default_dates': {p: default_target_date(p).isoformat() for p in PERIOD_LABELS},
        'source': 'https://dev.syosetu.com/',
        'note': 'データはなろう小説API・ランキングAPIから取得しています。',
    }

"""小説家になろう 公式API クライアント（なろうデベロッパー）"""
from __future__ import annotations

import gzip
import json
import time
from datetime import date, timedelta
from typing import Any

import requests

from config import NOVEL_API_URL, NOVEL_BATCH_SIZE, NOVEL_FIELDS, RANK_API_URL

_SESSION = requests.Session()
_SESSION.headers.update({'User-Agent': 'NarouRankingNav/0.1 (personal; dev.syosetu.com)'})


def _get_json_gzip(url: str, params: dict[str, Any]) -> Any:
    params = {**params, 'out': 'json', 'gzip': 5}
    r = _SESSION.get(url, params=params, timeout=45)
    r.raise_for_status()
    return json.loads(gzip.decompress(r.content))


def rank_rtype(target: date, period: str) -> str:
    """period: d=日間, w=週間(火曜), m=月間(1日), q=四半期(1日)"""
    if period == 'w':
        target = _nearest_tuesday(target)
    elif period in ('m', 'q'):
        target = target.replace(day=1)
    return f"{target.strftime('%Y%m%d')}-{period}"


def _nearest_tuesday(d: date) -> date:
    while d.weekday() != 1:
        d -= timedelta(days=1)
    return d


def fetch_ranking(target: date, period: str) -> list[dict[str, Any]]:
    rtype = rank_rtype(target, period)
    data = _get_json_gzip(RANK_API_URL, {'rtype': rtype})
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict) and row.get('ncode')]


def fetch_novels(ncodes: list[str]) -> dict[str, dict[str, Any]]:
    """ncode -> 作品情報"""
    out: dict[str, dict[str, Any]] = {}
    for i in range(0, len(ncodes), NOVEL_BATCH_SIZE):
        chunk = ncodes[i:i + NOVEL_BATCH_SIZE]
        joined = '-'.join(chunk)
        data = _get_json_gzip(
            NOVEL_API_URL,
            {'of': NOVEL_FIELDS, 'ncode': joined},
        )
        if not isinstance(data, list):
            continue
        for row in data[1:]:
            if isinstance(row, dict) and row.get('ncode'):
                out[row['ncode']] = row
        time.sleep(0.3)
    return out


def novel_url(ncode: str) -> str:
    return f'https://ncode.syosetu.com/{ncode.lower()}/'

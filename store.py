"""作品データ JSON ストア"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from config import WORKS_FILE

_slug_re = re.compile(r'[^\w\-]+', re.UNICODE)
_ascii_slug_re = re.compile(r'[^a-z0-9\-]+')


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = s.replace('～', '-').replace('〜', '-').replace(' ', '-')
    s = _slug_re.sub('-', s)
    s = re.sub(r'-+', '-', s).strip('-')[:80]
    if not s:
        s = 'work-' + hashlib.md5(text.encode('utf-8')).hexdigest()[:10]
    return s


def share_slugify(title: str, work_id: str) -> str:
    """ASCII-only slug for social sharing (X truncates Unicode in URLs)."""
    base = slugify(title).lower()
    ascii_only = _ascii_slug_re.sub('-', base)
    ascii_only = re.sub(r'-+', '-', ascii_only).strip('-')[:80]
    if len(ascii_only) >= 4:
        return ascii_only
    digest = hashlib.md5(work_id.encode('utf-8')).hexdigest()[:10]
    return f'w-{digest}'


def resolve_share_slug(work: dict[str, Any]) -> str:
    slug = work.get('share_slug') or share_slugify(work.get('title', ''), work.get('id', ''))
    return slug


def ensure_store():
    WORKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not WORKS_FILE.exists():
        WORKS_FILE.write_text('[]', encoding='utf-8')


def load_works() -> list[dict[str, Any]]:
    ensure_store()
    try:
        return json.loads(WORKS_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return []


def save_works(works: list[dict[str, Any]]):
    WORKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    WORKS_FILE.write_text(
        json.dumps(works, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


def find_work(work_id: str) -> dict[str, Any] | None:
    for w in load_works():
        if w.get('id') == work_id or w.get('share_slug') == work_id:
            return w
    return None


def upsert_work(work: dict[str, Any]) -> dict[str, Any]:
    works = load_works()
    work = {**work, 'updated_at': date.today().isoformat()}
    if not work.get('id'):
        work['id'] = slugify(work.get('title', 'work'))
    replaced = False
    for i, w in enumerate(works):
        if w.get('id') == work['id'] or (
            work.get('annict_id') and w.get('annict_id') == work.get('annict_id')
        ):
            # 手動メモは上書きしないようマージ
            merged = {**w, **{k: v for k, v in work.items() if v not in (None, '', [])}}
            works[i] = merged
            replaced = True
            work = merged
            break
    if not replaced:
        works.append(work)
    save_works(works)
    return work

"""2026年春・夏クールの作品を works.json に追加（既存IDはスキップ）"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import load_works, save_works, slugify, share_slugify

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = [
    ROOT / 'data' / 'season_expansion_spring.json',
    ROOT / 'data' / 'season_expansion_summer.json',
]


def _base(w: dict) -> dict:
    title = w['title']
    work_id = slugify(title)
    row = {
        'id': work_id,
        'season': w['season'],
        'status': 'upcoming',
        'media': 'tv',
        'memo': '',
        'official_url': w.get('official_url', ''),
        'title': title,
        'source_type': w['source_type'],
        'source_title': w['source_title'],
        'source_volume_from': w.get('source_volume_from'),
        'source_volume_to': w.get('source_volume_to'),
        'source_volume_approximate': w.get('source_volume_approximate', True),
        'source_volume_note': w.get('source_volume_note', ''),
        'read_order': w.get('read_order', '1巻から'),
        'amazon_search': w.get('amazon_search', f'{w["source_title"]} 原作'),
        'tags': w.get('tags', []),
        'watchers_count': w.get('watchers_count', 5000),
        'share_slug': w.get('share_slug') or share_slugify(title, work_id),
        'main_comment': w['main_comment'],
    }
    for key in ('isbn', 'amazon_asin', 'cover_image_url'):
        if w.get(key):
            row[key] = w[key]
    return row


def main() -> int:
    new_rows: list[dict] = []
    for path in DATA_FILES:
        new_rows.extend(json.loads(path.read_text(encoding='utf-8')))
    works = load_works()
    existing_ids = {w['id'] for w in works}
    existing_titles = {w['title'] for w in works}
    added_spring = added_summer = 0
    for raw in new_rows:
        row = _base(raw)
        if row['id'] in existing_ids or row['title'] in existing_titles:
            continue
        works.append(row)
        existing_ids.add(row['id'])
        existing_titles.add(row['title'])
        if row['season'] == '2026-spring':
            added_spring += 1
        else:
            added_summer += 1
    works.sort(key=lambda w: (-(w.get('watchers_count') or 0), w.get('season', ''), w.get('title', '')))
    save_works(works)
    spring_total = sum(1 for w in works if w.get('season') == '2026-spring')
    summer_total = sum(1 for w in works if w.get('season') == '2026-summer')
    print(f'added spring: {added_spring}, added summer: {added_summer}')
    print(f'totals -> spring: {spring_total}, summer: {summer_total}, all: {len(works)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

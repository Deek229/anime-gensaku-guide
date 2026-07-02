"""Generate Search Console index registration checklist CSV."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import SITE_URL
from store import resolve_share_slug

BASE = (SITE_URL if SITE_URL.startswith('http') and '127.0.0.1' not in SITE_URL and 'localhost' not in SITE_URL
        else 'https://anime-gensaku-guide.onrender.com').rstrip('/')
WORKS_FILE = ROOT / 'data' / 'works.json'
CSV_PATH = ROOT / 'docs' / 'インデックス登録チェックリスト.csv'

HEADERS = [
    '優先度',
    'ページ名',
    'URL（フル）',
    'インデックス登録リクエスト',
    'site:検索で確認',
    'メモ',
]

PRIORITY_ORDER = {'★★★': 0, '★★☆': 1, '★☆☆': 2}


def full_url(path: str) -> str:
    if path == '/':
        return f'{BASE}/'
    return BASE + path


def main() -> None:
    works = json.loads(WORKS_FILE.read_text(encoding='utf-8'))
    rows: list[dict[str, str]] = []

    rows.append({
        '優先度': '★★☆',
        'ページ名': 'トップ（ホーム）',
        'URL（フル）': full_url('/'),
        'インデックス登録リクエスト': '',
        'site:検索で確認': '済（6/28時点）',
        'メモ': 'Google検索 site: で表示確認済み',
    })
    rows.append({
        '優先度': '★★☆',
        'ページ名': 'なろうランキング',
        'URL（フル）': full_url('/rankings'),
        'インデックス登録リクエスト': '',
        'site:検索で確認': '済（6/28時点）',
        'メモ': 'Google検索 site: で表示確認済み',
    })

    sorted_works = sorted(works, key=lambda w: w.get('watchers_count', 0), reverse=True)
    for index, work in enumerate(sorted_works):
        if index < 5:
            priority = '★★★'
        elif index < 10:
            priority = '★★☆'
        else:
            priority = '★☆☆'
        rows.append({
            '優先度': priority,
            'ページ名': work['title'],
            'URL（フル）': full_url(f"/works/{resolve_share_slug(work)}"),
            'インデックス登録リクエスト': '',
            'site:検索で確認': '',
            'メモ': '',
        })

    rows.sort(key=lambda row: (PRIORITY_ORDER[row['優先度']], row['ページ名']))

    CSV_PATH.parent.mkdir(exist_ok=True)
    with CSV_PATH.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f'Created {CSV_PATH} ({len(rows)} rows)')


if __name__ == '__main__':
    main()

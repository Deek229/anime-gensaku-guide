"""Generate Search Console index registration checklist CSV."""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import SITE_URL
from guide_service import list_matome_pages
from store import resolve_share_slug

BASE = (SITE_URL if SITE_URL.startswith('http') and '127.0.0.1' not in SITE_URL and 'localhost' not in SITE_URL
        else 'https://anime-gensaku-guide.onrender.com').rstrip('/')
WORKS_FILE = ROOT / 'data' / 'works.json'
CSV_PATH = ROOT / 'docs' / 'インデックス登録チェックリスト.csv'
SHEET_IMPORT_PATH = ROOT / 'docs' / 'インデックス登録チェックリスト_スプレッドシート貼付用.csv'
USER_STATUS_PATH = ROOT / 'tools' / 'checklist_user_status.json'

HEADERS = [
    '優先度',
    'ページ名',
    'URL（フル）',
    'インデックス登録リクエスト',
    'site:検索で確認',
    'メモ',
]

PRIORITY_ORDER = {'★★★': 0, '★★☆': 1, '★☆☆': 2}

HUB_DEFAULTS = {
    '/': {
        'site:検索で確認': '済（6/28時点）',
        'メモ': 'Google検索 site: で表示確認済み',
    },
    '/rankings': {
        'site:検索で確認': '済（6/28時点）',
        'メモ': 'Google検索 site: で表示確認済み',
    },
    '/matome/2026-spring': {'メモ': 'SEOまとめページ'},
    '/matome/2026-summer': {'メモ': 'SEOまとめページ'},
    '/matome/2026-autumn': {'メモ': 'SEOまとめページ'},
    '/matome/2027-winter': {'メモ': 'SEOまとめページ'},
}


def full_url(path: str) -> str:
    if path == '/':
        return f'{BASE}/'
    return BASE + path


def _slug_from_url(url: str) -> str:
    url = (url or '').strip().rstrip('/')
    if url.endswith(BASE) or url == BASE.rstrip('/'):
        return '_top'
    if url.endswith('/rankings'):
        return '_rankings'
    if '/works/' in url:
        return url.rsplit('/works/', 1)[-1]
    return url


STATUS_FIELDS = ('インデックス登録リクエスト', 'site:検索で確認', 'メモ')


def _row_status(row: dict[str, str]) -> dict[str, str]:
    return {field: (row.get(field) or '').strip() for field in STATUS_FIELDS}


def _load_status_from_csv(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    status: dict[str, dict[str, str]] = {}
    text = None
    for encoding in ('utf-8-sig', 'utf-8', 'cp932'):
        try:
            text = path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        return {}
    rows = list(csv.DictReader(text.splitlines()))
    if not rows:
        return {}
    keys = list(rows[0].keys())

    def pick(row: dict[str, str], idx: int) -> str:
        if idx < len(keys):
            return str(row.get(keys[idx], '') or '')
        return ''

    for row in rows:
        if 'URL（フル）' in row:
            url = (row.get('URL（フル）') or '').strip()
            name = (row.get('ページ名') or '').strip()
            fields = _row_status(row)
        else:
            url = pick(row, 2).strip()
            name = pick(row, 1).strip()
            fields = {
                'インデックス登録リクエスト': pick(row, 3).strip(),
                'site:検索で確認': pick(row, 4).strip(),
                'メモ': pick(row, 5).strip(),
            }
        if not url:
            continue
        status[_slug_from_url(url)] = fields
        if name:
            status[f'name:{name}'] = fields
        if '/works/' in url:
            status[url.rstrip('/').rsplit('/', 1)[-1]] = fields
    return status


def _load_existing_status() -> dict[str, dict[str, str]]:
    return _load_status_from_csv(CSV_PATH)


def _normalize_done_status(status: dict[str, str]) -> dict[str, str]:
    """site:列だけに「済」がある場合はインデックス列にも反映（リマインダー用）。"""
    index = status.get('インデックス登録リクエスト', '')
    site = status.get('site:検索で確認', '')
    if not index and site and '済' in site:
        status = dict(status)
        status['インデックス登録リクエスト'] = site
    return status


def _merge_status(
    key: str,
    existing: dict[str, dict[str, str]],
    *,
    path: str | None = None,
    page_name: str | None = None,
) -> dict[str, str]:
    merged = {
        'インデックス登録リクエスト': '',
        'site:検索で確認': '',
        'メモ': '',
    }
    if path and path in HUB_DEFAULTS:
        merged.update(HUB_DEFAULTS[path])
    for lookup in (key, f'name:{page_name}' if page_name else None):
        if not lookup or lookup not in existing:
            continue
        for field in merged:
            if existing[lookup].get(field):
                merged[field] = existing[lookup][field]
    return _normalize_done_status(merged)


def _load_user_status_overlay() -> dict[str, dict[str, str]]:
    if not USER_STATUS_PATH.exists():
        return {}
    data = json.loads(USER_STATUS_PATH.read_text(encoding='utf-8'))
    overlay: dict[str, dict[str, str]] = {}
    for page_name, fields in data.items():
        if page_name.startswith('_') or not isinstance(fields, dict):
            continue
        overlay[f'name:{page_name}'] = {
            field: str(value).strip()
            for field, value in fields.items()
            if field in STATUS_FIELDS and str(value).strip()
        }
    return overlay


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description='インデックス登録チェックリストCSVを再生成')
    parser.add_argument(
        '--merge-csv',
        action='append',
        default=[],
        help='進捗をマージするCSV（スプレッドシート書き出しなど）。複数指定可',
    )
    parser.add_argument(
        '--also-sheet-import',
        action='store_true',
        help=f'貼付用コピーも書く: {SHEET_IMPORT_PATH.name}',
    )
    args = parser.parse_args(argv)

    works = json.loads(WORKS_FILE.read_text(encoding='utf-8'))
    existing = _load_existing_status()
    existing.update(_load_user_status_overlay())
    for merge_path in args.merge_csv:
        existing.update(_load_status_from_csv(Path(merge_path)))
    rows: list[dict[str, str]] = []

    for path, name in [('/', 'トップ（ホーム）'), ('/rankings', 'なろうランキング')]:
        key = '_top' if path == '/' else '_rankings'
        status = _merge_status(key, existing, path=path, page_name=name)
        rows.append({
            '優先度': '★★☆',
            'ページ名': name,
            'URL（フル）': full_url(path),
            **status,
        })

    for matome in list_matome_pages():
        status = _merge_status(matome['slug'], existing, path=matome['path'], page_name=matome['title'])
        rows.append({
            '優先度': '★★☆',
            'ページ名': matome['title'],
            'URL（フル）': full_url(matome['path']),
            **status,
        })

    sorted_works = sorted(works, key=lambda w: w.get('watchers_count', 0), reverse=True)
    for index, work in enumerate(sorted_works):
        if index < 5:
            priority = '★★★'
        elif index < 10:
            priority = '★★☆'
        else:
            priority = '★☆☆'
        slug = resolve_share_slug(work)
        status = _merge_status(slug, existing, page_name=work['title'])
        rows.append({
            '優先度': priority,
            'ページ名': work['title'],
            'URL（フル）': full_url(f'/works/{slug}'),
            **status,
        })

    rows.sort(key=lambda row: (PRIORITY_ORDER[row['優先度']], -_watchers_for_row(row, sorted_works), row['ページ名']))

    CSV_PATH.parent.mkdir(exist_ok=True)
    outputs = [CSV_PATH]
    if args.also_sheet_import:
        outputs.append(SHEET_IMPORT_PATH)
    for out_path in outputs:
        with out_path.open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)

    done = sum(1 for r in rows if '済' in r.get('インデックス登録リクエスト', ''))
    print(f'Created {CSV_PATH} ({len(rows)} rows, {done} 済)')
    if args.also_sheet_import:
        print(f'Also wrote {SHEET_IMPORT_PATH}')


def _watchers_for_row(row: dict[str, str], works: list[dict]) -> int:
    url = row.get('URL（フル）', '')
    if url.endswith('/'):
        return 100_000
    if url.endswith('/rankings'):
        return 99_999
    slug = _slug_from_url(url)
    for work in works:
        if resolve_share_slug(work) == slug:
            return int(work.get('watchers_count', 0))
    return 0


if __name__ == '__main__':
    main(sys.argv[1:])

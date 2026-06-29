"""作品の表紙画像を OpenBD / Amazon から取得して works.json を更新"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from amazon_links import amazon_cover_url
from store import load_works, save_works

sys.stdout.reconfigure(encoding='utf-8')

OPENBD_GET = 'https://api.openbd.jp/v1/get?isbn={isbn}'
PLACEHOLDER = '/static/cover-placeholder.svg'

# work id -> 表紙用の ISBN-13 / Amazon ASIN（原作1巻または該当巻）
DEFAULT_SOURCES: dict[str, dict[str, str]] = {
    '無職転生ⅲ-異世界行ったら本気だす': {
        'isbn': '9784040662206',
        'amazon_asin': '4040662202',
    },
    '幼女戦記ⅱ': {
        'isbn': '9784041051252',
        'amazon_asin': '4041051258',
    },
    're-ゼロから始める異世界生活-4th-season-奪還編': {
        'isbn': '9784040662084',
        'amazon_asin': '4040662083',
    },
    'ぐらんぶる-season-3': {
        'isbn': '9784063879902',
        'amazon_asin': '4063879909',
    },
    'bleach-千年血戦篇-禍進譚': {
        'isbn': '9784088806495',
        'amazon_asin': '4088806492',
    },
    '君のことが大大大大大好きな100人の彼女-第3期': {
        'isbn': '9784088915333',
        'amazon_asin': '408891533X',
    },
    '逃げ上手の若君-第二期': {
        'isbn': '9784088827100',
        'amazon_asin': '4088827104',
    },
    '骸骨騎士様-只今異世界へお出掛け中ⅱ': {
        'isbn': '9784865540543',
        'amazon_asin': '4865540547',
    },
    '乙女ゲー世界はモブに厳しい世界です2': {
        'isbn': '9784864361940',
        'amazon_asin': '4864361940',
    },
    '片田舎のおっさん-剣聖になるⅱ': {
        'isbn': '9784253306918',
        'amazon_asin': '4253306918',
    },
    'きみが死ぬまで恋をしたい': {
        'isbn': '9784758078986',
        'amazon_asin': '475807898X',
    },
    '株式会社マジルミエ-第2期': {
        'isbn': '9784088830285',
        'amazon_asin': '4088830288',
    },
    '正反対な君と僕-第2期': {
        'isbn': '9784088834569',
        'amazon_asin': '4088834569',
    },
    '攻殻機動隊-the-ghost-in-the-shell': {
        'isbn': '9784063337125',
        'amazon_asin': '406333712X',
    },
    '天幕のジャードゥーガル': {
        'isbn': '9784088835670',
        'amazon_asin': '4088835670',
    },
    'クレバテスⅱ-魔獣の王と偽りの勇者伝承': {
        'isbn': '9784866970804',
        'amazon_asin': '4866970804',
    },
    'スーパーの裏でヤニ吸うふたり': {
        'isbn': '9784757580947',
        'amazon_asin': '4757580940',
    },
    '追放された転生重騎士はゲーム知識で無双する': {
        'isbn': '9784065281437',
        'amazon_asin': '4065281431',
    },
    '二十世紀電氣目録-ユーレカ-エヴリカ': {
        'isbn': '9784907064884',
        'amazon_asin': '4907064888',
    },
    'ワンパンマン-第3期': {
        'isbn': '9784088815565',
        'amazon_asin': '4088815564',
    },
}


def _normalize_isbn(isbn: str) -> str:
    return ''.join(ch for ch in (isbn or '') if ch.isdigit())


def fetch_openbd_cover(isbn: str) -> str:
    isbn = _normalize_isbn(isbn)
    if len(isbn) != 13:
        return ''
    try:
        with urllib.request.urlopen(
            OPENBD_GET.format(isbn=isbn),
            timeout=12,
        ) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return ''
    if not data or not data[0]:
        return ''
    summary = data[0].get('summary') or {}
    return (summary.get('cover') or '').strip()


def _cover_exists(url: str, min_bytes: int = 1000) -> bool:
    if not url:
        return False
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            length = int(resp.headers.get('Content-Length', 0))
            return length >= min_bytes
    except urllib.error.URLError:
        return False


def resolve_cover_url(work: dict) -> tuple[str, str]:
    """(cover_url, source) source: openbd|amazon|placeholder|existing"""
    existing = (work.get('cover_image_url') or '').strip()
    if existing and existing != PLACEHOLDER and _cover_exists(existing):
        return existing, 'existing'

    isbn = _normalize_isbn(work.get('isbn') or '')
    asin = (work.get('amazon_asin') or '').strip()

    if isbn:
        openbd_url = fetch_openbd_cover(isbn)
        if openbd_url and _cover_exists(openbd_url):
            return openbd_url, 'openbd'
        time.sleep(0.15)

    if asin:
        amazon_url = amazon_cover_url(asin)
        if _cover_exists(amazon_url):
            return amazon_url, 'amazon'

    if work.get('source_type') in ('original', '') and not work.get('source_title'):
        return PLACEHOLDER, 'placeholder'

    return PLACEHOLDER, 'placeholder'


def merge_defaults(work: dict) -> dict:
    defaults = DEFAULT_SOURCES.get(work.get('id', ''), {})
    merged = {**work}
    if defaults.get('isbn') and not merged.get('isbn'):
        merged['isbn'] = defaults['isbn']
    if defaults.get('amazon_asin') and not merged.get('amazon_asin'):
        merged['amazon_asin'] = defaults['amazon_asin']
    return merged


def main() -> int:
    works = load_works()
    stats = {'openbd': 0, 'amazon': 0, 'placeholder': 0, 'existing': 0}
    updated = 0

    for i, work in enumerate(works):
        work = merge_defaults(work)
        cover_url, source = resolve_cover_url(work)
        work['cover_image_url'] = cover_url
        stats[source] = stats.get(source, 0) + 1
        works[i] = work
        updated += 1
        title = work.get('title', work.get('id', ''))
        print(f'[{source:11}] {title}')

    save_works(works)
    real_covers = sum(1 for w in works if w.get('cover_image_url') != PLACEHOLDER)
    print(f'\nupdated {updated} works | covers: {real_covers} | placeholder: {stats.get("placeholder", 0)}')
    print(f'sources: openbd={stats.get("openbd", 0)} amazon={stats.get("amazon", 0)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

"""作品の表紙画像を OpenBD / Amazon から取得し static/covers/ に保存して works.json を更新"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from amazon_links import amazon_cover_url
from store import load_works, resolve_share_slug, save_works

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
COVERS_DIR = ROOT / 'static' / 'covers'
OPENBD_GET = 'https://api.openbd.jp/v1/get?isbn={isbn}'
PLACEHOLDER = '/static/cover-placeholder.svg'
MIN_BYTES = 1000
HANMOTO_COVER = 'https://img.hanmoto.com/bd/img/{isbn}_600.jpg'
OVERLAP_COVER = 'https://over-lap.co.jp/Contents/ProductImages/0/{isbn}_L.jpg'
OPENBD_COVER = 'https://cover.openbd.jp/{isbn}_400.jpg'
USER_AGENT = 'Mozilla/5.0 (compatible; AnimeGensakuGuide/1.0)'

# share_slug -> direct cover URL (OpenBD/版元未登録の特例)
MANUAL_COVER_URLS: dict[str, str] = {
    'mobuseka-2': 'https://microgrouplibrary.com/web/img/uploads/book/179.jpg',
    '20seiki-eureka': 'https://makeshop-multi-images.akamaized.net/kyoanibtc/itemimages/000000001538_2wjBJZY.jpg',
    # OpenBD/Amazon から取得できない作品
    'tensura-4': 'https://microgrouplibrary.com/web/img/uploads/book/702.jpg',
    'all-works-maid': 'https://www.animatebookstore.com/get_image.php?product_id=770143&thumb=large',
    'last-boss-queen-2': 'https://www.animatebookstore.com/get_image.php?product_id=793008&thumb=large',
    'neko-to-ryu': 'https://www.cmoa.jp/data/image/title/title_0000206418/VOLUME/100002064180001.jpg',
    'futsutsuka-akujo': 'https://c.bookwalker.jp/9643044/t_700x780.jpg',
    # 単行本未刊行のWeb漫画
    'someya-san': 'https://www.cmoa.jp/data/image/title/title_0000356459/VOLUME/100003564590001.jpg',
}

# work id -> 表紙用の ISBN-13 / Amazon ASIN（原作1巻または該当巻）
DEFAULT_SOURCES: dict[str, dict[str, str]] = {
    '無職転生ⅲ-異世界行ったら本気だす': {
        'isbn': '9784040687452',
        'amazon_asin': '4040687452',
    },
    '幼女戦記ⅱ': {
        'isbn': '9784047309029',
        'amazon_asin': '4047309029',
    },
    're-ゼロから始める異世界生活-4th-season-奪還編': {
        'isbn': '9784040640068',
        'amazon_asin': '4040640068',
    },
    'ぐらんぶる-season-3': {
        'isbn': '9784065134474',
        'amazon_asin': '4065134474',
    },
    'bleach-千年血戦篇-禍進譚': {
        'isbn': '9784088806495',
        'amazon_asin': '4088806495',
    },
    '君のことが大大大大大好きな100人の彼女-第3期': {
        'isbn': '9784088921648',
        'amazon_asin': '408892164X',
    },
    '逃げ上手の若君-第二期': {
        'isbn': '9784088830735',
        'amazon_asin': '4088830735',
    },
    '骸骨騎士様-只今異世界へお出掛け中ⅱ': {
        'isbn': '9784865541465',
        'amazon_asin': '4865541465',
    },
    '乙女ゲー世界はモブに厳しい世界です2': {
        'isbn': '9784896379112',
        'amazon_asin': '4896379112',
    },
    '片田舎のおっさん-剣聖になるⅱ': {
        'isbn': '9784757580220',
        'amazon_asin': '4757580220',
    },
    'きみが死ぬまで恋をしたい': {
        'isbn': '9784758078986',
        'amazon_asin': '475807898X',
    },
    '株式会社マジルミエ-第2期': {
        'isbn': '9784088835402',
        'amazon_asin': '4088835402',
    },
    '正反対な君と僕-第2期': {
        'isbn': '9784088841434',
        'amazon_asin': '4088841434',
    },
    '攻殻機動隊-the-ghost-in-the-shell': {
        'isbn': '9784063132489',
        'amazon_asin': '4063132489',
    },
    '天幕のジャードゥーガル': {
        'isbn': '9784253264464',
        'amazon_asin': '4253264464',
    },
    'クレバテスⅱ-魔獣の王と偽りの勇者伝承': {
        'isbn': '9784048113502',
        'amazon_asin': '404811350X',
    },
    'スーパーの裏でヤニ吸うふたり': {
        'isbn': '9784757580947',
        'amazon_asin': '4757580947',
    },
    '追放された転生重騎士はゲーム知識で無双する': {
        'isbn': '9784065281437',
        'amazon_asin': '4065281437',
    },
    '二十世紀電氣目録-ユーレカ-エヴリカ': {
        'isbn': '9784907064884',
        'amazon_asin': '4907064884',
    },
    'ワンパンマン-第3期': {
        'isbn': '9784088815565',
        'amazon_asin': '4088815565',
    },
    'ワールド-イズ-ダンシング': {
        'isbn': '9784065245057',
        'amazon_asin': '4065245057',
    },
}


def _normalize_isbn(isbn: str) -> str:
    return ''.join(ch for ch in (isbn or '') if ch.isdigit())


def cover_slug(work: dict) -> str:
    return resolve_share_slug(work)


def local_cover_rel(work: dict) -> str:
    return f'/static/covers/{cover_slug(work)}.jpg'


def local_cover_file(work: dict) -> Path:
    return COVERS_DIR / f'{cover_slug(work)}.jpg'


def _local_cover_valid(path: Path) -> bool:
    try:
        return path.is_file() and path.stat().st_size >= MIN_BYTES
    except OSError:
        return False


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


def _download_image(url: str, dest: Path) -> bool:
    if not url:
        return False
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
    except urllib.error.URLError:
        return False
    if len(data) < MIN_BYTES:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True


def _remote_candidates(work: dict) -> list[tuple[str, str]]:
    """(url, source_label) in priority order."""
    candidates: list[tuple[str, str]] = []
    isbn = _normalize_isbn(work.get('isbn') or '')
    asin = (work.get('amazon_asin') or '').strip()
    slug = cover_slug(work)

    manual = MANUAL_COVER_URLS.get(slug, '')
    if manual:
        candidates.append((manual, 'manual'))

    if isbn:
        openbd_url = fetch_openbd_cover(isbn)
        if openbd_url:
            candidates.append((openbd_url, 'openbd'))
        candidates.append((HANMOTO_COVER.format(isbn=isbn), 'hanmoto'))
        candidates.append((OVERLAP_COVER.format(isbn=isbn), 'overlap'))
        candidates.append((OPENBD_COVER.format(isbn=isbn), 'openbd-cdn'))
        time.sleep(0.15)

    if asin:
        candidates.append((amazon_cover_url(asin), 'amazon'))

    existing = (work.get('cover_image_url') or '').strip()
    if existing and existing not in (PLACEHOLDER,) and not existing.startswith('/static/covers/'):
        candidates.append((existing, 'existing'))

    return candidates


def resolve_cover(work: dict, *, force: bool = False) -> tuple[str, str]:
    """(cover_url, source)"""
    dest = local_cover_file(work)
    if force and dest.is_file():
        dest.unlink(missing_ok=True)
    if _local_cover_valid(dest):
        return local_cover_rel(work), 'cached'

    if work.get('source_type') in ('original', '') and not work.get('source_title'):
        return PLACEHOLDER, 'placeholder'

    for url, source in _remote_candidates(work):
        if _download_image(url, dest):
            return local_cover_rel(work), source

    if _local_cover_valid(dest):
        return local_cover_rel(work), 'cached'

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
    parser = argparse.ArgumentParser(description='Fetch cover images for works')
    parser.add_argument('--force', action='store_true', help='Re-download even if cached')
    args = parser.parse_args()

    works = load_works()
    stats: dict[str, int] = {}
    updated = 0

    for i, work in enumerate(works):
        work = merge_defaults(work)
        cover_url, source = resolve_cover(work, force=args.force)
        work['cover_image_url'] = cover_url
        stats[source] = stats.get(source, 0) + 1
        works[i] = work
        updated += 1
        title = work.get('title', work.get('id', ''))
        print(f'[{source:11}] {title} -> {cover_url}')

    save_works(works)
    real_covers = sum(1 for w in works if w.get('cover_image_url') != PLACEHOLDER)
    print(f'\nupdated {updated} works | covers: {real_covers} | placeholder: {stats.get("placeholder", 0)}')
    print(f'sources: {", ".join(f"{k}={v}" for k, v in sorted(stats.items()))}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

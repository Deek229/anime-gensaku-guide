"""2026秋・2027冬の ISBN/ASIN/amazon_search を正規化し表紙を再取得"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fetch_covers import MANUAL_COVER_URLS, merge_defaults, resolve_cover
from store import load_works, save_works

TARGET_SEASONS = {'2026-autumn', '2027-winter'}

# share_slug -> ISBN-13（版元・出版社サイトで確認済み）
ISBN13_BY_SLUG: dict[str, str] = {
    # 誤表紙・誤書誌の差し替え
    'sakamoto-days-2': '9784088831916',
    'kanojo-no-tomodachi': '9784065264799',
    'koori-no-jouheki-2': '9784088836485',
    'jigen-chihara': '9784758024389',
    'golden-kamuy-final': '9784088921624',
    'db-super-beerus': '9784088834702',
    'saikyou-soubi-isekai': '9784040731926',
    'rayearth-2026': '9784063346428',
    'hotaru-no-yomeiri': '9784098521470',
    'black-clover-2': '9784088825946',
    'shangri-la-3': '9784065315866',
    'iruma-if-mafia': '9784253229180',
    'jojo-sbr-2-3': '9784088700601',
    # プレースホルダーだった作品
    'janken-bank': '9784088916576',
    'charisma': '9784575830385',
    'sudachi-maou': '9784065275573',
    'isshiki-san-koi': '9784041109328',
    'zatsuyou-fuyo': '9784575243994',
    'tensei-ken-2': '9784896378634',
    # チェックディジット修正（ISBN-13 正）
    'ao-no-hako-2': '9784088833897',
    'aoashi-2': '9784098605965',
    'akane-banashi-2': '9784088834276',
    'tokyo-revengers-santen': '9784065281789',
    'kusuriya-3': '9784757579859',
    'hotel-inhumans-2': '9784098702320',
    'hyouken-2': '9784040723260',
    'kanata-kara': '9784592216585',
    'kikansha-mahou-2': '9784046807342',
    'kizu-darake-seijo-2': '9784592217100',
    'nia-liston': '9784046840777',
    'psyren': '9784088741652',
    'ranma-1-2-3': '9784091433197',
    'sasaki-pea-2': '9784041124181',
    'shibou-yuugi': '9784041127830',
    'tantei-shinda-2': '9784049136322',
    'tensei-kizoku-3': '9784046809668',
    'tougen-anki-2': '9784088840810',
    'gacha-bishoujo': '9784046800479',
    'hime-kishi-himo': '9784046808642',
    'hirayasumi': '9784065284695',
    'historie': '9784063142392',
    'josemaru': '9784098720104',
    'kekkaishi-ichirinka': '9784049122141',
    'matsurika-kanri': '9784049134334',
    'ramen-akane-2': '9784040751753',
    'the-one-piece': '9784088725092',
    'zombie-harem': '9784046801223',
}

AMAZON_SEARCH_FIXES: dict[str, str] = {
    'tensei-ken-2': '転生したら剣でした ラノベ',
}

# オリジナル・ゲーム（公式キービジュアル／OGP）
ORIGINAL_COVER_URLS: dict[str, str] = {
    'cyberpunk-edgerunners-2': (
        'https://upload.wikimedia.org/wikipedia/en/8/8a/Cyberpunk_Edgerunners_poster.jpg'
    ),
    'kaze-wo-tsugumono': 'https://www.aniplex.co.jp/lineup/kazetsugu/assets/img/ogp.jpg',
    'mygo-ave-mujica': 'https://bang-dream.com/mygo/assets/img/common/ogp.jpg',
    'gensou-suikoden-anime': 'https://img.hanmoto.com/bd/img/9784041099145_600.jpg',
}


def digits(s: str) -> str:
    return ''.join(c for c in (s or '') if c.isdigit())


def isbn13_checksum_ok(isbn13: str) -> bool:
    s = digits(isbn13)
    if len(s) != 13:
        return False
    total = sum(int(s[i]) * (1 if i % 2 == 0 else 3) for i in range(12))
    check = (10 - total % 10) % 10
    return int(s[12]) == check


def isbn13_to_isbn10(isbn13: str) -> str:
    s = digits(isbn13)
    if len(s) != 13 or not s.startswith('978'):
        return ''
    core = s[3:12]
    total = sum(int(d) * (10 - i) for i, d in enumerate(core))
    rem = (11 - total % 11) % 11
    check = 'X' if rem == 10 else str(rem)
    return core + check


def main() -> int:
    for slug, url in ORIGINAL_COVER_URLS.items():
        MANUAL_COVER_URLS[slug] = url

    works = load_works()
    fixed_meta = 0
    fetched = 0
    stats: dict[str, int] = {}

    for i, work in enumerate(works):
        if work.get('season') not in TARGET_SEASONS:
            continue
        slug = work.get('share_slug', '')
        if slug in ISBN13_BY_SLUG:
            isbn = ISBN13_BY_SLUG[slug]
            asin = isbn13_to_isbn10(isbn)
            if isbn13_checksum_ok(isbn) and asin:
                work['isbn'] = isbn
                work['amazon_asin'] = asin
                fixed_meta += 1
            else:
                print(f'WARN checksum: {slug} isbn={isbn} asin={asin}')
        if slug in AMAZON_SEARCH_FIXES:
            work['amazon_search'] = AMAZON_SEARCH_FIXES[slug]

        work = merge_defaults(work)
        cover_url, source = resolve_cover(work, force=True)
        work['cover_image_url'] = cover_url
        works[i] = work
        stats[source] = stats.get(source, 0) + 1
        fetched += 1
        print(f'[{source:11}] {work.get("title", "")} -> {cover_url}')

    save_works(works)
    print(f'\nmetadata fixed: {fixed_meta} | covers refreshed: {fetched}')
    print(f'sources: {", ".join(f"{k}={v}" for k, v in sorted(stats.items()))}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

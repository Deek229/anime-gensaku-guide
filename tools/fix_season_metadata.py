"""2026秋・2027冬の ISBN/ASIN/amazon_search を正規化し表紙を再取得

IMPORTANT: ISBN13_BY_SLUG には版元で確認した正しい ISBN-13 のみ入れる。
偽ISBNのチェックディジットだけ直すと、別作品の表紙が付く。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fetch_covers import MANUAL_COVER_URLS, merge_defaults, resolve_cover
from store import load_works, save_works

TARGET_SEASONS = {'2026-autumn', '2027-winter'}

# share_slug -> ISBN-13（版元・OpenBDでタイトル一致確認済み）
ISBN13_BY_SLUG: dict[str, str] = {
    # --- スクショで誤表紙が確認された作品（最優先） ---
    'ranma-1-2-3': '9784091230959',           # らんま1/2 25
    'psyren': '9784088745329',                # PSYREN 1
    'kanata-kara': '9784592123514',           # 彼方から 1
    'kikansha-mahou-2': '9784046806611',      # 帰還者の魔法は特別です 漫画1（原作はWeb小説）
    'hotel-inhumans-2': '9784098513826',      # ホテル・インヒューマンズ 4
    'kizu-darake-seijo-2': '9784758018753',   # 傷だらけ聖女より報復をこめて 1
    'nia-liston': '9784798629704',            # 凶乱令嬢ニア・リストン LN 1
    'sasaki-pea-2': '9784046809155',          # 佐々木とピーちゃん 4
    'shibou-yuugi': '9784046819376',          # 死亡遊戯で飯を食う。 LN 1
    'tantei-shinda-2': '9784046800169',       # 探偵はもう、死んでいる。 4
    'tensei-kizoku-3': '9784065373095',       # 転生貴族 鑑定スキル LN 7
    'tougen-anki-2': '9784253280129',         # 桃源暗鬼 12
    'historie': '9784063143584',              # ヒストリエ 1
    'kekkaishi-ichirinka': '9784041118832',   # 結界師の一輪華 LN 1
    'zombie-harem': '9784861348600',          # ゾンビのあふれた世界… LN 1
    'matsurika-kanri': '9784047347045',       # 茉莉花官吏伝 LN 1
    'ramen-akane-2': '9784088836195',         # ラーメン赤猫 4
    'hime-kishi-himo': '9784049142150',       # 姫騎士様のヒモ LN 1
    'gacha-bishoujo': '9784896376029',        # ガチャを回して… LN 1
    'josemaru': '9784046074225',              # じょせまる つよくいきるひび
    # --- 以前の修正で正しいもの ---
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
    'janken-bank': '9784088916576',
    'charisma': '9784575830385',
    'sudachi-maou': '9784065275573',
    'isshiki-san-koi': '9784041109328',
    'zatsuyou-fuyo': '9784575243994',
    'tensei-ken-2': '9784896378634',
    'ao-no-hako-2': '9784088833897',
    'aoashi-2': '9784098605965',
    'akane-banashi-2': '9784088834276',
    'tokyo-revengers-santen': '9784065281789',
    'kusuriya-3': '9784757579859',
    'hirayasumi': '9784098611188',
    'hyouken-2': '9784065305539',
    'the-one-piece': '9784088725093',
    'mahoiku-restart': '9784800201829',
    'chojo-senpai': '9784088841083',
    'shuiro-no-kamen': '9784785969820',
    'magical-explorer': '9784041110072',
    'shin-tenipuri-u17': '9784088747248',
    'shinja-zero': '9784865544626',
    'ribarai-maryoku': '9784866753072',
    'fx-kurumi': '9784046806680',
    'ojisan-kawaii': '9784866750125',
    'romelia-senki': '9784800011374',
    'dark-summoner': '9784040747569',
    'mashle-3': '9784088823294',
    'marriage-toxin-2': '9784088832135',
    'kinioto': '9784046817327',
    'kizu-to-houtai': '9784065376928',
    'azley': '9784803007886',
    'kuroiwa-medaka-2': '9784065244906',
    'isekai-soudouki': '9784434189678',
}

# ゲーム・オリジナルは Amazon ASIN（ISBNなし）
ASIN_ONLY: dict[str, str] = {
    'gensou-suikoden-anime': 'B0DF9SBJ34',  # 幻想水滸伝 I&II HDリマスター Switch
}

AMAZON_SEARCH_FIXES: dict[str, str] = {
    'tensei-ken-2': '転生したら剣でした ラノベ',
    'gensou-suikoden-anime': '幻想水滸伝 I&II HDリマスター',
}

ORIGINAL_COVER_URLS: dict[str, str] = {
    'cyberpunk-edgerunners-2': (
        'https://upload.wikimedia.org/wikipedia/en/8/8a/Cyberpunk_Edgerunners_poster.jpg'
    ),
    'kaze-wo-tsugumono': 'https://kazetsugu.com/common/img/ogp.png',
    'mygo-ave-mujica': 'https://bang-dream.com/mygo/assets/img/ogp.png',
    # Amazon 商品画像（HDリマスター）
    'gensou-suikoden-anime': (
        'https://m.media-amazon.com/images/I/81qKQnJ8qLL._AC_SL1500_.jpg'
    ),
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
        elif slug in ASIN_ONLY:
            work['amazon_asin'] = ASIN_ONLY[slug]
            work.pop('isbn', None)
            fixed_meta += 1
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

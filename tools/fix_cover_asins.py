"""Fix wrong ISBN/ASIN metadata and re-fetch covers."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import load_works, save_works

# share_slug -> (isbn-13, amazon_asin / isbn-10)
FIXES: dict[str, tuple[str, str]] = {
    'aishiteru-game': ('9784098510474', '4098510472'),
    'akane-banashi': ('9784088831503', '4088831500'),
    'all-works-maid': ('9784866992723', '4866992723'),
    'beastars-final-2': ('9784253229081', '4253229085'),
    'black-torch': ('9784088810973', '4088810973'),
    'buchigire-reijo': ('9784798630762', '4798630764'),
    'dandadan': ('9784088825991', '4088825993'),
    'diamond-ace-2': ('9784065225172', '4065225172'),
    'dorohedoro-2': ('9784091882875', '4091882870'),
    'drstone-sf-3': ('9784088831602', '4088831608'),
    'futsutsuka-akujo': ('9784758036269', '4758036269'),
    'haibara-kun': ('9784798626802', '4798626805'),
    'hanashiori-san': ('9784065267493', '4065267493'),
    'hanazakari-2': ('9784592176657', '4592176650'),
    'hellmode-2': ('9784803015645', '4803015643'),
    'hidari-eri': ('9784088812984', '4088812984'),
    'himekishi-barbaroi': ('9784065227510', '4065227510'),
    'honzuki-oujo': ('9784864725217', '4864725217'),
    'ibitte-konai': ('9784758022453', '4758022453'),
    'ichijouma-mankitsu': ('9784832271395', '4832271393'),
    'iwamoto-senpai': ('9784088920382', '4088920384'),
    'jidouhanbaiki-3': ('9784041119594', '4041119594'),
    'jojo-sbr': ('9784088736013', '408873601X'),
    'kanokari-5': ('9784065328934', '4065328934'),
    'kimi-aishiteru-dokusha': ('9784866751733', '4866751733'),
    'kore-kaite-shine': ('9784098511433', '4098511433'),
    'kujima-utaeeba': ('9784098510924', '4098510928'),
    'kura2': ('9784046818812', '4046818812'),
    'last-boss-queen-2': ('9784758093941', '4758093941'),
    'liar-game': ('9784088768557', '4088768558'),
    'lv999-villager': ('9784047341173', '4047341173'),
    'mairimashita-iruma-4': ('9784253229180', '4253229182'),
    'mamonogurui': ('9784803018233', '4803018235'),
    'mao-2026': ('9784091293107', '4091293107'),
    'matatakorosareta': ('9784040748313', '4040748313'),
    'mujikaku-seijo': ('9784803015300', '4803015300'),
    'neko-to-ryu': ('9784800279866', '4800279866'),
    'nonbiri-nouka-2': ('9784047364554', '4047364554'),
    'oni-no-hanayome': ('9784813761242', '4813761240'),
    'otome-kaiju': ('9784040699141', '4040699141'),
    'otonari-tenshi-2': ('9784815608279', '481560827X'),
    'rakudai-kensha': ('9784041086247', '4041086248'),
    'reiwa-dara': ('9784046818515', '4046818514'),
    'reincarnation-no-kaben': ('9784800003768', '4800003768'),
    'replica-koi': ('9784049153774', '4049153777'),
    'ryomin-zero': ('9784803012385', '4803012385'),
    'saikyo-kareshi-oji': ('9784041085264', '4041085264'),
    'saikyo-ou-s2': ('9784046808929', '4046808929'),
    'sainan-osewa': ('9784798626475', '4798626473'),
    'saki-ike-densetsu': ('9784815601263', '4815601263'),
    'seihantaiteki-2': ('9784088841434', '4088841433'),
    'shuumatsu-3': ('9784867204153', '4867204153'),
    'snowball-earth': ('9784098611072', '4098611074'),
    'sora-wa-akai': ('9784091365019', '4091365019'),
    'suterare-seijo': ('9784040736457', '4040736457'),
    'taiari-deshita': ('9784040646138', '4040646138'),
    'tekkabe-jan': ('9784040692067', '4040692067'),
    'tenkou-osananajimi': ('9784040745015', '4040745019'),
    'tensura-4': ('9784867160565', '4867160565'),
    'tomei-yoru': ('9784815621452', '4815621452'),
    'tongari-boushi': ('9784063886900', '4063886900'),
    'tsue-to-ken-2': ('9784065303351', '4065303354'),
    'uchi-no-ototo': ('9784088443461', '4088443462'),
    'yani-neko': ('9784065323502', '4065323502'),
    'yojitsu-4': ('9784046805164', '4046805164'),
    'yomi-no-tsugai': ('9784757579620', '4757579620'),
}

def main() -> int:
    works = load_works()
    fixed = 0
    for w in works:
        slug = w.get('share_slug', '')
        if slug not in FIXES:
            continue
        isbn, asin = FIXES[slug]
        old_isbn = w.get('isbn', '')
        old_asin = w.get('amazon_asin', '')
        w['isbn'] = isbn
        w['amazon_asin'] = asin
        w['cover_image_url'] = '/static/cover-placeholder.svg'
        fixed += 1
        print(f'{slug}: {old_isbn}/{old_asin} -> {isbn}/{asin}')
    save_works(works)
    print(f'\nfixed metadata for {fixed} works')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

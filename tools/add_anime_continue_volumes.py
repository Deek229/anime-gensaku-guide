"""2026年春アニメ作品に anime_continue_volume / anime_continue_note を付与する。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import load_works, save_works

# share_slug -> (volume | None, note)
SPRING_CONTINUE: dict[str, tuple[int | None, str]] = {
    'jojo-sbr': (None, 'Part7（SBR）は全24巻で完結。次のパートは『ジョジョリオン』（Part8）から別作品として読み始めます。'),
    'tensura-4': (20, 'アニメ4期（第17〜19巻相当）の続きはラノベ20巻から。'),
    'akane-banashi': (5, '第1期終了後は漫画5巻から。未読の人は1巻から。'),
    'yomi-no-tsugai': (6, '第1期終了後は漫画6巻から。未読の人は1巻から。'),
    'drstone-sf-3': (None, '漫画は全28巻で完結済み。アニメ最終クール後に原作で読む続きはありません。'),
    'yojitsu-4': (8, '4期（2年生編）終了後はラノベ8巻から。3期まで見た人は4.5巻前後からでも可。'),
    'mairimashita-iruma-4': (33, '第4シリーズ終了後は漫画33巻から。'),
    'shuumatsu-3': (21, '3期終了後は漫画21巻から（全23巻）。'),
    'tongari-boushi': (5, '第1期終了後は漫画5巻から。未読の人は1巻から。'),
    'kanokari-5': (37, '5期終了後は漫画37巻から。'),
    'beastars-final-2': (None, '漫画は全22巻で完結。FINAL Part2で原作完結。'),
    'tsue-to-ken-2': (10, '2期終了後は漫画10巻から。'),
    'liar-game': (6, '第1期終了後は漫画6巻から（全19巻）。未読の人は1巻から。'),
    'dorohedoro-2': (21, '2期終了後は漫画21巻から（全23巻）。'),
    'otonari-tenshi-2': (7, '2期終了後はラノベ7巻から。'),
    'dandadan': (4, 'Netflix第1期終了後は漫画4巻から。未読の人は1巻から。'),
    'diamond-ace-2': (None, '漫画は全47巻で完結済み。アニメ追い込み後の続き巻はありません。'),
    'snowball-earth': (4, '第1期終了後は漫画4巻から。未読の人は1巻から。'),
    'nonbiri-nouka-2': (13, '2期終了後はラノベ13巻から。'),
    'hidari-eri': (4, '第1期終了後は漫画4巻から。未読の人は1巻から。'),
    'jidouhanbaiki-3': (16, '3期終了後はラノベ16巻から。'),
    'last-boss-queen-2': (7, 'Season2終了後はラノベ7巻から。'),
    'saikyo-ou-s2': (7, '2期終了後はラノベ7巻から。'),
    'reincarnation-no-kaben': (4, '第1期終了後は漫画4巻から。未読の人は1巻から。'),
    'kura2': (4, '第1期終了後は漫画4巻から。未読の人は1巻から。'),
    'himekishi-barbaroi': (4, '第1期終了後はラノベ4巻から。未読の人は1巻から。'),
    'mamonogurui': (4, '第1期終了後はラノベ4巻から。未読の人は1巻から。'),
    'kujima-utaeeba': (3, '第1期終了後は漫画3巻から（全2巻＋続編想定）。短編中心のため未読は1巻から。'),
    'aishiteru-game': (4, '第1期終了後は漫画4巻から。未読の人は1巻から。'),
    'replica-koi': (5, '第1期終了後は漫画5巻から。未読の人は1巻から。'),
    'mao-2026': (6, '第1期終了後は漫画6巻から。未読の人は1巻から。'),
    'matatakorosareta': (4, '第1期終了後は漫画4巻から。未読の人は1巻から。'),
    'haibara-kun': (3, '第1期終了後は漫画3巻から。未読の人は1巻から。'),
    'ichijouma-mankitsu': (None, '短編漫画は全2巻で完結。アニメは複数話をオムニバス収録する形式のため、原作は1巻から順に読むのがおすすめ。'),
    'honzuki-oujo': (4, '第1期終了後はスピンオフ漫画4巻から。本編ラノベとは別作品です。未読は1巻から。'),
}


def main() -> int:
    works = load_works()
    updated = 0
    for w in works:
        if w.get('season') != '2026-spring':
            continue
        slug = w.get('share_slug', '')
        if slug not in SPRING_CONTINUE:
            print(f'WARN: missing continue data for {slug}')
            continue
        vol, note = SPRING_CONTINUE[slug]
        w['anime_continue_volume'] = vol
        w['anime_continue_note'] = note
        updated += 1
    save_works(works)
    print(f'updated {updated} spring works')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

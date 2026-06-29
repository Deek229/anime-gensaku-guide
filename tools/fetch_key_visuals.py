"""オリジナルアニメ作品のキービジュアルを Annict / 公式サイトから取得して works.json を更新"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env')

from annict_client import fetch_official_og_image, fetch_work_images
from store import load_works, save_works

sys.stdout.reconfigure(encoding='utf-8')


def is_original(work: dict) -> bool:
    st = (work.get('source_type') or '').strip()
    source_title = (work.get('source_title') or '').strip()
    return st == 'original' or (st in ('', 'other') and not source_title)


def main() -> int:
    works = load_works()
    originals = [w for w in works if is_original(w)]
    print(f'original works: {len(originals)}')
    for w in originals:
        print(f'  - {w.get("title")} ({w.get("id")})')

    updated = 0
    for i, work in enumerate(works):
        if not is_original(work):
            continue
        title = work.get('title', '')
        annict_id = work.get('annict_id')
        key_url, annict_id = fetch_work_images(title, annict_id=annict_id)
        source = 'annict' if key_url else ''

        if not key_url:
            official = (work.get('official_url') or '').strip()
            if official:
                key_url = fetch_official_og_image(official)
                if key_url:
                    source = 'official_og'

        if annict_id and not work.get('annict_id'):
            works[i]['annict_id'] = annict_id
        if key_url:
            works[i]['key_visual_url'] = key_url
            updated += 1
            print(f'[{source:11}] {title} -> {key_url}')
        else:
            works[i].pop('key_visual_url', None)
            print(f'[fallback   ] {title} -> (text badge)')

    save_works(works)
    print(f'\nupdated {updated}/{len(originals)} with key_visual_url')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

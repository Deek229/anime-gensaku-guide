"""Fix ISBN/ASIN metadata in works.json for season-relevant cover volumes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import load_works, save_works

# work id -> (isbn-13, amazon asin / isbn-10)
CORRECTIONS: dict[str, tuple[str, str]] = {
    '無職転生ⅲ-異世界行ったら本気だす': ('9784040684833', '4040684833'),
    '幼女戦記ⅱ': ('9784047309029', '4047309028'),
    're-ゼロから始める異世界生活-4th-season-奪還編': ('9784040640068', '4040640068'),
    'ぐらんぶる-season-3': ('9784065134474', '4065134474'),
    '君のことが大大大大大好きな100人の彼女-第3期': ('9784088921648', '408892164X'),
    '逃げ上手の若君-第二期': ('9784088830735', '4088830733'),
    '骸骨騎士様-只今異世界へお出掛け中ⅱ': ('9784865541465', '4865541465'),
    '乙女ゲー世界はモブに厳しい世界です2': ('9784896379112', '4896379112'),
    '片田舎のおっさん-剣聖になるⅱ': ('9784757580220', '4757580226'),
    '株式会社マジルミエ-第2期': ('9784088835402', '4088835402'),
    '正反対な君と僕-第2期': ('9784088841434', '4088841433'),
    '攻殻機動隊-the-ghost-in-the-shell': ('9784063132489', '4063132489'),
    '天幕のジャードゥーガル': ('9784253264464', '4253264468'),
    'クレバテスⅱ-魔獣の王と偽りの勇者伝承': ('9784866972916', '4866972916'),
}


def main() -> int:
    works = load_works()
    updated = 0
    for work in works:
        fix = CORRECTIONS.get(work.get('id', ''))
        if not fix:
            continue
        isbn, asin = fix
        work['isbn'] = isbn
        work['amazon_asin'] = asin
        updated += 1
    save_works(works)
    print(f'updated metadata for {updated} works')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

"""表紙placeholder作品のISBN/ASINを修正"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import find_work, load_works, save_works

FIXES = {
    'jojo-sbr': ('9784088721624', '4088721624'),
    'tensura-4': ('9784040689845', '4040689845'),
    'shuumatsu-3': ('9784253268762', '4253268762'),
    'beastars-final-2': ('9784199500997', '4199500997'),
    'liar-game': ('9784088771238', '4088771238'),
    'dorohedoro-2': ('9784103001418', '4103001418'),
    'diamond-ace-2': ('9784063945201', '4063945201'),
    'snowball-earth': ('9784065298769', '4065298769'),
    'hanazakari-2': ('9784088478522', '4088478522'),
    'kore-kaite-shine': ('9784103009736', '4103009736'),
    'kujima-utaeeba': ('9784103019124', '4103019124'),
    'ichijouma-mankitsu': ('9784832278920', '4832278920'),
}

works = load_works()
fixed = 0
for w in works:
    slug = w.get('share_slug', '')
    if slug in FIXES:
        isbn, asin = FIXES[slug]
        w['isbn'] = isbn
        w['amazon_asin'] = asin
        w['cover_image_url'] = '/static/cover-placeholder.svg'
        fixed += 1
save_works(works)
print(f'fixed {fixed} works')

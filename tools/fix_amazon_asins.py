"""ISBN-13 から正しい ISBN-10 (Amazon ASIN) を算出して works.json を修正する。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from store import load_works, save_works


def isbn13_to_isbn10(isbn13: str) -> str | None:
    s = ''.join(c for c in isbn13 if c.isdigit())
    if len(s) != 13 or not s.startswith('978'):
        return None
    core = s[3:12]
    total = sum(int(d) * (10 - i) for i, d in enumerate(core))
    rem = (11 - total % 11) % 11
    check = 'X' if rem == 10 else str(rem)
    return core + check


def main() -> int:
    works = load_works()
    fixed = 0
    for w in works:
        isbn = w.get('isbn', '')
        asin = (w.get('amazon_asin') or '').strip()
        if not isbn or not asin:
            continue
        expected = isbn13_to_isbn10(isbn)
        if not expected:
            continue
        if asin.upper() != expected.upper():
            print(f'{w.get("share_slug")}: {asin} -> {expected}')
            w['amazon_asin'] = expected
            fixed += 1
    save_works(works)
    print(f'\nfixed {fixed} amazon_asin values')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

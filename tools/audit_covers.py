"""Audit ISBN/ASIN metadata against OpenBD title data."""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import load_works

sys.stdout.reconfigure(encoding='utf-8')

OPENBD_GET = 'https://api.openbd.jp/v1/get?isbn={isbn}'


def norm(s: str) -> str:
    s = (s or '').lower()
    s = re.sub(r'[\s　・\-‐‑‒–—―_!！?？。、,.「」『』（）()【】\[\]～~:：;；\'\"]', '', s)
    return s


def title_match(expected: str, actual: str) -> bool:
    e, a = norm(expected), norm(actual)
    if not e or not a:
        return False
    if e in a or a in e:
        return True
    # first 4 chars overlap for long titles
    if len(e) >= 4 and e[:4] in a:
        return True
    if len(a) >= 4 and a[:4] in e:
        return True
    return False


def fetch_openbd(isbn: str) -> dict:
    isbn = ''.join(ch for ch in isbn if ch.isdigit())
    if len(isbn) != 13:
        return {}
    try:
        with urllib.request.urlopen(OPENBD_GET.format(isbn=isbn), timeout=12) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return {}
    if not data or not data[0]:
        return {}
    return data[0].get('summary') or {}


def main() -> int:
    works = load_works()
    ok = mismatch = missing = placeholder = 0
    issues: list[str] = []

    for w in works:
        slug = w.get('share_slug', '')
        title = w.get('title', '')
        source = w.get('source_title') or title
        isbn = w.get('isbn', '')
        cover = w.get('cover_image_url', '')

        if cover == '/static/cover-placeholder.svg':
            placeholder += 1
            issues.append(f'PLACEHOLDER\t{slug}\t{title}\t{isbn}')
            continue

        summary = fetch_openbd(isbn)
        time.sleep(0.12)
        if not summary:
            missing += 1
            issues.append(f'NO_OPENBD\t{slug}\t{title}\t{isbn}')
            continue

        obd_title = summary.get('title', '')
        if title_match(source, obd_title):
            ok += 1
        else:
            mismatch += 1
            issues.append(f'MISMATCH\t{slug}\t{source}\t{isbn}\tOpenBD:{obd_title}')

    print(f'total={len(works)} ok={ok} mismatch={mismatch} no_openbd={missing} placeholder={placeholder}')
    print()
    for line in issues:
        print(line)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

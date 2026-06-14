#!/usr/bin/env python3
"""X/LINE用の投稿文を自動生成（週次で実行してコピペ投稿用）"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from anime_service import list_works  # noqa: E402
from config import DEFAULT_SEASON, SITE_URL  # noqa: E402
from seo import build_share_text, twitter_share_url  # noqa: E402


def main() -> None:
    works = list_works(season=DEFAULT_SEASON, has_source_only=True)
    works = sorted(works, key=lambda w: -(w.get('watchers_count') or 0))[:10]

    posts = []
    for work in works:
        page_url = f'{SITE_URL.rstrip("/")}/works/{work["id"]}'
        text = build_share_text(work)
        posts.append({
            'title': work['title'],
            'text': text,
            'url': page_url,
            'twitter_intent': twitter_share_url(text, page_url),
            'hashtags': ' '.join(f'#{t}' for t in (work.get('tags') or [])[:2]),
        })

    out_dir = ROOT / 'data'
    out_dir.mkdir(exist_ok=True)
    out_json = out_dir / 'social_posts.json'
    out_txt = out_dir / 'social_posts.txt'

    payload = {
        'generated_at': date.today().isoformat(),
        'site_url': SITE_URL,
        'posts': posts,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = [f'# 投稿文 {date.today()} ({SITE_URL})', '']
    for i, post in enumerate(posts, 1):
        lines.extend([
            f'## {i}. {post["title"]}',
            post['text'],
            post['url'],
            post.get('hashtags', ''),
            f'→ {post["twitter_intent"]}',
            '',
        ])
    out_txt.write_text('\n'.join(lines), encoding='utf-8')

    print(f'Wrote {out_json}')
    print(f'Wrote {out_txt}')
    print(f'{len(posts)} posts ready')


if __name__ == '__main__':
    main()

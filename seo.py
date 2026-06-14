"""SEO・シェア・フィード用の自動生成"""
from __future__ import annotations

import html
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote, urlencode
from xml.etree.ElementTree import Element, SubElement, tostring

from config import APP_TAGLINE, APP_TITLE, SITE_URL


def absolute_url(path: str = '/') -> str:
    base = SITE_URL.rstrip('/')
    if not path or path == '/':
        return f'{base}/'
    return f'{base}/{path.lstrip("/")}'


def work_page_title(work: dict[str, Any]) -> str:
    title = work.get('title', '')
    if work.get('has_source'):
        st = work.get('source_type_label', '原作')
        return f'{title} 原作は何巻まで？{st}の読む順'
    return f'{title} 原作情報・あらすじ'


def work_meta_description(work: dict[str, Any]) -> str:
    title = work.get('title', '')
    if not work.get('has_source'):
        return f'{title}（{work.get("season_label", "")}）の情報。{APP_TAGLINE}'

    parts = [
        f'{title}の原作は{work.get("source_type_label", "")}「{work.get("source_title", "")}」。',
        work.get('volumes_anime') or '',
        work.get('read_order') or '',
        'Amazonで原作を探すリンク付き。',
    ]
    text = ''.join(p for p in parts if p)
    return text[:155]


def build_intro(work: dict[str, Any]) -> str:
    title = work.get('title', '')
    season = work.get('season_label', '')
    if not work.get('has_source'):
        return f'「{title}」は{season}の作品です。本作はオリジナルアニメのため、原作小説・漫画はありません。'

    source = work.get('source_title') or '不明'
    st = work.get('source_type_label', '')
    chunks = [
        f'「{title}」の原作は{st}「{source}」です。',
        work.get('volumes_anime') or '',
        work.get('read_order') or '',
        'このページでは、アニメ化範囲と原作の読む順・購入リンクをまとめています。',
    ]
    return ' '.join(c for c in chunks if c)


def build_faq(work: dict[str, Any]) -> list[dict[str, str]]:
    title = work.get('title', '')
    if not work.get('has_source'):
        return [
            {
                'question': f'{title}に原作はありますか？',
                'answer': 'オリジナルアニメのため、原作小説・漫画はありません。',
            }
        ]

    faq = [
        {
            'question': f'{title}の原作は何ですか？',
            'answer': f'原作は{work.get("source_type_label", "")}「{work.get("source_title", "")}」です。',
        },
        {
            'question': f'{title}のアニメは原作の何巻・何話まで？',
            'answer': work.get('volumes_anime') or '放送に合わせて更新予定です。',
        },
        {
            'question': f'{title}の原作はどこから読めばいい？',
            'answer': work.get('read_order') or '1巻から順に読むのがおすすめです。',
        },
    ]
    if work.get('source_type') == 'light_novel':
        faq.append({
            'question': f'{title}はラノベと漫画どっちから読む？',
            'answer': '物語の本編はラノベが原作です。漫画版は別ルートのため、未読ならラノベ1巻からがおすすめです。',
        })
    return faq


def build_share_text(work: dict[str, Any]) -> str:
    title = work.get('title', '')
    if work.get('has_source'):
        return f'【{title}】原作は{work.get("source_type_label", "")}「{work.get("source_title", "")}」｜{work.get("volumes_anime", "")[:40]}'
    return f'【{title}】{work.get("season_label", "")}の情報'


def twitter_share_url(text: str, url: str) -> str:
    params = urlencode({'text': text, 'url': url}, quote_via=quote)
    return f'https://twitter.com/intent/tweet?{params}'


def line_share_url(text: str, url: str) -> str:
    params = urlencode({'text': f'{text}\n{url}'}, quote_via=quote)
    return f'https://social-plugins.line.me/lineit/share?{params}'


def faq_json_ld(faq: list[dict[str, str]]) -> dict[str, Any]:
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': item['question'],
                'acceptedAnswer': {
                    '@type': 'Answer',
                    'text': item['answer'],
                },
            }
            for item in faq
        ],
    }


def breadcrumb_json_ld(items: list[tuple[str, str]]) -> dict[str, Any]:
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': idx + 1,
                'name': label,
                'item': absolute_url(path) if path else absolute_url('/'),
            }
            for idx, (label, path) in enumerate(items)
        ],
    }


def render_sitemap(paths: list[tuple[str, str, str]]) -> str:
    """paths: (loc_path, changefreq, priority)"""
    urlset = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    for path, freq, priority in paths:
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = absolute_url(path)
        SubElement(url, 'lastmod').text = today
        SubElement(url, 'changefreq').text = freq
        SubElement(url, 'priority').text = priority
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(urlset, encoding='unicode')


def render_robots() -> str:
    return '\n'.join([
        'User-agent: *',
        'Allow: /',
        f'Sitemap: {absolute_url("/sitemap.xml")}',
        '',
    ])


def render_rss(items: list[dict[str, Any]], channel_title: str) -> str:
    now = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        '<channel>',
        f'<title>{html.escape(channel_title)}</title>',
        f'<link>{html.escape(absolute_url("/"))}</link>',
        f'<description>{html.escape(APP_TAGLINE)}</description>',
        f'<lastBuildDate>{now}</lastBuildDate>',
        f'<atom:link href="{html.escape(absolute_url("/feed.xml"))}" rel="self" type="application/rss+xml"/>',
    ]
    for item in items:
        link = absolute_url(item['path'])
        lines.extend([
            '<item>',
            f'<title>{html.escape(item["title"])}</title>',
            f'<link>{html.escape(link)}</link>',
            f'<guid isPermaLink="true">{html.escape(link)}</guid>',
            f'<description>{html.escape(item["description"])}</description>',
            '</item>',
        ])
    lines.extend(['</channel>', '</rss>'])
    return '\n'.join(lines)

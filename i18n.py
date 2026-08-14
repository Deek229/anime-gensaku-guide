"""サイト言語（ja / en）。URL は /en プレフィックス、切替は cookie。"""
from __future__ import annotations

import re

from starlette.requests import Request
from starlette.responses import RedirectResponse

COOKIE = 'site_lang'
BOT_RE = re.compile(
    r'bot|crawl|spider|slurp|bingpreview|facebookexternalhit|embedly|discordbot|whatsapp',
    re.I,
)
SKIP_REDIRECT_PREFIXES = (
    '/static', '/api', '/sitemap', '/robots', '/feed', '/set-lang', '/docs', '/openapi',
)

SEASON = {
    'ja': {
        '2026-summer': '2026年夏アニメ',
        '2026-spring': '2026年春アニメ',
        '2026-autumn': '2026年秋アニメ',
        '2026-winter': '2026年冬アニメ',
        'ln-picks': 'おすすめラノベ',
    },
    'en': {
        '2026-summer': 'Summer 2026 anime',
        '2026-spring': 'Spring 2026 anime',
        '2026-autumn': 'Autumn 2026 anime',
        '2026-winter': 'Winter 2026 anime',
        'ln-picks': 'Recommended light novels',
    },
}

SOURCE_TYPE = {
    'ja': {
        'light_novel': 'ラノベ',
        'manga': '漫画',
        'web_novel': 'Web小説',
        'novel': '小説',
        'game': 'ゲーム',
        'original': 'オリジナル',
        'other': 'その他',
    },
    'en': {
        'light_novel': 'Light novel',
        'manga': 'Manga',
        'web_novel': 'Web novel',
        'novel': 'Novel',
        'game': 'Game',
        'original': 'Original',
        'other': 'Other',
    },
}

STATUS = {
    'ja': {
        'upcoming': '放送予定',
        'airing': '放送開始',
        'finished': '放送終了',
        'ln_only': 'ラノベ',
    },
    'en': {
        'upcoming': 'Upcoming',
        'airing': 'Airing',
        'finished': 'Finished',
        'ln_only': 'Light novel',
    },
}

MATOME = {
    'ja': {
        '2026-spring': {
            'title': '2026年春アニメ 原作おすすめ10選',
            'lead': '2026年4月放送の春アニメから、原作を読む価値が高い作品を10本厳選。ラノベ・漫画の読み始め巻と、アニメ化範囲の目安をまとめました。',
        },
        '2026-summer': {
            'title': '2026年夏アニメ 原作おすすめ10選',
            'lead': '2026年7月放送の夏アニメから、原作チェックにおすすめの人気作10選。続編ものの「何巻から読むか」もひと目でわかります。',
        },
        '2026-autumn': {
            'title': '2026年秋アニメ 原作おすすめ10選',
            'lead': '2026年10月放送の秋アニメから、原作ファン・これから読み始める人向けのおすすめ10作品をピックアップしました。',
        },
        '2026-winter': {
            'title': '2026年冬アニメ 原作おすすめ10選',
            'lead': '2027年1月放送の冬アニメ（2026年冬クール）から、原作を押さえておきたい注目作10選を紹介します。',
        },
    },
    'en': {
        '2026-spring': {
            'title': 'Spring 2026 anime: 10 source-material picks',
            'lead': 'Ten Spring 2026 shows worth reading in the original. Start volumes and the anime adaptation range at a glance.',
        },
        '2026-summer': {
            'title': 'Summer 2026 anime: 10 source-material picks',
            'lead': 'Ten Summer 2026 shows to check in print or web novels — including where sequels pick up.',
        },
        '2026-autumn': {
            'title': 'Autumn 2026 anime: 10 source-material picks',
            'lead': 'Ten Autumn 2026 titles for readers who want the original novels or manga.',
        },
        '2026-winter': {
            'title': 'Winter 2026 anime: 10 source-material picks',
            'lead': 'Ten Winter 2026 (early 2027) shows to read ahead of or alongside the broadcast.',
        },
    },
}

UI = {
    'ja': {
        'app_title': 'アニメ原作ガイド',
        'hero_kicker': '表紙を眺めて、気になった一冊から開く',
        'tagline': '今期アニメの原作ラノベ・漫画をチェックして、買う順まで一発でわかる',
        'nav_current': '今期アニメ',
        'nav_matome': 'まとめ',
        'nav_rankings': 'なろうR',
        'disclosure': '※ Amazonリンクはアフィリエイトを使用する場合があります。データの一部はAnnict・なろうAPIを利用しています。',
        'access_count': '総アクセス数',
        'sitemap': 'サイトマップ',
        'season': 'シーズン',
        'source_type_ui': '原作タイプ',
        'all': 'すべて',
        'has_source_only': '原作ありのみ',
        'search': '検索',
        'search_ph': '作品名・原作名で検索…',
        'works_count': '{n}作品',
        'works_shown': '{n}作品表示',
        'empty': '条件に一致する作品がありません。',
        'detail': '詳細',
        'source_prefix': '原作:',
        'aff_aria': 'Amazonおすすめ',
        'aff_title': '今期のおすすめ原作',
        'aff_note': 'この端末で見た作品を優先して出します（Amazonアフィリエイト）',
        'aff_recent': '最近見た原作',
        'menu_aria': 'ガイドメニュー',
        'matome_heading': 'シーズンまとめ',
        'popular_heading': '人気の原作ガイド',
        'ln_heading': 'おすすめラノベ',
        'amazon_view': 'Amazonで見る',
        'amazon_search': 'Amazonで検索',
        'original_aria': 'アニメオリジナル作品',
        'original_l1': 'アニメ',
        'original_l2': 'オリジナル',
        'original_l3': '作品',
        'home_title': '{season} 原作ガイド｜{app}',
        'home_desc': '{season}の原作ラノベ・漫画一覧。アニメ化範囲・読む順・Amazon購入リンク付き。',
        'home_og': '{season} 原作ガイド',
        'share_x': 'Xでシェア',
        'list': '一覧',
        'home': 'ホーム',
        'matome_crumb': 'まとめ',
        'work_h1': '{title}の原作は？',
        'work_h1_ln': '{title} ラノベガイド',
        'ln_season_line': 'おすすめラノベ（アニメ化未定）',
        'main_comment': '主コメント',
        'continue_h': 'アニメの続きは何巻から？',
        'info_h': '原作情報',
        'info_h_ln': '作品情報',
        'th_source': '原作',
        'th_type': 'タイプ',
        'th_range': 'アニメ化範囲',
        'th_pub': '刊行状況',
        'th_order': '読む順・買い方',
        'no_anime_yet': 'アニメ化未定',
        'approx': '※放送進行で更新',
        'later': '後日更新',
        'no_source': 'オリジナルアニメ、または原作情報は未登録です。',
        'faq': 'よくある質問',
        'memo': 'メモ',
        'links': 'リンク',
        'official': '公式サイト',
        'post_on_x': 'Xで投稿',
        'copy_text': '文面をコピー',
        'copied': 'コピーしました',
        'copy_prompt': '以下をコピーしてください',
        'share_hint': '📷 画像付き投稿: 上の表紙を右クリック→「画像を保存」して、X投稿時に添付してください。',
        'share_preview': '投稿文プレビュー',
        'share_url': 'シェアURL',
        'affiliate_note': '※ 購入リンクはAmazonアソシエイトを使用する場合があります。',
        'related': '関連作品',
        'updated': '最終更新',
        'jp_body_note': '',
        'matome_other_seasons': 'ほかのシーズンまとめ',
        'detail_guide': '詳細ガイド',
        'rankings_title': 'なろうランキング',
        'rankings_lead': '公式APIのランキング閲覧（サブ機能）。書籍化・アニメ化候補の探索用。',
        'rank_d': '日間',
        'rank_w': '週間',
        'rank_m': '月間',
        'rank_q': '四半期',
        'rank_loading': '読み込み中...',
        'rank_th_rank': '順位',
        'rank_th_title': '作品',
        'rank_th_writer': '作者',
        'rank_th_status': '状態',
        'rank_th_pt': 'Pt',
        'rank_error': 'エラー',
        'lang_ja': '日本語',
        'lang_en': 'English',
    },
    'en': {
        'app_title': 'Anime Source Guide',
        'hero_kicker': 'Browse the covers. Open the one that pulls you in.',
        'tagline': 'See the original novels and manga for this season’s anime — and what to buy next.',
        'nav_current': 'This season',
        'nav_matome': 'Picks',
        'nav_rankings': 'Narou',
        'disclosure': 'Amazon links may be affiliate links. Some data comes from Annict and the Shosetsuka ni Naro API.',
        'access_count': 'Total visits',
        'sitemap': 'Sitemap',
        'season': 'Season',
        'source_type_ui': 'Source type',
        'all': 'All',
        'has_source_only': 'With source only',
        'search': 'Search',
        'search_ph': 'Search title or source…',
        'works_count': '{n} titles',
        'works_shown': '{n} titles shown',
        'empty': 'No titles match these filters.',
        'detail': 'Details',
        'source_prefix': 'Source:',
        'aff_aria': 'Amazon picks',
        'aff_title': 'Source books this season',
        'aff_note': 'Titles you viewed on this device are listed first (Amazon affiliate).',
        'aff_recent': 'Recently viewed',
        'menu_aria': 'Guide menu',
        'matome_heading': 'Season picks',
        'popular_heading': 'Popular guides',
        'ln_heading': 'Light novels',
        'amazon_view': 'View on Amazon',
        'amazon_search': 'Search Amazon',
        'original_aria': 'Anime-original title',
        'original_l1': 'Anime',
        'original_l2': 'original',
        'original_l3': 'title',
        'home_title': '{season} source guide | {app}',
        'home_desc': 'Original light novels and manga for {season}. Adaptation range, reading order, and Amazon links.',
        'home_og': '{season} source guide',
        'share_x': 'Share on X',
        'list': 'List',
        'home': 'Home',
        'matome_crumb': 'Picks',
        'work_h1': 'What is the source for {title}?',
        'work_h1_ln': '{title} light novel guide',
        'ln_season_line': 'Recommended light novel (not yet adapted)',
        'main_comment': 'Editor note',
        'continue_h': 'Which volume continues after the anime?',
        'info_h': 'Source info',
        'info_h_ln': 'Title info',
        'th_source': 'Source',
        'th_type': 'Type',
        'th_range': 'Anime range',
        'th_pub': 'Publication',
        'th_order': 'Reading order',
        'no_anime_yet': 'Not yet adapted',
        'approx': 'Updated as the show airs',
        'later': 'To be updated',
        'no_source': 'This is an original anime, or source details are not listed yet.',
        'faq': 'FAQ',
        'memo': 'Notes',
        'links': 'Links',
        'official': 'Official site',
        'post_on_x': 'Post on X',
        'copy_text': 'Copy text',
        'copied': 'Copied',
        'copy_prompt': 'Copy the text below',
        'share_hint': 'For an image post: save the cover (right-click → Save image), then attach it on X.',
        'share_preview': 'Post preview',
        'share_url': 'Share URL',
        'affiliate_note': 'Purchase links may use Amazon Associates.',
        'related': 'Related titles',
        'updated': 'Updated',
        'jp_body_note': 'Volume notes and comments below are in Japanese.',
        'matome_other_seasons': 'Other season picks',
        'detail_guide': 'Full guide',
        'rankings_title': 'Narou rankings',
        'rankings_lead': 'Official API rankings (side feature) for spotting print and anime candidates.',
        'rank_d': 'Daily',
        'rank_w': 'Weekly',
        'rank_m': 'Monthly',
        'rank_q': 'Quarterly',
        'rank_loading': 'Loading…',
        'rank_th_rank': 'Rank',
        'rank_th_title': 'Title',
        'rank_th_writer': 'Author',
        'rank_th_status': 'Status',
        'rank_th_pt': 'Pts',
        'rank_error': 'Error',
        'lang_ja': '日本語',
        'lang_en': 'English',
    },
}


def is_bot(ua: str | None) -> bool:
    return bool(ua and BOT_RE.search(ua))


def parse_accept_language(header: str | None) -> str:
    if not header:
        return 'ja'
    best = 'ja'
    best_q = -1.0
    for part in header.split(','):
        token = part.strip()
        if not token:
            continue
        lang, _, rest = token.partition(';')
        lang = lang.strip().lower()
        q = 1.0
        if 'q=' in rest.lower():
            try:
                q = float(rest.lower().split('q=')[1].split(';')[0])
            except ValueError:
                q = 0.0
        code = 'ja' if lang.startswith('ja') else 'en'
        if q > best_q:
            best_q = q
            best = code
        elif q == best_q and code == 'ja':
            best = 'ja'
    return best


def cookie_lang(request: Request) -> str | None:
    raw = request.cookies.get(COOKIE, '').strip().lower()
    if raw in ('ja', 'en'):
        return raw
    return None


def localized_path(path: str, lang: str) -> str:
    path = path or '/'
    if not path.startswith('/'):
        path = '/' + path
    if lang == 'en':
        return '/en' if path == '/' else '/en' + path
    return path


def ja_path(path: str) -> str:
    if path == '/en':
        return '/'
    if path.startswith('/en/'):
        return path[3:]
    return path


def should_skip_lang_redirect(path: str) -> bool:
    if path.startswith('/static'):
        return True
    return any(
        path == p or path.startswith(p + '/') or path.startswith(p + '.')
        for p in SKIP_REDIRECT_PREFIXES
    )


def strings(lang: str) -> dict:
    code = 'en' if lang == 'en' else 'ja'
    return {
        **UI[code],
        'season_labels': SEASON[code],
        'source_labels': SOURCE_TYPE[code],
        'status_labels': STATUS[code],
        'matome': MATOME[code],
    }


def buy_label(work: dict, lang: str) -> str:
    t = strings(lang)
    if (work.get('amazon_asin') or '').strip():
        return t['amazon_view']
    return t['amazon_search']


def i18n_context(request: Request, ja_path_value: str) -> dict:
    from urllib.parse import quote

    from seo import absolute_url

    lang = getattr(request.state, 'lang', 'ja') or 'ja'
    t = strings(lang)
    jp = ja_path(ja_path_value)
    if not jp.startswith('/'):
        jp = '/' + jp
    prefix = '/en' if lang == 'en' else ''
    nxt = quote(jp, safe='/')
    return {
        'lang': lang,
        't': t,
        'html_lang': 'en' if lang == 'en' else 'ja',
        'og_locale': 'en_US' if lang == 'en' else 'ja_JP',
        'lang_prefix': prefix,
        'ja_url': absolute_url(jp),
        'en_url': absolute_url(localized_path(jp, 'en')),
        'switch_en': f'/set-lang/en?next={nxt}',
        'switch_ja': f'/set-lang/ja?next={nxt}',
        'app_title': t['app_title'],
        'tagline': t['tagline'],
    }


def locale_redirect(request: Request) -> RedirectResponse | None:
    path = request.url.path
    if should_skip_lang_redirect(path) or request.method not in ('GET', 'HEAD'):
        return None
    if is_bot(request.headers.get('user-agent')):
        return None
    cookie = cookie_lang(request)
    has_en = path == '/en' or path.startswith('/en/')
    q = request.url.query
    suffix = f'?{q}' if q else ''
    if cookie == 'ja' and has_en:
        return RedirectResponse(ja_path(path) + suffix, status_code=302)
    if cookie == 'en' and not has_en:
        return RedirectResponse(localized_path(path, 'en') + suffix, status_code=302)
    if cookie is None and not has_en and parse_accept_language(request.headers.get('accept-language')) == 'en':
        return RedirectResponse(localized_path(path, 'en') + suffix, status_code=302)
    return None

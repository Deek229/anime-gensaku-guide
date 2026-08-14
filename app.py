"""
アニメ原作ガイド

起動:
  cd 11_名称未定Web作り
  python tools/seed_works.py          # data/works.json が空のときのみ
  python -m uvicorn app:app --reload --port 8052
"""
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from anime_service import affiliate_picks, get_work, list_meta, list_works, popular_works, related_works
from guide_service import get_matome, list_matome_pages
from config import (
    APP_TITLE,
    APP_VERSION,
    DEFAULT_SEASON,
    GOOGLE_SITE_VERIFICATION,
    SEASON_LABELS,
    SITE_URL,
)
from i18n import (
    COOKIE as LANG_COOKIE,
    cookie_lang,
    i18n_context,
    is_bot,
    ja_path,
    locale_redirect,
    localized_path,
    parse_accept_language,
    strings,
)
from ranking_service import get_ranking, list_meta as rank_meta
from seo import absolute_url, breadcrumb_json_ld, faq_json_ld, render_robots, render_rss, render_sitemap
from site_stats import increment, should_count_page_view
from templates_env import render as render_template

load_dotenv(Path(__file__).parent / '.env')

app = FastAPI(title=APP_TITLE, version=APP_VERSION)
ROOT = Path(__file__).parent
STATIC = ROOT / 'static'


class AccessCountMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if should_count_page_view(
            request.method,
            request.url.path,
            request.headers.get('user-agent'),
        ):
            increment()
        return await call_next(request)


class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        redir = locale_redirect(request)
        if redir:
            return redir
        path = request.url.path
        if path == '/en' or path.startswith('/en/'):
            request.state.lang = 'en'
            new_path = ja_path(path)
            request.scope['path'] = new_path
            request.scope['raw_path'] = new_path.encode('ascii', 'ignore') or b'/'
        else:
            if is_bot(request.headers.get('user-agent')):
                request.state.lang = 'ja'
            else:
                request.state.lang = cookie_lang(request) or parse_accept_language(
                    request.headers.get('accept-language')
                )
        return await call_next(request)


app.add_middleware(AccessCountMiddleware)
app.add_middleware(LocaleMiddleware)
app.mount('/static', StaticFiles(directory=STATIC), name='static')


def _season_label(season: str, lang: str = 'ja') -> str:
    return strings(lang)['season_labels'].get(season, SEASON_LABELS.get(season, season))


def _home_og_image(season: str) -> str | None:
    for work in popular_works(season=season):
        if work.get('og_image_url'):
            return work['og_image_url']
    return None


def html_page(request: Request, template: str, page_path: str, **ctx) -> HTMLResponse:
    i18n = i18n_context(request, page_path)
    canonical = absolute_url(localized_path(page_path, i18n['lang']))
    merged = {
        **i18n,
        'google_site_verification': GOOGLE_SITE_VERIFICATION,
        'site_url': SITE_URL,
        **ctx,
        'canonical_url': canonical,
        'og_url': canonical,
    }
    return HTMLResponse(render_template(template, **merged))


@app.get('/set-lang/{lang}')
def set_lang(lang: str, next: str = '/'):
    chosen = 'en' if lang == 'en' else 'ja'
    nxt = next if next.startswith('/') and not next.startswith('//') else '/'
    nxt = ja_path(nxt)
    dest = localized_path(nxt, chosen)
    resp = RedirectResponse(dest, status_code=303)
    resp.set_cookie(LANG_COOKIE, chosen, max_age=60 * 60 * 24 * 365, path='/', samesite='lax')
    return resp


@app.get('/', response_class=HTMLResponse)
def home(request: Request, season: str | None = None):
    lang = getattr(request.state, 'lang', 'ja')
    season = season or DEFAULT_SEASON
    return html_page(
        request,
        'index.html',
        '/',
        season=season,
        season_label_name=_season_label(season, lang),
        works=list_works(season=season),
        popular_works=popular_works(season=season),
        affiliate_picks=affiliate_picks(season=season),
        ln_pick_works=list_works(season='ln-picks'),
        meta=list_meta(),
        matome_pages=list_matome_pages(),
        og_image=_home_og_image(season),
        og_type='website',
    )


@app.head('/', include_in_schema=False)
def home_head():
    return Response(status_code=200)


@app.get('/works/{work_id}', response_class=HTMLResponse)
def work_page(request: Request, work_id: str):
    work = get_work(work_id)
    if not work:
        raise HTTPException(404, '作品が見つかりません')
    lang = getattr(request.state, 'lang', 'ja')
    t = strings(lang)
    if lang == 'en':
        page_title = f'{work["title"]} | {t["app_title"]}'
        description = f'{work["title"]} — source material, reading order, and Amazon links.'
    else:
        page_title = f'{work["seo_title"]}｜{APP_TITLE}'
        description = work['seo_description']
    return html_page(
        request,
        'work.html',
        f'/works/{work_id}',
        work=work,
        related_works=related_works(work_id),
        page_title=page_title,
        description=description,
        faq_json=faq_json_ld(work['faq']),
        breadcrumb_json=breadcrumb_json_ld([
            (t['home'], '/'),
            (t['season_labels'].get(work.get('season'), work.get('season_label', '')), '/'),
            (work['title'], work['page_path']),
        ]),
        og_image=work.get('og_image_url'),
        og_type='article',
    )


@app.get('/matome/{slug}', response_class=HTMLResponse)
def matome_page(request: Request, slug: str):
    page = get_matome(slug)
    if not page:
        raise HTTPException(404, 'まとめページが見つかりません')
    t = strings(getattr(request.state, 'lang', 'ja'))
    loc = t['matome'].get(slug)
    if loc:
        page = {**page, 'title': loc['title'], 'lead': loc['lead'], 'seo_description': loc['lead'][:155]}
    page = {**page, 'season_label': t['season_labels'].get(page['season'], page['season_label'])}
    other_matome = [m for m in list_matome_pages() if m['slug'] != slug]
    return html_page(
        request,
        'matome.html',
        page['path'],
        page=page,
        other_matome=other_matome,
        og_image=_home_og_image(page['season']),
        og_type='article',
    )


@app.get('/rankings', response_class=HTMLResponse)
def rankings_page(request: Request):
    return html_page(
        request,
        'rankings.html',
        '/rankings',
        og_image=_home_og_image(DEFAULT_SEASON),
        og_type='website',
    )


def _build_sitemap_xml() -> str:
    paths: list[tuple[str, str, str]] = [
        ('/', 'daily', '1.0'),
        ('/rankings', 'weekly', '0.6'),
        ('/en', 'daily', '0.9'),
        ('/en/rankings', 'weekly', '0.5'),
    ]
    for matome in list_matome_pages():
        paths.append((matome['path'], 'weekly', '0.7'))
        paths.append((f'/en{matome["path"]}', 'weekly', '0.6'))
    for work in list_works():
        paths.append((f'/works/{work["id"]}', 'weekly', '0.8'))
    return render_sitemap(paths)


@app.get('/sitemap.xml')
def sitemap():
    return Response(content=_build_sitemap_xml(), media_type='application/xml')


@app.head('/sitemap.xml', include_in_schema=False)
def sitemap_head():
    return Response(content=_build_sitemap_xml(), media_type='application/xml')


@app.get('/robots.txt', response_class=PlainTextResponse)
def robots():
    return PlainTextResponse(render_robots(), media_type='text/plain')


@app.head('/robots.txt', include_in_schema=False)
def robots_head():
    return PlainTextResponse(render_robots(), media_type='text/plain')


@app.get('/feed.xml')
def feed():
    season = DEFAULT_SEASON
    items = [
        {
            'path': f'/works/{w["id"]}',
            'title': w['seo_title'],
            'description': w['seo_description'],
        }
        for w in list_works(season=season, has_source_only=True)[:20]
    ]
    xml = render_rss(items, f'{APP_TITLE} - {_season_label(season)}')
    return Response(content=xml, media_type='application/rss+xml')


@app.get('/api/works')
def api_works(
    season: str | None = None,
    source_type: str | None = None,
    status: str | None = None,
    q: str | None = None,
    has_source: bool = False,
):
    return {
        'items': list_works(
            season=season or DEFAULT_SEASON,
            source_type=source_type or None,
            status=status or None,
            q=q,
            has_source_only=has_source,
        )
    }


@app.get('/api/works/{work_id}')
def api_work(work_id: str):
    work = get_work(work_id)
    if not work:
        raise HTTPException(404)
    return work


@app.get('/api/meta')
def api_meta():
    return list_meta()


@app.get('/api/rankings')
def api_rankings(
    period: str = Query('d', pattern='^(d|w|m|q)$'),
    target: str | None = None,
):
    target_date = date.today()
    if target:
        try:
            target_date = date.fromisoformat(target)
        except ValueError as e:
            raise HTTPException(400, 'target は YYYY-MM-DD') from e
    try:
        return get_ranking(period, target_date)
    except Exception as e:
        from ranking_service import _load_fallback
        fallback = _load_fallback(period)
        if fallback:
            return fallback
        return {
            'period': period,
            'period_label': {'d': '日間', 'w': '週間', 'm': '月間', 'q': '四半期'}.get(period, period),
            'count': 0,
            'items': [],
            'error': f'なろうAPI: {e}',
        }


@app.get('/api/rankings/meta')
def api_rankings_meta():
    return rank_meta()


@app.get('/api/health')
def health():
    return {'status': 'ok', 'app': APP_TITLE, 'version': APP_VERSION}


@app.head('/api/health', include_in_schema=False)
def health_head():
    return Response(status_code=200)

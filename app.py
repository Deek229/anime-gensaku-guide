"""
アニメ原作ガイド

起動:
  cd 11_名称未定Web作り
  python tools/seed_works.py          # 初回のみ
  python -m uvicorn app:app --reload --port 8052
"""
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

from anime_service import get_work, list_meta, list_works, popular_works, related_works
from config import (
    APP_TAGLINE,
    APP_TITLE,
    APP_VERSION,
    DEFAULT_SEASON,
    GOOGLE_SITE_VERIFICATION,
    SEASON_LABELS,
    SITE_URL,
)
from ranking_service import get_ranking, list_meta as rank_meta
from seo import absolute_url, breadcrumb_json_ld, faq_json_ld, render_robots, render_rss, render_sitemap
from templates_env import render as render_template

load_dotenv(Path(__file__).parent / '.env')

app = FastAPI(title=APP_TITLE, version=APP_VERSION)
ROOT = Path(__file__).parent
STATIC = ROOT / 'static'
app.mount('/static', StaticFiles(directory=STATIC), name='static')


def _season_label(season: str) -> str:
    return next(
        (s['label'] for s in list_meta()['seasons'] if s['id'] == season),
        SEASON_LABELS.get(season, season),
    )


@app.get('/', response_class=HTMLResponse)
def home(season: str | None = None):
    season = season or DEFAULT_SEASON
    works = list_works(season=season)
    meta = list_meta()
    season_label_name = _season_label(season)
    return HTMLResponse(render_template(
        'index.html',
        app_title=APP_TITLE,
        tagline=APP_TAGLINE,
        season=season,
        season_label_name=season_label_name,
        works=works,
        popular_works=popular_works(season=season),
        meta=meta,
        site_url=SITE_URL,
        canonical_url=absolute_url('/'),
        og_type='website',
        google_site_verification=GOOGLE_SITE_VERIFICATION,
    ))


@app.head('/', include_in_schema=False)
def home_head():
    return Response(status_code=200)


@app.get('/works/{work_id}', response_class=HTMLResponse)
def work_page(work_id: str):
    work = get_work(work_id)
    if not work:
        raise HTTPException(404, '作品が見つかりません')
    return HTMLResponse(render_template(
        'work.html',
        work=work,
        related_works=related_works(work_id),
        page_title=f'{work["seo_title"]}｜{APP_TITLE}',
        description=work['seo_description'],
        faq_json=faq_json_ld(work['faq']),
        breadcrumb_json=breadcrumb_json_ld([
            ('ホーム', '/'),
            (work['season_label'], '/'),
            (work['title'], work['page_path']),
        ]),
        site_url=SITE_URL,
        app_title=APP_TITLE,
        canonical_url=work['page_url'],
        og_type='article',
        google_site_verification=GOOGLE_SITE_VERIFICATION,
    ))


@app.get('/rankings', response_class=HTMLResponse)
def rankings_page():
    return HTMLResponse(render_template(
        'rankings.html',
        app_title=APP_TITLE,
        tagline='なろうランキング（サブ）',
        site_url=SITE_URL,
        canonical_url=absolute_url('/rankings'),
        og_type='website',
        google_site_verification=GOOGLE_SITE_VERIFICATION,
    ))


def _build_sitemap_xml() -> str:
    paths: list[tuple[str, str, str]] = [
        ('/', 'daily', '1.0'),
        ('/rankings', 'weekly', '0.6'),
    ]
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
        raise HTTPException(502, f'なろうAPI: {e}') from e


@app.get('/api/rankings/meta')
def api_rankings_meta():
    return rank_meta()


@app.get('/api/health')
def health():
    return {'status': 'ok', 'app': APP_TITLE, 'version': APP_VERSION}


@app.head('/api/health', include_in_schema=False)
def health_head():
    return Response(status_code=200)

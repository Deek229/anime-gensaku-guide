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
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from anime_service import get_work, list_meta, list_works
from config import APP_TAGLINE, APP_TITLE, APP_VERSION, DEFAULT_SEASON, SITE_URL
from ranking_service import get_ranking, list_meta as rank_meta
from templates_env import render as render_template

load_dotenv(Path(__file__).parent / '.env')

app = FastAPI(title=APP_TITLE, version=APP_VERSION)
ROOT = Path(__file__).parent
STATIC = ROOT / 'static'
app.mount('/static', StaticFiles(directory=STATIC), name='static')


@app.get('/', response_class=HTMLResponse)
def home(season: str | None = None):
    season = season or DEFAULT_SEASON
    works = list_works(season=season)
    meta = list_meta()
    season_label_name = next(
        (s['label'] for s in meta['seasons'] if s['id'] == season),
        season,
    )
    return HTMLResponse(render_template(
        'index.html',
        app_title=APP_TITLE,
        tagline=APP_TAGLINE,
        season=season,
        season_label_name=season_label_name,
        works=works,
        meta=meta,
        site_url=SITE_URL,
    ))


@app.get('/works/{work_id}', response_class=HTMLResponse)
def work_page(work_id: str):
    work = get_work(work_id)
    if not work:
        raise HTTPException(404, '作品が見つかりません')
    page_title = f'{work["title"]}の原作は？｜{APP_TITLE}'
    description = (
        f'{work["title"]}の原作は{work.get("source_type_label", "不明")}。'
        f'{work.get("volumes_anime", "")[:80]}'
    )
    return HTMLResponse(render_template(
        'work.html',
        work=work,
        page_title=page_title,
        description=description[:120],
        site_url=SITE_URL,
        app_title=APP_TITLE,
    ))


@app.get('/rankings', response_class=HTMLResponse)
def rankings_page():
    return HTMLResponse(render_template(
        'rankings.html',
        app_title=APP_TITLE,
        tagline='なろうランキング（サブ）',
    ))


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

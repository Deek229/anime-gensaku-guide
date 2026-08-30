#!/usr/bin/env python3
"""アニメ原作ガイド — 日本語タスク管理メールを送信（Brevo）"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import traceback
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / '.env')

from anime_service import list_works  # noqa: E402
from config import DEFAULT_SEASON, SEASON_LABELS  # noqa: E402
from seo import build_x_share_text, twitter_share_url  # noqa: E402

SITE_URL_RAW = os.environ.get('SITE_URL', 'https://anime-gensaku-guide.onrender.com').rstrip('/')
SITE_URL = (
    SITE_URL_RAW
    if SITE_URL_RAW.startswith('http')
    and '127.0.0.1' not in SITE_URL_RAW
    and 'localhost' not in SITE_URL_RAW
    else 'https://anime-gensaku-guide.onrender.com'
)
TO = os.environ.get('REMINDER_EMAIL_TO', 'a_n_k_6@hotmail.com').strip() or 'a_n_k_6@hotmail.com'
LAUNCH_DATE = date.fromisoformat(os.environ.get('SITE_LAUNCH_DATE', '2026-06-14'))

WEEKDAYS_JA = '月火水木金土日'

CHECKLIST_CSV = ROOT / 'docs' / 'インデックス登録チェックリスト.csv'
CHECKLIST_SHEET_URL = os.environ.get('CHECKLIST_SHEET_URL', '').strip()
DEFAULT_STATE_PATH = ROOT / 'tools' / '.gsc_reminder_state.json'
SHEET_FETCH_TIMEOUT = 10

# 曜日ごとのX投稿アングル（リアルタイム話題APIは使わず、今期人気作品をローテ）
_X_ANGLES = (
    ('今期人気枠', 'ウォッチ数上位。放送直後〜週末に反応が出やすい定番投稿'),
    ('原作なに巻から枠', '「何巻から読めばいい？」検索向け。表紙画像必須で反応率アップ'),
    ('続きが気になる枠', 'アニメ追ってる人向け。引用RTで「まだの人はここから」も有効'),
    ('中堅穴場枠', '上位以外も回すとサイト全体の回遊が伸びやすい'),
    ('まとめ誘導枠', '個別作品＋シーズンまとめページをセットで貼ると強い'),
    ('週末まとめ枠', '今週見た中で一番気になった1本を推す'),
    ('来週に向けて枠', '放送前に「原作ここまで」を先出ししておくと指名検索が増えやすい'),
)


@dataclass
class Task:
    title: str
    steps: list[str]
    minutes: int
    optional: bool = False


def _weekday_label(d: date) -> str:
    return WEEKDAYS_JA[d.weekday()]


def _days_since_launch(d: date) -> int:
    return (d - LAUNCH_DATE).days


def _phase_label(days: int) -> str:
    if days < 7:
        return 'フェーズ1: Googleにサイトを登録させる（公開〜1週間）'
    if days < 30:
        return 'フェーズ2: 検索に載るのを待つ＋少しずつ宣伝（2〜4週間）'
    return 'フェーズ3: 運用・改善（1ヶ月以降）'

def _is_ascii(s: str) -> bool:
    try:
        s.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def _priority_key(label: str) -> tuple[int, str]:
    # lower is higher priority
    label = (label or '').strip()
    order = {
        '★★★': 0,
        '★★☆': 1,
        '★☆☆': 2,
    }
    return (order.get(label, 9), label)


def _load_state(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            return data
    except FileNotFoundError:
        return {}
    except Exception:
        return {}
    return {}


def _save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def _iter_checklist_rows(csv_path: Path) -> Iterable[dict[str, str]]:
    with csv_path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            yield {k: (v or '').strip() for k, v in row.items() if k is not None}


def _fetch_sheet_csv(url: str, *, timeout: int = SHEET_FETCH_TIMEOUT) -> str:
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'AnimeGensakuGuide-Reminder/1.0'},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    text = raw.decode('utf-8-sig')
    stripped = text.lstrip()
    if stripped.startswith('<!DOCTYPE') or stripped.startswith('<html'):
        raise ValueError('スプレッドシートが非公開の可能性があります（HTMLが返されました）')
    lines = text.splitlines()
    if not lines or '優先度' not in lines[0]:
        raise ValueError('CSVの1行目に「優先度」列がありません')
    return text


def _count_checklist_rows(csv_path: Path) -> int:
    return sum(1 for _ in _iter_checklist_rows(csv_path))


def _count_rows_in_csv_text(text: str) -> int:
    lines = [line for line in text.splitlines() if line.strip()]
    return max(0, len(lines) - 1)


def ensure_checklist_csv(
    local_path: Path,
    *,
    sheet_url: str | None = None,
    mirror: bool = True,
) -> Path:
    """
    スプレッドシートURLが設定されていれば取得してローカルにミラー。
    失敗時はローカルCSVにフォールバックする。
    スプレッドシートの行数がローカルより少ない場合は上書きしない（安全策）。
    """
    url = (sheet_url if sheet_url is not None else CHECKLIST_SHEET_URL).strip()
    if not url:
        if not local_path.exists():
            raise FileNotFoundError(f'チェックリストCSVが見つかりません: {local_path}')
        return local_path

    try:
        content = _fetch_sheet_csv(url)
        sheet_rows = _count_rows_in_csv_text(content)
        local_rows = _count_checklist_rows(local_path) if local_path.exists() else 0

        if mirror and local_rows > 0 and sheet_rows < local_rows:
            print(
                f'警告: スプレッドシートは{sheet_rows}行ですが、ローカルCSVは{local_rows}行です。',
                file=sys.stderr,
            )
            print(
                '       ローカルCSVを上書きしません。スプレッドシートに全行をインポートしてください。',
                file=sys.stderr,
            )
            print(
                '       手順: docs/スプレッドシートに89行を入れる手順.md',
                file=sys.stderr,
            )
            print(
                f'       （取得は{sheet_rows}行で成功。ローカル{local_rows}行を使用します）',
                file=sys.stderr,
            )
            return local_path

        if mirror:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(content, encoding='utf-8-sig')
            print(f'スプレッドシートから取得: {sheet_rows}行 → {local_path}')
        return local_path
    except Exception as exc:
        print(
            f'警告: スプレッドシート取得失敗（{exc}）。ローカルCSVを使用します。',
            file=sys.stderr,
        )
        if local_path.exists():
            return local_path
        raise FileNotFoundError(
            f'スプレッドシート取得に失敗し、ローカルCSVもありません: {local_path}',
        ) from exc


def _checklist_edit_hint() -> str:
    if CHECKLIST_SHEET_URL:
        return '完了したら、スプレッドシートの「インデックス登録リクエスト」列に「済」や日付を書いてください。'
    return '完了したら、チェックリストCSVの「インデックス登録リクエスト」列に「済」や日付を書いてください。'


def _is_done_cell(cell: str) -> bool:
    cell = (cell or '').strip()
    if not cell:
        return False
    return '済' in cell


def pick_gsc_urls(today: date, *, csv_path: Path, state_path: Path, limit: int = 2) -> list[tuple[str, str, str]]:
    """
    Returns list of (priority, page_name, url).
    Skips rows already marked done in CSV and skips URLs already reminded (state).
    """
    if not csv_path.exists():
        raise FileNotFoundError(f'チェックリストCSVが見つかりません: {csv_path}')

    state = _load_state(state_path)
    reminded: set[str] = set(state.get('reminded_urls', [])) if isinstance(state.get('reminded_urls', []), list) else set()

    candidates: list[tuple[str, str, str]] = []
    for row in _iter_checklist_rows(csv_path):
        priority = row.get('優先度', '')
        name = row.get('ページ名', '')
        url = row.get('URL（フル）', '') or row.get('URL', '')
        requested = row.get('インデックス登録リクエスト', '')

        if not url:
            continue
        if not _is_ascii(url):
            # share_slug (ASCII) の URL を優先するため、非ASCIIはスキップ
            continue
        if _is_done_cell(requested):
            continue
        candidates.append((priority, name, url))

    candidates.sort(key=lambda x: (_priority_key(x[0]), x[1], x[2]))

    picked: list[tuple[str, str, str]] = []
    for item in candidates:
        if item[2] in reminded:
            continue
        picked.append(item)
        if len(picked) >= limit:
            break

    # If we ran out (e.g. state too strict), fall back to remaining candidates.
    if len(picked) < limit:
        for item in candidates:
            if item in picked:
                continue
            picked.append(item)
            if len(picked) >= limit:
                break

    # update state: track what we reminded today (even on dry-run? caller decides)
    state.setdefault('history', [])
    if isinstance(state['history'], list):
        state['history'].append({
            'date': today.isoformat(),
            'urls': [u for _, _, u in picked],
        })
        # keep it small
        if len(state['history']) > 60:
            state['history'] = state['history'][-60:]
    state['reminded_urls'] = sorted(set(reminded).union({u for _, _, u in picked}))
    state['last_date'] = today.isoformat()

    _save_state(state_path, state)
    return picked


def pick_x_tip(today: date, *, state_path: Path = DEFAULT_STATE_PATH) -> dict[str, str] | None:
    """今期作品から1本選び、投稿アングル付きで返す（外部トレンドAPIなし）。"""
    try:
        works = list_works(season=DEFAULT_SEASON, has_source_only=True)
    except Exception:
        return None
    works = [w for w in works if w.get('share_url') and w.get('has_source')]
    if not works:
        return None

    works = sorted(works, key=lambda w: -(w.get('watchers_count') or 0))
    top = works[:12]
    mid = works[12:36] or works

    angle_name, angle_hint = _X_ANGLES[today.weekday() % len(_X_ANGLES)]
    pool = mid if '穴場' in angle_name else top

    state = _load_state(state_path)
    recent = state.get('x_tip_slugs', [])
    if not isinstance(recent, list):
        recent = []
    recent_set = {str(s) for s in recent[-14:]}

    chosen = None
    for offset in range(len(pool)):
        candidate = pool[(today.toordinal() + offset) % len(pool)]
        slug = (candidate.get('share_slug') or candidate.get('id') or '').strip()
        if slug and slug not in recent_set:
            chosen = candidate
            break
    if chosen is None:
        chosen = pool[today.toordinal() % len(pool)]

    slug = (chosen.get('share_slug') or chosen.get('id') or '').strip()
    share_url = f'{SITE_URL}/works/{slug}' if slug else f'{SITE_URL}/'
    text = build_x_share_text(chosen)
    season_label = SEASON_LABELS.get(DEFAULT_SEASON, chosen.get('season_label') or '今期アニメ')
    watchers = int(chosen.get('watchers_count') or 0)

    recent.append(slug)
    state['x_tip_slugs'] = recent[-30:]
    state['last_x_tip_date'] = today.isoformat()
    _save_state(state_path, state)

    tip: dict[str, str] = {
        'title': str(chosen.get('title') or ''),
        'season_label': str(season_label),
        'angle_name': angle_name,
        'angle_hint': angle_hint,
        'watchers': f'{watchers:,}',
        'share_text': text,
        'share_url': share_url,
        'intent_url': twitter_share_url(text, share_url),
        'page_url': share_url,
    }
    if 'まとめ' in angle_name:
        tip['matome_url'] = f'{SITE_URL}/matome/{DEFAULT_SEASON}'
    return tip


def _format_x_tip(tip: dict[str, str] | None) -> str:
    if not tip:
        return ''
    lines = [
        '━━━━━━━━━━━━━━━━━━━━━━━━',
        '■ 今日のX投稿アドバイス',
        f'おすすめ作品: {tip["title"]}',
        f'枠: {tip["angle_name"]}（Annict人気目安 {tip["watchers"]}）',
        f'理由: {tip["season_label"]}の原作ガイド需要向け。{tip["angle_hint"]}',
        '',
        '投稿文（コピペ可）:',
        tip['share_text'],
        tip['share_url'],
        '',
        f'ワンクリック投稿: {tip["intent_url"]}',
        '手順: 表紙を保存 → 画像添付 → 上の文＋URL → 19〜22時に投稿',
    ]
    if tip.get('matome_url'):
        lines.append(f'セットで貼るまとめ: {tip["matome_url"]}')
    lines.append('')
    return '\n'.join(lines)


def _daily_tasks(
    today: date,
    *,
    gsc_urls: list[tuple[str, str, str]],
    x_tip: dict[str, str] | None = None,
) -> list[Task]:
    days = _days_since_launch(today)
    weekday = today.weekday()
    tasks: list[Task] = []

    tasks.append(Task(
        title='サイトが開くか確認',
        steps=[
            f'ブラウザで開く: {SITE_URL}/',
            'エラーや真っ白でないか見る',
        ],
        minutes=1,
    ))

    tasks.append(Task(
        title='Google検索でインデックス確認',
        steps=[
            'Googleで検索: site:anime-gensaku-guide.onrender.com',
            '結果が1件以上 → 登録開始！このタスクは週1回でOK',
            '0件 → まだ待ち。公開から3〜7日かかることあり',
        ],
        minutes=2,
    ))

    if gsc_urls:
        url_lines = [f'   ・({priority}) {name}: {url}' for priority, name, url in gsc_urls]
        tasks.append(Task(
            title='Search Console：インデックス登録リクエスト（今日の2件）',
            steps=[
                'Search Console を開く: https://search.google.com/search-console',
                '※ 依頼の前に、各URLをブラウザで開いて30秒待つ（Renderスリープ対策）',
                '上部「URL検査」にURLを貼る →「インデックス登録をリクエスト」',
                '【今日リクエストするURL（上から順に / 2件）】',
                *url_lines,
                _checklist_edit_hint(),
            ],
            minutes=8,
            optional=False,
        ))

    if weekday in (0, 3):
        tasks.append(Task(
            title='Search Console「ページ」で登録数をチェック',
            steps=[
                'Search Console → インデックス作成 → ページ',
                '「インデックス登録済み」の数が増えているか確認',
            ],
            minutes=2,
            optional=days >= 14,
        ))

    x_steps = [
        '下の「今日のX投稿アドバイス」の作品を使う（迷ったらこれ）',
        '作品ページで表紙を保存 → Xに画像添付',
        '投稿文をコピペ、またはワンクリック投稿リンクを開く',
        '19〜22時に投稿（反応が出やすい目安）',
    ]
    if x_tip:
        x_steps.insert(0, f'今日のおすすめ: {x_tip["title"]}（{x_tip["angle_name"]}）')
    tasks.append(Task(
        title='X（Twitter）で作品をシェア',
        steps=x_steps,
        minutes=5,
        optional=False,
    ))

    if weekday == 6:
        tasks.append(Task(
            title='今週のまとめ確認（週1回）',
            steps=[
                'Search Console → 効果（データが出ていればクリック数を見る）',
                'site: 検索で何件表示されるかメモ',
                '来週も同じペースでOK',
            ],
            minutes=5,
            optional=False,
        ))

    if days >= 30:
        tasks.append(Task(
            title='Amazonアソシエイトの売上確認',
            steps=[
                'アソシエイトセントラルで報酬・クリックを確認',
                '180日以内に有効売上3件が必要（アカウント継続条件）',
            ],
            minutes=3,
            optional=True,
        ))

    return tasks


def _format_task(index: int, task: Task) -> str:
    tag = '【できたら】' if task.optional else '【必須】'
    lines = [
        f'□ タスク{index}: {task.title}  {tag}（目安{task.minutes}分）',
    ]
    for step in task.steps:
        lines.append(f'   ・{step}')
    lines.append('')
    return '\n'.join(lines)


def build_subject(today: date) -> str:
    return f'【今日のタスク】アニメ原作ガイド｜{today.month}/{today.day}({_weekday_label(today)})'


def build_body(
    *,
    gsc_urls: list[tuple[str, str, str]],
    x_tip: dict[str, str] | None = None,
) -> str:
    today = date.today()
    days = _days_since_launch(today)
    if x_tip is None:
        x_tip = pick_x_tip(today)
    tasks = _daily_tasks(today, gsc_urls=gsc_urls, x_tip=x_tip)

    required = sum(1 for t in tasks if not t.optional)
    optional = sum(1 for t in tasks if t.optional)
    total_min = sum(t.minutes for t in tasks if not t.optional)

    header = f"""━━━━━━━━━━━━━━━━━━━━━━━━
■ アニメ原作ガイド｜今日のタスク
{today.year}年{today.month}月{today.day}日（{_weekday_label(today)}）
━━━━━━━━━━━━━━━━━━━━━━━━

{_phase_label(days)}
公開から {days} 日目 ／ 必須{required}件・任意{optional}件（約{total_min}分）

完了したら □ を OK に変えて進捗管理してください。

"""

    body = header
    for i, task in enumerate(tasks, 1):
        body += _format_task(i, task)
    body += _format_x_tip(x_tip)

    footer = f"""━━━━━━━━━━━━━━━━━━━━━━━━
🔗 よく使うリンク
・サイト: {SITE_URL}/
・Search Console: https://search.google.com/search-console
・サイトマップ送信: {SITE_URL}/sitemap.xml
・GitHub Actions（手動送信）: https://github.com/Deek229/anime-gensaku-guide/actions

※ このメールは毎朝9時に自動送信されます。
※ Xアドバイスは今期人気データ＋曜日アングルのローテです（外部トレンドAPIは未使用）。
"""
    return body + footer


def _missing_api_key_message() -> str:
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        return (
            'BREVO_API_KEY が未設定です。\n'
            '→ GitHub: Settings → Secrets and variables → Actions\n'
            '  名前 BREVO_API_KEY、値（BrevoのAPIキー）を追加してください。'
        )
    return (
        'BREVO_API_KEY が未設定です。\n'
        '→ Brevoメール設定を開く.bat の手順で API キーを .env に入れてください。'
    )


def _send_via_brevo(subject: str, body: str, to_addr: str) -> None:
    api_key = os.environ.get('BREVO_API_KEY', '').strip()
    if not api_key:
        raise ValueError(_missing_api_key_message())

    sender_email = os.environ.get('BREVO_SENDER_EMAIL', to_addr).strip()
    sender_name = os.environ.get('BREVO_SENDER_NAME', 'アニメ原作ガイド').strip()
    print(f'Brevo送信: {sender_email} → {to_addr}')

    payload = json.dumps({
        'sender': {'name': sender_name, 'email': sender_email},
        'to': [{'email': to_addr}],
        'subject': subject,
        'textContent': body,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.brevo.com/v3/smtp/email',
        data=payload,
        headers={
            'accept': 'application/json',
            'api-key': api_key,
            'content-type': 'application/json',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        print(f'Brevo API error ({e.code}): {detail}', file=sys.stderr)
        raise SystemExit(1) from e


def send_reminder() -> None:
    to_addr = TO.strip()
    today = date.today()
    subject = build_subject(today)
    csv_path = ensure_checklist_csv(CHECKLIST_CSV)
    gsc_urls = pick_gsc_urls(today, csv_path=csv_path, state_path=DEFAULT_STATE_PATH, limit=2)
    x_tip = pick_x_tip(today, state_path=DEFAULT_STATE_PATH)
    body = build_body(gsc_urls=gsc_urls, x_tip=x_tip)

    try:
        _send_via_brevo(subject, body, to_addr)
    except Exception:
        print('メール送信エラー:', file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)

    print(f'Sent to {to_addr}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='アニメ原作ガイド：毎朝のタスクメール（Brevo）')
    parser.add_argument('--dry-run', action='store_true', help='送信せず、件名と本文を表示する')
    parser.add_argument('--test-sheet', action='store_true', help='スプレッドシート取得のみテスト（メール送信なし）')
    parser.add_argument('--to', default=TO, help='送信先メールアドレス（REMINDER_EMAIL_TO の上書き）')
    parser.add_argument('--csv', default=str(CHECKLIST_CSV), help='チェックリストCSVのパス（ミラー先）')
    parser.add_argument('--sheet-url', default='', help='CHECKLIST_SHEET_URL の上書き（テスト用）')
    parser.add_argument('--state', default=str(DEFAULT_STATE_PATH), help='既に案内したURLの状態ファイル')
    args = parser.parse_args()

    csv_path = Path(args.csv)
    sheet_url = (args.sheet_url or CHECKLIST_SHEET_URL).strip() or None

    if args.test_sheet:
        resolved = ensure_checklist_csv(csv_path, sheet_url=sheet_url)
        rows = list(_iter_checklist_rows(resolved))
        print(f'OK: {len(rows)}行を読み込みました（{resolved}）')
        if sheet_url:
            print(f'取得元: {sheet_url}')
        else:
            print('CHECKLIST_SHEET_URL 未設定 → ローカルCSVのみ使用')
        raise SystemExit(0)

    today = date.today()
    resolved_csv = ensure_checklist_csv(csv_path, sheet_url=sheet_url)
    subject = build_subject(today)
    state_path = Path(args.state)
    gsc_urls = pick_gsc_urls(today, csv_path=resolved_csv, state_path=state_path, limit=2)
    x_tip = pick_x_tip(today, state_path=state_path)
    body = build_body(gsc_urls=gsc_urls, x_tip=x_tip)

    if args.dry_run:
        preview_path = ROOT / 'tools' / 'reminder_preview.txt'
        preview_path.write_text(subject + '\n\n' + body, encoding='utf-8')
        print('Dry-run: wrote preview to')
        print(str(preview_path))
        raise SystemExit(0)

    # regular send
    to_addr = (args.to or TO).strip()
    try:
        _send_via_brevo(subject, body, to_addr)
    except Exception:
        print('メール送信エラー:', file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)

    print(f'Sent to {to_addr}')

#!/usr/bin/env python3
"""アニメ原作ガイド — 日本語タスク管理メールを送信（Brevo）"""
from __future__ import annotations

import json
import os
import sys
import traceback
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')

SITE_URL = os.environ.get('SITE_URL', 'https://anime-gensaku-guide.onrender.com').rstrip('/')
TO = os.environ.get('REMINDER_EMAIL_TO', 'a_n_k_6@hotmail.com').strip() or 'a_n_k_6@hotmail.com'
LAUNCH_DATE = date.fromisoformat(os.environ.get('SITE_LAUNCH_DATE', '2026-06-14'))

WEEKDAYS_JA = '月火水木金土日'


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


def _daily_tasks(today: date) -> list[Task]:
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

    if days < 14:
        tasks.append(Task(
            title='Search Console でインデックス登録をリクエスト',
            steps=[
                'Search Console を開く: https://search.google.com/search-console',
                f'上部URL欄に入力: {SITE_URL}/',
                '「公開URLをテスト」→ OKなら「インデックス登録をリクエスト」',
                '※ 1日約10URLまで。上限なら明日でOK',
                '人気作品ページも1〜2件リクエスト（任意）',
            ],
            minutes=3,
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

    if weekday in (1, 3, 5):
        tasks.append(Task(
            title='X（Twitter）で作品をシェア',
            steps=[
                f'サイトを開く: {SITE_URL}/',
                '人気作品ページ → 「Xでシェア」ボタンを押す',
                'そのまま投稿（週2〜3回でOK）',
            ],
            minutes=3,
            optional=days < 7,
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


def build_body() -> str:
    today = date.today()
    days = _days_since_launch(today)
    tasks = _daily_tasks(today)

    required = sum(1 for t in tasks if not t.optional)
    optional = sum(1 for t in tasks if t.optional)
    total_min = sum(t.minutes for t in tasks if not t.optional)

    header = f"""━━━━━━━━━━━━━━━━━━━━━━━━
■ アニメ原作ガイド｜今日のタスク
{today.year}年{today.month}月{today.day}日（{_weekday_label(today)}）
━━━━━━━━━━━━━━━━━━━━━━━━

{_phase_label(days)}
公開から {days} 日目 ／ 必須{required}件・任意{optional}件（約{total_min}分）

完了したら □ を ✓ に変えて進捗管理してください。

"""

    body = header
    for i, task in enumerate(tasks, 1):
        body += _format_task(i, task)

    footer = f"""━━━━━━━━━━━━━━━━━━━━━━━━
🔗 よく使うリンク
・サイト: {SITE_URL}/
・Search Console: https://search.google.com/search-console
・GitHub Actions（手動送信）: https://github.com/Deek229/anime-gensaku-guide/actions

※ このメールは毎朝9時に自動送信されます。
"""
    return body + footer


def _send_via_brevo(subject: str, body: str, to_addr: str) -> None:
    api_key = os.environ.get('BREVO_API_KEY', '').strip()
    if not api_key:
        raise ValueError(
            'BREVO_API_KEY が未設定です。\n'
            '→ Brevoメール設定を開く.bat の手順で API キーを .env に入れてください。'
        )

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
    body = build_body()

    try:
        _send_via_brevo(subject, body, to_addr)
    except Exception:
        print('メール送信エラー:', file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)

    print(f'Sent to {to_addr}')


if __name__ == '__main__':
    send_reminder()

#!/usr/bin/env python3
"""アニメ原作ガイド — 日本語タスク管理メールを送信"""
from __future__ import annotations

import json
import os
import smtplib
import sys
import traceback
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')

SITE_URL = os.environ.get('SITE_URL', 'https://anime-gensaku-guide.onrender.com').rstrip('/')
TO = os.environ.get('REMINDER_EMAIL_TO', 'a_n_k_6@hotmail.com').strip() or 'a_n_k_6@hotmail.com'
# サイト公開日（この日から2週間はインデックス集中フェーズ）
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
    weekday = today.weekday()  # 0=月
    tasks: list[Task] = []

    # --- 毎日 ---
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

    # --- フェーズ1: インデックス集中 ---
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

    # --- 曜日別 ---
    if weekday in (0, 3):  # 月・木
        tasks.append(Task(
            title='Search Console「ページ」で登録数をチェック',
            steps=[
                'Search Console → インデックス作成 → ページ',
                '「インデックス登録済み」の数が増えているか確認',
            ],
            minutes=2,
            optional=days >= 14,
        ))

    if weekday in (1, 3, 5):  # 火・木・土
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

    if weekday == 6:  # 日
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


def _send_via_resend(subject: str, body: str, to_addr: str) -> None:
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    if not api_key:
        raise ValueError('RESEND_API_KEY が未設定')

    print(f'Resend送信先: {to_addr}')

    from_addr = os.environ.get('RESEND_FROM', 'onboarding@resend.dev').strip()
    payload = json.dumps({
        'from': from_addr,
        'to': [to_addr],
        'subject': subject,
        'text': body,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        print(f'Resend API error ({e.code}): {detail}', file=sys.stderr)
        if e.code == 403 and 'own email' in detail.lower():
            print(
                '\n対処: Resendに登録したメールアドレスと送信先を同じにしてください。\n'
                'Resend右上のアカウントメールを確認 → GitHub Secret RESEND_TO_EMAIL に設定\n'
                'または Resend を a_n_k_6@hotmail.com で登録し直す',
                file=sys.stderr,
            )
        raise SystemExit(1) from e


def _send_via_brevo(subject: str, body: str, to_addr: str) -> None:
    api_key = os.environ.get('BREVO_API_KEY', '').strip()
    if not api_key:
        raise ValueError('BREVO_API_KEY が未設定')

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


def _send_via_smtp(subject: str, body: str, to_addr: str) -> None:
    host = os.environ.get('SMTP_HOST', 'smtp-mail.outlook.com')
    port = int(os.environ.get('SMTP_PORT', '587'))
    user = os.environ.get('SMTP_USER', '').strip()
    password = os.environ.get('SMTP_PASSWORD', '').strip().replace(' ', '')

    if not user or not password:
        raise ValueError('SMTP_USER / SMTP_PASSWORD が未設定')

    if len(password) < 16:
        raise ValueError(
            'SMTP_PASSWORD は Microsoft のアプリパスワード（16文字）を入れてください。\n'
            '通常のログインパスワードでは送れません。\n'
            '作成: https://account.live.com/proofs/manage/additional → アプリパスワード'
        )

    msg = EmailMessage()
    msg.set_content(body, charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = to_addr

    with smtplib.SMTP(host, port, timeout=60) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, password)
        server.send_message(msg)


def send_reminder() -> None:
    to_addr = TO.strip()
    today = date.today()
    subject = build_subject(today)
    body = build_body()

    try:
        if os.environ.get('BREVO_API_KEY', '').strip():
            _send_via_brevo(subject, body, to_addr)
        elif os.environ.get('RESEND_API_KEY', '').strip():
            _send_via_resend(subject, body, to_addr)
        else:
            _send_via_smtp(subject, body, to_addr)
    except smtplib.SMTPAuthenticationError as e:
        err = str(e).lower()
        if 'basic authentication is disabled' in err:
            print(
                'HotmailのSMTP送信はMicrosoftで無効になっています。\n'
                '→ Brevoメール設定を開く.bat の手順で Brevo に切り替えてください。',
                file=sys.stderr,
            )
        else:
            print(
                'SMTP認証エラー:\n'
                '・アプリパスワード（16文字）を確認\n'
                '・または Brevo に切り替え（Brevoメール設定を開く.bat）',
                file=sys.stderr,
            )
        print(e, file=sys.stderr)
        raise SystemExit(1) from e
    except Exception:
        print('メール送信エラー:', file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)

    print(f'Sent to {to_addr}')


if __name__ == '__main__':
    send_reminder()

#!/usr/bin/env python3
"""Google Search Console 作業リマインダーをメール送信"""
from __future__ import annotations

import os
import smtplib
from datetime import date
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')

SITE_URL = os.environ.get('SITE_URL', 'https://anime-gensaku-guide.onrender.com').rstrip('/')
TO = os.environ.get('REMINDER_EMAIL_TO', 'a_n_k_6@hotmail.com')


def build_body() -> str:
    today = date.today()
    return f"""アニメ原作ガイド — Google Search Console リマインダー
{today}

【今日やること（5分）】

1. Google検索で確認
   site:anime-gensaku-guide.onrender.com
   → 結果が出ればインデックス開始！
   → 0件でも登録から3〜7日かかることがあります

2. Search Console（まだ0件のとき）
   https://search.google.com/search-console
   → 上部に URL を入力: {SITE_URL}/
   → 「公開URLをテスト」
   → OKなら「インデックス登録をリクエスト」
   ※ 1日約10URLまで。超えたら明日でOK

3. サイトが開くか確認
   {SITE_URL}/

【インデックス登録済みになったら】
→ 週1回、Search Console「効果」でクリック数を確認
→ 作品ページの「Xでシェア」を週2〜3回

---
anime-gensaku-guide 自動リマインダー
"""


def send_reminder() -> None:
    host = os.environ.get('SMTP_HOST', 'smtp-mail.outlook.com')
    port = int(os.environ.get('SMTP_PORT', '587'))
    user = os.environ.get('SMTP_USER', '').strip()
    password = os.environ.get('SMTP_PASSWORD', '').strip()
    to_addr = TO.strip()

    if not user or not password:
        raise SystemExit(
            'SMTP_USER / SMTP_PASSWORD が未設定です。\n'
            'GSCメール設定.md を参照してください。'
        )

    msg = MIMEText(build_body(), 'plain', 'utf-8')
    msg['Subject'] = f'【GSC確認】アニメ原作ガイド（{date.today()}）'
    msg['From'] = user
    msg['To'] = to_addr

    with smtplib.SMTP(host, port, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, password)
        server.sendmail(user, [to_addr], msg.as_string())

    print(f'Sent to {to_addr}')


if __name__ == '__main__':
    send_reminder()

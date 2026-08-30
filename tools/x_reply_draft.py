#!/usr/bin/env python3
"""Xポストを貼る → 「何巻から？」系の返信案＋原作ガイドURLを出す（半自動A案）"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from anime_service import enrich_work, list_works  # noqa: E402
from config import SITE_URL as SITE_URL_RAW  # noqa: E402
from seo import build_x_share_text  # noqa: E402
from store import resolve_share_slug  # noqa: E402

SITE_URL = (
    SITE_URL_RAW
    if SITE_URL_RAW.startswith('http')
    and '127.0.0.1' not in SITE_URL_RAW
    and 'localhost' not in SITE_URL_RAW
    else 'https://anime-gensaku-guide.onrender.com'
)

INTENT_PATTERNS = [
    (re.compile(r'何巻|なにかん|何話|どこから|何から読|何巻から', re.I), 'volume'),
    (re.compile(r'原作\s*(ある|あり|は？|は\?|なに|何)|原作ある|原作って|ラノベ|漫画版', re.I), 'has_source'),
    (re.compile(r'続き|その後|アニメ(の)?あと|アニメ終(わっ|了)', re.I), 'continue'),
    (re.compile(r'読む順|順番|どの順', re.I), 'order'),
]

# 略称 → 作品タイトルに含まれるキーワード
ALIASES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r're\s*:?\s*ゼロ|リゼロ|rezero', re.I), 're:ゼロ'),
    (re.compile(r'無職|むしょく|ルーデウス', re.I), '無職転生'),
    (re.compile(r'ワンパン|one\s*punch', re.I), 'ワンパンマン'),
    (re.compile(r'幼女|ターニャ|youjo', re.I), '幼女戦記'),
    (re.compile(r'ブリーチ|bleach', re.I), 'bleach'),
    (re.compile(r'スライム|転スラ|tensura', re.I), 'スライム'),
    (re.compile(r'薬屋|まおゆ', re.I), '薬屋'),
    (re.compile(r'シャングリラ|シャンフロ', re.I), 'シャングリラ'),
    (re.compile(r'サカモト|sakamoto', re.I), 'sakamoto'),
    (re.compile(r'逃げ上手|逃げ若', re.I), '逃げ上手'),
    (re.compile(r'百合|ヒャッカノ|100人の彼女', re.I), '100人の彼女'),
    (re.compile(r'スパイ教室', re.I), 'スパイ教室'),
]

# タイトル照合用に落とすノイズ
_NOISE = re.compile(
    r'(https?://\S+|@\w+|#\S+|RT\s+|何巻から|なにかん|原作ある|原作|何話|どこから|'
    r'教えて|誰か|わかる人|お願いします|お願い|？|\?|！|!|。|、|,|\.|…|・|〜|～)'
)


def _norm(text: str) -> str:
    t = text.lower()
    t = t.replace('　', ' ')
    for a, b in (
        ('ⅰ', 'i'), ('ⅱ', 'ii'), ('ⅲ', 'iii'), ('ⅳ', 'iv'),
        ('１', '1'), ('２', '2'), ('３', '3'),
        ('〜', ''), ('～', ''), ('-', ''), ('−', ''),
    ):
        t = t.replace(a, b)
    return re.sub(r'\s+', '', t)


def detect_intents(text: str) -> list[str]:
    found = []
    for pat, name in INTENT_PATTERNS:
        if pat.search(text):
            found.append(name)
    return found or ['general']


def score_work(post_text: str, work: dict) -> float:
    blob = _norm(post_text)
    title = _norm(work.get('title') or '')
    source = _norm(work.get('source_title') or '')
    score = 0.0

    if title and title in blob:
        score += 100 + min(len(title), 40)
    if source and len(source) >= 4 and source in blob:
        score += 80 + min(len(source), 30)

    # 略称ヒット
    for pat, needle in ALIASES:
        if pat.search(post_text) and _norm(needle) in title:
            score += 70
            break

    # 部分トークン（短い作品名対策）
    for cand in (title, source):
        if len(cand) < 4:
            continue
        # 先頭〜12文字がポストに含まれる
        head = cand[:12]
        if head and head in blob:
            score += 25
        # 4文字以上の連続部分
        for i in range(0, max(0, len(cand) - 3)):
            chunk = cand[i : i + 4]
            if chunk in blob:
                score += 3
                break

    # ノイズ除去後の投稿側からも
    cleaned = _norm(_NOISE.sub(' ', post_text))
    if title and len(title) >= 4:
        for n in (8, 6, 4):
            if len(title) >= n and title[:n] in cleaned:
                score += 15
                break

    return score


def find_candidates(post_text: str, *, limit: int = 5) -> list[tuple[float, dict]]:
    works = [enrich_work(w) for w in list_works(has_source_only=False)]
    scored = []
    for w in works:
        s = score_work(post_text, w)
        if s >= 20:
            scored.append((s, w))
    scored.sort(key=lambda x: (-x[0], -(x[1].get('watchers_count') or 0)))
    return scored[:limit]


def build_reply(work: dict, intents: list[str]) -> str:
    title = work.get('title') or ''
    short = title
    if len(short) > 28:
        short = short[:27] + '…'

    vol = work.get('anime_continue_volume')
    if vol is None:
        vol = work.get('source_volume_from')
    has_source = bool(work.get('has_source'))
    slug = resolve_share_slug(work)
    url = f'{SITE_URL}/works/{slug}'

    if not has_source:
        body = f'「{short}」はオリジナル寄りっぽいです。情報まとめはこちら👇'
    elif 'volume' in intents or 'continue' in intents or 'general' in intents:
        if vol is not None:
            body = f'「{short}」原作はだいたい第{vol}巻あたりからです。範囲と買う順はここ👇'
        else:
            note = (work.get('volume_short') or work.get('source_volume_note') or '').strip()
            if note:
                body = f'「{short}」{note} 詳細はここ👇'
            else:
                body = f'「{short}」の原作範囲・続きの巻はここにまとめてます👇'
    elif 'has_source' in intents:
        st = work.get('source_type_label') or '原作'
        body = f'「{short}」原作ありです（{st}）。何巻からかはここ👇'
    elif 'order' in intents:
        order = (work.get('read_order') or '').strip()
        if order:
            body = f'「{short}」読む順の目安: {order[:40]}… 詳細👇'
        else:
            body = f'「{short}」の読む順・買う順はここにまとめてます👇'
    else:
        body = build_x_share_text(work)

    # 返信は短め（URL別）
    body = body.strip()
    if len(body) > 100:
        body = body[:99].rstrip('。、 ') + '…'
    return f'{body}\n{url}'


def format_report(post_text: str) -> str:
    intents = detect_intents(post_text)
    cands = find_candidates(post_text)
    lines = [
        '━━━━━━━━━━━━━━━━━━━━━━━━',
        '■ X返信ドラフト（半自動A）',
        '━━━━━━━━━━━━━━━━━━━━━━━━',
        '',
        '【貼られたポスト】',
        post_text.strip()[:500],
        '',
        f'検知意図: {", ".join(intents)}',
        '',
    ]
    if not cands:
        lines += [
            '作品が特定できませんでした。',
            '→ 作品名が本文に入っているか確認するか、作品名を追記してもう一度。',
            '',
            '汎用返信例:',
            '今期アニメの「原作何巻から？」はここにまとめてます👇',
            f'{SITE_URL}/',
            '',
        ]
        return '\n'.join(lines)

    lines.append(f'候補 {len(cands)} 件（上から推奨）:')
    lines.append('')
    for i, (score, work) in enumerate(cands, 1):
        reply = build_reply(work, intents)
        lines += [
            f'--- 候補{i}（スコア {score:.0f} / 人気 {int(work.get("watchers_count") or 0):,}）---',
            f'作品: {work.get("title")}',
            f'季節: {work.get("season_label")}',
            f'ページ: {SITE_URL}/works/{resolve_share_slug(work)}',
            '',
            '【コピー用返信】',
            reply,
            '',
        ]
    lines += [
        '使い方: いちばん近い候補をコピー → Xで返信（自分が送る）',
        '注意: 同じ文面の連投は避け、1日の返信は控えめに。',
        '',
    ]
    return '\n'.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description='Xポスト → 原作ガイド返信案')
    parser.add_argument('text', nargs='*', help='ポスト本文（省略時は対話入力）')
    parser.add_argument('-f', '--file', help='ポスト本文ファイル')
    args = parser.parse_args()

    if args.file:
        post = Path(args.file).read_text(encoding='utf-8')
    elif args.text:
        post = ' '.join(args.text)
    elif not sys.stdin.isatty():
        post = sys.stdin.read()
    else:
        print('Xのポスト／コメントを貼って、空行のあと Ctrl+Z→Enter（Windows）:')
        print('（1行だけならそのまま Enter → もう一度 Enter で確定でも可）')
        chunks: list[str] = []
        empty_streak = 0
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line == '':
                empty_streak += 1
                if empty_streak >= 1 and chunks:
                    break
                continue
            empty_streak = 0
            chunks.append(line)
        post = '\n'.join(chunks)

    post = (post or '').strip()
    if not post:
        print('本文が空です。', file=sys.stderr)
        raise SystemExit(1)

    report = format_report(post)
    print(report)
    out = ROOT / 'tools' / 'x_reply_last.txt'
    out.write_text(report, encoding='utf-8')
    print(f'(保存: {out})')


if __name__ == '__main__':
    main()

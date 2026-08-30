"""2026-08-30 サイト更新: 2027冬ページ、秋アニメ追加、おすすめラノベ、玉葱コメント。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import load_works, save_works, slugify, share_slugify

ROOT = Path(__file__).resolve().parents[1]
WORKS_FILE = ROOT / 'data' / 'works.json'

AUTUMN_ADDITIONS = [
    {
        'title': '氷の城壁 第2期',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': '氷の城壁',
        'source_volume_from': 4,
        'source_volume_to': 6,
        'source_volume_approximate': True,
        'source_volume_note': '1期は第1〜3巻相当。2026年10月1日放送開始。',
        'read_order': '漫画1巻から。1期見た人は4巻前後から',
        'amazon_search': '氷の城壁 漫画',
        'tags': ['スポーツ', 'バスケ', '少年漫画'],
        'watchers_count': 9850,
        'share_slug': 'koori-no-jouheki-2',
        'main_comment': '高校バスケ漫画の人気作が2期へ。2026年10月1日からTBS系で放送開始。原作は試合の緊張感とチームの成長描写が秀逸で、1期を追った人は4巻前後から先読み可能。スポーツ漫画・バスケが好きな人に。秋クール早々の注目続編です。',
    },
    {
        'title': 'サイバーパンク エッジランナーズ2',
        'season': '2026-autumn',
        'source_type': 'original',
        'source_title': '',
        'source_volume_from': None,
        'source_volume_to': None,
        'source_volume_note': 'オリジナルTVアニメ続編。2026年10月20日Netflix配信開始予定。',
        'read_order': '前作を視聴後がおすすめ。原作なし',
        'amazon_search': '',
        'tags': ['SF', 'アクション', 'オリジナル'],
        'watchers_count': 9750,
        'share_slug': 'cyberpunk-edgerunners-2',
        'main_comment': 'Trigger×CD Projekt REDの話題作が続編へ。2026年10月20日からNetflixで配信予定のオリジナルアニメ。前作の世界観とキャラクター性を引き継ぎつつ、新たな物語が展開される見込み。SFアクション・サイバーパンクが好きな人は前作からの視聴を。原作はないためアニメ単体で楽しめます。',
    },
    {
        'title': '彼方から',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': '彼方から',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_approximate': True,
        'source_volume_note': '2026年10月4日放送開始。連載中。',
        'read_order': '漫画1巻から',
        'amazon_search': '彼方から 漫画',
        'tags': ['ファンタジー', '恋愛', '少女漫画'],
        'watchers_count': 8650,
        'share_slug': 'kanata-kara',
        'main_comment': '異世界から現代に迷い込んだ少女と高校生の恋愛ファンタジーが再アニメ化。2026年10月4日からTOKYO MXほかで放送開始。少女漫画の古典的名作で、切ない恋と異世界要素のバランスが魅力。懐かし名作の新アニメが好きな人、ファンタジー恋愛が好きな人に。1巻から先読みがおすすめです。',
    },
    {
        'title': '死亡遊戯で飯を食う。44:CLOUDY BEACH',
        'season': '2026-autumn',
        'source_type': 'light_novel',
        'source_title': '死亡遊戯で飯を食う。',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_approximate': True,
        'source_volume_note': '9月先行配信・10月地上波。連載中。',
        'read_order': 'ラノベ1巻から',
        'amazon_search': '死亡遊戯で飯を食う ラノベ',
        'tags': ['デスゲーム', 'サバイバル', 'バトル'],
        'watchers_count': 8550,
        'share_slug': 'shibou-yuugi',
        'main_comment': '死亡ゲームに参加して稼ぐ主人公のサバイバルラノベがアニメ化。2026年9月に先行配信、10月から地上波放送。心理戦とルール攻略が読みどころのデスゲーム系。カイジ・賭博黙示録系が好きな人に。初アニメ化なので1巻から先読みがおすすめです。',
    },
    {
        'title': 'スティール・ボール・ラン ジョジョの奇妙な冒険 2nd & 3rd STAGE',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': 'ジョジョの奇妙な冒険 スティール・ボール・ラン',
        'source_volume_from': 12,
        'source_volume_to': 18,
        'source_volume_approximate': True,
        'source_volume_note': '2026年秋クール。1st STAGEは第1〜11巻相当。',
        'read_order': 'SBR1巻から。1st STAGE見た人は12巻前後から',
        'amazon_search': 'ジョジョ SBR 漫画',
        'tags': ['バトル', '西部劇', '少年漫画'],
        'watchers_count': 9950,
        'share_slug': 'jojo-sbr-2-3',
        'main_comment': 'ジョジョシリーズ第7部「スティール・ボール・ラン」のアニメ続編。2026年秋に2nd・3rd STAGEが放送予定。西部劇×スタンドバトルの異色作で、1st STAGEを追った人は漫画12巻前後から先読み可能。ジョジョファンは必見、バトル漫画の傑作を味わいたい人にもおすすめです。',
    },
]

LN_ADDITIONS = [
    {
        'id': 'その無限の先へ',
        'season': 'ln-picks',
        'status': 'ln_only',
        'media': 'novel',
        'memo': '旧MFブックス版1〜6巻は絶版。クラファンでリブート第1巻発売中。',
        'official_url': '',
        'narou_url': 'https://ncode.syosetu.com/n6811ck/',
        'title': 'その無限の先へ',
        'source_type': 'light_novel',
        'source_title': 'その無限の先へ',
        'source_volume_from': 1,
        'source_volume_to': 1,
        'source_volume_approximate': False,
        'source_volume_note': 'なろう連載中。書籍第1巻発売中、第2巻準備中。',
        'read_order': 'なろう1話目から。書籍版は1巻から',
        'amazon_search': 'その無限の先へ ラノベ',
        'tags': ['異世界', 'ダンジョン', 'コメディ'],
        'watchers_count': 750,
        'share_slug': 'sono-mugen-no-saki-e',
        'cover_image_url': '/static/cover-placeholder.svg',
        'main_comment': '限界村落から迷宮都市へ。ゲーム的システムと過酷な現実が同居するダンジョン冒険譚。貧困から這い上がる主人公の成長と、クラン運営・階層攻略の読み応えが魅力。大体コメディ寄りだがシリアスな場面も。ダンジョンもの・成り上がりが好きな人に。',
    },
    {
        'id': '幻想再帰のアリュージョニスト',
        'season': 'ln-picks',
        'status': 'ln_only',
        'media': 'novel',
        'memo': '書籍未刊。なろう連載のみ。',
        'official_url': '',
        'narou_url': 'https://ncode.syosetu.com/n9073ca/',
        'title': '幻想再帰のアリュージョニスト',
        'source_type': 'web_novel',
        'source_title': '幻想再帰のアリュージョニスト',
        'source_volume_from': None,
        'source_volume_to': None,
        'source_volume_approximate': False,
        'source_volume_note': 'なろう連載中。書籍化なし。',
        'read_order': 'なろう1話目から',
        'amazon_search': '幻想再帰のアリュージョニスト',
        'tags': ['SF', 'オカルト', '哲学'],
        'watchers_count': 700,
        'share_slug': 'gensou-saiki-allusionist',
        'cover_image_url': '/static/cover-placeholder.svg',
        'main_comment': '言葉と理解をめぐる、頭脳派SFファンタジー。サイバーパンクとオカルトパンクが交差する世界で、主人公は「誰も自分の言葉を理解できない」という孤独を抱える。難解な部分もあるが、読み返すほど味が出る作品。哲学系・実験的なWeb小説が好きな人に。',
    },
    {
        'id': 'crawlers',
        'season': 'ln-picks',
        'status': 'ln_only',
        'media': 'novel',
        'memo': 'カクヨム版もあり。',
        'official_url': '',
        'narou_url': 'https://ncode.syosetu.com/n5472cu/',
        'title': "Crawler's",
        'source_type': 'web_novel',
        'source_title': "Crawler's",
        'source_volume_from': None,
        'source_volume_to': None,
        'source_volume_approximate': False,
        'source_volume_note': 'なろう連載中。書籍化なし。',
        'read_order': 'なろう「導入」から',
        'amazon_search': "Crawler's 小説",
        'tags': ['SF', 'ポストアポカリプス', 'ミリタリー'],
        'watchers_count': 650,
        'share_slug': 'crawlers',
        'cover_image_url': '/static/cover-placeholder.svg',
        'main_comment': 'ポールシフト後の再生地球を舞台にしたSFサバイバル。軍人の永瀬恭一郎が、女ばかりのドームポリスで異形生命体と戦いながら謎を解いていく。硬めのミリタリーSFと謎解きが好きな人に。書籍未刊のためなろうで読むのが基本です。',
    },
]

TAMANE_COMMENT = (
    'もっと評価されてほしいと願う作品。練られたストーリーは満足できるはず。'
    'いろんな要素がまざっている小説で、科学の内容や少し冗長的と感じる部分もあり、万人受けはしないかもしれない。'
    'それでもなろう徘徊者で未読なら、是非読んでほしい。2回読むのもいいと思う。'
    '\n\n'
    '異世界に迷い込んだ青年・但馬波留が、まずはマルチ商法で金稼ぎ→逮捕→紙の発明で英雄へという、'
    '詐欺師から始まる成り上がり英雄譚。内政チート国家づくりと本格モノ作り（紙・印刷・火薬など）が融合した異世界ファンタジー。'
    'HJ小説大賞受賞作で、なろうでも2000万PV超え。コミカライズも連載中だが、アニメ化は未定。'
    '\n\n'
    '「お前を消す方法を探してください」——作品の中核にある問いかけのように、'
    '主人公の知恵と狡猾さ、そして異世界での発明と政治が絡み合う物語は、読み終えたあとも余韻が残る。'
    '派手なバトルより頭脳と制度設計が好きな人、Re:ゼロや盾の勇者のような「異世界で何かを作る」系が好きな人に特におすすめ。'
)


def _row_from_expansion(raw: dict) -> dict:
    title = raw['title']
    work_id = slugify(title)
    row = {
        'id': work_id,
        'season': raw['season'],
        'status': 'upcoming',
        'media': 'tv',
        'memo': '',
        'official_url': raw.get('official_url', ''),
        'title': title,
        'source_type': raw['source_type'],
        'source_title': raw.get('source_title', ''),
        'source_volume_from': raw.get('source_volume_from'),
        'source_volume_to': raw.get('source_volume_to'),
        'source_volume_approximate': raw.get('source_volume_approximate', True),
        'source_volume_note': raw.get('source_volume_note', ''),
        'read_order': raw.get('read_order', '1巻から'),
        'amazon_search': raw.get('amazon_search', ''),
        'tags': raw.get('tags', []),
        'watchers_count': raw.get('watchers_count', 5000),
        'share_slug': raw.get('share_slug') or share_slugify(title, work_id),
        'main_comment': raw['main_comment'],
        'cover_image_url': '/static/cover-placeholder.svg',
    }
    return row


def main() -> int:
    works = load_works()
    existing_ids = {w['id'] for w in works}
    existing_titles = {w['title'] for w in works}

    # 2026-winter → 2027-winter（2027年1〜3月放送）
    for w in works:
        if w.get('season') == '2026-winter':
            w['season'] = '2027-winter'

    # 秋アニメ追加
    added_autumn = 0
    for raw in AUTUMN_ADDITIONS:
        row = _row_from_expansion(raw)
        if row['id'] in existing_ids or row['title'] in existing_titles:
            continue
        works.append(row)
        existing_ids.add(row['id'])
        existing_titles.add(row['title'])
        added_autumn += 1

    # おすすめラノベ追加
    added_ln = 0
    for raw in LN_ADDITIONS:
        if raw['id'] in existing_ids or raw['title'] in existing_titles:
            continue
        works.append(raw)
        existing_ids.add(raw['id'])
        existing_titles.add(raw['title'])
        added_ln += 1

    # 玉葱とクラリオン更新
    for w in works:
        if w.get('id') == '玉葱とクラリオン' or w.get('share_slug') == 'tamane-clarion':
            w['main_comment'] = TAMANE_COMMENT
            w['narou_url'] = w.get('narou_url') or 'https://ncode.syosetu.com/n0632db/'

    works.sort(key=lambda x: (-(x.get('watchers_count') or 0), x.get('season', ''), x.get('title', '')))
    save_works(works)

    autumn = sum(1 for w in works if w.get('season') == '2026-autumn')
    winter = sum(1 for w in works if w.get('season') == '2027-winter')
    ln = sum(1 for w in works if w.get('season') == 'ln-picks')
    print(f'added autumn: {added_autumn}, ln: {added_ln}')
    print(f'totals autumn={autumn} winter_2027={winter} ln_picks={ln} all={len(works)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

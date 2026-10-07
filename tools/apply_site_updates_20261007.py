"""2026-10-07: 秋を放送開始に、冬の欠落追加、2027春を新設。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from store import load_works, save_works, slugify, share_slugify

sys.stdout.reconfigure(encoding='utf-8')


def isbn13_to_isbn10(isbn13: str) -> str:
    s = ''.join(c for c in isbn13 if c.isdigit())
    if len(s) != 13 or not s.startswith('978'):
        return ''
    core = s[3:12]
    total = sum(int(d) * (10 - i) for i, d in enumerate(core))
    rem = (11 - total % 11) % 11
    check = 'X' if rem == 10 else str(rem)
    return core + check


def row(raw: dict) -> dict:
    title = raw['title']
    work_id = slugify(title)
    isbn = raw.get('isbn', '')
    asin = raw.get('amazon_asin') or (isbn13_to_isbn10(isbn) if isbn else '')
    out = {
        'id': work_id,
        'season': raw['season'],
        'status': raw.get('status', 'upcoming'),
        'media': 'tv',
        'memo': '',
        'official_url': raw.get('official_url', ''),
        'title': title,
        'source_type': raw['source_type'],
        'source_title': raw['source_title'],
        'source_volume_from': raw.get('source_volume_from'),
        'source_volume_to': raw.get('source_volume_to'),
        'source_volume_approximate': raw.get('source_volume_approximate', True),
        'source_volume_note': raw.get('source_volume_note', ''),
        'read_order': raw.get('read_order', '1巻から'),
        'amazon_search': raw.get('amazon_search', f'{raw["source_title"]} 原作'),
        'tags': raw.get('tags', []),
        'watchers_count': raw.get('watchers_count', 5000),
        'share_slug': raw.get('share_slug') or share_slugify(title, work_id),
        'main_comment': raw['main_comment'],
    }
    if isbn:
        out['isbn'] = isbn
    if asin:
        out['amazon_asin'] = asin
    return out


ADDITIONS = [
    {
        'title': 'マロニエ王国の七人の騎士',
        'season': '2026-autumn',
        'status': 'airing',
        'source_type': 'manga',
        'source_title': 'マロニエ王国の七人の騎士',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2026年10月スタート。月刊フラワーズ連載。',
        'read_order': '漫画1巻から',
        'amazon_search': 'マロニエ王国の七人の騎士 漫画',
        'tags': ['ファンタジー', '冒険', '少女漫画'],
        'watchers_count': 8100,
        'share_slug': 'marronnier-kingdom',
        'isbn': '9784091394279',
        'main_comment': '小さな姫と七人の騎士が国を守るファンタジー。2026年10月スタート。画の密度と宮廷の人間関係が原作の読みどころで、バトルより物語の厚みが売り。少女漫画ファンタジーが好きな人、秋の新作で王道以外を探している人は1巻から。',
    },
    {
        'title': 'アラフォー賢者の異世界生活日記',
        'season': '2027-winter',
        'source_type': 'light_novel',
        'source_title': 'アラフォー賢者の異世界生活日記',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2027年1月。MFブックス。',
        'read_order': 'ラノベ1巻から。漫画版でも可',
        'amazon_search': 'アラフォー賢者の異世界生活日記 ラノベ',
        'tags': ['異世界', '転生', 'ファンタジー'],
        'watchers_count': 8350,
        'share_slug': 'around40-kenja',
        'isbn': '9784040686417',
        'main_comment': 'ゲームの能力を引き継いだ40歳が、平穏を望みつつ異世界で賢者扱いされる転生もの。2027年1月。スローライフ志向と無自覚チートのギャップが原作の味。おっさん転生・異世界ものが好きな人は1巻から。冬の新作ラノベ枠です。',
    },
    {
        'title': 'ザ・ファブル 第2期',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': 'ザ・ファブル',
        'source_volume_from': 8,
        'source_volume_to': 14,
        'source_volume_approximate': True,
        'source_volume_note': '1期の続き。2027年1月 日本テレビ系。手塚プロダクション。',
        'read_order': '漫画1巻から。1期見た人は8巻前後から',
        'amazon_search': 'ザ・ファブル 漫画',
        'tags': ['アクション', 'コメディ', '青年漫画'],
        'watchers_count': 8900,
        'share_slug': 'the-fable-2',
        'isbn': '9784063825633',
        'main_comment': '殺しの天才が普通の生活を強いられるダークコメディの続編。2027年1月から日本テレビ系。1期の延長で、日常と殺意の落差が原作の核。青年漫画・殺し屋ものが好きな人、1期を見た人は8巻前後から。',
    },
    {
        'title': '世界最高の暗殺者、異世界貴族に転生する 第2期',
        'season': '2027-winter',
        'source_type': 'light_novel',
        'source_title': '世界最高の暗殺者、異世界貴族に転生する',
        'source_volume_from': 5,
        'source_volume_to': 8,
        'source_volume_approximate': True,
        'source_volume_note': '1期の続き。2027年冬。SILVER LINK。',
        'read_order': 'ラノベ1巻から。1期見た人は5巻前後から',
        'amazon_search': '世界最高の暗殺者 異世界貴族 ラノベ',
        'tags': ['異世界', '転生', 'アクション'],
        'watchers_count': 8550,
        'share_slug': 'ansatsu-kizoku-2',
        'isbn': '9784040731735',
        'main_comment': '現代の暗殺者が異世界貴族に転生するシリーズの2期。2027年冬。育成と任務のテンポが原作の売りで、1期の延長として十分楽しめる。転生もの・暗闘が好きな人、1期を見た人は5巻前後から。',
    },
    {
        'title': '真・侍伝 YAIBA かぐや編',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': 'YAIBA',
        'source_volume_from': 8,
        'source_volume_to': 14,
        'source_volume_approximate': True,
        'source_volume_note': '第2期。2027年1月9日 日本テレビ系。WIT STUDIO。',
        'read_order': '漫画1巻から。1期見た人はかぐや編該当巻から',
        'amazon_search': 'YAIBA 漫画',
        'tags': ['アクション', '少年漫画', '剣'],
        'watchers_count': 8450,
        'share_slug': 'yaiba-kaguya',
        'isbn': '9784091230010',
        'main_comment': '青山剛昌の剣戟バトル漫画の新作アニメ第2期。2027年1月9日から日本テレビ系。かぐや編が中心で、1期の勢いを引き継ぐ。少年漫画の剣術バトルが好きな人、1期を見た人は該当巻から。',
    },
    {
        'title': '魔女と傭兵',
        'season': '2027-spring',
        'source_type': 'light_novel',
        'source_title': '魔女と傭兵',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2027年4月 日本テレビ系。GCN文庫。8-bit。',
        'read_order': 'ラノベ1巻から。漫画版でも可',
        'amazon_search': '魔女と傭兵 ラノベ',
        'tags': ['ファンタジー', '冒険', 'ダーク'],
        'watchers_count': 9200,
        'share_slug': 'majo-to-youhei',
        'isbn': '9784867164242',
        'main_comment': '追われる魔女と双刃の傭兵が安住の地を探すダークファンタジー。2027年4月から日本テレビ系。なろう発の本格冒険もので、二人の信頼関係と世界の過酷さが原作の核。ダークファンタジーが好きな人は1巻から。春の注目ラノベ枠です。',
    },
    {
        'title': 'カグラバチ',
        'season': '2027-spring',
        'source_type': 'manga',
        'source_title': 'カグラバチ',
        'source_volume_from': 1,
        'source_volume_to': 5,
        'source_volume_note': '2027年4月。週刊少年ジャンプ連載。Cypic。',
        'read_order': '漫画1巻から',
        'amazon_search': 'カグラバチ 漫画',
        'tags': ['アクション', '復讐', '少年漫画'],
        'watchers_count': 9800,
        'share_slug': 'kagurabachi',
        'isbn': '9784088838199',
        'main_comment': '父を奪われた少年が妖刀を手に復讐へ向かうジャンプ新作。2027年4月。刀と術のバトル、殺気の密度が原作の魅力。少年漫画のダークアクションが好きな人は1巻から。春の看板新作枠です。',
    },
    {
        'title': '運命の巻戻士',
        'season': '2027-spring',
        'source_type': 'manga',
        'source_title': '運命の巻戻士',
        'source_volume_from': 1,
        'source_volume_to': 5,
        'source_volume_note': '2027年4月 テレビ朝日系 IMAnimation。月刊コロコロコミック。bones film。',
        'read_order': '漫画1巻から',
        'amazon_search': '運命の巻戻士 漫画',
        'tags': ['SF', 'サスペンス', '少年漫画'],
        'watchers_count': 9000,
        'share_slug': 'unmei-no-makimodoshi',
        'isbn': '9784091433992',
        'main_comment': '死者を救うため時間を巻き戻す少年のSFサスペンス。2027年4月からテレビ朝日系。コロコロ発だが暗めの運命ものと時間ループが核。SF・サスペンスが好きな人は1巻から。春の異色枠です。',
    },
    {
        'title': '幼稚園WARS',
        'season': '2027-spring',
        'source_type': 'manga',
        'source_title': '幼稚園WARS',
        'source_volume_from': 1,
        'source_volume_to': 5,
        'source_volume_note': '2027年春。少年ジャンプ＋連載。サンライズ×FelixFilm。',
        'read_order': '漫画1巻から',
        'amazon_search': '幼稚園WARS 漫画',
        'tags': ['アクション', 'コメディ', '少年漫画'],
        'watchers_count': 9100,
        'share_slug': 'youchien-wars',
        'isbn': '9784088834863',
        'main_comment': '元殺し屋が幼稚園で園児を守るバイオレンスラブコメ。2027年春。ギャグと殺傷の落差が原作の売りで、ただのバトルものではない。ジャンプ＋の人気作を先読みしたい人は1巻から。',
    },
    {
        'title': 'テンカイチ 日本最強武芸者決定戦',
        'season': '2027-spring',
        'source_type': 'manga',
        'source_title': 'テンカイチ 日本最強武芸者決定戦',
        'source_volume_from': 1,
        'source_volume_to': 5,
        'source_volume_note': '2027年4月。ヤングマガジン連載。冨嶽。',
        'read_order': '漫画1巻から',
        'amazon_search': 'テンカイチ 日本最強武芸者決定戦 漫画',
        'tags': ['バトル', '歴史', '青年漫画'],
        'watchers_count': 8800,
        'share_slug': 'tenkaichi',
        'isbn': '9784065230305',
        'main_comment': '信長が日本最強の武芸者を決める異種格闘の戦国バトル。2027年4月。武蔵や忠勝が史実と違う形でぶつかり合うのが原作の見どころ。格闘・歴史ものが好きな人は1巻から。春の青年漫画枠です。',
    },
    {
        'title': 'スキップとローファー 2nd season',
        'season': '2027-spring',
        'source_type': 'manga',
        'source_title': 'スキップとローファー',
        'source_volume_from': 6,
        'source_volume_to': 10,
        'source_volume_approximate': True,
        'source_volume_note': '1期の続き。2027年春。P.A.WORKS。',
        'read_order': '漫画1巻から。1期見た人は6巻前後から',
        'amazon_search': 'スキップとローファー 漫画',
        'tags': ['青春', '学園', '日常'],
        'watchers_count': 8700,
        'share_slug': 'skip-to-loafer-2',
        'isbn': '9784065102169',
        'main_comment': '地方出身の優等生が都内高校で居場所を見つける青春ものの2期。2027年春。人間関係の機微と季節の移ろいが原作の強み。1期を見た人は6巻前後から、初見なら1巻から。春の日常・青春枠です。',
    },
    {
        'title': '転生したらスライムだった件 クレイマンREVENGE',
        'season': '2027-spring',
        'source_type': 'manga',
        'source_title': '転生したらスライムだった件 クレイマンREVENGE',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2027年春。スピンオフ漫画。8-bit。',
        'read_order': '本作1巻から。本編既読なら世界観がより分かる',
        'amazon_search': '転スラ クレイマンREVENGE 漫画',
        'tags': ['ファンタジー', 'スピンオフ', '逆転'],
        'watchers_count': 9400,
        'share_slug': 'tensura-clayman-revenge',
        'isbn': '9784065300954',
        'main_comment': '死んだはずのクレイマンが復活し暗躍する転スラのスピンオフ。2027年春。本編の裏側から見た戦争と野心が原作の核。転スラを追っている人、悪役視点が好きな人は1巻から。春の続編シーズンと並ぶ注目作です。',
    },
    {
        'title': '薬屋のひとりごと 第3期 第2クール',
        'season': '2027-spring',
        'source_type': 'light_novel',
        'source_title': '薬屋のひとりごと',
        'source_volume_from': 12,
        'source_volume_to': 14,
        'source_volume_approximate': True,
        'source_volume_note': '第3期第1クールは2026年秋。第2クールは2027年春。',
        'read_order': 'ラノベ1巻から。3期前半を見た人は12巻前後から',
        'amazon_search': '薬屋のひとりごと ラノベ',
        'tags': ['ミステリー', '宮廷', '歴史'],
        'watchers_count': 9600,
        'share_slug': 'kusuriya-3-2nd',
        'isbn': '9784757579859',
        'main_comment': '後宮ミステリー3期の後半クール。2027年春。秋の第1クールの続きで、陰謀と人間関係がさらに深まる。1・2期や3期前半を見た人は12巻前後から。春の看板続編です。',
    },
    {
        'title': 'LONA',
        'season': '2027-spring',
        'status': 'upcoming',
        'source_type': 'original',
        'source_title': '',
        'source_volume_from': None,
        'source_volume_to': None,
        'source_volume_approximate': False,
        'source_volume_note': '2027年春。WIT STUDIO。オリジナル。',
        'read_order': '',
        'amazon_search': 'LONA アニメ',
        'tags': ['SF', 'ミステリー', 'オリジナル'],
        'watchers_count': 7800,
        'share_slug': 'lona-2027',
        'main_comment': '死者の脳に残った記憶を読む研究者たちのオリジナルSFミステリー。2027年春、WIT STUDIO。原作書籍はない。脳科学ものと謎解きが好きな人向けの春のオリジナル枠です。',
    },
    {
        'title': '機動戦士ガンダムRG XARX-ZERO',
        'season': '2027-spring',
        'source_type': 'original',
        'source_title': '',
        'source_volume_from': None,
        'source_volume_to': None,
        'source_volume_approximate': False,
        'source_volume_note': '2027年春。SOLA ANIMATION。オリジナル。',
        'read_order': '',
        'amazon_search': '機動戦士ガンダムRG XARX-ZERO',
        'tags': ['ロボット', 'SF', 'オリジナル'],
        'watchers_count': 8600,
        'share_slug': 'gundam-rg-xarx',
        'main_comment': 'ガンダムシリーズの新作オリジナル。2027年春。原作漫画・小説はなし。ロボットものと宇宙世紀周辺の新作を追いたい人向け。春の大型オリジナル枠です。',
    },
]

NOTE_UPDATES = {
    'kusuriya-3': '第1・2期は第1〜9巻相当。3期第1クールは2026年10月2日日本テレビ系。第2クールは2027年春。',
    'fool-night': '2026年11月26日 Netflix配信開始。ビッグコミックス。',
    'db-super-beerus': '破壊神ビルス編。2026年10月11日 フジテレビ系。',
}

# 11月以降スタートは upcoming のまま
KEEP_UPCOMING = {'fool-night'}


def main() -> int:
    works = load_works()
    existing_ids = {w['id'] for w in works}
    existing_titles = {w['title'] for w in works}
    existing_slugs = {w.get('share_slug') for w in works}

    added = {'2026-autumn': 0, '2027-winter': 0, '2027-spring': 0}
    for raw in ADDITIONS:
        item = row(raw)
        if item['id'] in existing_ids or item['title'] in existing_titles or item['share_slug'] in existing_slugs:
            print(f'skip existing: {item["title"]}')
            continue
        works.append(item)
        existing_ids.add(item['id'])
        existing_titles.add(item['title'])
        existing_slugs.add(item['share_slug'])
        added[item['season']] = added.get(item['season'], 0) + 1
        print(f'add {item["season"]}: {item["title"]}')

    notes = airing = 0
    for w in works:
        slug = w.get('share_slug')
        if slug in NOTE_UPDATES and w.get('source_volume_note') != NOTE_UPDATES[slug]:
            w['source_volume_note'] = NOTE_UPDATES[slug]
            notes += 1
        if w.get('season') == '2026-autumn' and slug not in KEEP_UPCOMING and w.get('status') == 'upcoming':
            w['status'] = 'airing'
            airing += 1

    works.sort(key=lambda w: (-(w.get('watchers_count') or 0), w.get('season', ''), w.get('title', '')))
    save_works(works)

    print(
        f'added autumn={added["2026-autumn"]} winter={added["2027-winter"]} '
        f'spring={added["2027-spring"]} notes={notes} autumn_airing={airing}'
    )
    for s in ['2026-autumn', '2027-winter', '2027-spring']:
        print(f'total {s}={sum(1 for w in works if w.get("season") == s)}')
    print(f'all={len(works)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

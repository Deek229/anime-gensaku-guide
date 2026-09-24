"""2026-09-24: 秋・冬の欠落作品追加、夏を放送終了、おすすめ欄を更新。"""
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
        'status': 'upcoming',
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
        'title': '塩対応の佐藤さんが俺にだけ甘い',
        'season': '2026-autumn',
        'source_type': 'light_novel',
        'source_title': '塩対応の佐藤さんが俺にだけ甘い',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2026年10月スタート。ガガガ文庫。漫画版もあり。',
        'read_order': 'ラノベ1巻から。漫画版でも可',
        'amazon_search': '塩対応の佐藤さん ラノベ',
        'tags': ['ラブコメ', '学園', '日常'],
        'watchers_count': 8300,
        'share_slug': 'shio-sato',
        'isbn': '9784094518238',
        'main_comment': 'クラスでは塩対応の佐藤さんが、主人公の前だけ甘い学園ラブコメ。2026年10月スタート。ギャップ萌えと日常の温度差が原作の読みどころで、重い異世界の合間に観やすい。ラブコメ・学園ものが好きな人は1巻から。漫画版でも入れます。',
    },
    {
        'title': '生徒会にも穴はある！',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': '生徒会にも穴はある！',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2026年10月3日 TOKYO MX・BS11ほか。週刊少年マガジン連載。',
        'read_order': '漫画1巻から',
        'amazon_search': '生徒会にも穴はある 漫画',
        'tags': ['コメディ', '学園', '少年漫画'],
        'watchers_count': 8500,
        'share_slug': 'seitokai-ana',
        'isbn': '9784065290866',
        'main_comment': '生徒会の穴（欠点）を突いて笑わせる学園ギャグ。2026年10月3日からTOKYO MX・BS11ほか。テンポの速さとキャラの癖が原作の強みで、秋のコメディ枠として入りやすい。ギャグ漫画が好きな人、学園ものが欲しい人は1巻から。',
    },
    {
        'title': '世界最強の魔女、始めました',
        'season': '2026-autumn',
        'source_type': 'light_novel',
        'source_title': '世界最強の魔女、始めました',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2026年10月7日 TOKYO MXほか。一迅社文庫。',
        'read_order': 'ラノベ1巻から。漫画版でも可',
        'amazon_search': '世界最強の魔女始めました ラノベ',
        'tags': ['ファンタジー', '魔女', '冒険'],
        'watchers_count': 8400,
        'share_slug': 'saikyou-majo',
        'isbn': '9784757583030',
        'main_comment': '平凡な少女が最強魔女としての力に目覚め、世界を巻き込むファンタジー。2026年10月7日からTOKYO MXほか。成り上がりと魔法バトルのテンポが原作の売り。異世界・魔女ものが好きな人、秋の新作ラノベ枠を探している人は1巻から。',
    },
    {
        'title': 'TANK CHAIR-戦車椅子-',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': '戦車椅子-TANK CHAIR-',
        'source_volume_from': 1,
        'source_volume_to': 5,
        'source_volume_note': '2026年10月4日 TOKYO MXほか。週刊ヤングマガジン連載。',
        'read_order': '漫画1巻から',
        'amazon_search': '戦車椅子 TANK CHAIR 漫画',
        'tags': ['アクション', 'サスペンス', '青年漫画'],
        'watchers_count': 8700,
        'share_slug': 'tank-chair',
        'isbn': '9784065299234',
        'main_comment': '車椅子を戦車に変えて戦う、青年漫画寄りのダークアクション。2026年10月4日からTOKYO MXほか。障害と暴力、家族の歪みが同居するのが原作の手触りで、ただのバトルものではない。サスペンスや青年漫画が好きな人は1巻から先読みがおすすめです。',
    },
    {
        'title': '転生ゴブリンだけど質問ある？',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': '転生ゴブリンだけど質問ある？',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2026年10月5日 TOKYO MX・BS11ほか。ジャンプ＋連載。',
        'read_order': '漫画1巻から',
        'amazon_search': '転生ゴブリンだけど質問ある 漫画',
        'tags': ['異世界', '転生', 'ファンタジー'],
        'watchers_count': 8650,
        'share_slug': 'tensei-goblin',
        'isbn': '9784088915753',
        'main_comment': '寿命7日のゴブリンに転生し、スキルを継ぎながら生き残る異世界無双。2026年10月5日からTOKYO MXほか。短命種族の制約と成り上がりのテンポが原作の面白さ。転生もの・無双ものが好きな人は1巻から。秋の新作ジャンプ枠です。',
    },
    {
        'title': 'とある暗部の少女共棲',
        'season': '2026-autumn',
        'source_type': 'light_novel',
        'source_title': 'とある暗部の少女共棲',
        'source_volume_from': 1,
        'source_volume_to': 1,
        'source_volume_approximate': False,
        'source_volume_note': '2026年10月9日 AT-X・TOKYO MXほか。禁書目録外伝ITEM。電撃文庫。',
        'read_order': '本作1巻から。本編既読なら世界観がより分かる',
        'amazon_search': 'とある暗部の少女共棲 ラノベ',
        'tags': ['学園', 'バトル', 'ダーク'],
        'watchers_count': 8800,
        'share_slug': 'toaru-item',
        'isbn': '9784049149395',
        'main_comment': '学園都市の暗部組織ITEMに属する少女たちの外伝。2026年10月9日からAT-X・TOKYO MXほか。本編の裏側で動く四人の仕事と友情が原作の核で、禁書目録を知っていると味が増す。ダークな能力バトルが好きな人、シリーズの隙間を埋めたい人に。外伝単体でも1巻から入れます。',
    },
    {
        'title': '転生した大聖女は、聖女であることをひた隠す',
        'season': '2026-autumn',
        'source_type': 'light_novel',
        'source_title': '転生した大聖女は、聖女であることをひた隠す',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2026年10月スタート。アース・スターノベル。',
        'read_order': 'ラノベ1巻から。漫画版でも可',
        'amazon_search': '転生した大聖女 ラノベ',
        'tags': ['ファンタジー', '転生', '聖女'],
        'watchers_count': 8250,
        'share_slug': 'tensei-daiseijo',
        'isbn': '9784803013061',
        'main_comment': '前世の大聖女が、今生では聖女だとバレないよう騎士を目指すファンタジー。2026年10月スタート。力を隠しながら便利に使ってしまうギャップが原作の味。なろう発の定番枠で、転生・聖女ものが好きな人は1巻から。秋の異世界で読みやすい一作です。',
    },
    {
        'title': '野生のラスボスが現れた！ 第2期',
        'season': '2026-autumn',
        'source_type': 'light_novel',
        'source_title': '野生のラスボスが現れた！',
        'source_volume_from': 5,
        'source_volume_to': 8,
        'source_volume_approximate': True,
        'source_volume_note': '1期の続き。2026年10月3日 TOKYO MXほか。',
        'read_order': 'ラノベ1巻から。1期見た人は5巻前後から',
        'amazon_search': '野生のラスボスが現れた ラノベ',
        'tags': ['異世界', 'ファンタジー', 'コメディ'],
        'watchers_count': 8150,
        'share_slug': 'yasei-lastboss-2',
        'isbn': '9784803008722',
        'main_comment': '異世界のラスボス側に転生した青年の続編。2026年10月3日からTOKYO MXほか。強すぎて周囲がざわつくコメディと世界観の広がりが原作の売り。1期を見た人は5巻前後から、初見なら1巻から。秋の続編異世界枠です。',
    },
    {
        'title': 'どうも、好きな人に惚れ薬を依頼された魔女です。',
        'season': '2026-autumn',
        'source_type': 'light_novel',
        'source_title': 'どうも、好きな人に惚れ薬を依頼された魔女です。',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2026年10月スタート。Mノベルスf。漫画版もあり。',
        'read_order': 'ラノベ1巻から。漫画版でも可',
        'amazon_search': 'どうも好きな人に惚れ薬を依頼された魔女です ラノベ',
        'tags': ['恋愛', 'ファンタジー', '日常'],
        'watchers_count': 8050,
        'share_slug': 'horegusuri-majo',
        'isbn': '9784575242171',
        'main_comment': '片想いの騎士に惚れ薬を頼まれた引きこもり魔女の恋愛ファンタジー。2026年10月スタート。完成を引き延ばしながら一緒にいる時間が原作の核で、バトルより会話と温度が売り。おとなしい恋愛もの・魔女ものが好きな人は1巻から。',
    },
    {
        'title': 'フールナイト',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': 'フールナイト',
        'source_volume_from': 1,
        'source_volume_to': 5,
        'source_volume_note': '2026年11月26日 Netflix配信開始。ビッグコミックス。',
        'read_order': '漫画1巻から',
        'amazon_search': 'フールナイト 漫画',
        'tags': ['ダークファンタジー', '吸血鬼', '青年漫画'],
        'watchers_count': 7950,
        'share_slug': 'fool-night',
        'isbn': '9784098608669',
        'main_comment': '資源が尽きた世界で植物化を拒み、吸血鬼として生きる青年のダークファンタジー。2026年11月26日からNetflix。生存と倫理の問いが原作の重みで、秋後半の異色枠。青年漫画・ディストピアが好きな人は1巻から。',
    },
    {
        'title': '電撃デイジー',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': '電撃デイジー',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2027年冬。スタジオディーン。別コミ連載の少女漫画。',
        'read_order': '漫画1巻から',
        'amazon_search': '電撃デイジー 漫画',
        'tags': ['恋愛', '学園', '少女漫画'],
        'watchers_count': 8600,
        'share_slug': 'dengeki-daisy',
        'isbn': '9784091313065',
        'main_comment': '秘密を抱えた少女と、謎の用務員の学園ラブストーリー。2027年冬。別コミの定番を新作アニメ化する枠で、年齢差と秘密のやり取りが原作の魅力。少女漫画・学園恋愛が好きな人は1巻から。冬の新作で王道恋愛が欲しい人に。',
    },
    {
        'title': 'ジャイアントお嬢様',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': 'ジャイアントお嬢様',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2027年冬。タツノコプロ。',
        'read_order': '漫画1巻から',
        'amazon_search': 'ジャイアントお嬢様 漫画',
        'tags': ['コメディ', '恋愛', '日常'],
        'watchers_count': 8300,
        'share_slug': 'giant-ojousama',
        'isbn': '9784098508075',
        'main_comment': '体の大きな令嬢と、彼女に振り回される周囲のギャグコメディ。2027年冬。ビジュアルの落差と愛情の真っ直ぐさが原作の売りで、重い冬アニメの合間に観やすい。ラブコメ・ギャグが好きな人は1巻から。',
    },
    {
        'title': '欠けた月のメルセデス',
        'season': '2027-winter',
        'source_type': 'light_novel',
        'source_title': '欠けた月のメルセデス～吸血鬼の貴族に転生したけど捨てられそうなのでダンジョンを制覇する～',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2027年1月。TOブックス。漫画版もあり。',
        'read_order': 'ラノベ1巻から。漫画版でも可',
        'amazon_search': '欠けた月のメルセデス ラノベ',
        'tags': ['ファンタジー', '転生', 'ダンジョン'],
        'watchers_count': 8400,
        'share_slug': 'kaketa-tsuki-mercedes',
        'isbn': '9784866992167',
        'main_comment': '貧乏貴族の吸血鬼少女が、ダンジョン制覇で家を立て直す冒険譚。2027年1月。転生知識と力押しの攻略が同居するのが原作のテンポ。ダンジョンもの・成り上がりが好きな人、冬の新作ラノベ枠を探している人は1巻から。',
    },
    {
        'title': 'ふつつかな悪女ではございますが 第2クール',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': 'ふつつかな悪女ではございますが',
        'source_volume_from': 5,
        'source_volume_to': 8,
        'source_volume_approximate': True,
        'source_volume_note': '第1クールは2026年夏。第2クールは2027年1月。はじめての外遊編。',
        'read_order': '漫画1巻から。1クール見た人は5巻前後から',
        'amazon_search': 'ふつつかな悪女 漫画',
        'tags': ['ファンタジー', '恋愛', '悪役令嬢'],
        'watchers_count': 8200,
        'share_slug': 'futsutsuka-akujo-2',
        'isbn': '9784758036269',
        'main_comment': '入れ替わり後宮ものの続き。2027年1月から第2クール。南領での豊穣祭と新たな黒幕が原作の山場で、1クールの延長として十分楽しめる。悪役令嬢・後宮ものが好きな人、夏に1クールを見た人は5巻前後から。',
    },
    {
        'title': 'おデブ悪女に転生したら、なぜかラスボス王子様に執着されています',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': 'おデブ悪女に転生したら、なぜかラスボス王子様に執着されています',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2027年冬。FLOS COMIC。スタジオリングス。',
        'read_order': '漫画1巻から',
        'amazon_search': 'おデブ悪女に転生したら 漫画',
        'tags': ['恋愛', '転生', '悪役令嬢'],
        'watchers_count': 7900,
        'share_slug': 'odebu-akujo',
        'isbn': '9784046842138',
        'main_comment': '悪役令嬢として転生したセリーヌが、ラスボス王子の執着を受けながら平穏を目指す溺愛もの。2027年冬。更生とヤンデレが同時に走るのが原作の味。転生恋愛・悪役令嬢が好きな人は1巻から。冬の乙女向け新作枠です。',
    },
]

NOTE_UPDATES = {
    'jojo-sbr-2-3': '2nd & 3rd STAGE。2026年9月25日 Netflix配信開始。',
    'shibou-yuugi': '2026年9月25日スタート。電撃の新文芸。',
    'tensei-kizoku-3': '1・2期の続き。2026年9月27日スタート。',
    'shin-tenipuri-u17': '2026年9月30日 テレビ東京ほか。WORLD CUP編の続き。',
    'sasaki-pea-2': '2026年10月7日 AT-X・TOKYO MXほか。初回1時間SP。',
    'tougen-anki-2': '日光・華厳の滝編。2026年10月 日本テレビ系。',
    'futsutsuka-akujo': '第1クールは2026年夏。第2クールは2027年1月。',
}

AIRING_SLUGS = {
    'jojo-sbr-2-3',
    'shibou-yuugi',
    'tensei-kizoku-3',
    'shin-tenipuri-u17',
}

LN_PICK_UPDATES = {
    'sono-mugen-no-saki-e': {
        'isbn': '9784040679501',
        'source_volume_from': 1,
        'source_volume_to': 2,
        'source_volume_approximate': False,
        'source_volume_note': 'なろう連載中。旧MFブックス版は絶版。リブート版は1〜2巻刊。',
        'memo': '旧MFブックス版1〜6巻は絶版。クラファンリブートは第2巻まで刊行。',
        'read_order': 'なろう1話目から。書籍はリブート版1巻から',
        'watchers_count': 780,
        'main_comment': '限界村落から迷宮都市へ。ゲーム的システムと過酷な現実が同居するダンジョン冒険譚。貧困から這い上がる成長と、クラン運営・階層攻略の読み応えが魅力。リブート書籍は2巻まで出ているが、続きはなろうが基本。ダンジョンもの・成り上がりが好きな人に。',
    },
    'tamane-clarion': {
        'watchers_count': 860,
        'source_volume_note': 'HJノベルス刊。書籍は2巻まで。なろう版もあり。コミカライズ連載中。',
    },
    'gensou-saiki-allusionist': {
        'watchers_count': 720,
        'source_volume_note': 'なろう連載中。書籍化なし（2026年9月時点）。',
    },
    'crawlers': {
        'watchers_count': 680,
        'source_volume_note': 'なろう連載中。カクヨム版もあり。書籍化なし（2026年9月時点）。',
    },
}


def main() -> int:
    works = load_works()
    existing_ids = {w['id'] for w in works}
    existing_titles = {w['title'] for w in works}
    existing_slugs = {w.get('share_slug') for w in works}

    added_autumn = added_winter = 0
    for raw in ADDITIONS:
        item = row(raw)
        if item['id'] in existing_ids or item['title'] in existing_titles or item['share_slug'] in existing_slugs:
            print(f'skip existing: {item["title"]}')
            continue
        works.append(item)
        existing_ids.add(item['id'])
        existing_titles.add(item['title'])
        existing_slugs.add(item['share_slug'])
        if item['season'] == '2026-autumn':
            added_autumn += 1
        else:
            added_winter += 1
        print(f'add {item["season"]}: {item["title"]}')

    notes = finished = airing = ln_updated = 0
    for w in works:
        slug = w.get('share_slug')
        if slug in NOTE_UPDATES and w.get('source_volume_note') != NOTE_UPDATES[slug]:
            w['source_volume_note'] = NOTE_UPDATES[slug]
            notes += 1
        if w.get('season') == '2026-summer' and w.get('status') in ('airing', 'upcoming'):
            w['status'] = 'finished'
            finished += 1
        if slug in AIRING_SLUGS and w.get('status') != 'airing':
            w['status'] = 'airing'
            airing += 1
        if slug in LN_PICK_UPDATES:
            patch = LN_PICK_UPDATES[slug]
            for key, value in patch.items():
                if w.get(key) != value:
                    w[key] = value
                    ln_updated += 1
            isbn = w.get('isbn', '')
            if isbn and not w.get('amazon_asin'):
                asin = isbn13_to_isbn10(isbn)
                if asin:
                    w['amazon_asin'] = asin
                    ln_updated += 1

    works.sort(key=lambda w: (-(w.get('watchers_count') or 0), w.get('season', ''), w.get('title', '')))
    save_works(works)

    autumn = sum(1 for w in works if w.get('season') == '2026-autumn')
    winter = sum(1 for w in works if w.get('season') == '2027-winter')
    print(f'added autumn={added_autumn} winter={added_winter} notes={notes} summer_finished={finished} airing={airing} ln_fields={ln_updated}')
    print(f'totals autumn={autumn} winter={winter} all={len(works)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

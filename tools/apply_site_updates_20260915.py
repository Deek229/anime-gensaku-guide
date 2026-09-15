"""2026-09-15: 秋・冬アニメの欠落作品追加、放送日メモ更新、トップを秋へ。"""
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
    # --- 2026 autumn ---
    {
        'title': '魔法少女育成計画 restart',
        'season': '2026-autumn',
        'source_type': 'light_novel',
        'source_title': '魔法少女育成計画 restart',
        'source_volume_from': 1,
        'source_volume_to': 2,
        'source_volume_note': 'restart前・後編。2026年10月5日 テレビ東京ほか。1期は無印相当。',
        'read_order': '無印を読んでからrestart前編。アニメ1期視聴済みならrestartから',
        'amazon_search': '魔法少女育成計画 restart ラノベ',
        'tags': ['魔法少女', 'サスペンス', 'デスゲーム'],
        'watchers_count': 9200,
        'share_slug': 'mahoiku-restart',
        'isbn': '9784800201829',
        'main_comment': '魔法少女たちが理不尽な生存ゲームに巻き込まれるシリーズの続編。2026年10月5日からテレビ東京ほかで放送。原作はrestart前編・後編が今回の中心で、1期を見た人は無印を飛ばして続きから入れる。サスペンス寄りの魔法少女もの、デスゲームの駆け引きが好きな人に。秋の異色枠です。',
    },
    {
        'title': '超巡！超条先輩',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': '超巡！超条先輩',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2026年10月スタート。週刊少年ジャンプ連載。',
        'read_order': '漫画1巻から',
        'amazon_search': '超巡 超条先輩 漫画',
        'tags': ['コメディ', '超能力', '少年漫画'],
        'watchers_count': 8900,
        'share_slug': 'chojo-senpai',
        'isbn': '9784088841083',
        'main_comment': '超能力を持ちながら場末の交番にいる先輩と、怪力の新米が組むポリスコメディ。2026年10月スタートのジャンプ新作アニメ。ギャグのテンポと能力バトルが同居するのが読みどころ。初アニメ化なので1巻から。コメディ×能力ものが好きな人、秋の新顔を探している人に。',
    },
    {
        'title': '朱色の仮面',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': '朱色の仮面',
        'source_volume_from': 1,
        'source_volume_to': 5,
        'source_volume_note': '2026年10月10日 読売テレビ・日本テレビ系。分割2クール。',
        'read_order': '漫画1巻から',
        'amazon_search': '朱色の仮面 漫画',
        'tags': ['ファンタジー', 'バトル', '青年漫画'],
        'watchers_count': 8750,
        'share_slug': 'shuiro-no-kamen',
        'isbn': '9784785969820',
        'main_comment': '仮面を着けると能力が目覚める世界で、贖罪の旅に出る少年のファンタジー。2026年10月から読売テレビ・日本テレビ系で分割2クール。土曜夕方枠の新作で、画の密度と世界観の厚みが原作の強み。ダークファンタジーや能力バトルが好きな人は1巻から先読みがおすすめです。',
    },
    {
        'title': 'マジカル★エクスプローラー',
        'season': '2026-autumn',
        'source_type': 'light_novel',
        'source_title': 'マジカル★エクスプローラー エロゲの友人キャラに転生したけど、ゲーム知識使って自由に生きる',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2026年10月3日 TOKYO MXほか。ラノベ原作。',
        'read_order': 'ラノベ1巻から。漫画版でも可',
        'amazon_search': 'マジカルエクスプローラー ラノベ',
        'tags': ['転生', '学園', 'ラブコメ'],
        'watchers_count': 8600,
        'share_slug': 'magical-explorer',
        'isbn': '9784041110072',
        'main_comment': '美少女ゲームの友人キャラに転生し、知識で自由に立ち回る学園ファンタジー。2026年10月3日からTOKYO MXほか。原作ラノベはハーレム要素と攻略知識の使い方が読みどころ。転生もの・学園ものが好きな人、秋のライトな異世界枠を探している人に。1巻からで十分入れます。',
    },
    {
        'title': '新テニスの王子様 U-17 WORLD CUP 決勝メンバー決定戦',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': '新テニスの王子様',
        'source_volume_from': 30,
        'source_volume_to': 34,
        'source_volume_approximate': True,
        'source_volume_note': '2026年9月30日 テレビ東京ほか。WORLD CUP編の続き。',
        'read_order': '本編から。WORLD CUPまで見た人は該当巻から',
        'amazon_search': '新テニスの王子様 漫画',
        'tags': ['スポーツ', 'テニス', '少年漫画'],
        'watchers_count': 8550,
        'share_slug': 'shin-tenipuri-u17',
        'isbn': '9784088747248',
        'main_comment': 'テニプリシリーズのU-17ワールドカップ編が続編へ。2026年9月30日からテレビ東京ほか。代表争いの緊張感と個性的なプレースタイルが原作の魅力。前作まで追った人は続き巻から、初見なら漫画1巻か旧アニメから。スポーツアニメの秋の定番枠です。',
    },
    {
        'title': '信者ゼロの女神サマと始める異世界攻略',
        'season': '2026-autumn',
        'source_type': 'light_novel',
        'source_title': '信者ゼロの女神サマと始める異世界攻略',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2026年10月スタート。オーバーラップ文庫。',
        'read_order': 'ラノベ1巻から',
        'amazon_search': '信者ゼロの女神サマ ラノベ',
        'tags': ['異世界', 'ダンジョン', '冒険'],
        'watchers_count': 8450,
        'share_slug': 'shinja-zero',
        'isbn': '9784865544626',
        'main_comment': 'クラス最弱の転移者に、信者ゼロのマイナー女神が噛みついてくる異世界攻略もの。2026年10月スタート。ゲーム知識とダンジョン攻略のテンポが原作の売り。よくある転移ものより「弱い側からの成り上がり」がはっきりしている。秋の異世界枠で1巻から先読みしやすい作品です。',
    },
    {
        'title': '貸した魔力は【リボ払い】で強制徴収',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': '貸した魔力は【リボ払い】で強制徴収',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2026年10月1日 テレビ朝日系ほか。',
        'read_order': '漫画1巻から',
        'amazon_search': '貸した魔力はリボ払い 漫画',
        'tags': ['異世界', '復讐', 'ファンタジー'],
        'watchers_count': 8350,
        'share_slug': 'ribarai-maryoku',
        'isbn': '9784866753072',
        'main_comment': 'パーティーに魔力を貸したあげく追放された少年が、リボ払いで取り立てる異色ファンタジー。2026年10月1日からテレビ朝日系ほか。追放ものに「債権回収」を足した切り口が面白い。スカッと系・成り上がりが好きな人は1巻から。秋の新作でネタが刺さる人向けです。',
    },
    {
        'title': 'FX戦士くるみちゃん',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': 'FX戦士くるみちゃん',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2026年10月1日 AT-X・TOKYO MXほか。',
        'read_order': '漫画1巻から',
        'amazon_search': 'FX戦士くるみちゃん 漫画',
        'tags': ['コメディ', '金融', '日常'],
        'watchers_count': 8200,
        'share_slug': 'fx-kurumi',
        'isbn': '9784046806680',
        'main_comment': 'FXをテーマにした異色の金融コメディ漫画が10月1日から放送。数字と生活が直結するテンポで、ただのギャグに終わらないのが原作の味。お金・仕事系の漫画が好きな人、秋の変わり種を観たい人に。話数も読みやすく、1巻からで十分間に合います。',
    },
    {
        'title': 'おじさんはカワイイものがお好き。',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': 'おじさんはカワイイものがお好き。',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2026年10月4日スタート。連載中。',
        'read_order': '漫画1巻から',
        'amazon_search': 'おじさんはカワイイものがお好き 漫画',
        'tags': ['コメディ', '日常', '職場'],
        'watchers_count': 8100,
        'share_slug': 'ojisan-kawaii',
        'isbn': '9784866750125',
        'main_comment': '仕事はデキるのに、隠れて可愛いものを愛でる課長の日常コメディ。2026年10月4日スタート。ギャップ萌えと職場の人間関係が読みどころで、重い秋アニメの合間に観やすい。癒し・コメディ枠が欲しい人は1巻から。実写化もされた人気作のアニメ版です。',
    },
    {
        'title': 'ロメリア戦記',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': 'ロメリア戦記 伯爵令嬢、魔王を倒した後も人類やばそうだから軍隊組織した',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2026年10月スタート TOKYO MXほか。',
        'read_order': '漫画1巻から',
        'amazon_search': 'ロメリア戦記 漫画',
        'tags': ['ファンタジー', '戦記', '転生'],
        'watchers_count': 8000,
        'share_slug': 'romelia-senki',
        'isbn': '9784800011374',
        'main_comment': '魔王を倒したあと、次の危機に備えて軍隊を組織する令嬢の戦記ファンタジー。2026年10月からTOKYO MXほか。転生ものでも「戦いのあとの国家運営」に寄っているのが原作の個性。戦記・軍略ものが好きな人、秋の異世界で王道以外を探している人に。1巻から先読みできます。',
    },
    {
        'title': 'ダークサモナーとデキている',
        'season': '2026-autumn',
        'source_type': 'manga',
        'source_title': 'ダークサモナーとデキている',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2026年10月スタート。',
        'read_order': '漫画1巻から',
        'amazon_search': 'ダークサモナーとデキている 漫画',
        'tags': ['ファンタジー', 'ラブコメ', '冒険'],
        'watchers_count': 7900,
        'share_slug': 'dark-summoner',
        'isbn': '9784040747569',
        'main_comment': '神官見習いと悪魔使いが秘密の関係を抱えたまま旅するファンタジーラブコメ。2026年10月スタート。バトルより二人の温度差と世界観の軽さが売り。ラブコメ×ファンタジーが好きな人、秋の新作で肩の力を抜きたい人に。初アニメ化なので1巻からがおすすめです。',
    },
    # --- 2027 winter ---
    {
        'title': 'マッシュル-MASHLE- 三魔対争神覚者最終試験編',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': 'マッシュル-MASHLE-',
        'source_volume_from': 13,
        'source_volume_to': 18,
        'source_volume_approximate': True,
        'source_volume_note': '漫画は全18巻完結。1・2期の続き、最終試験編。2027年冬。',
        'read_order': '漫画1巻から。2期まで見た人は13巻前後から',
        'amazon_search': 'マッシュル 漫画',
        'tags': ['バトル', 'ギャグ', '少年漫画'],
        'watchers_count': 9880,
        'share_slug': 'mashle-3',
        'isbn': '9784088823294',
        'main_comment': '魔法が使えない筋肉少年が魔法界で無双するギャグバトルの最終章。2027年冬に三魔対争神覚者最終試験編として放送。原作は全18巻完結済みなので、結末まで先読みできる。2期まで追った人は13巻前後から。ジャンプの馬鹿力コメディが好きな人、冬の看板続編です。',
    },
    {
        'title': 'マリッジトキシン 第2期',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': 'マリッジトキシン',
        'source_volume_from': 8,
        'source_volume_to': 12,
        'source_volume_approximate': True,
        'source_volume_note': '1期は序盤相当。2027年1月放送。',
        'read_order': '漫画1巻から。1期見た人は8巻前後から',
        'amazon_search': 'マリッジトキシン 漫画',
        'tags': ['アクション', 'コメディ', '少年漫画'],
        'watchers_count': 9450,
        'share_slug': 'marriage-toxin-2',
        'isbn': '9784088832135',
        'main_comment': '殺し屋と結婚詐欺師のバディが「世界一ハードな婚活」を続けるアクションコメディの2期。2027年1月放送。毒と策略、ギャグの温度差が原作の魅力。1期を見た人は8巻前後から。バトルコメ・ジャンプ作品の続編を冬に観たい人向けです。',
    },
    {
        'title': '気になってる人が男じゃなかった',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': '気になってる人が男じゃなかった',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2027年冬 CloverWorks。Web発の人気作。',
        'read_order': '漫画1巻から',
        'amazon_search': '気になってる人が男じゃなかった 漫画',
        'tags': ['百合', '青春', '恋愛'],
        'watchers_count': 9300,
        'share_slug': 'kinioto',
        'isbn': '9784046817327',
        'main_comment': 'CDショップの「おにーさん」が実は同級生の女子だった、Web発の青春百合作。2027年冬にCloverWorksがアニメ化。音楽と視線の温度で関係性が進むタイプで、大声のラブコメではない。百合・青春ものが好きな人は1巻から。冬の注目新作です。',
    },
    {
        'title': '傷口と包帯',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': '傷口と包帯',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2027年1月 ABC・テレビ朝日系 ANiMAZiNG!!!枠。',
        'read_order': '漫画1巻から',
        'amazon_search': '傷口と包帯 漫画',
        'tags': ['恋愛', '青年漫画', 'ヒューマンドラマ'],
        'watchers_count': 8700,
        'share_slug': 'kizu-to-houtai',
        'isbn': '9784065376928',
        'main_comment': 'ヤクザの若頭が、特殊な体質を持つ組長の娘の世話係になるヒューマンドラマ。2027年1月からABC・テレビ朝日系。依存と世話の関係が生々しく、王道ラブコメではない。人間関係の歪みが好きな人、冬の新作で濃い話が欲しい人は1巻から。',
    },
    {
        'title': '黒岩メダカに私の可愛いが通じない Season2',
        'season': '2027-winter',
        'source_type': 'manga',
        'source_title': '黒岩メダカに私の可愛いが通じない',
        'source_volume_from': 6,
        'source_volume_to': 10,
        'source_volume_approximate': True,
        'source_volume_note': '1期の続き。2027年冬 Season2。',
        'read_order': '漫画1巻から。1期見た人は6巻前後から',
        'amazon_search': '黒岩メダカに私の可愛いが通じない 漫画',
        'tags': ['ラブコメ', '学園', '少年漫画'],
        'watchers_count': 8650,
        'share_slug': 'kuroiwa-medaka-2',
        'main_comment': 'ぶりっ子が通じない男子を落とそうとする学園ラブコメの2期。2027年冬。原作は「可愛さの定義」をずらして笑わせるタイプで、1期の延長で十分楽しめる。ラブコメの続編を冬に観たい人、1期を見た人は6巻前後から。',
    },
    {
        'title': '悠久の愚者アズリーの、賢者のすゝめ',
        'season': '2027-winter',
        'source_type': 'light_novel',
        'source_title': '悠久の愚者アズリーの、賢者のすゝめ',
        'source_volume_from': 1,
        'source_volume_to': 3,
        'source_volume_note': '2027年1月。アース・スターノベル。',
        'read_order': 'ラノベ1巻から',
        'amazon_search': '悠久の愚者アズリー ラノベ',
        'tags': ['ファンタジー', '魔法', 'スローライフ'],
        'watchers_count': 7800,
        'share_slug': 'azley',
        'isbn': '9784803007886',
        'main_comment': '5000年生きた落ちこぼれ魔法使いが、現代の魔法大学で再評価されるファンタジー。2027年1月放送。長期視点の成長と、周囲が追いつかないギャップが原作の味。スロー寄りの異世界・魔法ものが好きな人に。冬の新作ラノベ枠として1巻から読めます。',
    },
    {
        'title': '異世界転生騒動記',
        'season': '2027-winter',
        'source_type': 'light_novel',
        'source_title': '異世界転生騒動記',
        'source_volume_from': 1,
        'source_volume_to': 4,
        'source_volume_note': '2027年冬。スタジオディーン。',
        'read_order': 'ラノベ1巻から',
        'amazon_search': '異世界転生騒動記 ラノベ',
        'tags': ['異世界', '転生', '戦記'],
        'watchers_count': 7700,
        'share_slug': 'isekai-soudouki',
        'main_comment': '戦国武将とオタク高校生の魂が一人の少年に入り、異世界で成り上がる戦記もの。2027年冬。一人の体に複数人格、という設定で内政と戦争が同時に進む。転生ものでも戦記寄りの作品が欲しい人に。初アニメ化なので1巻からがおすすめです。',
    },
]

NOTE_UPDATES = {
    'kusuriya-3': '第1・2期は第1〜9巻相当。3期は第10巻前後から。2026年10月2日日本テレビ系で第1クール開始。',
    'tokyo-revengers-santen': '三天戦争編。漫画は全31巻で完結済み。2026年10月2日 MBS/TBS系。',
    'ao-no-hako-2': '1期は第1〜7巻相当。2期は8巻以降。2026年10月4日 TBS系。',
    'aoashi-2': '1期は青年編中心。2期はプロ編へ。2026年10月4日 NHK Eテレ。',
    'ranma-1-2-3': '2026年10月2日 日本テレビほか。',
    'rayearth-2026': '2026年10月7日 テレビ朝日系。',
    'nia-liston': '2026年10月6日 TOKYO MXほか。HJ文庫。',
    'kanata-kara': '2026年10月2日 TOKYO MXほか。連載当時の名作の新アニメ。',
    'kizu-darake-seijo-2': '2026年10月1日 tvk・CBCほか。',
    'tougen-anki-2': '日光・華厳の滝編。2026年10月 日本テレビ系。',
    'koori-no-jouheki-2': '1期は第1〜3巻相当。2026年10月1日 TBS系放送開始。',
    'akane-banashi-2': '1期は第1〜4巻相当。第2期は前座修業篇。2027年1月 テレビ朝日系 IMAnimation。',
    'the-one-piece': 'Netflix版リメイク。2027年2月配信開始予定。',
    'hirayasumi': '2027年1月 NHK総合。連載中。',
    'sakamoto-days-2': '1期は第1〜7巻相当。2027年1月放送。',
    'shangri-la-3': '1・2期は第1〜12巻相当。3期は13巻以降。2027年1月 MBS/TBS系。',
    'golden-kamuy-final': '最終章「暴走列車編」。公式表記は今冬。漫画は完結済み。',
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

    notes = 0
    for w in works:
        slug = w.get('share_slug')
        if slug in NOTE_UPDATES:
            if w.get('source_volume_note') != NOTE_UPDATES[slug]:
                w['source_volume_note'] = NOTE_UPDATES[slug]
                notes += 1

    works.sort(key=lambda w: (-(w.get('watchers_count') or 0), w.get('season', ''), w.get('title', '')))
    save_works(works)

    autumn = sum(1 for w in works if w.get('season') == '2026-autumn')
    winter = sum(1 for w in works if w.get('season') == '2027-winter')
    print(f'added autumn={added_autumn} winter={added_winter} notes={notes}')
    print(f'totals autumn={autumn} winter={winter} all={len(works)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

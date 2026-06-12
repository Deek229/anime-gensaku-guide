"""11 アニメ原作ガイド 設定"""
import os
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / 'data'
WORKS_FILE = DATA_DIR / 'works.json'
CACHE_DIR = DATA_DIR / 'cache'

APP_TITLE = 'アニメ原作ガイド'
APP_TAGLINE = '今期アニメの原作ラノベ・漫画をチェックして、買う順まで一発でわかる'
APP_VERSION = '0.2.0'
DEFAULT_PORT = 8052
SITE_URL = os.environ.get('SITE_URL', os.environ.get('RENDER_EXTERNAL_URL', 'http://127.0.0.1:8052')).rstrip('/')

# Amazonアソシエイト（未設定時は検索リンクのみ）
AMAZON_ASSOCIATE_TAG = os.environ.get('AMAZON_ASSOCIATE_TAG', '').strip()

# Annict API（任意: https://annict.com/settings/apps）
ANNICT_ACCESS_TOKEN = os.environ.get('ANNICT_ACCESS_TOKEN', '').strip()
ANNICT_API_URL = 'https://api.annict.com/v1/works'

DEFAULT_SEASON = '2026-summer'

SEASON_LABELS = {
    '2026-summer': '2026年夏アニメ',
    '2026-spring': '2026年春アニメ',
    '2026-autumn': '2026年秋アニメ',
    '2026-winter': '2026年冬アニメ',
}

SOURCE_TYPE_LABELS = {
    'light_novel': 'ラノベ',
    'manga': '漫画',
    'web_novel': 'Web小説',
    'novel': '小説',
    'game': 'ゲーム',
    'original': 'オリジナル',
    'other': 'その他',
}

STATUS_LABELS = {
    'upcoming': '放送予定',
    'airing': '放送中',
    'finished': '放送終了',
}

# なろうAPI（サブ機能）
RANK_API_URL = 'https://api.syosetu.com/rank/rankget/'
NOVEL_API_URL = 'https://api.syosetu.com/novelapi/api/'
NOVEL_BATCH_SIZE = 40
NOVEL_FIELDS = 't-n-w-s-e-i-bg-g-k-gl-ga'
RANK_CACHE_TTL_SEC = 60 * 60

BIGGENRE_LABELS = {
    1: 'ファンタジー', 2: '恋愛', 3: 'ラブコメ', 4: '純文学',
    5: 'ホラー', 6: 'ミステリー', 7: 'SF', 8: 'ポエム',
    9: '童話', 10: 'エッセイ', 11: 'リプレイ', 12: 'その他', 99: 'ノンジャンル',
}
END_LABELS = {0: '連載中', 1: '完結'}

"""Amazonアソシエイトリンク生成"""
from __future__ import annotations

from urllib.parse import quote_plus

from config import AMAZON_ASSOCIATE_TAG


def amazon_product_url(asin: str) -> str:
    asin = (asin or '').strip()
    if not asin:
        return ''
    url = f'https://www.amazon.co.jp/dp/{asin}'
    if AMAZON_ASSOCIATE_TAG:
        url += f'?tag={AMAZON_ASSOCIATE_TAG}'
    return url


def amazon_search_url(query: str) -> str:
    q = quote_plus((query or '').strip())
    if not q:
        return ''
    url = f'https://www.amazon.co.jp/s?k={q}'
    if AMAZON_ASSOCIATE_TAG:
        url += f'&tag={AMAZON_ASSOCIATE_TAG}'
    return url


def amazon_cover_url(asin: str, width: int = 250) -> str:
    """Amazon商品画像URL（書籍のISBN-10/ASIN）"""
    asin = (asin or '').strip()
    if not asin:
        return ''
    return f'https://images-na.ssl-images-amazon.com/images/P/{asin}.09._SL{width}_.jpg'


def buy_url(work: dict) -> tuple[str, str]:
    """(url, label)"""
    asin = work.get('amazon_asin', '')
    if asin:
        return amazon_product_url(asin), 'Amazonで見る'
    query = work.get('amazon_search') or work.get('source_title') or work.get('title', '')
    return amazon_search_url(query), 'Amazonで検索'

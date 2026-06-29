"""原作巻数のフォーマット・解決"""
from __future__ import annotations

from typing import Any

from config import SOURCE_TYPE_LABELS


def _type_label(work: dict[str, Any]) -> str:
    st = work.get('source_type', 'other')
    return SOURCE_TYPE_LABELS.get(st, st)


def has_volume_fields(work: dict[str, Any]) -> bool:
    return work.get('source_volume_from') is not None or work.get('source_volume_to') is not None


def format_volume_range(work: dict[str, Any]) -> str:
    st = work.get('source_type', 'other')
    if st == 'original':
        return 'オリジナル作品（原作小説・漫画なし）'

    vf = work.get('source_volume_from')
    vt = work.get('source_volume_to')

    if vf is None and vt is None:
        legacy = (work.get('volumes_anime') or '').strip()
        return legacy or '放送に合わせて更新予定です。'

    label = _type_label(work)
    if vf is not None and vt is not None:
        if vf == vt:
            core = f'第{vf}巻（{label}）'
        else:
            core = f'第{vf}巻〜第{vt}巻（{label}）'
    elif vf is not None:
        core = f'第{vf}巻から（{label}）'
    else:
        core = f'第{vt}巻まで（{label}）'

    note = (work.get('source_volume_note') or '').strip()
    if note:
        core = f'{core}。{note}'

    if work.get('source_volume_approximate'):
        core = f'{core} ※放送進行で更新'

    return core


def format_volume_short(work: dict[str, Any]) -> str:
    """Xシェア用の短い巻数表記"""
    st = work.get('source_type', 'other')
    if st == 'original':
        return 'オリジナル'

    vf = work.get('source_volume_from')
    vt = work.get('source_volume_to')
    if vf is None and vt is None:
        return (work.get('volumes_anime') or '')[:40]

    if vf is not None and vt is not None:
        if vf == vt:
            return f'第{vf}巻'
        return f'第{vf}〜{vt}巻'
    if vf is not None:
        return f'第{vf}巻〜'
    return f'第{vt}巻まで'


def enrich_volume_fields(work: dict[str, Any]) -> dict[str, Any]:
    """構造化巻数フィールドから表示用テキストを生成"""
    if has_volume_fields(work) or work.get('source_type') == 'original':
        volumes_anime = format_volume_range(work)
    else:
        volumes_anime = work.get('volumes_anime') or format_volume_range(work)
    return {
        **work,
        'volumes_anime': volumes_anime,
        'volume_short': format_volume_short(work),
        'has_volume_data': has_volume_fields(work),
    }

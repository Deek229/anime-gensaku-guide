# 11 アニメ原作ガイド

今期アニメの**原作ラノベ・漫画**と**購入リンク**をまとめる個人用Webサイトです。  
収益化は Amazonアソシエイトを想定（タグ設定は任意）。

## 機能

- **今期アニメ一覧**（2026夏など）— 原作タイプ・検索で絞り込み
- **作品詳細ページ** — アニメ化範囲・読む順・Amazonリンク（SEO向けHTML）
- **なろうランキング** — サブ機能（`/rankings`）

## セットアップ

```bash
cd 11_名称未定Web作り
pip install -r requirements.txt
copy .env.example .env    # Amazonタグ等を設定
python tools/seed_works.py
python -m uvicorn app:app --reload --port 8052
```

http://127.0.0.1:8052

## 無料でインターネット公開

詳細は **[公開手順.md](公開手順.md)**（Render 無料プラン）。

1. `GitHubに上げる.bat` をダブルクリック
2. [Render](https://render.com) で Web Service を作成

公開URLを Amazonアソシエイトの「ウェブサイト」欄に登録します。

## データの編集

`data/works.json` を直接編集するか、`tools/seed_works.py` を参考に項目を追加します。

| 項目 | 説明 |
|------|------|
| `source_type` | light_novel / manga / web_novel / original |
| `source_volume_from` | アニメ化範囲の開始巻（int、未設定可） |
| `source_volume_to` | アニメ化範囲の終了巻（int、未設定可） |
| `source_volume_approximate` | `true` なら「※放送進行で更新」を付与 |
| `source_volume_note` | 補足（前期の対応巻など） |
| `read_order` | 読む・買う順のメモ |
| `amazon_asin` | あれば直リンク |
| `amazon_search` | ASIN未設定時の検索語 |
| `isbn` | 表紙取得用 ISBN-13（OpenBD） |
| `cover_image_url` | 表紙画像URL（`tools/fetch_covers.py` で自動設定可） |
| `share_slug` | Xシェア用のASCII専用URL（`/works/{share_slug}`）。日本語 `id` は canonical のまま |

`volumes_anime` は廃止し、上記フィールドから FAQ・一覧・Xシェア文を自動生成します。

## 表紙画像の取得

原作の表紙サムネイルは `tools/fetch_covers.py` で一括設定できます。

```bash
python tools/fetch_covers.py
```

1. 各作品の `isbn` / `amazon_asin` から [OpenBD API](https://api.openbd.jp/v1/get?isbn=...) を試行
2. 見つからなければ Amazon 商品画像 URL を使用
3. オリジナルアニメなど取得不可の場合は `/static/cover-placeholder.svg`

Render デプロイ時も `render.yaml` の build で自動実行されます。

## X（Twitter）シェアについて

作品URLの `id` には日本語が含まれることがあります。Xはシェア時にURL内の非ASCII文字でリンクが切れるため、**シェアボタンは ASCII の `share_slug` URL** を使います（例: `/works/re-zero-4th-dakkan`）。ページの canonical は従来どおり日本語 `id` です。

## Annict同期（任意）

`.env` に `ANNICT_ACCESS_TOKEN` を設定後:

```bash
python tools/sync_annict.py 2026-summer
```

人気順で作品リストを取り込み、手動データはマージされます。

## 毎朝のタスクメール

`PCリマインダー登録.bat` で PC のタスクスケジューラに登録。GitHub Actions は手動のみ。

## 注意

- あらすじの長文転載はしない（SEOは自作の「原作ガイド」文で）
- Amazonリンクにはサイト上でアフィリエイト開示を表示
- なろうランキングは公式API利用

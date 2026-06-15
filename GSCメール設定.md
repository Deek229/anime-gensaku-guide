# GSC リマインダーメール設定（1回だけ）

毎朝 **9:00** に `a_n_k_6@hotmail.com` へ、Google Search Console でやることをメールで送ります。

---

## 手順1: Microsoft アプリパスワードを作る

1. https://account.microsoft.com/security を開く
2. **二段階認証** をオンにする（まだなら）
3. **アプリパスワード** を作成
4. 表示された **16文字のパスワード** をコピー（後で使う）

---

## 手順2: GitHub に秘密情報を登録

1. https://github.com/Deek229/anime-gensaku-guide/settings/secrets/actions を開く
2. **New repository secret** を2つ追加:

| Name | Value |
|------|-------|
| `SMTP_USER` | `a_n_k_6@hotmail.com` |
| `SMTP_PASSWORD` | 手順1のアプリパスワード（スペースなし） |

---

## 手順3: テスト送信

1. https://github.com/Deek229/anime-gensaku-guide/actions を開く
2. 左の **GSC daily email reminder** をクリック
3. **Run workflow** → **Run workflow**
4. 1〜2分後、`a_n_k_6@hotmail.com` にメールが届けば成功

---

## スケジュール

| 項目 | 内容 |
|------|------|
| 送信時刻 | 毎日 **9:00（日本時間）** |
| 送信先 | `a_n_k_6@hotmail.com` |
| 内容 | `site:` 検索・インデックス登録リクエスト・サイト確認 |

---

## 届かないとき

- GitHub Actions のログでエラーを確認
- アプリパスワードが正しいか再確認
- Hotmailの迷惑メールフォルダを確認

---

## PCから手動送信（任意）

`.env` に以下を書いて:

```
SMTP_USER=a_n_k_6@hotmail.com
SMTP_PASSWORD=アプリパスワード
REMINDER_EMAIL_TO=a_n_k_6@hotmail.com
```

```bash
python tools/gsc_reminder.py
```

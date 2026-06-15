# タスク管理メール設定（1回だけ）

毎朝 **9:00** に `a_n_k_6@hotmail.com` へ、今日やることをチェックリスト形式で送信します。

> **HotmailのSMTPはGitHub Actionsから送れません**（Microsoftがクラウドからの基本認証を拒否）。
> 代わりに **Resend**（無料・APIキー方式）を使います。

---

## 手順1: Resend に登録（3分）

1. https://resend.com/signup を開く（GitHubログイン可）
2. ログイン後 **API Keys** → **Create API Key**
3. 名前: `gsc-reminder` → 表示されたキー（`re_...`）をコピー

---

## 手順2: 送信先メールを確認

1. Resend の **Emails** または **Audience** で
2. `a_n_k_6@hotmail.com` を **確認（verify）** する
   - 届いた確認メールのリンクをクリック

※ 無料プランは確認済みアドレスにのみ送信できます。

---

## 手順3: GitHub Secret に登録

https://github.com/Deek229/anime-gensaku-guide/settings/secrets/actions

**New repository secret**:

| Name | Value |
|------|-------|
| `RESEND_API_KEY` | `re_...`（手順1のキー） |

※ 古い `SMTP_USER` / `SMTP_PASSWORD` は不要（残っていても害はありません）

---

## 手順4: テスト送信

1. https://github.com/Deek229/anime-gensaku-guide/actions
2. **Daily task email reminder** → **Run workflow**
3. 緑の ✓ になれば成功
4. Hotmail に **【今日のタスク】** メールが届く

---

## スケジュール

| 項目 | 内容 |
|------|------|
| 送信時刻 | 毎日 **9:00（日本時間）** |
| 送信先 | `a_n_k_6@hotmail.com` |
| 形式 | □ チェックリスト＋【必須】/【できたら】 |

---

## 届かないとき

- Resend で送信先メールが **verified** か確認
- GitHub Actions のログでエラーを確認
- 迷惑メールフォルダを確認

---

## PCから手動送信（任意）

`.env` に:

```
RESEND_API_KEY=re_...
REMINDER_EMAIL_TO=a_n_k_6@hotmail.com
```

```bash
python tools/gsc_reminder.py
```

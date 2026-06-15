# Resend で送信先エラー (403) が出たとき

`onboarding@resend.dev` から送る場合、**Resendに登録したメールアドレスにしか送れません**。

---

## 確認方法

1. https://resend.com にログイン
2. 右上のアカウント → **表示されているメールアドレス** を確認

---

## 対処（どちらか）

### 方法A: GitHub Secret を追加（おすすめ）

https://github.com/Deek229/anime-gensaku-guide/settings/secrets/actions

| Name | Value |
|------|-------|
| `RESEND_TO_EMAIL` | Resendに登録しているメールアドレス |

例: Resendが `githubのメール@...` ならそれを入れる  
例: Resendが `a_n_k_6@hotmail.com` ならそれを入れる

→ **Run workflow** で再テスト

### 方法B: Resend を Hotmail で使う

Resendの登録メールが Hotmail と違う場合:
- Resendを **a_n_k_6@hotmail.com** で再登録する

---

## 補足: PCから送る方法（Hotmail SMTP）

GitHub Actions では Hotmail SMTP は使えませんが、**自分のPCからなら送れます**。

1. `.env` に SMTP_USER / SMTP_PASSWORD を設定
2. `PCリマインダー登録.bat` をダブルクリック
3. 毎朝9時にPCが起動していれば Hotmail 宛に送信

※ PCがスリープ中は送られません

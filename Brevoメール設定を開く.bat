@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo  メール設定（Brevo・Hotmail宛に送れる）
echo ========================================
echo.
echo HotmailのSMTPはMicrosoftで無効のため、
echo 無料の Brevo を使います（5分で設定）。
echo.
start https://www.brevo.com/jp/
start https://app.brevo.com/settings/keys/api
start https://app.brevo.com/senders/list
echo.
echo 【手順】
echo 1. Brevo に無料登録
echo 2. Senders で a_n_k_6@hotmail.com を追加→届いた確認コードを入力
echo 3. API Keys でキーを作成
echo 4. .env に追加:
echo    BREVO_API_KEY=（キー）
echo    BREVO_SENDER_EMAIL=a_n_k_6@hotmail.com
echo    REMINDER_EMAIL_TO=a_n_k_6@hotmail.com
echo 5. メールテスト送信.bat を実行
echo 6. 毎朝9時の自動送信（GitHub）用:
echo    GitHub → Settings → Secrets → Actions
echo    名前 BREVO_API_KEY、値は上と同じキー
echo.
pause

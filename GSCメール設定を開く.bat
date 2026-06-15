@echo off
chcp 65001 >nul
echo ========================================
echo  タスク管理メール設定（Resend）
echo ========================================
echo.
echo HotmailのSMTPはGitHubから送れないため、
echo 無料の Resend API に切り替えます。
echo.
start "" "%~dp0GSCメール設定.md"
start https://resend.com/signup
start https://github.com/Deek229/anime-gensaku-guide/settings/secrets/actions
echo.
echo 1. Resend で API Key を作成
echo 2. a_n_k_6@hotmail.com を Resend で確認(verify)
echo 3. GitHub Secret に RESEND_API_KEY を登録
echo 4. Actions で Run workflow
echo.
pause

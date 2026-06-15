@echo off
chcp 65001 >nul
echo ========================================
echo  GSC リマインダーメール設定
echo ========================================
echo.
echo 1. 設定手順を開きます
echo 2. GitHub Secrets のページを開きます
echo 3. Microsoft セキュリティ設定を開きます
echo.
start "" "%~dp0GSCメール設定.md"
start https://github.com/Deek229/anime-gensaku-guide/settings/secrets/actions
start https://account.microsoft.com/security
echo.
echo GSCメール設定.md の手順どおりに
echo SMTP_USER と SMTP_PASSWORD を GitHub に登録してください。
echo.
echo 登録後、GitHub Actions で「Run workflow」でテストできます。
pause

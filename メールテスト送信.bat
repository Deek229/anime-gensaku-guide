@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo  メールテスト送信（PC / Hotmail）
echo ========================================
echo.
if not exist .env (
  echo .env がありません。作成します...
  copy /Y .env.example .env >nul
  echo.
  echo .env を開いて次を設定してください:
  echo   SMTP_USER=a_n_k_6@hotmail.com
  echo   SMTP_PASSWORD=アプリパスワード16文字
  echo   REMINDER_EMAIL_TO=a_n_k_6@hotmail.com
  echo.
  notepad .env
  pause
  exit /b 1
)
echo 送信中...
python tools\gsc_reminder.py
if errorlevel 1 (
  echo.
  echo 失敗しました。.env の SMTP_PASSWORD を確認してください。
) else (
  echo.
  echo 成功! メールを確認してください。
  echo 毎朝9時に自動送信するには PCリマインダー登録.bat を実行。
)
pause

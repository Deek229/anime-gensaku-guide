@echo off
chcp 65001 >nul
echo PCのタスクスケジューラに毎朝9時のリマインダーを登録します。
echo .env に BREVO_API_KEY が必要です。
echo チェックリストは Googleスプレッドシート連携可（docs\スプレッドシート連携手順.md）
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\register_pc_reminder.ps1"
pause

@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo  メール内容確認（送信なし / dry-run）
echo ========================================
echo.
python tools\gsc_reminder.py --dry-run
echo.
pause

@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  X返信ドラフト作成（ポストを貼る → 返信案）
echo  貼り付けたら空行で Enter
echo.
python tools\x_reply_draft.py
echo.
pause

@echo off

chcp 65001 >nul

cd /d "%~dp0"

echo ========================================

echo  スプレッドシート連携テスト（取得のみ）

echo ========================================

echo.

echo .env に CHECKLIST_SHEET_URL を設定してから実行してください。

echo  ※ このテストは「スプレッドシート → PC」の読み取りのみです。

echo  ※ シートに行を増やすには docs\スプレッドシートに89行を入れる手順.md を参照。

echo.

python tools\gsc_reminder.py --test-sheet

echo.

pause


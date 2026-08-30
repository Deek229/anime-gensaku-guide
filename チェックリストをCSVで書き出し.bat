@echo off

chcp 65001 >nul

cd /d "%~dp0"

echo ========================================

echo  チェックリストCSVを書き出し（89行）

echo ========================================

echo.

python tools\generate_index_checklist.py

echo.

echo 次のファイルを Googleスプレッドシートにインポートしてください:

echo   docs\インデックス登録チェックリスト.csv

echo.

echo 手順: docs\スプレッドシートに89行を入れる手順.md

echo.

pause

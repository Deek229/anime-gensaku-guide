@echo off
chcp 65001 >nul
echo ========================================
echo  GitHub に上げる（公開の準備）
echo ========================================
echo.
echo 1. ブラウザで GitHub 新規リポジトリを開きます
echo    名前: anime-gensaku-guide （Public）
echo.
start https://github.com/new
echo.
echo 2. リポジトリ作成後、表示される URL をコピーして
echo    このウィンドウに貼り付けて Enter
echo    例: https://github.com/あなたの名前/anime-gensaku-guide.git
echo.
set /p REPO_URL="リポジトリURL: "
if "%REPO_URL%"=="" (
  echo URLが空です。終了します。
  pause
  exit /b 1
)

cd /d "%~dp0"
set GIT="C:\Program Files\Git\bin\git.exe"

%GIT% init 2>nul
%GIT% add .
%GIT% -c user.name="anime-gensaku-guide" -c user.email="noreply@users.noreply.github.com" commit -m "Initial deploy: anime gensaku guide"
%GIT% branch -M main
%GIT% remote remove origin 2>nul
%GIT% remote add origin %REPO_URL%
%GIT% push -u origin main

if errorlevel 1 (
  echo.
  echo push に失敗しました。GitHubにログインが必要な場合:
  echo   winget install GitHub.cli
  echo   gh auth login
  echo を実行してから再度お試しください。
) else (
  echo.
  echo 成功! 次は Render で公開:
  start https://dashboard.render.com/
  echo   公開手順.md の「手順2」を参照
)
pause

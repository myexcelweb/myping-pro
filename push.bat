@echo off
:: ─────────────────────────────────────────────────────────────
:: If launched from PowerShell, relaunch in a real cmd.exe window
:: ─────────────────────────────────────────────────────────────
if "%1"=="RELAUNCHED" goto :main
start "MY PING PRO" cmd.exe /k "%~f0" RELAUNCHED
exit /b

:main
title MY PING PRO - AUTO PUSH
color 0A
cd /d %~dp0

echo.
echo ============================================
echo   MY PING PRO - AUTO PUSH
echo ============================================
echo.

:: Initialize git if not already initialized
if not exist ".git" (
    echo [INIT] Initializing Git repository...
    git init
    git branch -M main
    git remote add origin https://github.com/myexcelweb/myping-pro.git
    echo [INIT] Done.
    echo.
)

:: Stash any local changes before pulling
echo [STEP 1] Stashing local changes...
git stash
echo [STEP 1] Done.
echo.

:: Pull latest from remote
echo [STEP 2] Pulling latest from remote...
git pull origin main --rebase
echo [STEP 2] Done.
echo.

:: Restore stashed changes
echo [STEP 3] Restoring local changes...
git stash pop
echo [STEP 3] Done.
echo.

:: Stage all files
echo [STEP 4] Staging all files...
git add .
echo [STEP 4] Done.
echo.

:: Auto commit with date and time
for /f %%i in ('powershell -command "Get-Date -Format \"yyyy-MM-dd HH:mm:ss\""') do set datetime=%%i
echo [STEP 5] Committing: Auto update %datetime%
git commit -m "Auto update %datetime%"
echo [STEP 5] Done.
echo.

:: Push to remote
echo [STEP 6] Pushing to GitHub...
git push origin main
echo [STEP 6] Done.
echo.

echo ============================================
echo   DONE! All changes pushed successfully.
echo ============================================
echo.
pause
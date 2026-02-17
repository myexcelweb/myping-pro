@echo off
title MY PING PRO - AUTO PUSH

cd /d %~dp0

:: Initialize git if not already initialized
if not exist ".git" (
    git init
    git branch -M main
    git remote add origin https://github.com/myexcelweb/myping-pro.git
)

:: Pull remote changes first to avoid conflicts
git pull origin main --rebase

:: Add all files
git add .

:: Auto commit with date & time
for /f %%i in ('powershell -command "Get-Date -Format \"yyyy-MM-dd HH:mm:ss\""') do set datetime=%%i
git commit -m "Auto update %datetime%"

:: Push to remote
git push origin main

exit

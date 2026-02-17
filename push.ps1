# ============================================
#   MY PING PRO - AUTO PUSH
# ============================================

Set-Location $PSScriptRoot

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   MY PING PRO - AUTO PUSH" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Initialize git if needed
if (-not (Test-Path ".git")) {
    Write-Host "[INIT] Initializing Git repository..." -ForegroundColor Yellow
    git init
    git branch -M main
    git remote add origin https://github.com/myexcelweb/myping-pro.git
    Write-Host "[INIT] Done." -ForegroundColor Green
    Write-Host ""
}

# STEP 1 - Stash
Write-Host "[STEP 1] Stashing local changes..." -ForegroundColor Yellow
git stash
Write-Host "[STEP 1] Done." -ForegroundColor Green
Write-Host ""

# STEP 2 - Pull
Write-Host "[STEP 2] Pulling latest from remote..." -ForegroundColor Yellow
git pull origin main --rebase
Write-Host "[STEP 2] Done." -ForegroundColor Green
Write-Host ""

# STEP 3 - Pop stash
Write-Host "[STEP 3] Restoring local changes..." -ForegroundColor Yellow
git stash pop
Write-Host "[STEP 3] Done." -ForegroundColor Green
Write-Host ""

# STEP 4 - Stage
Write-Host "[STEP 4] Staging all files..." -ForegroundColor Yellow
git add .
Write-Host "[STEP 4] Done." -ForegroundColor Green
Write-Host ""

# STEP 5 - Commit
$datetime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "[STEP 5] Committing: Auto update $datetime" -ForegroundColor Yellow
git commit -m "Auto update $datetime"
Write-Host "[STEP 5] Done." -ForegroundColor Green
Write-Host ""

# STEP 6 - Push
Write-Host "[STEP 6] Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
Write-Host "[STEP 6] Done." -ForegroundColor Green
Write-Host ""

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   DONE! All changes pushed successfully." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
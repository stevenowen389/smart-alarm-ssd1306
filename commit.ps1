<# commit_and_bundle_fixed.ps1 - Unstage bundle, commit staged files, and recreate bundle
   Run this from the repo root: .\scripts\commit_and_bundle_fixed.ps1 #>
param(
    [string]$repoRoot = "C:/Users/steve/Documents/GitHub/smart_alarm.worktrees/retrieve-archived-chat",
    [string]$branch = 'ssd1306-updates',
    [string]$bundleName = 'smart_alarm_ssd1306.bundle'
)

Set-Location $repoRoot

Write-Host "Repository root: $repoRoot"

# Ensure git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git not found in PATH"
    exit 1
}

# Unstage and remove bundle from index if present
if (Test-Path "$repoRoot\$bundleName") {
    Write-Host "Removing bundle from index (if staged) and leaving file on disk"
    & git reset HEAD -- $bundleName 2>$null
    & git rm --cached $bundleName 2>$null
}

# Ensure we are on the right branch
$current = (& git rev-parse --abbrev-ref HEAD)
if ($current -ne $branch) {
    Write-Host "Switching to branch $branch (current: $current)"
    & git checkout $branch
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Branch $branch does not exist; creating it"
        & git checkout -b $branch
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create branch $branch"
            exit 1
        }
    }
}

# Commit staged changes
Write-Host "Committing staged changes"
$commitMsg = "Add SSD1306 wrapper and test scripts"
$coauthor = "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
& git commit -m $commitMsg -m $coauthor
if ($LASTEXITCODE -ne 0) {
    Write-Host "git commit returned non-zero (nothing to commit or error)."
} else {
    Write-Host "Commit successful"
}

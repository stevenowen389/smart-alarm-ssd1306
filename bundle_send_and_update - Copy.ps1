# bundle_send_and_update.ps1
# Create a git bundle from branch 'ssd1306-updates', scp it to the Pi, and run an update script there.
# Edit $piUser and $piHost below if needed.

param(
    [switch]$InstallDependencies
)

$ErrorActionPreference = 'Stop'

# Configuration
$localRepo = "C:/Users/steve/Documents/GitHub/smart_alarm.worktrees/retrieve-archived-chat"
$branch = 'ssd1306-updates'
$bundleName = 'smart_alarm_ssd1306.bundle'
$bundlePath = "$localRepo/$bundleName"
$piUser = 'steven'
$piHost = '192.168.1.79'
$piTargetDir = '~/'

if ($InstallDependencies) {
    Write-Host "Dependency install on Pi: enabled"
} else {
    Write-Host "Dependency install on Pi: skipped (use -InstallDependencies to enable)"
}

Write-Host "Using local repo: $localRepo"
if (-not (Test-Path $localRepo)) {
    Write-Error "Local repo path does not exist: $localRepo"
    exit 1
}

Push-Location $localRepo
try {
    # ensure we're in a git repo and branch exists
    $isGit = & git rev-parse --is-inside-work-tree 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Local folder is not a git repository. Create the bundle manually or run this from a git clone."
        exit 1
    }

    # Create bundle (overwrite if exists)
    if (Test-Path $bundlePath) { Remove-Item $bundlePath -Force }
    Write-Host "Creating git bundle for branch $branch -> $bundlePath"
    & git bundle create $bundlePath $branch
    if ($LASTEXITCODE -ne 0) {
        Write-Error "git bundle create failed"
        exit 1
    }

    Write-Host "Transferring bundle to $($piUser)@$($piHost):$piTargetDir/"
    # Use forward-slash style local path to avoid scp parsing C: as remote host
    scp "$bundlePath" "$($piUser)@$($piHost):$piTargetDir/"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "scp failed"
        exit 1
    }

    Write-Host "Testing SSH connectivity to $piHost"
    & ssh "$($piUser)@$($piHost)" "echo 'SSH connection OK on $(hostname)'"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "SSH connectivity test failed"
        exit 1
    }

    Write-Host "Running remote update script on $piHost"

    $remoteScript = @'
#!/bin/bash
set -euo pipefail
trap 'echo "Remote update failed at line $LINENO"; exit 1' ERR
cd "$HOME"
mkdir -p "$HOME/smart_alarm"
if [ ! -d "$HOME/smart_alarm/.git" ]; then
    git -C "$HOME/smart_alarm" init
    echo "Initialized new repo at $HOME/smart_alarm"
fi
echo "[1/5] Preparing repo directory"
echo "[2/5] Fetching from bundle"
git -C "$HOME/smart_alarm" fetch "$HOME/smart_alarm_ssd1306.bundle" ssd1306-updates
echo "[3/5] Checking out branch"
# Discard local tracked/untracked changes before checkout so log files
# or other local edits do not block branch updates.
git -C "$HOME/smart_alarm" reset --hard
git -C "$HOME/smart_alarm" clean -fd
git -C "$HOME/smart_alarm" checkout -B ssd1306-updates -f FETCH_HEAD
git -C "$HOME/smart_alarm" reset --hard FETCH_HEAD
echo "Checked out ssd1306-updates at $HOME/smart_alarm"
git -C "$HOME/smart_alarm" --no-pager log -1 --oneline
grep -n "decimal_x\|character_spacing - 5" "$HOME/smart_alarm/smart_alarm/modules/display_class.py" || true

echo "[4/5] Cleaning uploaded bundle"
rm -f "$HOME/smart_alarm_ssd1306.bundle"

echo "[5/5] Optional dependency installation"
if [ "${INSTALL_DEPS:-0}" = "1" ]; then
    echo "Ensuring virtualenv and dependencies are installed/up to date..."
    sed -i 's/\r$//' "$HOME/smart_alarm/scripts/install_dependencies.sh"
    bash -n "$HOME/smart_alarm/scripts/install_dependencies.sh"
    bash "$HOME/smart_alarm/scripts/install_dependencies.sh" "$HOME/smart_alarm"
    echo "Remote update complete; dependencies are installed and up to date"
else
    echo "Remote update complete; dependency install was skipped"
fi
'@

    # Remove Windows CRs from the here-string before piping so remote bash isn't given CRLFs
    $remoteScriptNoCR = $remoteScript -replace "`r", ""
    $installDepsFlag = if ($InstallDependencies) { '1' } else { '0' }
    $remoteScriptNoCR | ssh "$($piUser)@$($piHost)" "tr -d '\r' | INSTALL_DEPS=$installDepsFlag bash -s"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Remote update failed"
        exit 1
    }

    Write-Host "Bundle transferred and remote update finished successfully."
} finally {
    Pop-Location
}

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

# Bundles created with `git bundle create <file> <branch>` do not record a HEAD,
# so `git clone` alone may leave the working tree empty on a brand-new install.
# Always init (if needed) then fetch + checkout explicitly so files are present either way.
echo "[1/5] Preparing repo directory"
mkdir -p "$HOME/smart_alarm"
if [ ! -d "$HOME/smart_alarm/.git" ]; then
    git -C "$HOME/smart_alarm" init
    echo "Initialized new repo at $HOME/smart_alarm"
fi

echo "[2/5] Fetching from bundle"
git -C "$HOME/smart_alarm" fetch "$HOME/smart_alarm_ssd1306.bundle" ssd1306-updates

echo "[3/5] Checking out branch"
# Preserve runtime settings before the forced checkout replaces tracked files.
if [ -f "$HOME/smart_alarm/smart_alarm/data.xml" ]; then
    cp "$HOME/smart_alarm/smart_alarm/data.xml" "$HOME/.smart_alarm-data.xml"
fi
# Discard local tracked/untracked changes before checkout so log files
# or other local edits do not block branch updates.
git -C "$HOME/smart_alarm" reset --hard
git -C "$HOME/smart_alarm" clean -fd -e wheelhouse/ -e wheelhouse/**
git -C "$HOME/smart_alarm" checkout -B ssd1306-updates -f FETCH_HEAD
git -C "$HOME/smart_alarm" reset --hard FETCH_HEAD
if [ -f "$HOME/.smart_alarm-data.xml" ]; then
    cp "$HOME/.smart_alarm-data.xml" "$HOME/smart_alarm/smart_alarm/data.xml"
    rm -f "$HOME/.smart_alarm-data.xml"
fi

echo "[4/5] Cleaning uploaded bundle"
rm -f "$HOME/smart_alarm_ssd1306.bundle"

echo "[5/5] Optional dependency installation"
sed -i 's/\r$//' "$HOME/smart_alarm/scripts/install_dependencies.sh" "$HOME/smart_alarm/scripts/install_systemd_unit.sh"
bash -n "$HOME/smart_alarm/scripts/install_systemd_unit.sh"
if [ "${INSTALL_DEPS:-0}" = "1" ]; then
    echo "Ensuring virtualenv and dependencies are installed/up to date..."
    bash -n "$HOME/smart_alarm/scripts/install_dependencies.sh"
    bash "$HOME/smart_alarm/scripts/install_dependencies.sh" "$HOME/smart_alarm"
    echo "Remote update complete; dependencies are installed and up to date"
else
    echo "Remote update complete; dependency install was skipped"
fi

echo "[6/6] Setting file permissions for web server"
chmod 666 "$HOME/smart_alarm/smart_alarm/data.xml"
# 777: www-data (Apache) is not in the file owner's group, so it needs "other" write access
chmod 777 "$HOME/smart_alarm/smart_alarm/music/"
echo "File permissions updated for Apache web server access"
'@

    # Remove Windows CRs from the here-string before piping so remote bash isn't given CRLFs
    $remoteScriptNoCR = $remoteScript -replace "`r", ""
    $installDepsFlag = if ($InstallDependencies) { '1' } else { '0' }
    if ($InstallDependencies) {
        ssh -tt "$($piUser)@$($piHost)" "sudo -v"
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Sudo authentication failed"
            exit 1
        }
    }
    $remoteScriptNoCR | ssh "$($piUser)@$($piHost)" "tr -d '\r' | INSTALL_DEPS=$installDepsFlag bash -s"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Remote update failed"
        exit 1
    }

    Write-Host "Bundle transferred and remote update finished successfully."
} finally {
    Pop-Location
}

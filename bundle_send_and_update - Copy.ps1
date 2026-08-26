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

    Write-Host "Running remote update script on $piHost"

    $remoteScript = @'
#!/bin/bash
set -e
cd "$HOME"
mkdir -p "$HOME/smart_alarm"
if [ ! -d "$HOME/smart_alarm/.git" ]; then
    git -C "$HOME/smart_alarm" init
    echo "Initialized new repo at $HOME/smart_alarm"
fi
git -C "$HOME/smart_alarm" fetch "$HOME/smart_alarm_ssd1306.bundle" ssd1306-updates
git -C "$HOME/smart_alarm" checkout -B ssd1306-updates FETCH_HEAD
git -C "$HOME/smart_alarm" reset --hard FETCH_HEAD
git -C "$HOME/smart_alarm" clean -fd
echo "Checked out ssd1306-updates at $HOME/smart_alarm"
git -C "$HOME/smart_alarm" --no-pager log -1 --oneline
grep -n "decimal_x\|character_spacing - 5" "$HOME/smart_alarm/smart_alarm/modules/display_class.py" || true

rm -f "$HOME/smart_alarm_ssd1306.bundle"

if [ "${INSTALL_DEPS:-0}" = "1" ]; then
    echo "Ensuring virtualenv and dependencies are installed/up to date..."
    bash "$HOME/smart_alarm/scripts/install_dependencies.sh" "$HOME/smart_alarm"
    echo "Remote update complete; dependencies are installed and up to date"
else
    echo "Remote update complete; dependency install was skipped"
fi

if command -v systemctl >/dev/null 2>&1; then
    if systemctl list-unit-files | grep -q '^smart_alarm\.service'; then
        echo "Restarting smart_alarm.service"
        sudo systemctl restart smart_alarm.service
        sudo systemctl --no-pager --full status smart_alarm.service | sed -n '1,20p'
    else
        echo "smart_alarm.service not found; skipping service restart"
    fi
fi
'@

    # Remove Windows CRs from the here-string before piping so remote bash isn't given CRLFs
    $remoteScriptNoCR = $remoteScript -replace "`r", ""
    $installDepsFlag = if ($InstallDependencies) { '1' } else { '0' }
    $remoteScriptNoCR | ssh "$($piUser)@$($piHost)" "INSTALL_DEPS=$installDepsFlag bash -s"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Remote update failed"
        exit 1
    }

    Write-Host "Bundle transferred and remote update finished successfully."
} finally {
    Pop-Location
}

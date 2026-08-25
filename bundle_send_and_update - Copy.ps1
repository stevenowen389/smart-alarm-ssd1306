# bundle_send_and_update.ps1
# Create a git bundle from branch 'ssd1306-updates', scp it to the Pi, and run an update script there.
# Edit $piUser and $piHost below if needed.

$ErrorActionPreference = 'Stop'

# Configuration
$localRepo = "C:/Users/steve/Documents/GitHub/smart_alarm.worktrees/retrieve-archived-chat"
$branch = 'ssd1306-updates'
$bundleName = 'smart_alarm_ssd1306.bundle'
$bundlePath = "$localRepo/$bundleName"
$piUser = 'steven'
$piHost = '192.168.1.79'
$piTargetDir = '~/'

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
if [ -d "$HOME/smart_alarm/.git" ]; then
    git -C "$HOME/smart_alarm" fetch "$HOME/smart_alarm_ssd1306.bundle" ssd1306-updates
    git -C "$HOME/smart_alarm" checkout -B ssd1306-updates FETCH_HEAD
    echo "Updated existing checkout at $HOME/smart_alarm"
elif git clone smart_alarm_ssd1306.bundle smart_alarm; then
    echo "Cloned bundle into $HOME/smart_alarm"
else
    echo "Git clone from bundle failed"
    exit 1
fi

rm -f "$HOME/smart_alarm_ssd1306.bundle"
echo "Remote update complete; existing virtualenv and dependencies were preserved"
'@

    # Remove Windows CRs from the here-string before piping so remote bash isn't given CRLFs
    $remoteScriptNoCR = $remoteScript -replace "`r", ""
    $remoteScriptNoCR | ssh "$($piUser)@$($piHost)" 'bash -s'
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Remote update failed"
        exit 1
    }

    Write-Host "Bundle transferred and remote update finished successfully."
} finally {
    Pop-Location
}

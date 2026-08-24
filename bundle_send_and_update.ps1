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
rm -rf smart_alarm
# Clone from the bundle file (assumes bundle contains the branch refs)
if git clone smart_alarm_ssd1306.bundle smart_alarm; then
    echo "Cloned bundle into $HOME/smart_alarm"
  cd smart_alarm
  # Try to check out the branch; if not present, create a local branch
  git checkout ssd1306-updates || git checkout -b ssd1306-updates
else
  echo "git clone from bundle failed; attempting to init and fetch"
  rm -rf smart_alarm
  mkdir -p smart_alarm && cd smart_alarm
  git init
  git remote add origin /tmp/smart_alarm_ssd1306.bundle || true
  git fetch origin
  git checkout -b ssd1306-updates origin/ssd1306-updates || true
  cd ..
fi

# Prepare the venv and install all system and Python dependencies from the repo
cd "$HOME/smart_alarm" || exit 1
bash scripts/install_dependencies.sh "$HOME/smart_alarm"

echo "Remote update complete"
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

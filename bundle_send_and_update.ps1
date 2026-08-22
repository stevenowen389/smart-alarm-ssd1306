$branch = "ssd1306-updates"
$bundleName = "smart_alarm_ssd1306.bundle"
$worktreeDir = "C:\Users\steve\Documents\GitHub\smart_alarm.worktrees\retrieve-archived-chat"
$piUser = "steven"
$piHost = "192.168.1.42"
$piTarget = "/tmp/$bundleName"

Set-Location $worktreeDir

Write-Host "Checking out branch: $branch"
git checkout $branch

Write-Host "Staging and committing changes if any exist"
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Update display to SSD1306"
} else {
    Write-Host "No changes to commit."
}

Write-Host "Creating bundle from named branch"
git bundle create $bundleName $branch

Write-Host "Copying bundle to the Pi"
$localBundle = Join-Path $worktreeDir $bundleName
$remote = "${piUser}@${piHost}:${piTarget}"
scp "$localBundle" $remote

Write-Host "Connecting to the Pi and updating the repo"
ssh "$piUser@$piHost" @"
set -e
rm -rf /home/steven/smart_alarm
cd /home/steven
git clone /tmp/$bundleName smart_alarm
cd /home/steven/smart_alarm
git checkout $branch
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install Adafruit-SSD1306 pillow
python -m py_compile smart_alarm/modules/display_class.py playground/display_time.py playground/scroll_text.py

echo "Update complete. Repo is at /home/steven/smart_alarm"
"@

Write-Host "All done."

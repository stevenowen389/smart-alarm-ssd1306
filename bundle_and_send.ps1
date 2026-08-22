$branch = "ssd1306-updates"
$bundleName = "smart_alarm_ssd1306.bundle"
$worktreeDir = "C:\Users\steve\Documents\GitHub\smart_alarm.worktrees\retrieve-archived-chat"
$piUser = "steven"
$piHost = "192.168.1.79"
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
scp "$localBundle" "$piUser@$piHost:$piTarget"

Write-Host "Done. Bundle sent to $piUser@$piHost:$piTarget"

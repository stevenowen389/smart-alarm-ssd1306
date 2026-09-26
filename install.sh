#!/bin/bash
# install.sh
# Install or update smart_alarm from an existing clone on the Raspberry Pi.
# Equivalent to the remote-update portion of bundle_send_and_update.sh, but pulls
# from the git remote instead of receiving a bundle over scp/ssh.
# Usage: ./install.sh

set -euo pipefail
trap 'echo "Install/update failed at line $LINENO"; exit 1' ERR

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_USER="${SUDO_USER:-$(id -un)}"
BRANCH='smart-alarm-ssd1306'
REMOTE='origin'

if [ "$#" -ne 0 ]; then
  echo "Usage: $0" >&2
  exit 1
fi

cd "$REPO_DIR"

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "Not a git repository: $REPO_DIR" >&2
  exit 1
fi

echo "[1/5] Fetching latest changes from $REMOTE"
git fetch "$REMOTE" "$BRANCH"

echo "[2/5] Checking out branch (preserving local data.xml)"
if [ -f "$REPO_DIR/smart_alarm/data.xml" ]; then
  cp "$REPO_DIR/smart_alarm/data.xml" "$HOME/.smart_alarm-data.xml"
fi
git reset --hard
git clean -fd -e wheelhouse/ -e wheelhouse/**
git checkout -B "$BRANCH" -f "$REMOTE/$BRANCH"
git reset --hard "$REMOTE/$BRANCH"
if [ -f "$HOME/.smart_alarm-data.xml" ]; then
  cp "$HOME/.smart_alarm-data.xml" "$REPO_DIR/smart_alarm/data.xml"
  rm -f "$HOME/.smart_alarm-data.xml"
fi
echo "Checked out $BRANCH at $REPO_DIR"
git --no-pager log -1 --oneline

echo "[3/5] Installing system and Python dependencies"
bash "$REPO_DIR/install_dependencies.sh" "$REPO_DIR"
echo "Dependencies are installed and up to date"

echo "[4/5] Installing and starting systemd service"
bash "$REPO_DIR/install_systemd_unit.sh" "$REPO_DIR" "$RUN_USER"

echo "[5/5] Setting file permissions for web server"
chmod 666 "$REPO_DIR/smart_alarm/data.xml"
# 777: www-data (Apache) is not in the file owner's group, so it needs "other" write access
chmod 777 "$REPO_DIR/smart_alarm/music/"

echo "Local update complete."

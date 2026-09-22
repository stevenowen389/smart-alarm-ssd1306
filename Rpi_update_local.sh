#!/bin/bash
# update_local.sh
# Update an existing smart_alarm clone in place (run directly on the Raspberry Pi).
# Equivalent to the remote-update portion of bundle_send_and_update.sh, but pulls
# from the git remote instead of receiving a bundle over scp/ssh.
# Usage: ./update_local.sh [--install-dependencies]

set -euo pipefail
trap 'echo "Update failed at line $LINENO"; exit 1' ERR

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH='smart-alarm-ssd1306'
REMOTE='origin'

INSTALL_DEPENDENCIES=0
for arg in "$@"; do
  case "$arg" in
    --install-dependencies)
      INSTALL_DEPENDENCIES=1
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      echo "Usage: $0 [--install-dependencies]" >&2
      exit 1
      ;;
  esac
done

cd "$REPO_DIR"

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "Not a git repository: $REPO_DIR" >&2
  exit 1
fi

echo "[1/4] Fetching latest changes from $REMOTE"
git fetch "$REMOTE" "$BRANCH"

echo "[2/4] Checking out branch (preserving local data.xml)"
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

echo "[3/4] Optional dependency installation"
if [ "$INSTALL_DEPENDENCIES" -eq 1 ]; then
  echo "Ensuring virtualenv and dependencies are installed/up to date..."
  bash "$REPO_DIR/install_dependencies.sh" "$REPO_DIR"
  echo "Dependencies are installed and up to date"
else
  echo "Dependency install skipped (use --install-dependencies to enable)"
fi

echo "[4/4] Setting file permissions for web server"
chmod 666 "$REPO_DIR/smart_alarm/data.xml"
# 777: www-data (Apache) is not in the file owner's group, so it needs "other" write access
chmod 777 "$REPO_DIR/smart_alarm/music/"

echo "Local update complete."

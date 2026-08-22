#!/usr/bin/env bash
set -euo pipefail

BRANCH="ssd1306-updates"
BUNDLE_NAME="smart_alarm_ssd1306.bundle"
PI_HOME="/home/steven"
REPO_PATH="${PI_HOME}/smart_alarm"
BUNDLE_PATH="/tmp/${BUNDLE_NAME}"

if [ ! -f "$BUNDLE_PATH" ]; then
  echo "Bundle not found at $BUNDLE_PATH"
  echo "Copy it to the Pi first with scp or rsync."
  exit 1
fi

rm -rf "$REPO_PATH"
cd "$PI_HOME"
git clone "$BUNDLE_PATH" smart_alarm
cd "$REPO_PATH"
git checkout "$BRANCH"

git status
git branch

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install Adafruit-SSD1306 pillow
python -m py_compile smart_alarm/modules/display_class.py playground/display_time.py playground/scroll_text.py

echo "Pi update complete. Repo is at $REPO_PATH"

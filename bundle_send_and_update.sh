#!/usr/bin/env bash
set -euo pipefail

BRANCH="ssd1306-updates"
BUNDLE_NAME="smart_alarm_ssd1306.bundle"
WORKTREE_DIR="/home/steven/src/smart_alarm"  # Update this to your local repo path on the PC if needed
PI_USER="steven"
PI_HOST="192.168.1.42"
PI_BUNDLE_PATH="/tmp/${BUNDLE_NAME}"

cd "$WORKTREE_DIR"

git checkout "$BRANCH"
git add -A
git diff --cached --quiet || git commit -m "Update display to SSD1306"
git bundle create "$BUNDLE_NAME" "$BRANCH"

scp "$WORKTREE_DIR/$BUNDLE_NAME" "${PI_USER}@${PI_HOST}:${PI_BUNDLE_PATH}"

ssh "${PI_USER}@${PI_HOST}" <<EOF
set -e
rm -rf /home/steven/smart_alarm
cd /home/steven
git clone /tmp/$BUNDLE_NAME smart_alarm
cd /home/steven/smart_alarm
git checkout $BRANCH
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install Adafruit-SSD1306 pillow
python -m py_compile smart_alarm/modules/display_class.py playground/display_time.py playground/scroll_text.py
echo "Update complete. Repo is at /home/steven/smart_alarm"
EOF

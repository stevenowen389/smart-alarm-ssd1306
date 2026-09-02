#!/bin/bash
# bundle_send_and_update.sh
# Create a git bundle from branch 'ssd1306-updates', scp it to the Pi, and run an update script there.
# Usage: ./bundle_send_and_update.sh [--install-dependencies]

set -euo pipefail

# Configuration
LOCAL_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH='ssd1306-updates'
BUNDLE_NAME='smart_alarm_ssd1306.bundle'
BUNDLE_PATH="$LOCAL_REPO/$BUNDLE_NAME"
PI_USER='steven'
PI_HOST='192.168.1.79'
PI_TARGET_DIR='~/'

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

if [ "$INSTALL_DEPENDENCIES" -eq 1 ]; then
  echo "Dependency install on Pi: enabled"
else
  echo "Dependency install on Pi: skipped (use --install-dependencies to enable)"
fi

echo "Using local repo: $LOCAL_REPO"
if [ ! -d "$LOCAL_REPO" ]; then
  echo "Local repo path does not exist: $LOCAL_REPO" >&2
  exit 1
fi

cd "$LOCAL_REPO"

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "Local folder is not a git repository. Create the bundle manually or run this from a git clone." >&2
  exit 1
fi

# Create bundle (overwrite if exists)
[ -f "$BUNDLE_PATH" ] && rm -f "$BUNDLE_PATH"
echo "Creating git bundle for branch $BRANCH -> $BUNDLE_PATH"
git bundle create "$BUNDLE_PATH" "$BRANCH"

echo "Transferring bundle to $PI_USER@$PI_HOST:$PI_TARGET_DIR/"
scp "$BUNDLE_PATH" "$PI_USER@$PI_HOST:$PI_TARGET_DIR/"

echo "Testing SSH connectivity to $PI_HOST"
ssh "$PI_USER@$PI_HOST" "echo 'SSH connection OK on \$(hostname)'"

echo "Running remote update script on $PI_HOST"

read -r -d '' REMOTE_SCRIPT << 'EOF' || true
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
git -C "$HOME/smart_alarm" clean -fd
git -C "$HOME/smart_alarm" checkout -B ssd1306-updates -f FETCH_HEAD
git -C "$HOME/smart_alarm" reset --hard FETCH_HEAD
if [ -f "$HOME/.smart_alarm-data.xml" ]; then
  cp "$HOME/.smart_alarm-data.xml" "$HOME/smart_alarm/smart_alarm/data.xml"
  rm -f "$HOME/.smart_alarm-data.xml"
fi
echo "Checked out ssd1306-updates at $HOME/smart_alarm"
git -C "$HOME/smart_alarm" --no-pager log -1 --oneline
grep -n "decimal_x\|character_spacing - 5" "$HOME/smart_alarm/smart_alarm/modules/display_class.py" || true

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
sudo chmod 666 "$HOME/smart_alarm/smart_alarm/data.xml"
# 777: www-data (Apache) is not in the file owner's group, so it needs "other" write access
sudo chmod 777 "$HOME/smart_alarm/smart_alarm/music/"
echo "File permissions updated for Apache web server access"
EOF

echo "$REMOTE_SCRIPT" | ssh "$PI_USER@$PI_HOST" "INSTALL_DEPS=$INSTALL_DEPENDENCIES bash -s"

echo "Bundle transferred and remote update finished successfully."

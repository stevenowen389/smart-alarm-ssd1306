#!/bin/bash
# Install Raspberry Pi system and Python dependencies for smart_alarm.
# Usage: bash scripts/install_dependencies.sh [project_root]

set -e

PROJECT_ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
VENV="$PROJECT_ROOT/.venv"

if [ "$(uname -s)" != "Linux" ]; then
  echo "This installer is intended for Raspberry Pi OS or another Debian-based Linux system."
  exit 1
fi

if [ "$(id -u)" -eq 0 ]; then
  APT=""
else
  APT="sudo"
fi

echo "Installing system dependencies..."
$APT apt-get update
$APT apt-get install -y python3-venv python3-dev python3-pip i2c-tools libgpiod2 alsa-utils mpc espeak-ng libespeak1

if [ ! -x "$VENV/bin/python" ]; then
  echo "Creating virtual environment at $VENV..."
  python3 -m venv --system-site-packages "$VENV"
fi

echo "Installing Python dependencies..."
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$PROJECT_ROOT/requirements.txt"

echo
echo "Dependencies installed. Run the alarm with:"
echo "  $VENV/bin/python $PROJECT_ROOT/run_smart_alarm.py"
echo
echo "LED support includes the colorschemes package from requirements.txt."
echo "Set APA102_PI_PATH if the legacy APA102_Pi library is outside ~/APA102_Pi."
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
$APT apt-get install -y python3-venv python3-dev python3-pip i2c-tools libgpiod2 alsa-utils mpd mpc espeak-ng libespeak1 apache2 libapache2-mod-wsgi-py3

echo "Configuring apache2 for smart_alarm..."
$APT a2enmod wsgi
$APT cp "$PROJECT_ROOT/misc/apache/envvars" /etc/apache2/envvars
# envvars is sourced as root at apache startup, so $HOME there means /root,
# not this user's home. Override with the actual absolute project paths.
{
  echo "export smart_alarm_path=\"$PROJECT_ROOT/smart_alarm\""
  echo "export smart_alarm_venv=\"$VENV\""
} | $APT tee -a /etc/apache2/envvars > /dev/null
$APT cp "$PROJECT_ROOT/misc/apache/000-default.conf" /etc/apache2/sites-available/000-default.conf
$APT chmod o+w "$PROJECT_ROOT/smart_alarm/data.xml"
# www-data needs execute (traversal) permission on every directory leading to
# the DocumentRoot; a restrictive home directory (e.g. 750) causes 403s.
$APT chmod o+x "$HOME" "$PROJECT_ROOT" "$PROJECT_ROOT/smart_alarm"
$APT systemctl restart apache2

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
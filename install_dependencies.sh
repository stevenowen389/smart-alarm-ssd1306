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
# --no-install-recommends avoids pulling in unrelated extras (e.g. mesa/vulkan
# drivers dragged in as recommends of mpd's codec libraries, desktop utilities
# recommended by apache2/alsa-utils, etc.) that this headless installer doesn't need.
$APT apt-get install -y --no-install-recommends git python3-rpi.gpio python3-venv python3-dev python3-pip i2c-tools gpiod alsa-utils mpd mpc espeak-ng libespeak1 apache2 libapache2-mod-wsgi-py3

echo "Enabling I2C interface (required for the SSD1306 display)..."
CONFIG_TXT=/boot/firmware/config.txt
[ -f "$CONFIG_TXT" ] || CONFIG_TXT=/boot/config.txt
if command -v raspi-config > /dev/null; then
  $APT raspi-config nonint do_i2c 0
else
  grep -q '^dtparam=i2c_arm=on' "$CONFIG_TXT" 2>/dev/null || echo 'dtparam=i2c_arm=on' | $APT tee -a "$CONFIG_TXT" > /dev/null
fi
if [ ! -e /dev/i2c-1 ]; then
  echo "NOTE: /dev/i2c-1 not present yet; a reboot is required before the display will work."
fi

echo "Configuring onboard audio (PWM output via the PAM8403 amplifier)..."
grep -q '^dtparam=audio=on' "$CONFIG_TXT" 2>/dev/null || echo 'dtparam=audio=on' | $APT tee -a "$CONFIG_TXT" > /dev/null
# audremap is a dtoverlay (not a dtparam) - it remaps PWM audio from GPIO40/41 to GPIO12/13.
grep -q '^dtoverlay=audremap' "$CONFIG_TXT" 2>/dev/null || echo 'dtoverlay=audremap,pins_12_13' | $APT tee -a "$CONFIG_TXT" > /dev/null
if ! aplay -l > /dev/null 2>&1; then
  echo "NOTE: no sound card detected yet; a reboot is required before audio will work."
fi

if [ ! -x "$VENV/bin/python" ]; then
  echo "Creating virtual environment at $VENV..."
  python3 -m venv --system-site-packages "$VENV"
fi

echo "Installing Python dependencies..."
if [ -d "$PROJECT_ROOT/wheelhouse" ]; then
  echo "Installing Python dependencies from local wheelhouse..."
  "$VENV/bin/python" -m pip install --no-index \
    --find-links "$PROJECT_ROOT/wheelhouse" \
    -r "$PROJECT_ROOT/requirements.txt"
else
  echo "Installing Python dependencies from PyPI..."
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install -r "$PROJECT_ROOT/requirements.txt"
fi

echo "Configuring apache2 for smart_alarm..."
$APT a2enmod wsgi
# Keep Debian's envvars package file intact. Apache loads conf-enabled before
# sites-enabled, so these values are available to the virtual host config.
{
  echo "ServerName localhost"
  echo "Define smart_alarm_path $PROJECT_ROOT/smart_alarm"
  echo "Define smart_alarm_venv $VENV"
} | $APT tee /etc/apache2/conf-available/smart-alarm-paths.conf > /dev/null
$APT a2enconf smart-alarm-paths
$APT cp "$PROJECT_ROOT/misc/apache/000-default.conf" /etc/apache2/sites-available/000-default.conf
$APT chmod o+w "$PROJECT_ROOT/smart_alarm/data.xml" "$PROJECT_ROOT/smart_alarm/music"
# www-data needs execute (traversal) permission on every directory leading to
# the DocumentRoot. Walk up from PROJECT_ROOT instead of trusting $HOME, since
# $HOME resolves to /root (not the invoking user's home) when this script is
# run as "sudo bash install_dependencies.sh" rather than as a normal user.
p="$(cd "$PROJECT_ROOT" && pwd)"
while [ "$p" != "/" ]; do
  $APT chmod o+x "$p"
  p="$(dirname "$p")"
done
$APT apache2ctl configtest
$APT systemctl restart apache2

echo
echo "Dependencies installed. Run the alarm with:"
echo "  $VENV/bin/python $PROJECT_ROOT/run_smart_alarm.py"
echo
echo "LED support includes the colorschemes package from requirements.txt."
echo "Set APA102_PI_PATH if the legacy APA102_Pi library is outside ~/APA102_Pi."
if [ ! -e /dev/i2c-1 ]; then
  echo
  echo "IMPORTANT: I2C was just enabled but requires a reboot to take effect (needed for the display)."
  echo "  sudo reboot"
fi
if ! aplay -l > /dev/null 2>&1; then
  echo
  echo "IMPORTANT: audio was just enabled but requires a reboot to take effect (needed for sound)."
  echo "  sudo reboot"
fi
#!/bin/bash
# install_systemd_unit.sh - install a systemd service for smart_alarm
# Usage: sudo ./scripts/install_systemd_unit.sh /home/steven/smart_alarm steven

# This file is stored with LF line endings; run it with bash if it was copied
# through a tool that changes line endings.

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <project_root> <user>"
  exit 1
fi

PROJECT_ROOT="$1"
RUN_USER="$2"
SERVICE_NAME="smart_alarm.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

cat > /tmp/$SERVICE_NAME <<'UNIT'
[Unit]
Description=Smart Alarm Service
After=network.target

[Service]
Type=simple
User=%RUN_USER%
WorkingDirectory=%PROJECT_ROOT%
ExecStart=%PROJECT_ROOT%/.venv/bin/python %PROJECT_ROOT%/run_smart_alarm.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

# Replace placeholders and move into place
sed -e "s|%PROJECT_ROOT%|$PROJECT_ROOT|g" -e "s|%RUN_USER%|$RUN_USER|g" /tmp/$SERVICE_NAME > /tmp/$SERVICE_NAME.real
sudo mv /tmp/$SERVICE_NAME.real $SERVICE_PATH
sudo systemctl daemon-reload
sudo systemctl enable --now $SERVICE_NAME

echo "Installed and started $SERVICE_NAME"
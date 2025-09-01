#!/bin/bash

# Voice Assistant Service Configuration Script
# Creates and configures the systemd service for auto-startup

USER_NAME=$(whoami)
HOME_DIR=$(eval echo ~$USER_NAME)
SERVICE_FILE="/etc/systemd/system/voice-assistant.service"

echo "🔧 Configuring Voice Assistant Service..."

# Create the systemd service file
sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Voice Assistant Service
Documentation=https://github.com/AsalStarboy/Verbi-voice-assistance
After=network.target sound.target ollama.service graphical-session.target
Wants=network.target sound.target
Requires=ollama.service

[Service]
Type=simple
User=$USER_NAME
Group=audio
WorkingDirectory=$HOME_DIR/voice_assistant
Environment=HOME=$HOME_DIR
Environment=USER=$USER_NAME
Environment=XDG_RUNTIME_DIR=/run/user/$(id -u $USER_NAME)
Environment=PULSE_RUNTIME_PATH=/run/user/$(id -u $USER_NAME)/pulse

# Wait for system to be ready
ExecStartPre=/bin/sleep 15
ExecStartPre=/bin/bash -c 'until curl -s http://localhost:11434/api/tags >/dev/null 2>&1; do sleep 5; done'

# Start the voice assistant
ExecStart=$HOME_DIR/voice_assistant/start_voice_assistant.sh

# Restart policies
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Resource limits (important for Pi)
MemoryMax=1.5G
CPUQuota=80%

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=voice-assistant

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created: $SERVICE_FILE"

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant.service

echo "✅ Voice Assistant service enabled for auto-start"
echo ""
echo "Service Commands:"
echo "  Start:   sudo systemctl start voice-assistant"
echo "  Stop:    sudo systemctl stop voice-assistant"
echo "  Status:  sudo systemctl status voice-assistant"
echo "  Logs:    sudo journalctl -u voice-assistant -f"
echo ""
echo "🚀 Reboot your Pi to test auto-start: sudo reboot"

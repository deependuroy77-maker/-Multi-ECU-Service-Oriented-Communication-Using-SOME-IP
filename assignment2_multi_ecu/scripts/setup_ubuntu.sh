#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y python3 python3-venv python3-pip wireshark tshark
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
sudo ip addr add 224.224.224.245 dev lo autojoin 2>/dev/null || true
echo
echo "Setup complete. Activate with: source .venv/bin/activate"
echo "Start daemon: someipyd --config someipyd.json"

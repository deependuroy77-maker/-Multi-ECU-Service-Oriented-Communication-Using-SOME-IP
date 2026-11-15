#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
echo "Starting daemon and four ECU applications in this terminal session."
echo "Use Ctrl+C to stop. For screenshot-friendly separate terminals, follow README.md."
someipyd --config someipyd.json &
DAEMON_PID=$!
sleep 2
python -m src.cluster_client &
P1=$!
python -m src.central_display &
P2=$!
python -m src.vehicle_speed_service &
P3=$!
python -m src.climate_service &
P4=$!
cleanup(){ kill "$P1" "$P2" "$P3" "$P4" "$DAEMON_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
wait

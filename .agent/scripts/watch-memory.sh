#!/bin/bash
# .agent/scripts/watch-memory.sh
# Real-time Memory Watchdog (Mac/Linux Polling Version)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_SCRIPT="$SCRIPT_DIR/check-memory.sh"

if [ ! -f "$CHECK_SCRIPT" ]; then
    echo "Error: check-memory.sh not found at $CHECK_SCRIPT"
    exit 1
fi

echo "[Watchdog] Starting Mac/Linux Daemon..."
echo "  Target Script: $CHECK_SCRIPT"
echo "  Interval: 2s"

while true; do
  bash "$CHECK_SCRIPT" "daemon" 2
  sleep 2
done

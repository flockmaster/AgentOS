#!/bin/bash
# .agent/scripts/check-memory.sh
# Cross-platform Memory Check Script (macOS/Linux compatible)

# Default Params
SESSION_ID=${1:-"unknown"}
THRESHOLD=${2:-2}

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
MEMORY_DIR="$AGENT_ROOT/.agent/memory"
STATUS_FILE="$MEMORY_DIR/watchdog_status.lock"
TEMP_FILE="$MEMORY_DIR/watchdog_status.tmp"

# Detect Home Directory for Antigravity Paths
CONVERSATIONS_DIR="$HOME/.gemini/antigravity/conversations"

# Initialize Status
STATUS="NORMAL"
SIZE_MB=0

if [ -d "$CONVERSATIONS_DIR" ]; then
    # Find the most recently modified .pb file
    # Uses ls -t to sort by time, head -1 to pick first.
    LATEST_PB=$(ls -t "$CONVERSATIONS_DIR"/*.pb 2>/dev/null | head -1)
    
    if [ -n "$LATEST_PB" ]; then
        # Get Size in Bytes
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS stat
            SIZE_BYTES=$(stat -f %z "$LATEST_PB")
        else
            # Linux stat
            SIZE_BYTES=$(stat -c %s "$LATEST_PB")
        fi
        
        # Calculate MB (using awk for float math)
        SIZE_MB=$(awk "BEGIN {printf \"%.4f\", $SIZE_BYTES/1048576}")
        
        # Threshold Logic
        # Compare floats using awk
        IS_CRITICAL=$(awk "BEGIN {print ($SIZE_MB >= $THRESHOLD)}")
        IS_WARNING=$(awk "BEGIN {print ($SIZE_MB >= ($THRESHOLD * 0.8))}")
        
        if [ "$IS_CRITICAL" -eq 1 ]; then
            STATUS="CRITICAL"
        elif [ "$IS_WARNING" -eq 1 ]; then
            STATUS="WARNING"
        fi
    fi
fi

# Create JSON Payload
TIMESTAMP=$(date +%s)
JSON_PAYLOAD=$(printf '{"status":"%s","size_mb":%s,"limit_mb":%s,"timestamp":%s,"session_id":"%s"}' \
    "$STATUS" "$SIZE_MB" "$THRESHOLD" "$TIMESTAMP" "$SESSION_ID")

# Atomic Write
echo "$JSON_PAYLOAD" > "$TEMP_FILE"
mv "$TEMP_FILE" "$STATUS_FILE"

exit 0

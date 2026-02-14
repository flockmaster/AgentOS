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

# Read Previous State
PREV_SIZE=0
PREV_STATUS="NORMAL"

if [ -f "$STATUS_FILE" ]; then
    # Extract values using grep/sed/awk to avoid jq dependency
    PREV_SIZE=$(grep -o '"size_mb":[0-9.]*' "$STATUS_FILE" | cut -d':' -f2)
    PREV_STATUS=$(grep -o '"status":"[^"]*"' "$STATUS_FILE" | cut -d':' -f2 | tr -d '"')
fi

# Compare State (Delta < 0.01MB considered no change)
DIFF=$(awk "BEGIN {print ($SIZE_MB - $PREV_SIZE < 0 ? $PREV_SIZE - $SIZE_MB : $SIZE_MB - $PREV_SIZE)}")
IS_SAME=$(awk "BEGIN {print ($DIFF < 0.01)}")

if [ "$IS_SAME" -eq 1 ] && [ "$STATUS" == "$PREV_STATUS" ]; then
    # No significant change, skip update
    exit 0
fi

# --- VISUALIZATION ---
# Colors
RESET='\033[0m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'

COLOR="$GREEN"
if [ "$STATUS" == "WARNING" ]; then COLOR="$YELLOW"; fi
if [ "$STATUS" == "CRITICAL" ]; then COLOR="$RED"; fi

# Progress Bar
PCT=$(awk "BEGIN {printf \"%d\", ($SIZE_MB / $THRESHOLD) * 100}")
BAR_LEN=20
FILLED=$(awk "BEGIN {printf \"%d\", ($PCT * $BAR_LEN) / 100}")
if [ "$FILLED" -gt "$BAR_LEN" ]; then FILLED=$BAR_LEN; fi
EMPTY=$((BAR_LEN - FILLED))

BAR_STR=""
for ((i=0; i<FILLED; i++)); do BAR_STR="${BAR_STR}#"; done
for ((i=0; i<EMPTY; i++)); do BAR_STR="${BAR_STR}-"; done

TIME_STR=$(date +"%H:%M:%S")
FNAME=$(basename "$LATEST_PB")
# Truncate filename if too long
if [ ${#FNAME} -gt 15 ]; then FNAME="${FNAME:0:12}..."; fi

# Print to Stdout (matches Windows format)
printf "${GRAY}[%s]${RESET} %-15s ${COLOR}[%s] ${PCT}%% (%.4f MB / %d MB) -> %s${RESET}\n" \
    "$TIME_STR" "$FNAME" "$BAR_STR" "$SIZE_MB" "$THRESHOLD" "$STATUS"

# Create JSON Payload
TIMESTAMP=$(date +%s)
JSON_PAYLOAD=$(printf '{"status":"%s","size_mb":%s,"limit_mb":%s,"timestamp":%s,"session_id":"%s"}' \
    "$STATUS" "$SIZE_MB" "$THRESHOLD" "$TIMESTAMP" "$SESSION_ID")

# Atomic Write
echo "$JSON_PAYLOAD" > "$TEMP_FILE"
mv "$TEMP_FILE" "$STATUS_FILE"

exit 0

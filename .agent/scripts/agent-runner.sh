#!/bin/bash
# .agent/scripts/agent-runner.sh
# Agent Execution Lifecycle Manager (Mac/Linux version)
# 1. Pre-Execution: Check Watchdog Status -> Inject Prompt if needed.
# 2. Execution: Run the Agent (Codex Worker).
# 3. Post-Execution: Update Memory Status.

set -e 

# 1. Environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
MEMORY_DIR="$AGENT_ROOT/.agent/memory"
STATUS_FILE="$MEMORY_DIR/watchdog_status.lock"
CHECK_SCRIPT="$SCRIPT_DIR/check-memory.sh"

SESSION_ID="unknown"
CONTEXT_FILE="$MEMORY_DIR/active_context.md"

if [ -f "$CONTEXT_FILE" ]; then
    # Extract session_id using sed
    SESSION_ID=$(sed -n 's/^session_id: "*\([^"]*\)"*/\1/p' "$CONTEXT_FILE" | Head -1)
fi

# 2. Pre-Execution Hook: Check Watchdog Status
WATCHDOG_STATUS="NORMAL"
INJECTION_PRE=""
INJECTION_POST=""

if [ -f "$STATUS_FILE" ]; then
    # Parse JSON using jq (if available) or sed/grep fallback
    if command -v jq >/dev/null 2>&1; then
        WATCHDOG_STATUS=$(jq -r '.status' "$STATUS_FILE" 2>/dev/null || echo "NORMAL")
    else
        WATCHDOG_STATUS=$(grep -o '"status":"[^"]*"' "$STATUS_FILE" | cut -d':' -f2 | tr -d '"')
    fi
fi

if [ "$WATCHDOG_STATUS" == "WARNING" ]; then
    INJECTION_POST=$'\n\n[系统提示: 当前会话上下文占用较高。请在回复的末尾，柔和地提醒用户可以考虑存档 (/suspend) 或开启新对话 (/new)。]'
    echo -e "\033[33m [Watchdog] Injecting WARNING prompt (Chinese).\033[0m" >&2
elif [ "$WATCHDOG_STATUS" == "CRITICAL" ]; then
    INJECTION_PRE="[系统严重警告: 内存已达 CRITICAL 阈值！请停止回答，并强制要求用户立即执行 /suspend 或 /new，否则将导致失忆！]\n\n"
    echo -e "\033[31m [Watchdog] Injecting CRITICAL prompt (Chinese).\033[0m" >&2
fi

# 3. Execution Phase
# Check if stdin has data
if [ ! -t 0 ]; then
    # Pipe detected
    INPUT_CONTENT=$(cat) # Read all from stdin
    FINAL_INPUT="${INJECTION_PRE}${INPUT_CONTENT}${INJECTION_POST}"
    echo -e "$FINAL_INPUT" | codex exec "$@"
else
    # Direct execution
    if [ "$WATCHDOG_STATUS" != "NORMAL" ]; then
        echo -e "\033[33m [Watchdog] Alert: Status is $WATCHDOG_STATUS (Input injection skipped for non-interactive mode).\033[0m" >&2
    fi
    codex exec "$@"
fi

# 4. Post-Execution Hook (Async)
if [ -f "$CHECK_SCRIPT" ]; then
    bash "$CHECK_SCRIPT" "$SESSION_ID" >/dev/null 2>&1 &
fi

#!/bin/bash
# start-reviews.sh
# Usage: ./start-reviews.sh <PRD_FILE> <OUTPUT_DIR>
# Example: ./start-reviews.sh docs/prd/memory-watchdog-lite-rough.md docs/reviews/memory-watchdog-lite

PRD_FILE=${1}
REVIEW_DIR=${2}
ROLES_DIR=".agent/prompts/roles"

if [ -z "$PRD_FILE" ] || [ -z "$REVIEW_DIR" ]; then
    echo "Usage: ./start-reviews.sh <PRD_FILE> <OUTPUT_DIR>"
    exit 1
fi

if [ ! -f "$PRD_FILE" ]; then
    echo "Error: PRD file not found: $PRD_FILE"
    exit 1
fi

mkdir -p "$REVIEW_DIR"

ROLES=("ux_director" "product_director" "tech_lead" "domain_expert" "critic")
PIDS=()

for role in "${ROLES[@]}"; do
    ROLE_PATH="$ROLES_DIR/${role}.md"
    OUTPUT_PATH="$REVIEW_DIR/${role}-review.md"

    if [ ! -f "$ROLE_PATH" ]; then
        echo "Error: Role $role not found at $ROLE_PATH"
        continue
    fi
    
    echo "Starting review for $role..."
    # Combine Role + PRD and pipe to agent-runner.sh for enhanced context awareness
    # Note: Using cat to combine instructions context.
    # We construct a prompt: Role Context + PRD Content
    (
        echo "# Role Context"
        cat "$ROLE_PATH"
        echo -e "\n\n# PRD Content"
        cat "$PRD_FILE"
    ) | bash .agent/scripts/agent-runner.sh > "$OUTPUT_PATH" &
    
    PIDS+=($!)
done

echo "Waiting for 5 parallel review processes to complete..."
for pid in "${PIDS[@]}"; do
    wait $pid
done

echo "All reviews completed."

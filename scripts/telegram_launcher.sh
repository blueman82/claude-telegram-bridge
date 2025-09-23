#!/bin/bash

# Telegram Listener LaunchAgent Wrapper Script
# Sources environment and starts telegram listener with proper error handling

# Set up logging
exec > ~/telegram_listener.log 2>&1

echo "=== Telegram Listener Starting $(date) ==="

# Source environment
if [ -f ~/.claude/.env ]; then
    source ~/.claude/.env
    echo "✓ Environment loaded from ~/.claude/.env"
else
    echo "✗ Error: ~/.claude/.env not found"
    exit 1
fi

# Verify API key
if [ -z "$TELEGRAM_API" ]; then
    echo "✗ Error: TELEGRAM_API not set"
    exit 1
fi
echo "✓ TELEGRAM_API found"

# Verify chat ID file
if [ ! -f ~/.claude/.chat_id ]; then
    echo "✗ Error: ~/.claude/.chat_id not found"
    exit 1
fi
echo "✓ Chat ID file found"

# Change to correct directory
cd /Users/harrison/Documents/Github/claude_text || {
    echo "✗ Error: Cannot change to project directory"
    exit 1
}
echo "✓ Changed to project directory: $(pwd)"

# Start telegram listener
echo "✓ Starting telegram listener..."
exec python3 scripts/telegram_listener_simple.py
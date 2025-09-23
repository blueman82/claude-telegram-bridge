# Claude-Telegram Bot Setup Guide

This guide walks you through setting up the Claude-Telegram integration for 2-way communication.

## Prerequisites

- macOS or Linux system
- Python 3.7+
- Claude Code CLI installed
- Telegram account

## Step 1: Create Your Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` to BotFather
3. Choose a name for your bot (e.g., "Claude Assistant")
4. Choose a username ending in `bot` (e.g., `claude_assistant_bot`)
5. Save the API token BotFather gives you - it looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   ```

## Step 2: Get Your Chat ID

1. Send any message to your new bot
2. Open this URL in your browser (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Find your chat ID in the response:
   ```json
   "chat": {"id": 7062493332, ...}
   ```

## Step 3: Set Up Environment

1. Create the Claude hooks directory:
   ```bash
   mkdir -p ~/.claude/hooks
   ```

2. Copy the required scripts:
   ```bash
   # Copy stop hook
   cp scripts/stop.py ~/.claude/hooks/
   chmod +x ~/.claude/hooks/stop.py

   # Copy listener script
   cp scripts/telegram_listener_simple.py ~/.claude/
   chmod +x ~/.claude/telegram_listener_simple.py

   # Copy show-telegram script
   cp scripts/show-telegram.py ~/.claude/
   chmod +x ~/.claude/show-telegram.py
   ```

3. Create environment file:
   ```bash
   # Copy from example
   cp .env.example ~/.claude/.env

   # Edit with your API key
   nano ~/.claude/.env
   # Add: TELEGRAM_API=your_bot_token_here
   ```

4. Create chat ID file:
   ```bash
   echo "YOUR_CHAT_ID" > ~/.claude/.chat_id
   ```

## Step 4: Configure Claude Code

1. Update Claude settings to use the stop hook:
   ```bash
   nano ~/.claude/settings.json
   ```

2. Add or update the hooks section:
   ```json
   {
     "hooks": {
       "Stop": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "~/.claude/hooks/stop.py"
             }
           ]
         }
       ]
     }
   }
   ```

## Step 5: Install Python Dependencies

```bash
pip install requests python-dotenv
```

## Step 6: Start the Background Listener

The listener needs to run continuously to handle delayed replies:

```bash
# Run in background
nohup python3 ~/.claude/telegram_listener_simple.py > ~/telegram_listener.log 2>&1 &

# Or use screen/tmux for better management
screen -dmS telegram-listener python3 ~/.claude/telegram_listener_simple.py
```

## Step 7: Add Convenience Alias (Optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Show Telegram conversation history
alias show-telegram="python3 ~/.claude/show-telegram.py"

# Check listener status
alias telegram-status="ps aux | grep telegram_listener"
```

## Usage

### How It Works

1. **Automatic Notifications**: When Claude finishes responding, you get a Telegram message with:
   - Session ID (e.g., `abc123`)
   - Project name
   - Claude's full response with preserved formatting

2. **Reply Format**: To continue the conversation from Telegram:
   ```
   abc123:your message here
   ```

3. **View History**: See what happened in Telegram conversations:
   ```bash
   show-telegram abc123
   ```

### Testing Your Setup

1. Start a Claude session:
   ```bash
   claude "Hello, test the Telegram integration"
   ```

2. Check Telegram for the notification

3. Reply with:
   ```
   session_id:Does the reply work?
   ```

4. Check if session continues or new session starts (depending on timing)

## Troubleshooting

### No Telegram Messages

1. Check API key is correct:
   ```bash
   cat ~/.claude/.env
   ```

2. Verify chat ID:
   ```bash
   cat ~/.claude/.chat_id
   ```

3. Test API directly:
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
        -d "chat_id=<YOUR_CHAT_ID>" \
        -d "text=Test message"
   ```

### Listener Not Running

Check if running:
```bash
ps aux | grep telegram_listener
```

Restart if needed:
```bash
pkill -f telegram_listener_simple.py
nohup python3 ~/.claude/telegram_listener_simple.py > ~/telegram_listener.log 2>&1 &
```

### Replies Not Working

1. Ensure correct format: `session_id:message`
2. Check listener logs:
   ```bash
   tail -f ~/telegram_listener.log
   ```

## Security Notes

- Keep your `.env` file private - never commit it to git
- The chat ID file restricts who can send commands
- Consider using a private bot (disable joining groups in BotFather)

## Advanced Configuration

### Auto-start on Boot (macOS)

Create `~/Library/LaunchAgents/com.claude.telegram.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claude.telegram</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOUR_USERNAME/.claude/telegram_listener_simple.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.claude.telegram.plist
```

## Support

For issues or improvements, please open an issue on GitHub.
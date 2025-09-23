#!/bin/bash

# Claude-Telegram Bridge Setup Script
# Automates the entire setup process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_status() { echo -e "${BLUE}[*]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }

# Create macOS app bundle for auto-start functionality
create_telegram_app_bundle() {
    local app_path="$HOME/Applications/TelegramListener.app"
    local script_path="$HOME/.claude/telegram_listener.py"
    local project_dir="$(pwd)"

    print_status "Creating TelegramListener app bundle..."

    # Create app bundle structure
    mkdir -p "$app_path/Contents/MacOS"
    mkdir -p "$app_path/Contents/Resources"

    # Create executable wrapper script
    cat > "$app_path/Contents/MacOS/TelegramListener" << EOF
#!/bin/bash
# TelegramListener wrapper script for auto-start
cd "$project_dir"
source ~/.claude/.env 2>/dev/null || true
exec python3 "$script_path"
EOF

    chmod +x "$app_path/Contents/MacOS/TelegramListener"

    # Create Info.plist with proper bundle information
    cat > "$app_path/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>TelegramListener</string>
    <key>CFBundleIdentifier</key>
    <string>com.claude-telegram-bridge.listener</string>
    <key>CFBundleName</key>
    <string>TelegramListener</string>
    <key>CFBundleDisplayName</key>
    <string>Telegram Listener</string>
    <key>CFBundleVersion</key>
    <string>1.1.6</string>
    <key>CFBundleShortVersionString</key>
    <string>1.1.6</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSBackgroundOnly</key>
    <true/>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
EOF

    print_success "App bundle created at $app_path"
}

# Add app to macOS Login Items
add_to_login_items() {
    local app_path="$HOME/Applications/TelegramListener.app"

    print_status "Adding TelegramListener to Login Items..."

    if osascript -e "tell application \"System Events\" to make login item at end with properties {path:\"$app_path\", hidden:true}" 2>/dev/null; then
        print_success "Added to Login Items (will start automatically on login)"
    else
        print_warning "Could not add to Login Items automatically"
        echo "You can add it manually in System Preferences > Users & Groups > Login Items"
        echo "Add: $app_path"
    fi
}

# Remove app from macOS Login Items
remove_from_login_items() {
    print_status "Removing TelegramListener from Login Items..."

    if osascript -e "tell application \"System Events\" to delete login item \"TelegramListener\"" 2>/dev/null; then
        print_success "Removed from Login Items"
    else
        print_status "TelegramListener not found in Login Items (already removed or not added)"
    fi
}

# Configure telegram listener startup method
configure_telegram_startup() {
    echo ""
    print_status "Telegram Listener Configuration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Choose how you want the telegram listener to start:"
    echo "  1) Auto-start on login (recommended)"
    echo "     - Creates macOS app bundle"
    echo "     - Adds to Login Items"
    echo "     - Starts automatically when you log in"
    echo ""
    echo "  2) Manual start"
    echo "     - Start/stop manually using aliases"
    echo "     - More control over when it runs"
    echo ""

    while true; do
        read -p "Choose option (1 for auto-start, 2 for manual): " startup_choice
        case $startup_choice in
            1)
                setup_auto_start
                break
                ;;
            2)
                setup_manual_start
                break
                ;;
            *)
                print_error "Please choose 1 or 2"
                ;;
        esac
    done
}

# Setup auto-start functionality
setup_auto_start() {
    print_status "Setting up auto-start functionality..."

    # Create app bundle
    create_telegram_app_bundle

    # Add to login items
    add_to_login_items

    # Ask if they want to start it now
    echo ""
    read -p "Start the listener now? (Y/n): " start_now
    if [[ ! "$start_now" =~ ^[Nn]$ ]]; then
        start_listener_via_app
    else
        print_success "Auto-start configured - will start automatically on next login"
        print_status "Use 'open ~/Applications/TelegramListener.app' to start manually"
    fi
}

# Setup manual start functionality
setup_manual_start() {
    print_status "Manual start selected"
    read -p "Start the Telegram listener now? (Y/n): " start_listener
    if [[ ! "$start_listener" =~ ^[Nn]$ ]]; then
        start_listener_manually
    else
        print_status "Listener not started. Run 'telegram-start' to start it later"
    fi
}

# Start listener via app bundle
start_listener_via_app() {
    # Kill any existing listeners (both old and new filenames)
    pkill -f telegram_listener_simple.py 2>/dev/null || true
    pkill -f telegram_listener.py 2>/dev/null || true

    # Start the app bundle
    print_status "Starting TelegramListener app..."
    open "$HOME/Applications/TelegramListener.app"
    sleep 3

    if ps aux | grep -v grep | grep -q telegram_listener.py; then
        print_success "Telegram listener started via app bundle (PID: $(pgrep -f telegram_listener.py))"
        print_success "Auto-start configured - will start automatically on next login"
    else
        print_warning "App bundle created but listener not running. Trying manual start..."
        start_listener_manually
    fi
}

# Start listener manually
start_listener_manually() {
    # Kill any existing listeners (both old and new filenames)
    pkill -f telegram_listener_simple.py 2>/dev/null || true
    pkill -f telegram_listener.py 2>/dev/null || true

    # Start new listener
    nohup python3 ~/.claude/telegram_listener.py > ~/telegram_listener.log 2>&1 &
    sleep 2

    if ps aux | grep -v grep | grep -q telegram_listener.py; then
        print_success "Telegram listener started (PID: $(pgrep -f telegram_listener.py))"
    else
        print_error "Failed to start listener. Check ~/telegram_listener.log for errors"
    fi
}

echo "╔═══════════════════════════════════════════╗"
echo "║     Claude-Telegram Bridge Setup         ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.7+"
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check Claude CLI
if ! command -v claude &> /dev/null; then
    print_error "Claude CLI is not installed. Please install Claude Code first"
    exit 1
fi
print_success "Claude CLI found"

# Check/Install Python packages
print_status "Checking Python dependencies..."

# Check if packages are already available
if python3 -c "import requests, dotenv" 2>/dev/null; then
    print_success "Python dependencies already available"
else
    print_warning "Installing Python dependencies..."
    # Try user install first, then with break-system-packages if needed
    if ! pip3 install --user -q requests python-dotenv 2>/dev/null; then
        print_warning "User install failed, trying with system override..."
        pip3 install --user --break-system-packages requests python-dotenv || {
            print_error "Failed to install Python dependencies"
            echo "Please install manually: pip3 install --user requests python-dotenv"
            exit 1
        }
    fi
    print_success "Python dependencies installed"
fi

# Create directories
print_status "Creating necessary directories..."
mkdir -p ~/.claude/hooks
print_success "Directories created"

# Copy scripts
print_status "Installing scripts..."
cp scripts/stop.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/stop.py
print_success "Stop hook installed"

cp scripts/telegram_listener.py ~/.claude/
chmod +x ~/.claude/telegram_listener.py
print_success "Telegram listener installed"

cp scripts/show-telegram.py ~/.claude/
chmod +x ~/.claude/show-telegram.py
print_success "Show-telegram script installed"

cp scripts/show-changes.py ~/.claude/
chmod +x ~/.claude/show-changes.py
print_success "Show-changes script installed"

# Get Telegram Bot Token
echo ""
print_status "Telegram Bot Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ~/.claude/.env ] && grep -q "TELEGRAM_API=" ~/.claude/.env; then
    print_warning "Existing Telegram configuration found"
    read -p "Do you want to reconfigure? (y/N): " reconfigure
    if [[ ! "$reconfigure" =~ ^[Yy]$ ]]; then
        print_status "Keeping existing configuration"
    else
        rm -f ~/.claude/.env ~/.claude/.chat_id
    fi
fi

if [ ! -f ~/.claude/.env ] || ! grep -q "TELEGRAM_API=" ~/.claude/.env; then
    echo ""
    echo "To create a Telegram bot:"
    echo "1. Open Telegram and search for @BotFather"
    echo "2. Send /newbot and follow instructions"
    echo "3. Copy the API token"
    echo ""

    while true; do
        read -p "Enter your Telegram Bot API token: " bot_token
        if [[ "$bot_token" =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
            echo "TELEGRAM_API=$bot_token" > ~/.claude/.env
            print_success "Bot token saved"
            break
        else
            print_error "Invalid token format. Should look like: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
        fi
    done
fi

# Get Chat ID
if [ ! -f ~/.claude/.chat_id ]; then
    echo ""
    print_status "Getting your Chat ID..."
    echo "1. Send any message to your bot on Telegram"
    echo "2. Press Enter when ready"
    read -p ""

    # Try to get chat ID automatically
    bot_token=$(grep TELEGRAM_API ~/.claude/.env | cut -d'=' -f2)
    response=$(curl -s "https://api.telegram.org/bot$bot_token/getUpdates")

    chat_id=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data.get('result'):
        print(data['result'][-1]['message']['chat']['id'])
except: pass
" 2>/dev/null)

    if [ -n "$chat_id" ]; then
        echo "$chat_id" > ~/.claude/.chat_id
        print_success "Chat ID detected: $chat_id"
    else
        print_warning "Could not auto-detect chat ID"
        echo "Visit: https://api.telegram.org/bot$bot_token/getUpdates"
        echo "Find your chat ID in the response"
        read -p "Enter your Chat ID: " chat_id
        echo "$chat_id" > ~/.claude/.chat_id
        print_success "Chat ID saved"
    fi
fi

# Configure Claude settings
print_status "Configuring Claude Code hooks..."

# Check if settings.json exists
if [ ! -f ~/.claude/settings.json ]; then
    echo '{}' > ~/.claude/settings.json
fi

# Update settings using Python for proper JSON handling
python3 << EOF
import json
import os

settings_file = os.path.expanduser('~/.claude/settings.json')

try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
except:
    settings = {}

# Ensure hooks structure exists
if 'hooks' not in settings:
    settings['hooks'] = {}

if 'Stop' not in settings['hooks']:
    settings['hooks']['Stop'] = []

# Check if our hook is already configured
hook_configured = False
for stop_config in settings['hooks']['Stop']:
    if isinstance(stop_config, dict) and 'hooks' in stop_config:
        for hook in stop_config['hooks']:
            if hook.get('command') == '~/.claude/hooks/stop.py':
                hook_configured = True
                break

if not hook_configured:
    # Add our stop hook
    if not settings['hooks']['Stop']:
        settings['hooks']['Stop'] = [{'hooks': []}]

    settings['hooks']['Stop'][0]['hooks'].append({
        'type': 'command',
        'command': '~/.claude/hooks/stop.py'
    })

    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    print("Hook configuration added")
else:
    print("Hook already configured")
EOF

print_success "Claude Code configured"

# Test the setup
echo ""
print_status "Testing configuration..."

# Test Telegram API
bot_token=$(grep TELEGRAM_API ~/.claude/.env | cut -d'=' -f2)
chat_id=$(cat ~/.claude/.chat_id)

response=$(curl -s -X POST "https://api.telegram.org/bot$bot_token/sendMessage" \
    -d "chat_id=$chat_id" \
    -d "text=🎉 Claude-Telegram Bridge setup complete!")

if echo "$response" | grep -q '"ok":true'; then
    print_success "Test message sent to Telegram!"
else
    print_warning "Could not send test message. Check your token and chat ID"
fi

# Initialize sessions file if it doesn't exist
if [ ! -f ~/.claude/.sessions ]; then
    echo '{}' > ~/.claude/.sessions
    print_success "Sessions tracking file initialized"
fi

# Test that the stop hook is executable
if [ -x ~/.claude/hooks/stop.py ]; then
    print_success "Stop hook is properly configured"
else
    print_error "Stop hook is not executable"
    chmod +x ~/.claude/hooks/stop.py
fi

# Setup aliases
echo ""
print_status "Setting up convenient aliases..."

# Detect shell
# Check user's actual shell, not just script environment
USER_SHELL=$(basename "$SHELL" 2>/dev/null || echo "unknown")
if [ "$USER_SHELL" = "zsh" ] || [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ "$USER_SHELL" = "bash" ] || [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    # Fallback: check which config files exist
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    else
        SHELL_RC="$HOME/.profile"
    fi
fi

print_status "Detected shell config: $SHELL_RC"

# Add aliases if not already present
if ! grep -q "show-telegram" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Claude-Telegram Bridge aliases" >> "$SHELL_RC"
    echo "alias show-telegram='python3 ~/.claude/show-telegram.py'" >> "$SHELL_RC"
    echo "alias show-changes='python3 ~/.claude/show-changes.py'" >> "$SHELL_RC"
    echo "alias telegram-status='ps aux | grep telegram_listener | grep -v grep'" >> "$SHELL_RC"
    echo "alias telegram-start='nohup python3 ~/.claude/telegram_listener.py > ~/telegram_listener.log 2>&1 &'" >> "$SHELL_RC"
    echo "alias telegram-stop='pkill -f telegram_listener.py'" >> "$SHELL_RC"
    print_success "Aliases added to $SHELL_RC"
else
    print_status "Aliases already configured (telegram-start, telegram-stop, telegram-status, show-telegram, show-changes)"
fi

# Configure telegram listener startup
configure_telegram_startup

# Success message
echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║         Setup Complete! 🎉               ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
echo "Quick commands:"
echo "  telegram-start    - Start the background listener"
echo "  telegram-stop     - Stop the listener"
echo "  telegram-status   - Check if listener is running"
echo "  show-telegram ID  - View Telegram conversation"
echo ""
echo "Test it out:"
echo "  1. Run: claude 'Hello from Claude!'"
echo "  2. Check Telegram for notification with session ID"
echo "  3. Reply with format: session_id:your message"
echo ""
echo "Log files:"
echo "  Listener log: ~/telegram_listener.log"
echo "  Claude logs: ~/.claude/logs/"
echo ""
print_success "Setup complete! Source your shell config or restart terminal for aliases."
echo ""
echo -e "  ${GREEN}source $SHELL_RC${NC}"
echo ""
echo "Or open a new terminal window."
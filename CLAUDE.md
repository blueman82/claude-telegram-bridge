# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Claude-Telegram Bridge** - a Python-based system that creates seamless 2-way communication between Claude Code and Telegram. It allows users to receive Claude responses on their phone and reply from anywhere to continue conversations.

## Development Commands

### Installation and Setup
```bash
# Automated setup (recommended)
chmod +x setup.sh && ./setup.sh

# Manual dependency installation
pip install requests python-dotenv

# Test dependencies
pip install -r requirements-test.txt
```

### Testing
```bash
# Run all tests (manual runner)
for test in tests/test_*.py; do python "$test"; done

# Run specific tests
python tests/test_stop_hook.py
python tests/test_git_integration.py

# With pytest (if available)
pytest tests/ -v
```

### Running the System
```bash
# Start background listener (required for replies)
nohup python3 ~/.claude/telegram_listener_simple.py > ~/telegram_listener.log 2>&1 &

# Check listener status
ps aux | grep telegram_listener

# View conversation history
python3 scripts/show-telegram.py <session_id>

# View git changes for a session
python3 scripts/show-changes.py <session_id>
python3 scripts/show-changes.py <session_id> --full  # with complete diff
```

## Architecture

### Core Components

1. **Stop Hook** (`scripts/stop.py`)
   - Runs after each Claude response via Claude's hook system
   - Sends formatted notifications to Telegram
   - Manages session ID generation and persistence
   - Integrates with git to show file changes
   - Supports multiple TTS and LLM services for enhanced notifications

2. **Telegram Listener** (`scripts/telegram_listener_simple.py`)
   - Background service monitoring Telegram for replies
   - Parses messages with format `session_id:message`
   - Resumes Claude sessions using `claude --resume`
   - Handles session mapping and validation

3. **History Viewer** (`scripts/show-telegram.py`)
   - Displays Telegram conversation history for debugging
   - Session-based filtering and formatting

4. **Git Integration** (`scripts/show-changes.py`)
   - Shows file changes during specific Claude sessions
   - Supports file list view and complete diff output
   - Helps track what code was modified

### Data Flow
```
[Claude Response] → [Stop Hook] → [Telegram Bot] → [User's Phone]
                                       ↓
[Claude Resume] ← [Telegram Listener] ← [User Reply: session_id:message]
```

### Configuration Files
- `~/.claude/.env` - Telegram bot API key
- `~/.claude/.chat_id` - Authorized Telegram chat ID
- `~/.claude/.sessions` - Session ID mappings (auto-managed)
- `~/.claude/settings.json` - Claude hook configuration

## Development Patterns

### Session Management
- 6-character hex session IDs generated from current directory hash
- Session mappings stored in JSON format
- Auto-cleanup of sessions older than 30 days
- Session validation ensures only valid hex IDs are processed

### Error Handling
- Graceful failures with logging to prevent Claude disruption
- API errors don't break Claude functionality
- Network timeouts handled with retries
- Invalid session formats rejected silently

### Testing Strategy
- Unit tests mock external dependencies (subprocess, requests)
- Comprehensive edge case coverage
- Built-in test runner for environments without pytest
- Session management and message parsing thoroughly tested

### Git Integration
- Git status and diff capture using subprocess
- Change tracking per session for debugging
- Safe git command execution with error handling
- Support for both summary and detailed diff views

## Project Structure

```
scripts/
├── stop.py                    # Main stop hook (runs after Claude responses)
├── telegram_listener_simple.py # Background service for Telegram replies
├── show-telegram.py           # View conversation history
└── show-changes.py           # View git changes per session

tests/
├── test_stop_hook.py         # Core functionality tests
└── test_git_integration.py   # Git integration tests

setup.sh                      # Automated installation script
requirements.txt              # Runtime dependencies
requirements-test.txt         # Testing dependencies
```

## Common Development Tasks

### Adding New Features
1. Follow existing patterns for error handling and logging
2. Update tests for new functionality
3. Ensure backwards compatibility with existing sessions
4. Test with both manual runner and pytest

### Debugging Issues
1. Check listener logs: `tail -f ~/telegram_listener.log`
2. View session mappings: `cat ~/.claude/.sessions`
3. Test Telegram API directly with curl commands
4. Use `show-telegram` and `show-changes` for session debugging

### Modifying Message Format
- Update parsing logic in `telegram_listener_simple.py`
- Modify formatting in `stop.py`
- Ensure tests cover new message formats
- Consider backwards compatibility

## Security Considerations

- API keys stored in `~/.claude/.env` (not tracked in git)
- Chat ID validation prevents unauthorized access
- Session IDs are non-guessable hex strings
- No sensitive data logged or transmitted in plain text
# Changelog

## [1.0.0] - 2024-09-23

### Added
- Initial release of Claude-Telegram Bridge
- Automated setup script (`setup.sh`) with:
  - Automatic Python dependency installation
  - Telegram bot configuration wizard
  - Chat ID auto-detection
  - Claude Code hooks configuration
  - Shell alias setup (telegram-start, telegram-stop, telegram-status, show-telegram)
  - Background listener auto-start option
  - Sessions tracking file initialization
  - Executable permission checks
- Core scripts:
  - `stop.py` - Stop hook for Telegram notifications with HTML formatting support
  - `telegram_listener_simple.py` - Background listener using long polling
  - `show-telegram.py` - Conversation history viewer
- Documentation:
  - Comprehensive README with architecture diagram
  - Detailed SETUP.md with manual configuration steps
  - Troubleshooting guide
- Markdown to HTML conversion for preserving Claude's formatting:
  - Headers (##, ###) converted to bold
  - Bold, italic, and code formatting preserved
  - Lists converted to bullet points
- Session management with 6-character IDs to prevent conflicts
- 24-hour message history with deduplication
- Plain text reply instructions for simplicity

### Technical Details
- Python 3.7+ compatible
- Uses Telegram Bot API with long polling
- Claude Code hook integration via settings.json
- Environment variables stored in ~/.claude/.env
- Chat ID stored in ~/.claude/.chat_id
- Session mappings in ~/.claude/.sessions

### Known Issues
- Stop hook only triggers when Claude is finishing a response
- Markdown parsing can conflict with special characters in responses
- Replies must follow exact format: `session_id:message`

### Security
- API tokens stored in local .env file (not in repository)
- Chat ID verification prevents unauthorized access
- No sensitive data logged
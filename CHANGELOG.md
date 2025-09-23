# Changelog

## [1.1.1] - 2024-09-23

### Added
- **Basic test suite for core functionality**
  - `tests/test_stop_hook.py` - Session ID generation, message parsing, session mapping
  - `tests/test_git_integration.py` - Git change detection with subprocess mocking
  - `requirements-test.txt` - Test dependencies (pytest, requests, python-dotenv)
  - `tests/README.md` - Testing guide and setup instructions
- **Test infrastructure**
  - Simple built-in test runner (no external dependencies required)
  - Comprehensive edge case coverage and error handling tests
  - Mock-based testing for external subprocess calls
  - Virtual environment setup for isolated testing

### Enhanced
- **Documentation updates**
  - Updated README.md with testing guide and contributor instructions
  - Added testing section to contributing guidelines
  - Updated test status badge from "none" to "basic"
- **Quality assurance**
  - All core functions now have test coverage
  - Validation of session ID uniqueness and deterministic generation
  - Message parsing edge cases thoroughly tested

### Technical Details
- 7 test functions for stop hook core functionality
- 6 test functions for git integration with comprehensive mocking
- Tests validate error handling, edge cases, and expected behavior
- No external dependencies for basic test execution

## [1.1.0] - 2024-09-23

### Added
- **Git diff integration in Telegram notifications**
  - Added `get_recent_changes()` function to detect modified, added, deleted, and untracked files
  - Enhanced stop hook to show git changes before Claude's response
  - Added file type icons (✏️ modified, ➕ added, ➖ deleted, 📄 untracked, 📦 commits)
  - Automatic truncation to first 5 changes to prevent long messages
  - Shows recent commits if no working changes exist
- **Enhanced session tracking**
  - Added `start_time` field to session mappings for change tracking
  - Preserves session start time across multiple notifications
- **New show-changes command**
  - `scripts/show-changes.py` - View detailed git changes for any session
  - Support for `--full` flag to show complete diffs
  - Support for `--files` flag for file list only (default)
  - Shows both working directory changes and recent commits
  - Refactored into focused functions for maintainability

### Enhanced
- Stop hook now includes git changes in notification format:
  ```
  🤖 Session abc123 - project (14:30)

  📂 Recent changes:
  ✏️ src/app.py (modified)
  ➕ src/new_feature.py (added)

  [Claude's response...]

  Reply: abc123:your message
  ```

### Technical Details
- All functions maintain <100 line limit for new code
- Non-destructive changes to existing hook functionality
- Graceful fallback when not in git repository
- Error handling for git command failures

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
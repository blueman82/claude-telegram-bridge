# Changelog

## [1.1.6] - 2025-09-23

### Added
- **Auto-start functionality via Login Items** - macOS native auto-start implementation
  - Created `create_telegram_app_bundle()` function to generate TelegramListener.app bundle
  - Added `add_to_login_items()` and `remove_from_login_items()` for macOS Login Items management
  - Integrated auto-start choice into setup.sh with user prompt (auto vs manual)
  - App bundle approach bypasses LaunchAgent security restrictions
  - Background app runs invisibly with proper macOS integration
  - **TDD Validation**: 5/5 tests passed proving Login Items automation viability

### Enhanced
- **Setup script modularization** - Refactored for maintainability and size compliance
  - Split startup configuration into dedicated functions (400+ line size limit compliance)
  - Created `configure_telegram_startup()`, `setup_auto_start()`, `setup_manual_start()`
  - Added `start_listener_via_app()` and `start_listener_manually()` functions
  - Improved user experience with clear choice between auto-start and manual modes
  - Fallback logic: app bundle failure gracefully falls back to manual start

### Fixed
- **File size compliance** - Refactored setup.sh to stay under 400-line limit
  - Extracted inline startup logic into modular functions
  - Maintained all functionality while improving code organization
  - Each new function under 100 lines (compliance with function size limits)
- **Python package installation** - Enhanced dependency checking with graceful fallbacks
  - Checks if packages already available before attempting installation
  - Uses --user flag first, --break-system-packages only as last resort
  - Provides clear error messages and manual installation instructions
  - Fixes pip install errors on modern macOS systems with Homebrew Python
  - Complies with PEP 668 externally-managed environment requirements
- **Shell detection improvements** - Enhanced shell config file detection for proper alias installation
  - Checks user's actual shell via $SHELL environment variable
  - Fallback logic checks for existing .zshrc/.bashrc files
  - Fixes aliases not working when setup detects wrong shell config file
  - Provides clear feedback showing detected shell config location

## [1.1.5] - 2025-09-23

### Added
- **Telegram listener wrapper script** - Enhanced LaunchAgent support with diagnostic capabilities
  - Created `scripts/telegram_launcher.sh` with comprehensive error handling
  - Environment validation and detailed logging for troubleshooting
  - Sources `~/.claude/.env` and validates required configuration
  - **Note**: Auto-start blocked by macOS security restrictions on user Documents access

### Added (Additional)
- **Login Items automation test suite** - TDD approach for viable auto-start solution
  - Created `tests/test_login_items.py` with comprehensive macOS Login Items testing
  - Tests app bundle creation, adding/removing login items, and verification
  - **Result**: 5/5 tests PASSED - Login Items automation is VIABLE
  - Created `HANDOVER.md` with implementation plan for setup script integration
  - Updated test documentation with new Login Items test coverage

### Updated
- **Documentation cleanup** - Removed non-functional auto-start instructions
  - Updated SETUP.md to reflect manual start requirement due to macOS security
  - Replaced LaunchAgent instructions with background listener management guide
  - Added clear status check and stop commands for manual listener control

### Fixed (Updated)
- **Auto-start limitations** - LaunchAgent cannot access user Documents directory
  - Manual telegram listener start required: `python3 scripts/telegram_listener_simple.py &`
  - Alternative: Move scripts to system-accessible location for auto-start

### Fixed
- **Telegram conversation history bug** - Fixed `show-telegram` command not finding conversations initiated via Telegram
  - Added missing "User replied via Telegram:" prefix to messages in `telegram_listener_simple.py`
  - Messages from Telegram replies are now properly formatted for history viewing
  - Resolves disconnect between working Telegram notifications and broken conversation history display
  - `show-telegram <session_id>` now correctly shows Telegram-initiated conversations

## [1.1.4] - 2024-09-23

### Added
- **CLAUDE.md file** - Comprehensive guidance for Claude Code when working in this repository
  - Project overview and architecture documentation
  - Development commands (installation, testing, running)
  - Core component descriptions and data flow
  - Development patterns and coding conventions
  - Project structure reference
  - Common development tasks guidance
  - Security considerations and best practices

### Enhanced
- **Developer experience** - Future Claude Code instances will be more productive
  - Clear build, test, and deployment commands
  - Architecture understanding without needing to read multiple files
  - Development patterns for consistent code contributions
  - Debugging guidance for common issues

## [1.1.3] - 2024-09-23

### Fixed
- **Setup script completeness** - Fixed missing `show-changes` alias in automated setup
  - Added missing `show-changes` alias to setup.sh script (line 249)
  - Script now properly installs all documented commands and aliases
  - Ensures consistent setup experience matching documentation promises

### Enhanced
- **Documentation clarity** - Improved usage instructions across all documentation
  - Updated both SETUP.md and README.md with clear distinction between terminal/bash shell and Claude Code session usage
  - Documented required `!` prefix for commands when inside active Claude Code sessions
  - Enhanced examples for `show-telegram` and `show-changes` commands with both contexts
  - Added helpful notes in system status section for consistent user experience

## [1.1.2] - 2024-09-23

### Added
- **Automatic session cleanup** - Prevents unlimited growth of `.sessions` file
  - `cleanup_old_sessions()` function removes sessions older than 30 days
  - Automatically triggered with 10% probability during normal operation
  - Uses pathlib for modern file handling
  - Maintains performance by only cleaning when sessions are actually removed

### Enhanced
- **Session management** - More efficient long-term operation
  - Prevents performance degradation from large session files
  - Automatic maintenance without user intervention
  - Preserves all active/recent sessions while cleaning old data

### Technical Details
- 29-line cleanup function with configurable retention period
- Probabilistic trigger (10% chance) to distribute cleanup load
- Graceful error handling maintains system stability
- Uses pathlib instead of os module for file operations

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
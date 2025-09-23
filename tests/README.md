# Tests

Basic test suite for Claude-Telegram Bridge core functionality.

## Setup

1. **Create test environment:**
   ```bash
   python -m venv test_env
   source test_env/bin/activate  # On Windows: test_env\Scripts\activate
   ```

2. **Install test dependencies:**
   ```bash
   pip install -r requirements-test.txt
   ```

## Running Tests

### Manual test runner (no pytest required):
```bash
# Individual test files
python tests/test_stop_hook.py
python tests/test_git_integration.py

# All tests
for test in tests/test_*.py; do python "$test"; done
```

### With pytest:
```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_stop_hook.py

# Verbose output
pytest -v tests/
```

## Test Coverage

- **Session Management** - ID generation, mapping persistence
- **Message Parsing** - Telegram reply format validation
- **Git Integration** - Change detection with subprocess mocking
- **Login Items Automation** - macOS auto-start capability testing
- **Error Handling** - Graceful failures and edge cases

## Test Structure

- `test_stop_hook.py` - Core stop hook functionality
- `test_git_integration.py` - Git change detection with mocks
- `test_login_items.py` - Login Items automation verification (TDD)
- Simple built-in test runner (no external dependencies)
- Comprehensive assertions and edge case coverage

All tests use standard library mocking to avoid external dependencies.
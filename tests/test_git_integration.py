#!/usr/bin/env python3
"""
Basic tests for git integration functionality.
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the hooks directory to path for imports (where actual stop.py lives)
sys.path.insert(0, os.path.expanduser('~/.claude/hooks'))

# Import functions from stop.py
from stop import get_recent_changes


def test_get_recent_changes_not_git_repo():
    """Test behavior when not in a git repository."""
    mock_result = MagicMock()
    mock_result.returncode = 1  # Git command fails

    with patch('stop.subprocess.run', return_value=mock_result):
        result = get_recent_changes("/fake/path")

    assert result is None, "Should return None for non-git directories"


def test_get_recent_changes_with_working_changes():
    """Test detection of working directory changes."""
    # Mock git rev-parse (check if git repo)
    git_check = MagicMock()
    git_check.returncode = 0

    # Mock git status output
    status_result = MagicMock()
    status_result.returncode = 0
    status_result.stdout = " M src/app.py\n A tests/test.py\n?? README.md\n"

    # Mock git log (not used when there are working changes)
    log_result = MagicMock()
    log_result.returncode = 0
    log_result.stdout = ""

    with patch('stop.subprocess.run') as mock_run:
        mock_run.side_effect = [git_check, status_result, log_result]
        result = get_recent_changes("/test/path")

    assert result is not None, "Should detect changes"
    assert "✏️ src/app.py (modified)" in result
    assert "➕ tests/test.py (added)" in result
    assert "📄 README.md (untracked)" in result


def test_get_recent_changes_with_commits():
    """Test detection of recent commits when no working changes."""
    # Mock git rev-parse (check if git repo)
    git_check = MagicMock()
    git_check.returncode = 0

    # Mock git status (no working changes)
    status_result = MagicMock()
    status_result.returncode = 0
    status_result.stdout = ""

    # Mock git log output
    log_result = MagicMock()
    log_result.returncode = 0
    log_result.stdout = "abc1234 Add new feature\ndef5678 Fix bug in parser\n"

    with patch('stop.subprocess.run') as mock_run:
        mock_run.side_effect = [git_check, status_result, log_result]
        result = get_recent_changes("/test/path")

    assert result is not None, "Should detect recent commits"
    assert "📦 abc1234: Add new feature" in result
    assert "📦 def5678: Fix bug in parser" in result


def test_get_recent_changes_no_changes():
    """Test when there are no working changes or recent commits."""
    # Mock git rev-parse (check if git repo)
    git_check = MagicMock()
    git_check.returncode = 0

    # Mock git status (no working changes)
    status_result = MagicMock()
    status_result.returncode = 0
    status_result.stdout = ""

    # Mock git log (no recent commits)
    log_result = MagicMock()
    log_result.returncode = 0
    log_result.stdout = ""

    with patch('stop.subprocess.run') as mock_run:
        mock_run.side_effect = [git_check, status_result, log_result]
        result = get_recent_changes("/test/path")

    assert result is None, "Should return None when no changes"


def test_get_recent_changes_truncation():
    """Test that changes are truncated to prevent long messages."""
    # Mock git rev-parse (check if git repo)
    git_check = MagicMock()
    git_check.returncode = 0

    # Mock git status with many changes
    status_result = MagicMock()
    status_result.returncode = 0
    status_result.stdout = (
        " M file1.py\n"
        " M file2.py\n"
        " M file3.py\n"
        " M file4.py\n"
        " M file5.py\n"
        " M file6.py\n"
        " M file7.py\n"
    )

    # Mock git log (not used when there are working changes)
    log_result = MagicMock()
    log_result.returncode = 0
    log_result.stdout = ""

    with patch('stop.subprocess.run') as mock_run:
        mock_run.side_effect = [git_check, status_result, log_result]
        result = get_recent_changes("/test/path")

    assert result is not None, "Should detect changes"
    lines = result.split('\n')
    # Should have 5 files + "... and N more changes" message
    assert len(lines) == 6, "Should truncate to 5 changes plus more message"
    assert "... and 2 more changes" in result


def test_get_recent_changes_exception_handling():
    """Test that exceptions are handled gracefully."""
    with patch('stop.subprocess.run', side_effect=Exception("Git command failed")):
        result = get_recent_changes("/test/path")

    assert result is None, "Should return None on exceptions"


if __name__ == "__main__":
    # Simple test runner
    test_functions = [
        test_get_recent_changes_not_git_repo,
        test_get_recent_changes_with_working_changes,
        test_get_recent_changes_with_commits,
        test_get_recent_changes_no_changes,
        test_get_recent_changes_truncation,
        test_get_recent_changes_exception_handling,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
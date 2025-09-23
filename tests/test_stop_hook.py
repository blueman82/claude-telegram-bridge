#!/usr/bin/env python3
"""
Basic tests for stop hook core functionality.
"""

import sys
import os
import tempfile
import json
from unittest.mock import patch, mock_open

# Add the scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# Import functions from stop.py
from stop import generate_session_id, parse_targeted_message, save_session_mapping


def test_generate_session_id():
    """Test session ID generation creates consistent 6-char IDs."""
    session_id = "test-session-123"
    project = "my_project"

    # Should always generate same ID for same inputs
    id1 = generate_session_id(session_id, project)
    id2 = generate_session_id(session_id, project)

    assert id1 == id2, "Session ID should be deterministic"
    assert len(id1) == 6, "Session ID should be 6 characters"
    assert id1.isalnum(), "Session ID should be alphanumeric"


def test_generate_session_id_uniqueness():
    """Test that different inputs generate different session IDs."""
    base_session = "test-session"

    id1 = generate_session_id(base_session, "project1")
    id2 = generate_session_id(base_session, "project2")
    id3 = generate_session_id("different-session", "project1")

    assert id1 != id2, "Different projects should generate different IDs"
    assert id1 != id3, "Different sessions should generate different IDs"
    assert id2 != id3, "All combinations should be unique"


def test_parse_targeted_message_valid():
    """Test parsing valid targeted messages."""
    target_session = "abc123"

    # Valid message
    result = parse_targeted_message("abc123:hello world", target_session)
    assert result == "hello world", "Should extract message content"

    # With extra colons in message
    result = parse_targeted_message("abc123:check this: error", target_session)
    assert result == "check this: error", "Should handle colons in message"

    # With whitespace
    result = parse_targeted_message("  abc123 : hello  ", target_session)
    assert result == "hello", "Should handle whitespace"


def test_parse_targeted_message_invalid():
    """Test parsing invalid or non-targeted messages."""
    target_session = "abc123"

    # Wrong session ID
    result = parse_targeted_message("xyz789:hello", target_session)
    assert result is None, "Should reject wrong session ID"

    # No colon
    result = parse_targeted_message("abc123 hello", target_session)
    assert result is None, "Should reject messages without colon"

    # Empty message
    result = parse_targeted_message("abc123:", target_session)
    assert result == "", "Should handle empty message"

    # Too short
    result = parse_targeted_message("abc:hi", target_session)
    assert result is None, "Should reject too short messages"


def test_parse_targeted_message_case_insensitive():
    """Test that session ID matching is case insensitive."""
    target_session = "AbC123"

    result = parse_targeted_message("abc123:hello", target_session)
    assert result == "hello", "Should be case insensitive"

    result = parse_targeted_message("ABC123:world", target_session)
    assert result == "world", "Should handle uppercase"


def test_save_session_mapping_new_session():
    """Test saving a new session mapping."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        with patch('stop.os.path.expanduser', return_value=tmp_path):
            save_session_mapping("abc123", "real-session-id", "/test/path")

        # Read and verify the saved data
        with open(tmp_path, 'r') as f:
            data = json.load(f)

        assert "abc123" in data, "Should save session mapping"
        session_data = data["abc123"]
        assert session_data["session_id"] == "real-session-id"
        assert session_data["cwd"] == "/test/path"
        assert "timestamp" in session_data
        assert "start_time" in session_data

    finally:
        os.unlink(tmp_path)


def test_save_session_mapping_existing_session():
    """Test updating an existing session mapping preserves start_time."""
    initial_data = {
        "abc123": {
            "session_id": "old-session",
            "cwd": "/old/path",
            "timestamp": 1000,
            "start_time": 500
        }
    }

    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        json.dump(initial_data, tmp)
        tmp_path = tmp.name

    try:
        with patch('stop.os.path.expanduser', return_value=tmp_path):
            save_session_mapping("abc123", "new-session-id", "/new/path")

        # Read and verify the updated data
        with open(tmp_path, 'r') as f:
            data = json.load(f)

        session_data = data["abc123"]
        assert session_data["session_id"] == "new-session-id"
        assert session_data["cwd"] == "/new/path"
        assert session_data["start_time"] == 500, "Should preserve original start_time"
        assert session_data["timestamp"] > 1000, "Should update timestamp"

    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    # Simple test runner
    test_functions = [
        test_generate_session_id,
        test_generate_session_id_uniqueness,
        test_parse_targeted_message_valid,
        test_parse_targeted_message_invalid,
        test_parse_targeted_message_case_insensitive,
        test_save_session_mapping_new_session,
        test_save_session_mapping_existing_session,
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
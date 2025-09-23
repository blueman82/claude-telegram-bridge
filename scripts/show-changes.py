#!/usr/bin/env python3
"""
Show git changes for a specific Claude session.

Usage:
    show-changes <session_id>
    show-changes <session_id> --full  # Show full diff
    show-changes <session_id> --files # Show only file list
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def load_session_data(session_id):
    """Load session data from .sessions file."""
    sessions_file = os.path.expanduser('~/.claude/.sessions')
    if not os.path.exists(sessions_file):
        return None

    try:
        with open(sessions_file, 'r') as f:
            sessions = json.load(f)
        return sessions.get(session_id)
    except:
        return None


def get_git_changes(cwd, since_time=None, show_diff=False):
    """Get git changes for the session directory."""
    try:
        # Check if this is a git repository
        git_check = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if git_check.returncode != 0:
            return "Not a git repository"

        results = []

        # Get git status for working changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True
        )

        if status_result.returncode == 0 and status_result.stdout.strip():
            results.append("📋 Working Directory Changes:")
            results.append("=" * 40)

            status_lines = status_result.stdout.strip().split('\n')
            for line in status_lines:
                if len(line) >= 3:
                    status = line[:2]
                    filename = line[3:]

                    # Determine change type
                    if 'M' in status:
                        change_type = "✏️ Modified"
                    elif 'A' in status:
                        change_type = "➕ Added"
                    elif 'D' in status:
                        change_type = "➖ Deleted"
                    elif '?' in status:
                        change_type = "📄 Untracked"
                    else:
                        change_type = "📝 Changed"

                    results.append(f"{change_type}: {filename}")

                    # Show diff for modified files if requested
                    if show_diff and 'M' in status:
                        diff_result = subprocess.run(
                            ["git", "diff", filename],
                            cwd=cwd,
                            capture_output=True,
                            text=True
                        )
                        if diff_result.returncode == 0 and diff_result.stdout.strip():
                            results.append(f"\nDiff for {filename}:")
                            results.append("-" * 30)
                            results.append(diff_result.stdout.strip())
                            results.append("")

        # Get recent commits if no working changes
        if not status_result.stdout.strip():
            commits_result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--since=2 hours ago"],
                cwd=cwd,
                capture_output=True,
                text=True
            )

            if commits_result.returncode == 0 and commits_result.stdout.strip():
                results.append("📦 Recent Commits (last 2 hours):")
                results.append("=" * 40)

                commit_lines = commits_result.stdout.strip().split('\n')
                for commit_line in commit_lines:
                    if commit_line.strip():
                        commit_hash = commit_line.split()[0]
                        commit_msg = ' '.join(commit_line.split()[1:])
                        results.append(f"📦 {commit_hash}: {commit_msg}")

                        # Show commit diff if requested
                        if show_diff:
                            diff_result = subprocess.run(
                                ["git", "show", "--stat", commit_hash],
                                cwd=cwd,
                                capture_output=True,
                                text=True
                            )
                            if diff_result.returncode == 0:
                                results.append(f"\nCommit {commit_hash} changes:")
                                results.append("-" * 30)
                                results.append(diff_result.stdout.strip())
                                results.append("")

        return '\n'.join(results) if results else "No git changes found"

    except Exception as e:
        return f"Error checking git changes: {e}"


def main():
    parser = argparse.ArgumentParser(description="Show git changes for a Claude session")
    parser.add_argument("session_id", help="Session ID to show changes for")
    parser.add_argument("--full", action="store_true", help="Show full diff content")
    parser.add_argument("--files", action="store_true", help="Show only file list (default)")

    args = parser.parse_args()

    # Load session data
    session_data = load_session_data(args.session_id)
    if not session_data:
        print(f"❌ Session {args.session_id} not found")
        print("\nAvailable sessions:")

        # Show available sessions
        sessions_file = os.path.expanduser('~/.claude/.sessions')
        if os.path.exists(sessions_file):
            try:
                with open(sessions_file, 'r') as f:
                    sessions = json.load(f)
                for sid, data in sessions.items():
                    cwd = data.get('cwd', 'unknown')
                    project = os.path.basename(cwd)
                    print(f"  {sid}: {project}")
            except:
                print("  (unable to read sessions file)")

        sys.exit(1)

    cwd = session_data.get('cwd')
    if not cwd or not os.path.exists(cwd):
        print(f"❌ Session directory not found: {cwd}")
        sys.exit(1)

    project = os.path.basename(cwd)
    start_time = session_data.get('start_time')

    print(f"🔍 Git Changes for Session {args.session_id}")
    print(f"📁 Project: {project}")
    print(f"📂 Directory: {cwd}")
    if start_time:
        import datetime
        start_dt = datetime.datetime.fromtimestamp(start_time)
        print(f"⏰ Session started: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Show git changes
    show_diff = args.full
    changes = get_git_changes(cwd, start_time, show_diff)
    print(changes)


if __name__ == "__main__":
    main()
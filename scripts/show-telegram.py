#!/usr/bin/env python3
"""
Simple tool to show what happened in a Telegram conversation
Usage: show-telegram.py 81950c
"""
import json
import sys
from pathlib import Path

def load_sessions():
    """Load session mappings"""
    sessions_file = Path.home() / '.claude' / '.sessions'
    if sessions_file.exists():
        try:
            return json.loads(sessions_file.read_text())
        except:
            print("Error reading sessions file")
    return {}

def show_transcript(session_id):
    """Display the conversation from a session transcript"""
    # First try short session ID
    sessions = load_sessions()
    session_info = sessions.get(session_id)

    if not session_info:
        # Try as full session ID
        for short_id, info in sessions.items():
            if info.get('session_id') == session_id:
                session_info = info
                break

    if not session_info:
        print(f"Session {session_id} not found")
        return False

    # Find the transcript file
    real_session_id = session_info.get('session_id')
    cwd = session_info.get('cwd', '')

    # Build correct transcript path (handle underscores in directory names)
    # Replace slashes with hyphens, then underscores with hyphens
    project_path = cwd.replace('/', '-').replace('_', '-')
    transcript_file = Path.home() / '.claude' / 'projects' / project_path / f"{real_session_id}.jsonl"

    if not transcript_file.exists():
        print(f"Transcript not found for session {session_id}")
        print(f"Looked in: {transcript_file}")
        return False

    print(f"\n{'='*60}")
    print(f"📱 Telegram Session: {session_id}")
    print(f"📂 Project: {Path(cwd).name}")
    print(f"{'='*60}\n")

    # Read and display the conversation
    with open(transcript_file, 'r') as f:
        lines = f.readlines()

    conversation_started = False
    message_count = 0

    for line in lines:
        try:
            data = json.loads(line)

            # Look for user messages (likely from Telegram)
            if data.get('type') == 'user':
                message = data.get('message', {})
                content = message.get('content', '')

                # Check if this looks like a Telegram-injected message
                if 'User replied via Telegram:' in content:
                    if not conversation_started:
                        print("🔄 Telegram Conversation Started\n")
                        conversation_started = True

                    # Extract the actual message
                    telegram_msg = content.replace('User replied via Telegram:', '').strip()
                    print(f"👤 You: {telegram_msg}\n")
                    message_count += 1

            # Show assistant responses after Telegram started
            elif conversation_started and data.get('type') == 'assistant':
                message = data.get('message', {})
                content = message.get('content', '')

                # Handle both string and list content
                if isinstance(content, list):
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict) and part.get('type') == 'text':
                            text_parts.append(part.get('text', ''))
                    content = '\n'.join(text_parts)

                if content and len(content.strip()) > 10:
                    # Truncate very long responses
                    if len(content) > 500:
                        content = content[:500] + '...\n[truncated]'
                    print(f"🤖 Claude: {content}\n")
                    print("-" * 40 + "\n")

        except json.JSONDecodeError:
            continue

    if not conversation_started:
        print("No Telegram messages found in this session")
        print("(Session may have been terminal-only)")
    else:
        print(f"{'='*60}")
        print(f"📊 Total Telegram exchanges: {message_count}")
        print(f"{'='*60}\n")

    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: show-telegram 81950c")
        print("       show-telegram <session-id>")
        sys.exit(1)

    session_id = sys.argv[1]
    show_transcript(session_id)

if __name__ == "__main__":
    main()
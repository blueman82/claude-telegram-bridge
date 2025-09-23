#!/usr/bin/env python3
"""
Simple Telegram listener that resumes Claude sessions using claude --resume
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

def load_session_mapping():
    """Load session ID mappings"""
    sessions_file = Path.home() / '.claude' / '.sessions'
    if sessions_file.exists():
        try:
            return json.loads(sessions_file.read_text())
        except:
            pass
    return {}

def parse_targeted_message(message):
    """Parse message with format 'session_id:message'"""
    if ':' in message and len(message) > 7:
        parts = message.split(':', 1)
        session_id = parts[0].strip().lower()
        text = parts[1].strip()

        # Validate session_id format (6 hex chars)
        if len(session_id) == 6 and all(c in '0123456789abcdef' for c in session_id):
            return session_id, text

    return None, None

def resume_claude_session(real_session_id, message, cwd):
    """Resume Claude session with message using claude --resume"""
    try:
        # Add prefix so show-telegram can find the conversation later
        prefixed_message = f"User replied via Telegram: {message}"

        # Use claude --resume to continue the exact same session
        subprocess.Popen([
            'claude', '--resume', real_session_id, prefixed_message
        ], cwd=cwd)
        print(f"Resumed Claude session {real_session_id} with: {message}")
        return True
    except Exception as e:
        print(f"Failed to resume Claude session: {e}")
        return False

def main():
    """Main listener loop"""
    # Load environment
    env_file = Path.home() / '.claude' / '.env'
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

    api_key = os.getenv('TELEGRAM_API')
    chat_id_file = Path.home() / '.claude' / '.chat_id'

    if not api_key or not chat_id_file.exists():
        print("Missing TELEGRAM_API or .chat_id file")
        sys.exit(1)

    chat_id = chat_id_file.read_text().strip()
    last_update_id = 0

    print("Simple Telegram→Claude listener started...")

    while True:
        try:
            import requests

            # Long polling
            url = f"https://api.telegram.org/bot{api_key}/getUpdates"
            params = {'timeout': 30, 'offset': last_update_id + 1}

            resp = requests.get(url, params=params, timeout=35)
            data = resp.json()

            if not data.get('ok'):
                time.sleep(5)
                continue

            for update in data.get('result', []):
                last_update_id = max(last_update_id, update.get('update_id', 0))

                message = update.get('message', {})
                if str(message.get('chat', {}).get('id')) == chat_id:
                    text = message.get('text', '').strip()

                    # Parse targeted message
                    short_id, reply_text = parse_targeted_message(text)
                    if short_id and reply_text:
                        print(f"Got targeted reply for {short_id}: {reply_text}")

                        # Load session mappings
                        sessions = load_session_mapping()
                        session_info = sessions.get(short_id)

                        if session_info:
                            real_session_id = session_info['session_id']
                            cwd = session_info['cwd']

                            # Resume the exact same Claude session
                            if resume_claude_session(real_session_id, reply_text, cwd):
                                print(f"Session {short_id} resumed successfully")
                            else:
                                print(f"Failed to resume session {short_id}")
                        else:
                            print(f"Session {short_id} not found")

        except requests.Timeout:
            continue
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
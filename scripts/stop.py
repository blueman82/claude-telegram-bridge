#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///

import argparse
import json
import os
import random
import subprocess
import sys
import hashlib
import time
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()


def get_completion_messages():
    """Return list of friendly completion messages."""
    return [
        "Work complete!",
        "All done!",
        "Task finished!",
        "Job complete!",
        "Ready for next task!",
    ]


def get_tts_script_path():
    """
    Determine which TTS script to use based on available API keys.
    Priority order: ElevenLabs > OpenAI > pyttsx3
    """
    # Get current script directory and construct utils/tts path
    script_dir = Path(__file__).parent
    tts_dir = script_dir / "utils" / "tts"

    # Check for ElevenLabs API key (highest priority)
    if os.getenv("ELEVENLABS_API_KEY"):
        elevenlabs_script = tts_dir / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            return str(elevenlabs_script)

    # Check for OpenAI API key (second priority)
    if os.getenv("OPENAI_API_KEY"):
        openai_script = tts_dir / "openai_tts.py"
        if openai_script.exists():
            return str(openai_script)

    # Fall back to pyttsx3 (no API key required)
    pyttsx3_script = tts_dir / "pyttsx3_tts.py"
    if pyttsx3_script.exists():
        return str(pyttsx3_script)

    return None


def get_llm_completion_message():
    """
    Generate completion message using available LLM services.
    Priority order: OpenAI > Anthropic > Ollama > fallback to random message

    Returns:
        str: Generated or fallback completion message
    """
    # Get current script directory and construct utils/llm path
    script_dir = Path(__file__).parent
    llm_dir = script_dir / "utils" / "llm"

    # Try OpenAI first (highest priority)
    if os.getenv("OPENAI_API_KEY"):
        oai_script = llm_dir / "oai.py"
        if oai_script.exists():
            try:
                result = subprocess.run(
                    ["uv", "run", str(oai_script), "--completion"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Try Anthropic second
    if os.getenv("ANTHROPIC_API_KEY"):
        anth_script = llm_dir / "anth.py"
        if anth_script.exists():
            try:
                result = subprocess.run(
                    ["uv", "run", str(anth_script), "--completion"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Try Ollama third (local LLM)
    ollama_script = llm_dir / "ollama.py"
    if ollama_script.exists():
        try:
            result = subprocess.run(
                ["uv", "run", str(ollama_script), "--completion"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

    # Fallback to random predefined message
    messages = get_completion_messages()
    return random.choice(messages)


def get_recent_changes(cwd, since_time=None):
    """Get git changes since the session started or last commit."""
    try:
        # Check if this is a git repository
        git_check = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if git_check.returncode != 0:
            return None

        # Get git status for staged/unstaged changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True
        )

        # Get recent commits (last 10) if no working changes
        commits_result = subprocess.run(
            ["git", "log", "--oneline", "-10", "--since=1 hour ago"],
            cwd=cwd,
            capture_output=True,
            text=True
        )

        changes = []

        # Parse git status output
        if status_result.returncode == 0 and status_result.stdout.strip():
            status_lines = status_result.stdout.strip().split('\n')
            for line in status_lines:
                if len(line) >= 3:
                    status = line[:2]
                    filename = line[3:]

                    # Determine change type
                    if 'M' in status:
                        change_type = "✏️"
                        action = "modified"
                    elif 'A' in status:
                        change_type = "➕"
                        action = "added"
                    elif 'D' in status:
                        change_type = "➖"
                        action = "deleted"
                    elif '?' in status:
                        change_type = "📄"
                        action = "untracked"
                    else:
                        change_type = "📝"
                        action = "changed"

                    changes.append(f"{change_type} {filename} ({action})")

        # If no working changes but recent commits, show those
        elif commits_result.returncode == 0 and commits_result.stdout.strip():
            commit_lines = commits_result.stdout.strip().split('\n')[:3]  # Max 3 commits
            for commit_line in commit_lines:
                if commit_line.strip():
                    commit_hash = commit_line.split()[0]
                    commit_msg = ' '.join(commit_line.split()[1:])[:50]
                    changes.append(f"📦 {commit_hash}: {commit_msg}")

        if not changes:
            return None

        # Limit to first 5 changes to avoid long messages
        if len(changes) > 5:
            display_changes = changes[:5]
            display_changes.append(f"... and {len(changes) - 5} more changes")
        else:
            display_changes = changes

        return '\n'.join(display_changes)

    except Exception:
        return None


def generate_session_id(session_id, project):
    """Generate a simple 6-character session ID"""
    combined = f"{session_id}-{project}"
    hash_obj = hashlib.md5(combined.encode())
    return hash_obj.hexdigest()[:6]


def cleanup_old_sessions(max_age_days=30):
    """Clean up sessions older than max_age_days to prevent unlimited growth."""
    try:
        sessions_file = Path.home() / '.claude' / '.sessions'
        if not sessions_file.exists():
            return

        # Load existing sessions
        with sessions_file.open('r') as f:
            sessions = json.load(f)

        # Calculate cutoff time (30 days ago)
        cutoff_time = int(time.time()) - (max_age_days * 24 * 60 * 60)

        # Filter out old sessions
        original_count = len(sessions)
        sessions = {
            session_id: session_data
            for session_id, session_data in sessions.items()
            if session_data.get('timestamp', 0) > cutoff_time
        }

        # Only write back if we actually removed sessions
        if len(sessions) < original_count:
            with sessions_file.open('w') as f:
                json.dump(sessions, f, indent=2)

    except Exception:
        pass  # Fail silently


def save_session_mapping(short_session_id, real_session_id, cwd):
    """Save short session ID to real session ID and directory mapping"""
    try:
        sessions_file = os.path.expanduser('~/.claude/.sessions')

        # Load existing mappings
        sessions = {}
        if os.path.exists(sessions_file):
            try:
                with open(sessions_file, 'r') as f:
                    sessions = json.load(f)
            except:
                pass

        current_time = int(time.time())

        # Update mapping - preserve start_time if session exists, otherwise set it
        if short_session_id in sessions:
            start_time = sessions[short_session_id].get("start_time", current_time)
        else:
            start_time = current_time

        sessions[short_session_id] = {
            "session_id": real_session_id,
            "cwd": cwd,
            "timestamp": current_time,
            "start_time": start_time
        }

        # Save back
        with open(sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)

        # Occasionally clean up old sessions (10% chance)
        if random.randint(1, 10) == 1:
            cleanup_old_sessions()
    except:
        pass  # Fail silently


def parse_targeted_message(message, target_session_id):
    """Parse message with format 'session_id:message' - only return if targeting our session"""
    if ':' in message and len(message) > 7:  # Minimum: "abc123:hi"
        parts = message.split(':', 1)
        session_id = parts[0].strip().lower()
        text = parts[1].strip()

        # Check if it's targeting our session
        if session_id == target_session_id.lower():
            return text

    return None


def load_processed_messages():
    """Load list of processed message IDs"""
    processed_file = os.path.expanduser('~/.claude/.processed_messages')
    if os.path.exists(processed_file):
        try:
            with open(processed_file, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        except:
            pass
    return set()


def save_processed_message(update_id):
    """Save a processed message ID"""
    processed_file = os.path.expanduser('~/.claude/.processed_messages')
    try:
        with open(processed_file, 'a') as f:
            f.write(f"{update_id}\n")
    except:
        pass


def check_for_telegram_reply(target_session_id):
    """Check for pending Telegram replies targeting our session from last 24 hours"""
    try:
        # Load environment from Claude directory
        env_file = os.path.expanduser('~/.claude/.env')
        if os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)

        api_key = os.getenv('TELEGRAM_API')
        if not api_key:
            return None

        # Get chat ID
        chat_id_file = os.path.expanduser('~/.claude/.chat_id')
        if not os.path.exists(chat_id_file):
            return None

        with open(chat_id_file, 'r') as f:
            chat_id = f.read().strip()

        # Load processed messages
        processed_messages = load_processed_messages()

        # Check for new messages
        url = f"https://api.telegram.org/bot{api_key}/getUpdates"
        resp = requests.get(url, timeout=5)
        data = resp.json()

        if not data.get('result'):
            return None

        # Find latest unprocessed message from our chat targeting our session
        latest_reply = None
        latest_update_id = 0

        for update in reversed(data['result']):
            update_id = str(update.get('update_id', ''))

            # Skip if already processed
            if update_id in processed_messages:
                continue

            message = update.get('message', {})
            if str(message.get('chat', {}).get('id')) == chat_id:
                text = message.get('text', '').strip()
                timestamp = message.get('date', 0)

                # Check messages from last 24 hours
                import time
                if text and len(text) > 1 and (time.time() - timestamp) < 86400:  # 24 hours
                    # Check if message is targeting our session
                    targeted_message = parse_targeted_message(text, target_session_id)
                    if targeted_message:
                        latest_reply = targeted_message
                        latest_update_id = update_id
                        break

        if latest_reply:
            # Mark message as processed
            save_processed_message(latest_update_id)
            return latest_reply

        return None

    except Exception:
        return None


def send_telegram_notification(input_data=None):
    """Send Telegram notification with session summary and session ID."""
    try:
        # Load environment from Claude directory
        env_file = os.path.expanduser('~/.claude/.env')
        if os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)

        api_key = os.getenv('TELEGRAM_API')
        if not api_key:
            return

        # Get chat ID
        chat_id_file = os.path.expanduser('~/.claude/.chat_id')
        if not os.path.exists(chat_id_file):
            return

        with open(chat_id_file, 'r') as f:
            chat_id = f.read().strip()

        # Generate session ID
        real_session_id = input_data.get('session_id', 'unknown')
        project = os.path.basename(input_data.get('cwd', 'project'))
        cwd = input_data.get('cwd', os.getcwd())
        short_session_id = generate_session_id(real_session_id, project)

        # Save session mapping for Telegram service
        save_session_mapping(short_session_id, real_session_id, cwd)

        # Send Claude's latest response with session ID (using HTML)
        timestamp = datetime.now().strftime("%H:%M")
        summary = f"🤖 <b>Session {short_session_id}</b> - {project} ({timestamp})\n\n"

        # Add git changes if available
        git_changes = get_recent_changes(cwd)
        if git_changes:
            summary += f"📂 <b>Recent changes:</b>\n{git_changes}\n\n"

        # Get session data and extract Claude's latest response
        session_data = input_data or {}
        transcript_path = session_data.get('transcript_path', '')

        if transcript_path and os.path.exists(transcript_path):
            try:
                # Read transcript and find latest assistant message
                with open(transcript_path, 'r') as f:
                    lines = f.readlines()

                # Find the most recent assistant response
                claude_response = None
                for line in reversed(lines):
                    try:
                        data = json.loads(line)
                        if (data.get('type') == 'assistant' and
                            data.get('message', {}).get('role') == 'assistant'):

                            content = data.get('message', {}).get('content', '')
                            if isinstance(content, list):
                                # Extract text content, excluding tool calls
                                text_parts = []
                                for part in content:
                                    if part.get('type') == 'text':
                                        text_parts.append(part.get('text', ''))
                                claude_response = '\n'.join(text_parts)
                            else:
                                claude_response = content

                            if claude_response and len(claude_response.strip()) > 10:
                                break
                    except:
                        continue

                if claude_response:
                    # Escape HTML entities first
                    html_response = claude_response.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    # Convert markdown to HTML
                    import re
                    # Headers: ### -> bold, ## -> bold, # -> bold (Telegram doesn't have H tags)
                    html_response = re.sub(r'^### (.+)$', r'<b>\1</b>', html_response, flags=re.MULTILINE)
                    html_response = re.sub(r'^## (.+)$', r'<b>\1</b>', html_response, flags=re.MULTILINE)
                    html_response = re.sub(r'^# (.+)$', r'<b>\1</b>', html_response, flags=re.MULTILINE)
                    # Bold: **text** -> <b>text</b>
                    html_response = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html_response)
                    # Italic: *text* -> <i>text</i>  (but not part of bold)
                    html_response = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', html_response)
                    # Code: `text` -> <code>text</code>
                    html_response = re.sub(r'`([^`]+?)`', r'<code>\1</code>', html_response)
                    # Lists: - item -> • item (convert markdown lists to bullets)
                    html_response = re.sub(r'^- (.+)$', r'• \1', html_response, flags=re.MULTILINE)
                    html_response = re.sub(r'^\* (.+)$', r'• \1', html_response, flags=re.MULTILINE)
                    summary += "\n" + html_response + "\n"
                else:
                    summary += "\n<i>Claude response processed</i>\n"

            except:
                summary += "*Response processing...*"
        else:
            summary += "*Claude task completed*"

        summary += f"\n\nReply: {short_session_id}:your message"

        # Send message with HTML formatting to preserve Claude's markdown
        url = f"https://api.telegram.org/bot{api_key}/sendMessage"
        data = {'chat_id': chat_id, 'text': summary, 'parse_mode': 'HTML'}
        requests.post(url, json=data, timeout=5)

    except Exception:
        pass  # Fail silently


def announce_completion():
    """Announce completion using the best available TTS service."""
    try:
        tts_script = get_tts_script_path()
        if not tts_script:
            return  # No TTS scripts available

        # Get completion message (LLM-generated or fallback)
        completion_message = get_llm_completion_message()

        # Call the TTS script with the completion message
        subprocess.run(
            ["uv", "run", tts_script, completion_message],
            capture_output=True,  # Suppress output
            timeout=10,  # 10-second timeout
        )

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        # Fail silently if TTS encounters issues
        pass
    except Exception:
        # Fail silently for any other errors
        pass


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--chat", action="store_true", help="Copy transcript to chat.json"
        )
        parser.add_argument(
            "--notify", action="store_true", help="Enable TTS completion announcement"
        )
        args = parser.parse_args()

        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Extract required fields
        session_id = input_data.get("session_id", "")
        stop_hook_active = input_data.get("stop_hook_active", False)

        # Ensure log directory exists
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "stop.json")

        # Read existing log data or initialize empty list
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        # Append new data
        log_data.append(input_data)

        # Write back to file with formatting
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)

        # Handle --chat switch
        if args.chat and "transcript_path" in input_data:
            transcript_path = input_data["transcript_path"]
            if os.path.exists(transcript_path):
                # Read .jsonl file and convert to JSON array
                chat_data = []
                try:
                    with open(transcript_path, "r") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    chat_data.append(json.loads(line))
                                except json.JSONDecodeError:
                                    pass  # Skip invalid lines

                    # Write to logs/chat.json
                    chat_file = os.path.join(log_dir, "chat.json")
                    with open(chat_file, "w") as f:
                        json.dump(chat_data, f, indent=2)
                except Exception:
                    pass  # Fail silently

        # Send Telegram notification
        send_telegram_notification(input_data)

        # Generate session ID for reply checking
        session_id = input_data.get('session_id', 'unknown')
        project = os.path.basename(input_data.get('cwd', 'project'))
        short_session_id = generate_session_id(session_id, project)

        # Check for immediate Telegram reply (within last few seconds)
        telegram_reply = check_for_telegram_reply(short_session_id)

        if telegram_reply:
            # Block stopping and continue with Telegram reply
            response = {
                "decision": "block",
                "reason": f"User replied via Telegram: {telegram_reply}"
            }
            print(json.dumps(response))
            sys.exit(0)

        # Announce completion via TTS (only if --notify flag is set)
        if args.notify:
            announce_completion()

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()

"""Session Context Manager - Short-term memory for conversation state"""
import json
from datetime import datetime
from pathlib import Path

SESSION_FILE = "6-session-context.json"

def load_session(book_dir):
    """Load or create session context"""
    session_path = Path(book_dir) / SESSION_FILE
    if session_path.exists():
        with open(session_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return create_new_session()

def create_new_session():
    """Create new session context"""
    return {
        "current_phase": None,
        "pending_confirmation": None,
        "user_modifications": [],
        "generation_attempts": 0,
        "temp_outline_draft": None,
        "chapter_draft_segments": [],
        "last_action": None,
        "timestamp": datetime.now().isoformat()
    }

def save_session(book_dir, session):
    """Save session context"""
    session["timestamp"] = datetime.now().isoformat()
    session_path = Path(book_dir) / SESSION_FILE
    with open(session_path, 'w', encoding='utf-8') as f:
        json.dump(session, f, indent=2, ensure_ascii=False)

def record_pending(book_dir, content_type, content):
    """Record content waiting for user confirmation"""
    session = load_session(book_dir)
    session["pending_confirmation"] = {
        "type": content_type,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    save_session(book_dir, session)

def record_modification(book_dir, modification):
    """Record user's modification request"""
    session = load_session(book_dir)
    session["user_modifications"].append({
        "request": modification,
        "timestamp": datetime.now().isoformat()
    })
    save_session(book_dir, session)

def clear_pending(book_dir):
    """Clear pending confirmation after user confirms"""
    session = load_session(book_dir)
    session["pending_confirmation"] = None
    session["user_modifications"] = []
    save_session(book_dir, session)

def set_phase(book_dir, phase):
    """Set current workflow phase"""
    session = load_session(book_dir)
    session["current_phase"] = phase
    save_session(book_dir, session)

def record_action(book_dir, action):
    """Record last action performed"""
    session = load_session(book_dir)
    session["last_action"] = action
    save_session(book_dir, session)

def get_recovery_info(book_dir):
    """Get info for resuming after interruption"""
    session = load_session(book_dir)
    if not session["current_phase"]:
        return None
    return {
        "phase": session["current_phase"],
        "has_pending": session["pending_confirmation"] is not None,
        "modifier_count": len(session["user_modifications"]),
        "last_action": session["last_action"]
    }

def can_resume(book_dir):
    """Check if there's a session to resume"""
    return (Path(book_dir) / SESSION_FILE).exists()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: session_context.py <book_dir> <command> [args]")
        print("Commands: load, save, phase, pending, clear")
        sys.exit(1)
    
    book_dir, cmd = sys.argv[1], sys.argv[2]
    
    if cmd == "load":
        print(json.dumps(load_session(book_dir), indent=2, ensure_ascii=False))
    elif cmd == "phase":
        set_phase(book_dir, sys.argv[3])
        print(f"Phase set to: {sys.argv[3]}")
    elif cmd == "recovery":
        info = get_recovery_info(book_dir)
        print(json.dumps(info, indent=2, ensure_ascii=False) if info else "No session to resume")

"""
Novel Writing State Manager
Tracks progress of each book being written
"""
import json
import os
from datetime import datetime
from pathlib import Path

def get_novels_dir():
    """Get the novels working directory"""
    # Default Windows path, can be overridden by environment variable
    base_path = os.environ.get("NOVELS_DIR", "C:\\Users\\10179\\clawd\\novels")
    return Path(base_path)

def get_registry_path():
    """Get the books registry file path"""
    return get_novels_dir() / "books-registry.json"

def ensure_workspace():
    """Ensure novels directory exists"""
    novels_dir = get_novels_dir()
    novels_dir.mkdir(parents=True, exist_ok=True)
    return novels_dir

def create_new_book(genre, target_words, book_title=None):
    """Create a new book workspace"""
    ensure_workspace()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not book_title:
        book_title = f"novel_{timestamp}"
    
    # Sanitize title for folder name
    safe_title = "".join(c for c in book_title if c.isalnum() or c in "-_").strip()
    book_dir = get_novels_dir() / f"{timestamp}_{safe_title}"
    book_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (book_dir / "chapters").mkdir(exist_ok=True)
    (book_dir / "drafts").mkdir(exist_ok=True)
    (book_dir / "final").mkdir(exist_ok=True)
    
    # Initialize book config
    config = {
        "book_id": f"{timestamp}_{safe_title}",
        "title": book_title,
        "genre": genre,
        "target_words": target_words,
        "created_at": datetime.now().isoformat(),
        "status": "outlining",  # outlining, worldbuilding, writing, completed
        "current_chapter": 0,
        "total_chapters": 0,
        "completed_words": 0
    }
    
    with open(book_dir / "0-book-config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Update registry
    registry = load_registry()
    registry[config["book_id"]] = {
        "title": book_title,
        "path": str(book_dir),
        "status": config["status"],
        "created_at": config["created_at"]
    }
    save_registry(registry)
    
    return book_dir, config

def load_registry():
    """Load books registry"""
    registry_path = get_registry_path()
    if registry_path.exists():
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_registry(registry):
    """Save books registry"""
    registry_path = get_registry_path()
    ensure_workspace()
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def get_book_path(book_id_or_title):
    """Find book path by ID or title"""
    registry = load_registry()
    
    # Try exact ID match first
    if book_id_or_title in registry:
        return registry[book_id_or_title]["path"]
    
    # Try title match
    for book_id, info in registry.items():
        if info["title"] == book_id_or_title:
            return info["path"]
    
    # Try partial match
    matches = []
    for book_id, info in registry.items():
        if book_id_or_title.lower() in book_id.lower() or book_id_or_title.lower() in info["title"].lower():
            matches.append((book_id, info["path"]))
    
    if len(matches) == 1:
        return matches[0][1]
    elif len(matches) > 1:
        raise ValueError(f"Multiple books match '{book_id_or_title}': {[m[0] for m in matches]}")
    
    raise ValueError(f"Book not found: {book_id_or_title}")

def load_book_config(book_dir):
    """Load book configuration"""
    config_path = Path(book_dir) / "0-book-config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_book_config(book_dir, config):
    """Save book configuration"""
    config_path = Path(book_dir) / "0-book-config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Also update registry
    registry = load_registry()
    if config["book_id"] in registry:
        registry[config["book_id"]]["status"] = config["status"]
        save_registry(registry)

def update_chapter_progress(book_dir, chapter_num):
    """Update current chapter progress"""
    config = load_book_config(book_dir)
    config["current_chapter"] = chapter_num
    config["status"] = "writing"
    save_book_config(book_dir, config)

def list_books():
    """List all books in registry"""
    registry = load_registry()
    return registry

def get_writing_state(book_dir):
    """Load writing state"""
    state_path = Path(book_dir) / "4-writing-state.json"
    if state_path.exists():
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "current_chapter": 1,
        "chapters_completed": [],
        "total_words_written": 0,
        "last_modified": datetime.now().isoformat()
    }

def save_writing_state(book_dir, state):
    """Save writing state"""
    state_path = Path(book_dir) / "4-writing-state.json"
    state["last_modified"] = datetime.now().isoformat()
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: state_manager.py <command> [args]")
        print("Commands:")
        print("  create <genre> <target_words> [title] - Create new book")
        print("  list - List all books")
        print("  path <book_id_or_title> - Get book path")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "create":
        if len(sys.argv) < 4:
            print("Usage: state_manager.py create <genre> <target_words> [title]")
            sys.exit(1)
        genre = sys.argv[2]
        target_words = int(sys.argv[3])
        title = sys.argv[4] if len(sys.argv) > 4 else None
        book_dir, config = create_new_book(genre, target_words, title)
        print(f"Created book: {config['book_id']}")
        print(f"Path: {book_dir}")
        
    elif cmd == "list":
        books = list_books()
        for book_id, info in books.items():
            print(f"{book_id}: {info['title']} ({info['status']})")
            
    elif cmd == "path":
        if len(sys.argv) < 3:
            print("Usage: state_manager.py path <book_id_or_title>")
            sys.exit(1)
        path = get_book_path(sys.argv[2])
        print(path)

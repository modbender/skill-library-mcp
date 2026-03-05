"""
Fanfic Writer v2.0 - Workspace Manager
Handles workspace creation, run initialization, and directory management
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from .utils import (
    generate_run_id, generate_book_uid, to_slug, sanitize_filename,
    get_workspace_root, get_run_dir, create_directory_structure,
    get_timestamp_iso, validate_path_in_workspace, validate_run_id_consistency
)
from .atomic_io import atomic_write_json, atomic_append_jsonl


# ============================================================================
# Workspace Manager
# ============================================================================

class WorkspaceManager:
    """
    Manages novel workspace lifecycle:
    - Create new book workspace
    - Initialize new run
    - Validate workspace integrity
    - Handle resume/continue
    """
    
    def __init__(self, base_dir: Path):
        """
        Initialize WorkspaceManager
        
        Args:
            base_dir: Base directory for all novels (e.g., ~/.openclaw/novels)
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_new_book(
        self,
        book_title: str,
        genre: str,
        target_words: int,
        **kwargs
    ) -> Tuple[Path, str, str, Dict[str, Any]]:
        """
        Create a new book workspace with initial run
        
        Args:
            book_title: Book title (can be Chinese)
            genre: Genre (e.g., "都市灵异")
            target_words: Target word count (<= 500000)
            **kwargs: Additional config options
            
        Returns:
            Tuple of (run_dir, book_uid, run_id, paths_dict)
        """
        # Generate IDs
        book_uid = generate_book_uid(book_title)
        title_slug = to_slug(book_title)
        run_id = generate_run_id()
        
        # Create workspace structure
        workspace_root = get_workspace_root(self.base_dir, title_slug, book_uid)
        run_dir = get_run_dir(workspace_root, run_id)
        
        # Validate no collision
        if run_dir.exists():
            raise RuntimeError(f"Run directory already exists: {run_dir}")
        
        # Create directory structure
        paths = create_directory_structure(run_dir, book_title)
        
        # Generate initial config
        config = self._generate_initial_config(
            book_title=book_title,
            title_slug=title_slug,
            book_uid=book_uid,
            run_id=run_id,
            genre=genre,
            target_words=min(target_words, 500000),  # Hard limit
            **kwargs
        )
        
        # Write config atomically
        if not atomic_write_json(paths['book_config'], config):
            raise RuntimeError("Failed to write initial config")
        
        # Create lock file
        lock_data = {
            'run_id': run_id,
            'book_uid': book_uid,
            'title_slug': title_slug,
            'start_ts': get_timestamp_iso(),
            'pid': os.getpid(),
            'host': os.environ.get('COMPUTERNAME', 'unknown'),
            'mode': kwargs.get('mode', 'manual')
        }
        lock_path = run_dir / ".lock.json"
        atomic_write_json(lock_path, lock_data)
        
        # Create initial writing state
        writing_state = self._generate_initial_writing_state(
            book_title, run_id, kwargs.get('mode', 'manual')
        )
        atomic_write_json(paths['writing_state'], writing_state)
        
        # Create empty log files
        (paths['logs_dir'] / ".gitkeep").touch()
        (paths['logs_prompts'] / ".gitkeep").touch()
        
        return run_dir, book_uid, run_id, paths
    
    def _generate_initial_config(
        self,
        book_title: str,
        title_slug: str,
        book_uid: str,
        run_id: str,
        genre: str,
        target_words: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate initial 0-book-config.json"""
        
        chapter_target = kwargs.get('chapter_target_words', 2500)
        if chapter_target < 1500:
            chapter_target = 1500
        elif chapter_target > 8000:
            chapter_target = 8000
        
        return {
            'version': '2.0.0',
            'book': {
                'title': book_title,
                'title_slug': title_slug,
                'book_uid': book_uid,
                'subtitle': kwargs.get('subtitle', None),
                'genre': genre,
                'subgenre': kwargs.get('subgenre', None),
                'target_word_count': min(target_words, 500000),
                'chapter_target_words': chapter_target,
                'language': kwargs.get('language', 'zh'),
                'rating': kwargs.get('rating', 'PG-13'),
                'tone': kwargs.get('tone', '轻松')
            },
            'generation': {
                'model': kwargs.get('model', 'nvidia/moonshotai/kimi-k2.5'),
                'temperature_outline': kwargs.get('temperature_outline', 0.8),
                'temperature_chapter': kwargs.get('temperature_chapter', 0.75),
                'max_attempts': kwargs.get('max_attempts', 3),
                'mode': kwargs.get('mode', 'manual'),
                'auto_threshold': kwargs.get('auto_threshold', 85),
                'auto_rescue_enabled': kwargs.get('auto_rescue_enabled', True),
                'auto_rescue_max_rounds': kwargs.get('auto_rescue_max_rounds', 3)
            },
            'qc': {
                'enabled': True,
                'dimensions': [
                    'outline_adherence',
                    'main_plot',
                    'character',
                    'logic',
                    'continuity',
                    'pacing',
                    'style'
                ],
                'weights': {
                    'outline_adherence': 20,
                    'main_plot': 15,
                    'character': 15,
                    'logic': 20,
                    'continuity': 10,
                    'pacing': 10,
                    'style': 10
                },
                'pass_threshold': 85,
                'warning_threshold': 75
            },
            'backpatch': {
                'frequency_chapters': kwargs.get('backpatch_frequency', 5),
                'severity_threshold_for_block': 'high'
            },
            'time': {
                'timezone_standard': 'Asia/Shanghai',
                'timezone_offset': '+08:00',
                'timestamp_format': 'ISO8601'
            },
            'run_id': run_id,
            'created_at': get_timestamp_iso(),
            'updated_at': get_timestamp_iso()
        }
    
    def _generate_initial_writing_state(
        self,
        book_title: str,
        run_id: str,
        mode: str
    ) -> Dict[str, Any]:
        """Generate initial 4-writing-state.json"""
        return {
            'book_title': book_title,
            'run_id': run_id,
            'mode': mode,
            'current_chapter': 0,
            'completed_chapters': [],
            'current_attempt': 1,
            'qc_score': 0,
            'qc_status': 'INIT',
            'forced_streak': 0,
            'forced_streak_rules': {
                'increment_on_forced': 'forced_streak += 1',
                'reset_on_pass_warning': 'forced_streak = 0',
                'decrement_on_backpatch': 'forced_streak = max(0, forced_streak-1)',
                'threshold': 2
            },
            'flags': {
                'is_paused': False,
                'requires_backpatch': False,
                'prev_chapter_forced': False
            },
            'ending_state': 'not_ready',  # not_ready | ready_to_end | ended
            'ending_checklist': {
                'main_conflict_resolved': False,
                'core_arc_closed': False,
                'major_threads_resolved_ratio': 0.0,
                'final_hook_present': False
            },
            'last_state_commit': get_timestamp_iso(),
            'last_snapshot_id': None,
            'last_outline_summary': '',
            'warning_summary': None,
            'token_spent': 0,
            'cost_total_rmb': 0.0,
            'created_at': get_timestamp_iso(),
            'updated_at': get_timestamp_iso()
        }
    
    def detect_existing_run(
        self,
        book_title: str = None,
        book_uid: str = None,
        run_id: str = None
    ) -> Optional[Path]:
        """
        Detect if a run already exists for the given parameters
        
        Returns:
            Path to run_dir if found, None otherwise
        """
        if book_uid and run_id:
            # Direct lookup
            title_slug = to_slug(book_title) if book_title else "*"
            pattern = f"{title_slug}__{book_uid}/runs/{run_id}"
            matches = list(self.base_dir.glob(pattern))
            if matches:
                return matches[0]
        
        if book_uid:
            # Search by book_uid
            for workspace in self.base_dir.iterdir():
                if workspace.is_dir() and f"__{book_uid}" in workspace.name:
                    runs_dir = workspace / "runs"
                    if runs_dir.exists():
                        if run_id:
                            run_dir = runs_dir / run_id
                            if run_dir.exists():
                                return run_dir
                        else:
                            # Return most recent run
                            runs = sorted(runs_dir.iterdir(), key=lambda p: p.stat().st_mtime)
                            if runs:
                                return runs[-1]
        
        return None
    
    def validate_workspace_integrity(self, run_dir: Path) -> Tuple[bool, List[str]]:
        """
        Validate workspace integrity before operations
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check run_dir exists
        if not run_dir.exists():
            errors.append(f"Run directory does not exist: {run_dir}")
            return False, errors
        
        # Check required files
        required_files = [
            run_dir / "0-config" / "0-book-config.json",
            run_dir / "4-state" / "4-writing-state.json"
        ]
        
        for req_file in required_files:
            if not req_file.exists():
                errors.append(f"Required file missing: {req_file}")
        
        # Validate lock consistency
        lock_file = run_dir / ".lock.json"
        if lock_file.exists():
            try:
                with open(lock_file, 'r', encoding='utf-8') as f:
                    lock_data = json.load(f)
                
                run_id_from_dir = run_dir.name
                run_id_from_lock = lock_data.get('run_id')
                
                if run_id_from_lock != run_id_from_dir:
                    errors.append(f"Lock file run_id mismatch: {run_id_from_lock} != {run_id_from_dir}")
                    
            except Exception as e:
                errors.append(f"Failed to read lock file: {e}")
        
        # Check no path escaping
        if not validate_path_in_workspace(run_dir, run_dir):
            errors.append("Workspace path validation failed")
        
        return len(errors) == 0, errors
    
    def get_book_list(self) -> List[Dict[str, Any]]:
        """List all books in the base directory"""
        books = []
        
        for workspace in self.base_dir.iterdir():
            if not workspace.is_dir():
                continue
            
            # Parse workspace name: {title_slug}__{book_uid}
            parts = workspace.name.rsplit('__', 1)
            if len(parts) != 2:
                continue
            
            title_slug, book_uid = parts
            
            # Find runs
            runs_dir = workspace / "runs"
            if not runs_dir.exists():
                continue
            
            for run_dir in runs_dir.iterdir():
                config_file = run_dir / "0-config" / "0-book-config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        
                        books.append({
                            'book_title': config['book']['title'],
                            'book_uid': book_uid,
                            'run_id': run_dir.name,
                            'genre': config['book']['genre'],
                            'status': config['book'].get('status', 'unknown'),
                            'path': str(run_dir),
                            'created_at': config.get('created_at', 'unknown')
                        })
                    except Exception:
                        pass
        
        return sorted(books, key=lambda x: x['created_at'], reverse=True)


# ============================================================================
# Intent Checklist Generator
# ============================================================================

def generate_intent_checklist(book_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate initial intent_checklist.json based on book config
    
    This is the 10-item alignment checklist from design doc
    """
    book = book_config.get('book', {})
    genre = book.get('genre', '')
    subgenre = book.get('subgenre', '')
    tone = book.get('tone', '轻松')
    
    return {
        'version': '1.0',
        'source': '0-book-config',
        'items': [
            {
                'id': 1,
                'name': '题材关键词',
                'description': f'必须是{genre}',
                'must_be': [genre] + ([subgenre] if subgenre else []),
                'must_not': [],
                'required': True,
                'weight': 0.1
            },
            {
                'id': 2,
                'name': '核心基调',
                'description': f'必须是{tone}',
                'must_be': tone,
                'must_not': '黑暗' if tone != '暗黑' else '轻松',
                'required': True,
                'weight': 0.1
            },
            {
                'id': 3,
                'name': '主角身份',
                'description': '主角身份设定',
                'must_be': '待设定',
                'must_not': None,
                'required': True,
                'weight': 0.1
            },
            {
                'id': 4,
                'name': '世界规则',
                'description': '核心世界观规则存在',
                'must_be': '待设定',
                'must_not': None,
                'required': True,
                'weight': 0.1
            },
            {
                'id': 5,
                'name': '主要冲突类型',
                'description': '故事主要冲突类型',
                'must_be': '待设定',
                'must_not': None,
                'required': True,
                'weight': 0.1
            },
            {
                'id': 6,
                'name': '叙事视角',
                'description': '叙事视角设定',
                'must_be': '第三人称限知',
                'must_not': ['第一人称', '上帝视角'],
                'required': True,
                'weight': 0.1
            },
            {
                'id': 7,
                'name': '目标受众',
                'description': '目标读者群体',
                'must_be': '网文',
                'must_not': None,
                'required': False,
                'weight': 0.1
            },
            {
                'id': 8,
                'name': '核心伏笔',
                'description': '主线伏笔设定',
                'must_be': '待设定',
                'must_not': None,
                'required': True,
                'weight': 0.1
            },
            {
                'id': 9,
                'name': '力量等级',
                'description': '力量/技能体系',
                'must_be': '待设定',
                'must_not': None,
                'required': False,
                'weight': 0.1
            },
            {
                'id': 10,
                'name': '结局走向',
                'description': '故事结局方向',
                'must_be': ['HE', '开放式'],
                'must_not': 'BE',
                'required': True,
                'weight': 0.1
            }
        ]
    }


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=== Workspace Manager Test ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir) / "novels"
        
        # Create manager
        mgr = WorkspaceManager(base_dir)
        
        # Test create new book
        run_dir, book_uid, run_id, paths = mgr.create_new_book(
            book_title="阴间外卖",
            genre="都市灵异",
            target_words=250000,
            subgenre="系统流",
            mode="manual"
        )
        
        print(f"[Test] Book created: {run_dir.exists()}")
        print(f"  book_uid: {book_uid}")
        print(f"  run_id: {run_id}")
        
        # Test directory structure
        print(f"\n[Test] Directory structure:")
        print(f"  0-config exists: {paths['config_dir'].exists()}")
        print(f"  4-state exists: {paths['state_dir'].exists()}")
        print(f"  chapters exists: {paths['chapters_dir'].exists()}")
        print(f"  logs exists: {paths['logs_dir'].exists()}")
        
        # Test config written
        config_path = paths['book_config']
        print(f"\n[Test] Config file exists: {config_path.exists()}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"  Title: {config['book']['title']}")
        print(f"  Genre: {config['book']['genre']}")
        print(f"  Target words: {config['book']['target_word_count']}")
        print(f"  Mode: {config['generation']['mode']}")
        
        # Test writing state
        state_path = paths['writing_state']
        print(f"\n[Test] Writing state exists: {state_path.exists()}")
        
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        print(f"  Current chapter: {state['current_chapter']}")
        print(f"  QC status: {state['qc_status']}")
        
        # Test detect existing run
        detected = mgr.detect_existing_run(book_uid=book_uid)
        print(f"\n[Test] Detect existing run: {detected == run_dir}")
        
        # Test validate integrity
        is_valid, errors = mgr.validate_workspace_integrity(run_dir)
        print(f"\n[Test] Workspace integrity: {'PASS' if is_valid else 'FAIL'}")
        if errors:
            for err in errors:
                print(f"  Error: {err}")
        
        # Test book list
        books = mgr.get_book_list()
        print(f"\n[Test] Book list: {len(books)} book(s)")
        if books:
            print(f"  First book: {books[0]['book_title']}")
        
        # Test intent checklist generation
        checklist = generate_intent_checklist(config)
        print(f"\n[Test] Intent checklist generated: {len(checklist['items'])} items")
        
    print("\n=== All tests completed ===")

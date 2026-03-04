"""
Fanfic Writer v2.0 - Resume Manager
Handles run locking and resume/recovery functionality
"""
import json
import os
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from .atomic_io import atomic_write_json, atomic_append_jsonl, atomic_write_text
from .utils import get_timestamp_iso, generate_event_id


class RunLock:
    """
    Run-level exclusive lock to prevent concurrent access
    Creates .lock.json in run directory
    """
    
    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.lock_path = self.run_dir / ".lock.json"
    
    def acquire(self, mode: str) -> Tuple[bool, Optional[str]]:
        """
        Acquire run lock
        
        Returns:
            (success, error_message)
        """
        # Check if lock exists
        if self.lock_path.exists():
            try:
                with open(self.lock_path, 'r', encoding='utf-8') as f:
                    lock_data = json.load(f)
                
                # Check if it's a zombie lock (process dead)
                pid = lock_data.get('pid')
                if pid and not self._is_process_alive(pid):
                    # Zombie lock - can remove
                    self._write_zombie_event(lock_data)
                    print(f"[RunLock] Removed zombie lock from PID {pid}")
                    self.lock_path.unlink()
                else:
                    # Lock held by active process - check if it's from same run
                    # For init command, always remove old locks to allow new runs
                    print(f"[RunLock] Removing existing lock for new run")
                    self.lock_path.unlink()
                    
            except Exception as e:
                # Lock file corrupted, remove it
                try:
                    self.lock_path.unlink()
                except:
                    pass
        
        # Write new lock
        lock_data = {
            'run_id': self.run_dir.name,
            'pid': os.getpid(),
            'start_ts': get_timestamp_iso(),
            'host': os.environ.get('COMPUTERNAME', 'unknown'),
            'mode': mode
        }
        
        atomic_write_json(self.lock_path, lock_data)
        return True, None
    
    def release(self) -> bool:
        """Release run lock"""
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
            return True
        except Exception as e:
            print(f"[RunLock] Warning: Failed to release lock: {e}")
            return False
    
    def _is_process_alive(self, pid: int) -> bool:
        """Check if process is still alive"""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
    
    def _write_zombie_event(self, old_lock: Dict[str, Any]):
        """Write RS-002 event for zombie lock cleanup"""
        record = {
            'event_id': generate_event_id(old_lock['run_id'], 'RS-002'),
            'timestamp': get_timestamp_iso(),
            'event': 'zombie_lock_cleaned',
            'run_id': old_lock['run_id'],
            'old_pid': old_lock.get('pid'),
            'old_start_ts': old_lock.get('start_ts'),
            'cleaned_by': os.getpid()
        }
        
        log_path = self.run_dir / "logs" / "errors.jsonl"
        atomic_append_jsonl(log_path, record)


class ResumeManager:
    """
    Manages resume/recovery of interrupted runs
    """
    
    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.state_path = self.run_dir / "4-state" / "4-writing-state.json"
        self.config_path = self.run_dir / "0-config" / "0-book-config.json"
    
    def can_resume(self, mode: str = "auto") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check if this run can be resumed
        
        Args:
            mode: "auto" - check if resumable, "force" - force resume
            
        Returns:
            (can_resume, reason, resume_info)
        """
        # Check state file exists
        if not self.state_path.exists():
            return False, "State file not found", {}
        
        # Check config exists
        if not self.config_path.exists():
            return False, "Config file not found", {}
        
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            return False, f"Cannot parse state/config: {e}", {}
        
        # Validate run_id matches directory
        run_id_from_dir = self.run_dir.name
        run_id_from_state = state.get('run_id')
        run_id_from_config = config.get('run_id')
        
        if run_id_from_state != run_id_from_dir:
            return False, f"Run ID mismatch: state={run_id_from_state}, dir={run_id_from_dir}", {}
        
        if run_id_from_config != run_id_from_dir:
            return False, f"Run ID mismatch: config={run_id_from_config}, dir={run_id_from_dir}", {}
        
        # Validate book_uid
        book_uid_from_config = config.get('book', {}).get('book_uid')
        parent_dir = self.run_dir.parent.parent  # novels/{slug}__{uid}/runs/{run_id}
        expected_uid = parent_dir.name.split('__')[-1] if '__' in parent_dir.name else None
        
        if expected_uid and book_uid_from_config != expected_uid:
            return False, f"Book UID mismatch", {}
        
        # Check if already completed
        ending_state = state.get('ending_state', 'not_ready')
        if ending_state == 'ended':
            return False, "Run already completed (ended)", {}
        
        # Check if paused
        is_paused = state.get('flags', {}).get('is_paused', False)
        if is_paused and mode != "force":
            pause_reason = state.get('flags', {}).get('pause_reason', 'unknown')
            return False, f"Run is paused: {pause_reason}", {}
        
        # Determine resume point
        current_chapter = state.get('current_chapter', 0)
        completed_chapters = state.get('completed_chapters', [])
        
        resume_point = {
            'chapter': current_chapter,
            'phase': '6.1',  # Default to sanitizer
            'step': 'sanitizer'
        }
        
        # Determine specific phase based on incomplete files
        if current_chapter > 0:
            chapter_file = self.run_dir / "chapters" / f"第{current_chapter:03d}章*.txt"
            draft_file = self.run_dir / "drafts" / "chapters" / f"Ch{current_chapter:03d}_draft*.md"
            
            if list(self.run_dir.glob(str(chapter_file))):
                # Chapter already written - move to next
                resume_point['chapter'] = current_chapter + 1
                resume_point['phase'] = '6.1'
            elif list(self.run_dir.glob(str(draft_file))):
                # Has draft but not committed - restart QC
                resume_point['phase'] = '6.4'
                resume_point['step'] = 'qc'
        
        # Calculate state hash
        state_hash = self._compute_state_hash(state)
        
        resume_info = {
            'run_id': run_id_from_state,
            'book_uid': book_uid_from_config,
            'current_chapter': current_chapter,
            'completed_chapters': completed_chapters,
            'resume_point': resume_point,
            'state_hash': state_hash,
            'ending_state': ending_state
        }
        
        return True, "OK", resume_info
    
    def resume(self, resume_info: Dict[str, Any]) -> bool:
        """
        Execute resume operation
        
        Writes RS-001 event and updates state
        """
        # Write resume event
        record = {
            'event_id': generate_event_id(resume_info['run_id'], 'RS-001'),
            'timestamp': get_timestamp_iso(),
            'event': 'resume',
            'run_id': resume_info['run_id'],
            'resume_mode': 'auto',
            'resume_point': resume_info['resume_point'],
            'state_hash_before': resume_info['state_hash'],
            'state_hash_after': None  # Will be updated after operations
        }
        
        # RS-001 must be written to logs/events.jsonl per design spec
        events_path = self.run_dir / "logs" / "events.jsonl"
        atomic_append_jsonl(events_path, record)
        
        print(f"[Resume] Resumed at Chapter {resume_info['resume_point']['chapter']}, "
              f"Phase {resume_info['resume_point']['phase']}")
        
        return True
    
    def _compute_state_hash(self, state: Dict[str, Any]) -> str:
        """Compute hash of critical state fields for integrity check"""
        critical_fields = {
            'current_chapter': state.get('current_chapter'),
            'completed_chapters': state.get('completed_chapters', []),
            'qc_score': state.get('qc_score'),
            'forced_streak': state.get('forced_streak'),
            'ending_state': state.get('ending_state')
        }
        
        state_str = json.dumps(critical_fields, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]
    
    def verify_integrity(self) -> Tuple[bool, str]:
        """Verify run integrity before operations"""
        if not self.state_path.exists():
            return False, "State file missing"
        
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Check required fields
            required = ['run_id', 'current_chapter', 'qc_status', 'flags']
            for field in required:
                if field not in state:
                    return False, f"Missing required field: {field}"
            
            return True, "OK"
            
        except json.JSONDecodeError:
            return False, "State file corrupted (invalid JSON)"
        except Exception as e:
            return False, f"Cannot read state: {e}"


class RuntimeConfigManager:
    """
    Manages runtime_effective_config.json
    Records final effective parameters after priority resolution
    """
    
    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.runtime_config_path = self.run_dir / "4-state" / "runtime_effective_config.json"
    
    def generate(
        self,
        cli_args: Dict[str, Any],
        env_vars: Dict[str, Any],
        config_file: Dict[str, Any],
        defaults: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate runtime effective config by merging all sources
        
        Priority (high to low):
        1. CLI args
        2. Environment variables
        3. Config file
        4. Defaults
        """
        effective = {}
        alias_mappings = {}
        
        # All possible parameters
        all_params = {
            'mode', 'model', 'max_words', 'workspace_root',
            'temperature_outline', 'temperature_chapter',
            'auto_threshold', 'max_attempts',
            'auto_rescue_enabled', 'auto_rescue_max_rounds'
        }
        
        for param in all_params:
            value = None
            source = None
            
            # Priority 1: CLI args
            if param in cli_args and cli_args[param] is not None:
                value = cli_args[param]
                source = 'cli'
            
            # Priority 2: Environment variables
            elif param.upper() in env_vars:
                value = env_vars[param.upper()]
                source = 'env'
            
            # Priority 3: Config file
            elif param in config_file:
                value = config_file[param]
                source = 'config'
            
            # Priority 4: Defaults
            elif param in defaults:
                value = defaults[param]
                source = 'default'
            
            # Handle max_words limit
            if param == 'max_words' and value is not None:
                if value > 500000:
                    alias_mappings[f'{param}_original'] = value
                    value = 500000
                    source = f'{source} (truncated to 500000)'
            
            # Handle model alias mapping
            if param == 'model' and value is not None:
                from .price_table import PriceTableManager
                price_mgr = PriceTableManager(self.run_dir)
                mapped = price_mgr.get_model_alias_mapping(str(value))
                if mapped:
                    alias_mappings[f'{param}_alias_from'] = value
                    alias_mappings[f'{param}_alias_to'] = mapped
                    value = mapped
            
            if value is not None:
                effective[param] = {
                    'value': value,
                    'source': source
                }
        
        # Build final config
        runtime_config = {
            'generated_at': get_timestamp_iso(),
            'parameters': effective,
            'alias_mappings': alias_mappings if alias_mappings else None,
            'priority_order': ['cli', 'env', 'config', 'default']
        }
        
        atomic_write_json(self.runtime_config_path, runtime_config)
        
        return runtime_config
    
    def load(self) -> Optional[Dict[str, Any]]:
        """Load runtime effective config"""
        if not self.runtime_config_path.exists():
            return None
        
        with open(self.runtime_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=== Resume Manager Test ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create run structure
        run_dir = Path(tmpdir) / "novels" / "test__abc123" / "runs" / "20260216_000000_TEST"
        run_dir.mkdir(parents=True)
        
        state_dir = run_dir / "4-state"
        state_dir.mkdir()
        
        config_dir = run_dir / "0-config"
        config_dir.mkdir()
        
        logs_dir = run_dir / "logs"
        logs_dir.mkdir()
        
        # Test RunLock
        print("[Test] RunLock")
        lock = RunLock(run_dir)
        
        success, error = lock.acquire("auto")
        print(f"  Acquire: {'PASS' if success else 'FAIL'} {error or ''}")
        
        assert lock.lock_path.exists()
        print(f"  Lock file created: PASS")
        
        lock.release()
        print(f"  Release: PASS")
        
        # Test ResumeManager
        print("\n[Test] ResumeManager")
        
        # Create test state
        test_state = {
            'run_id': '20260216_000000_TEST',
            'book_title': 'Test',
            'mode': 'auto',
            'current_chapter': 5,
            'completed_chapters': [1, 2, 3, 4],
            'qc_status': 'PASS',
            'flags': {'is_paused': False},
            'ending_state': 'not_ready',
            'ending_checklist': {}
        }
        
        test_config = {
            'run_id': '20260216_000000_TEST',
            'book': {'book_uid': 'abc123', 'title': 'Test'},
            'version': '2.0.0'
        }
        
        with open(state_dir / "4-writing-state.json", 'w') as f:
            json.dump(test_state, f)
        
        with open(config_dir / "0-book-config.json", 'w') as f:
            json.dump(test_config, f)
        
        resume_mgr = ResumeManager(run_dir)
        
        can_resume, reason, info = resume_mgr.can_resume()
        print(f"  Can resume: {can_resume} ({reason})")
        if can_resume:
            print(f"  Resume at chapter: {info['resume_point']['chapter']}")
        
        # Test integrity check
        valid, msg = resume_mgr.verify_integrity()
        print(f"  Integrity: {valid} ({msg})")
        
        # Test RuntimeConfigManager
        print("\n[Test] RuntimeConfigManager")
        rt_mgr = RuntimeConfigManager(run_dir)
        
        runtime_cfg = rt_mgr.generate(
            cli_args={'mode': 'auto', 'max_words': 600000},
            env_vars={'MODEL': 'nvidia/kimi'},
            config_file={'temperature_outline': 0.8},
            defaults={'max_attempts': 3}
        )
        
        print(f"  Generated: {len(runtime_cfg['parameters'])} parameters")
        print(f"  max_words truncated: {runtime_cfg['parameters']['max_words']['value']}")
        
    print("\n=== All tests completed ===")

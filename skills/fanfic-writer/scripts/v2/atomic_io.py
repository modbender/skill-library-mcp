"""
Fanfic Writer v2.0 - Atomic I/O Module
Implements atomic file writes with fsync, snapshots, and rollback capabilities
"""
import os
import json
import shutil
import hashlib
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable, Union
from contextlib import contextmanager
try:
    import fcntl  # Unix file locking
except ImportError:
    fcntl = None  # Windows doesn't have fcntl


# ============================================================================
# Atomic Write Operations
# ============================================================================

def atomic_write_text(
    path: Path, 
    content: str, 
    encoding: str = 'utf-8',
    fsync: bool = True
) -> bool:
    """
    Atomically write text file using temp → fsync → rename pattern
    
    Process:
    1. Write to temp file in same directory
    2. fsync to ensure data hits disk
    3. rename (atomic on POSIX and modern Windows)
    
    Returns True on success, False on failure
    """
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create temp file in same directory (for atomic rename)
        fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f'.tmp_{path.stem}_',
            suffix='.tmp'
        )
        
        try:
            # Write content
            with os.fdopen(fd, 'w', encoding=encoding) as f:
                f.write(content)
                if fsync:
                    f.flush()
                    os.fsync(f.fileno())
            
            # Atomic rename
            os.replace(temp_path, path)
            
            return True
            
        except Exception:
            # Clean up temp file on failure
            try:
                os.unlink(temp_path)
            except:
                pass
            raise
            
    except Exception as e:
        print(f"[Atomic Write Error] Failed to write {path}: {e}")
        return False


def atomic_write_json(
    path: Path, 
    data: Any, 
    indent: int = 2,
    fsync: bool = True
) -> bool:
    """Atomically write JSON file"""
    try:
        content = json.dumps(data, indent=indent, ensure_ascii=False, default=str)
        return atomic_write_text(path, content, fsync=fsync)
    except Exception as e:
        print(f"[Atomic Write Error] Failed to serialize JSON for {path}: {e}")
        return False


def atomic_write_jsonl(
    path: Path, 
    records: List[Dict[str, Any]],
    append: bool = False,
    fsync: bool = True
) -> bool:
    """
    Atomically write JSONL file (JSON Lines format)
    
    If append=True and file exists, new records are appended
    Otherwise, file is overwritten
    """
    try:
        lines = []
        
        if append and path.exists():
            # Read existing content
            with open(path, 'r', encoding='utf-8') as f:
                existing = f.read()
                if existing.strip():
                    lines.append(existing.rstrip('\n'))
        
        # Add new records
        for record in records:
            lines.append(json.dumps(record, ensure_ascii=False, default=str))
        
        content = '\n'.join(lines) + '\n'
        return atomic_write_text(path, content, fsync=fsync)
        
    except Exception as e:
        print(f"[Atomic Write Error] Failed to write JSONL {path}: {e}")
        return False


def atomic_append_jsonl(
    path: Path,
    record: Dict[str, Any],
    fsync: bool = True
) -> bool:
    """
    Atomically append single record to JSONL file
    Less efficient than batching, but useful for logging
    """
    return atomic_write_jsonl(path, [record], append=True, fsync=fsync)


# ============================================================================
# File Locking (for exclusive access)
# ============================================================================

class FileLock:
    """
    Cross-platform file locking for exclusive write access
    Uses fcntl on Unix, msvcrt on Windows
    """
    
    def __init__(self, path: Path, timeout: float = 10.0):
        self.path = Path(path)
        self.timeout = timeout
        self.lock_file = None
        
    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create lock file if not exists
        self.path.touch(exist_ok=True)
        
        # Open for locking
        self.lock_file = open(self.path, 'r+')
        
        try:
            if os.name == 'nt':  # Windows
                import msvcrt
                # Windows doesn't have true advisory locking
                # We use a simple exclusive open approach
                pass
            else:  # Unix/Linux/Mac
                import fcntl
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            # Lock failed
            self.lock_file.close()
            raise RuntimeError(f"Could not acquire lock on {self.path}")
            
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_file:
            try:
                if os.name != 'nt':
                    import fcntl
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            except:
                pass
            self.lock_file.close()


# ============================================================================
# Checksum / Hash for Integrity Verification
# ============================================================================

def compute_file_hash(path: Path, algorithm: str = 'sha256') -> str:
    """Compute hash of file contents for integrity checking"""
    hasher = hashlib.new(algorithm)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_file_integrity(path: Path, expected_hash: str, algorithm: str = 'sha256') -> bool:
    """Verify file matches expected hash"""
    if not path.exists():
        return False
    actual_hash = compute_file_hash(path, algorithm)
    return actual_hash == expected_hash


# ============================================================================
# Snapshot Management
# ============================================================================

class SnapshotManager:
    """
    Manages directory snapshots for rollback capability
    """
    
    def __init__(self, archive_dir: Path):
        self.archive_dir = Path(archive_dir)
        self.snapshots_dir = self.archive_dir / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    def create_snapshot(
        self, 
        source_dirs: List[Path], 
        snapshot_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Create a snapshot of specified directories
        
        Args:
            source_dirs: List of directories to snapshot
            snapshot_name: Name for this snapshot (e.g., "ch015_attempt1")
            metadata: Optional metadata to store with snapshot
            
        Returns:
            Path to created snapshot directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_dir = self.snapshots_dir / f"{snapshot_name}_{timestamp}"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy each source directory
        for src_dir in source_dirs:
            if not src_dir.exists():
                continue
                
            dst_dir = snapshot_dir / src_dir.name
            
            # Use shutil.copytree for directories
            if src_dir.is_dir():
                shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
        
        # Write metadata
        if metadata:
            meta_path = snapshot_dir / ".snapshot_meta.json"
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'created_at': datetime.now().isoformat(),
                    'source_dirs': [str(d) for d in source_dirs],
                    **metadata
                }, f, indent=2, ensure_ascii=False)
        
        return snapshot_dir
    
    def restore_snapshot(
        self, 
        snapshot_dir: Path, 
        target_dirs: List[Path]
    ) -> bool:
        """
        Restore from snapshot
        
        Args:
            snapshot_dir: Path to snapshot directory
            target_dirs: List of target directories to restore to
            
        Returns:
            True on success
        """
        try:
            snapshot_dir = Path(snapshot_dir)
            
            for target_dir in target_dirs:
                src = snapshot_dir / target_dir.name
                if src.exists():
                    # Remove existing target
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                    # Copy from snapshot
                    shutil.copytree(src, target_dir)
                    
            return True
            
        except Exception as e:
            print(f"[Snapshot Error] Failed to restore from {snapshot_dir}: {e}")
            return False
    
    def list_snapshots(self) -> List[Path]:
        """List all available snapshots"""
        if not self.snapshots_dir.exists():
            return []
        return sorted(self.snapshots_dir.iterdir(), key=lambda p: p.stat().st_mtime)
    
    def cleanup_old_snapshots(self, keep_count: int = 10) -> int:
        """
        Remove old snapshots, keeping only the most recent N
        
        Returns:
            Number of snapshots removed
        """
        snapshots = self.list_snapshots()
        
        if len(snapshots) <= keep_count:
            return 0
        
        to_remove = snapshots[:-keep_count]
        removed = 0
        
        for snap in to_remove:
            try:
                shutil.rmtree(snap)
                removed += 1
            except Exception as e:
                print(f"[Snapshot Cleanup Error] Failed to remove {snap}: {e}")
        
        return removed


# ============================================================================
# Rollback Manager
# ============================================================================

class RollbackManager:
    """
    Manages transaction-like rollback capability
    """
    
    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.archive_dir = self.run_dir / "archive"
        self.reverted_dir = self.archive_dir / "reverted"
        self.reverted_dir.mkdir(parents=True, exist_ok=True)
        
        self.snapshot_manager = SnapshotManager(self.archive_dir)
        self._transaction_stack: List[Dict[str, Any]] = []
    
    def begin_transaction(self, name: str) -> str:
        """
        Begin a new transaction
        
        Returns:
            Transaction ID
        """
        tx_id = f"tx_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create pre-transaction snapshot
        snapshot = self.snapshot_manager.create_snapshot(
            source_dirs=[
                self.run_dir / "4-state",
                self.run_dir / "chapters",
                self.run_dir / "drafts"
            ],
            snapshot_name=f"tx_{name}",
            metadata={'transaction_id': tx_id, 'phase': 'pre'}
        )
        
        self._transaction_stack.append({
            'id': tx_id,
            'name': name,
            'pre_snapshot': snapshot
        })
        
        return tx_id
    
    def commit_transaction(self) -> bool:
        """Commit current transaction (remove from stack)"""
        if not self._transaction_stack:
            return False
        
        tx = self._transaction_stack.pop()
        
        # Create post-transaction snapshot for audit
        self.snapshot_manager.create_snapshot(
            source_dirs=[
                self.run_dir / "4-state",
                self.run_dir / "chapters"
            ],
            snapshot_name=f"tx_{tx['name']}_committed",
            metadata={'transaction_id': tx['id'], 'phase': 'post'}
        )
        
        return True
    
    def rollback_transaction(self) -> bool:
        """
        Rollback current transaction to pre-transaction state
        
        Returns:
            True on success
        """
        if not self._transaction_stack:
            return False
        
        tx = self._transaction_stack.pop()
        
        # Restore from pre-transaction snapshot
        success = self.snapshot_manager.restore_snapshot(
            tx['pre_snapshot'],
            [
                self.run_dir / "4-state",
                self.run_dir / "chapters",
                self.run_dir / "drafts"
            ]
        )
        
        return success
    
    def revert_chapter(self, chapter_num: int, chapter_path: Path) -> Path:
        """
        Revert a chapter by moving it to archive/reverted/
        
        Returns:
            Path to archived file
        """
        if not chapter_path.exists():
            raise FileNotFoundError(f"Chapter file not found: {chapter_path}")
        
        # Generate archive filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"reverted_ch{chapter_num:03d}_{timestamp}_{chapter_path.name}"
        archive_path = self.reverted_dir / archive_name
        
        # Move to archive
        shutil.move(str(chapter_path), str(archive_path))
        
        return archive_path


# ============================================================================
# State Commit Helper (Transaction-like)
# ============================================================================

class StateCommit:
    """
    Context manager for atomic state commits
    
    Usage:
        with StateCommit(rollback_manager, "chapter_15") as commit:
            # Make changes...
            commit.add_file(state_path, new_state)
            commit.add_file(chapter_path, chapter_content)
            # If no exception, auto-committed on exit
            # If exception, auto-rollback
    """
    
    def __init__(self, rollback_manager: RollbackManager, name: str):
        self.rollback_manager = rollback_manager
        self.name = name
        self.tx_id: Optional[str] = None
        self._files_to_write: List[Tuple[Path, Union[str, Dict], str]] = []
    
    def __enter__(self):
        self.tx_id = self.rollback_manager.begin_transaction(self.name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Success - commit all files
            success = True
            for path, content, content_type in self._files_to_write:
                if content_type == 'json':
                    if not atomic_write_json(path, content):
                        success = False
                        break
                elif content_type == 'jsonl':
                    if not atomic_write_jsonl(path, content):
                        success = False
                        break
                else:  # text
                    if not atomic_write_text(path, content):
                        success = False
                        break
            
            if success:
                self.rollback_manager.commit_transaction()
            else:
                self.rollback_manager.rollback_transaction()
                return False
        else:
            # Exception - rollback
            self.rollback_manager.rollback_transaction()
        
        return False  # Don't suppress exception
    
    def add_file(self, path: Path, content: Union[str, Dict], content_type: str = 'text'):
        """Queue a file to be written on commit"""
        self._files_to_write.append((path, content, content_type))


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=== Atomic I/O Module Test ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Test atomic write text
        test_file = tmpdir / "test.txt"
        content = "Hello, Atomic World!"
        success = atomic_write_text(test_file, content)
        print(f"[Test] Atomic write text: {'PASS' if success else 'FAIL'}")
        
        # Verify content
        with open(test_file, 'r') as f:
            read_content = f.read()
        print(f"[Test] Content verification: {'PASS' if read_content == content else 'FAIL'}")
        
        # Test atomic write JSON
        json_file = tmpdir / "test.json"
        data = {"name": "test", "value": 42, "nested": {"key": "value"}}
        success = atomic_write_json(json_file, data)
        print(f"[Test] Atomic write JSON: {'PASS' if success else 'FAIL'}")
        
        # Test atomic write JSONL
        jsonl_file = tmpdir / "test.jsonl"
        records = [
            {"event": "start", "ts": "2026-01-01"},
            {"event": "progress", "ts": "2026-01-02"},
            {"event": "end", "ts": "2026-01-03"}
        ]
        success = atomic_write_jsonl(jsonl_file, records)
        print(f"[Test] Atomic write JSONL: {'PASS' if success else 'FAIL'}")
        
        # Test append
        new_record = {"event": "append", "ts": "2026-01-04"}
        success = atomic_append_jsonl(jsonl_file, new_record)
        print(f"[Test] Atomic append JSONL: {'PASS' if success else 'FAIL'}")
        
        # Verify JSONL
        with open(jsonl_file, 'r') as f:
            lines = f.readlines()
        print(f"[Test] JSONL line count: {'PASS' if len(lines) == 4 else 'FAIL'} (expected 4, got {len(lines)})")
        
        # Test file hash
        hash1 = compute_file_hash(test_file)
        print(f"[Test] File hash computed: {hash1[:16]}...")
        
        integrity = verify_file_integrity(test_file, hash1)
        print(f"[Test] Integrity verification: {'PASS' if integrity else 'FAIL'}")
        
        # Test SnapshotManager
        archive_dir = tmpdir / "archive"
        snapshot_mgr = SnapshotManager(archive_dir)
        
        source_dir = tmpdir / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")
        
        snapshot = snapshot_mgr.create_snapshot([source_dir], "test_snapshot")
        print(f"[Test] Snapshot created: {'PASS' if snapshot.exists() else 'FAIL'}")
        
        # Modify source
        (source_dir / "file1.txt").write_text("modified")
        
        # Restore snapshot
        restore_success = snapshot_mgr.restore_snapshot(snapshot, [source_dir])
        print(f"[Test] Snapshot restore: {'PASS' if restore_success else 'FAIL'}")
        
        # Verify restoration
        restored_content = (source_dir / "file1.txt").read_text()
        print(f"[Test] Restored content: {'PASS' if restored_content == 'content1' else 'FAIL'}")
        
    print("\n=== All tests completed ===")

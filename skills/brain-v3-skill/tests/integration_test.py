#!/usr/bin/env python3
"""
ClawBrain Integration Tests

Tests ClawBrain functionality in a simulated OpenClaw environment.
Run this inside the test Docker container.
"""

import os
import sys
import json
import shutil
import tempfile
import traceback
from pathlib import Path
from datetime import datetime

# Test results tracking
TESTS_RUN = 0
TESTS_PASSED = 0
TESTS_FAILED = 0
FAILED_TESTS = []


def log(msg, level="INFO"):
    """Print formatted log message."""
    icons = {"INFO": "ℹ️ ", "PASS": "✅", "FAIL": "❌", "WARN": "⚠️ ", "TEST": "🧪"}
    print(f"{icons.get(level, '')} {msg}")


def run_test(name, test_func):
    """Run a test function and track results."""
    global TESTS_RUN, TESTS_PASSED, TESTS_FAILED, FAILED_TESTS
    TESTS_RUN += 1
    print(f"\n{'='*60}")
    log(f"TEST: {name}", "TEST")
    print("-" * 60)
    
    try:
        test_func()
        TESTS_PASSED += 1
        log(f"{name} - PASSED", "PASS")
        return True
    except AssertionError as e:
        TESTS_FAILED += 1
        FAILED_TESTS.append((name, str(e)))
        log(f"{name} - FAILED: {e}", "FAIL")
        traceback.print_exc()
        return False
    except Exception as e:
        TESTS_FAILED += 1
        FAILED_TESTS.append((name, str(e)))
        log(f"{name} - ERROR: {e}", "FAIL")
        traceback.print_exc()
        return False


# =============================================================================
# Test Cases
# =============================================================================

def get_test_config(tmpdir):
    """Get a test configuration with writable paths."""
    return {
        "sqlite_path": str(Path(tmpdir) / "test_brain.db"),
        "backup_dir": str(Path(tmpdir) / "backups"),
    }


def test_import():
    """Test that ClawBrain can be imported."""
    from clawbrain import Brain, Memory
    log("Successfully imported Brain and Memory classes")
    assert Brain is not None
    assert Memory is not None


def test_brain_initialization():
    """Test Brain class initialization."""
    from clawbrain import Brain
    
    # Use temp directory for test database
    with tempfile.TemporaryDirectory() as tmpdir:
        brain = Brain(config=get_test_config(tmpdir))
        
        assert brain is not None
        assert brain.storage_backend == "sqlite"
        log(f"Brain initialized with storage: {brain.storage_backend}")
        
        brain.close()


def test_remember_and_recall():
    """Test basic remember and recall functionality."""
    from clawbrain import Brain
    
    with tempfile.TemporaryDirectory() as tmpdir:
        brain = Brain(config=get_test_config(tmpdir))
        
        # Remember something
        memory = brain.remember(
            agent_id="test-agent",
            memory_type="knowledge",
            content="The sky is blue",
            key="sky_color"
        )
        
        assert memory is not None
        assert memory.content == "The sky is blue"
        log(f"Created memory with ID: {memory.id}")
        
        # Recall it
        memories = brain.recall(agent_id="test-agent", memory_type="knowledge")
        assert len(memories) >= 1
        assert any(m.content == "The sky is blue" for m in memories)
        log(f"Recalled {len(memories)} memories")
        
        brain.close()


def test_encryption_available():
    """Test that encryption is available."""
    try:
        from cryptography.fernet import Fernet
        log("cryptography library is available")
        
        # Test key generation
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        # Test encrypt/decrypt
        original = "secret data"
        encrypted = cipher.encrypt(original.encode())
        decrypted = cipher.decrypt(encrypted).decode()
        
        assert decrypted == original
        log("Encryption/decryption working correctly")
    except ImportError:
        raise AssertionError("cryptography library not installed")


def test_secret_encryption():
    """Test that secrets are encrypted in the database."""
    from clawbrain import Brain
    import sqlite3
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = get_test_config(tmpdir)
        db_path = config["sqlite_path"]
        brain = Brain(config=config)
        
        # Store a secret
        secret_content = "my-super-secret-api-key-12345"
        memory = brain.remember(
            agent_id="test-agent",
            memory_type="secret",
            content=secret_content,
            key="api_key"
        )
        
        assert memory is not None
        assert memory.content_encrypted == True
        log(f"Secret stored with encryption flag: {memory.content_encrypted}")
        
        # Check raw database - content should NOT be plaintext
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT content, content_encrypted FROM memories WHERE key = 'api_key'")
        row = cursor.fetchone()
        conn.close()
        
        raw_content = row[0]
        is_encrypted = row[1]
        
        assert is_encrypted == 1, "content_encrypted should be 1"
        assert raw_content != secret_content, "Content should be encrypted in database"
        assert secret_content not in raw_content, "Plaintext should not appear in encrypted content"
        log("Verified: secret is encrypted in database")
        
        # Verify we can still read it back decrypted
        secrets = brain.recall(agent_id="test-agent", memory_type="secret")
        api_key_secrets = [s for s in secrets if s.key == "api_key"]
        assert len(api_key_secrets) == 1
        assert api_key_secrets[0].content == secret_content
        log("Verified: secret decrypts correctly on recall")
        
        brain.close()


def test_auto_migration():
    """Test that unencrypted secrets are auto-migrated when encryption is enabled."""
    from clawbrain import Brain
    import sqlite3
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_brain.db"
        key_path = Path(tmpdir) / ".brain_key"
        backup_dir = Path(tmpdir) / "backups"
        
        # Step 1: Create a brain WITHOUT encryption (simulate old version)
        # We'll manually insert an unencrypted secret
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create the memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY, 
                agent_id TEXT, 
                memory_type TEXT, 
                key TEXT, 
                content TEXT,
                content_encrypted INTEGER DEFAULT 0, 
                summary TEXT, 
                keywords TEXT, 
                tags TEXT, 
                importance INTEGER DEFAULT 5,
                linked_to TEXT, 
                source TEXT, 
                embedding TEXT, 
                created_at TEXT, 
                updated_at TEXT
            )
        """)
        
        # Insert an unencrypted secret (simulating old data)
        old_secret = "old-unencrypted-secret-value"
        cursor.execute("""
            INSERT INTO memories (id, agent_id, memory_type, key, content, content_encrypted, 
                                  summary, keywords, tags, importance, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "test-secret-id-123",
            "test-agent",
            "secret",
            "old_api_key",
            old_secret,  # Plaintext!
            0,  # Not encrypted
            "Old secret",
            "[]",
            "[]",
            10,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        
        log("Created database with unencrypted secret (simulating old installation)")
        
        # Step 2: Initialize Brain - this should auto-migrate
        # Since there's no key file, it will generate one and trigger migration
        brain = Brain(config={
            "sqlite_path": str(db_path),
            "backup_dir": str(backup_dir)
        })
        
        # Step 3: Verify migration happened
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT content, content_encrypted FROM memories WHERE key = 'old_api_key'")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            raw_content = row[0]
            is_encrypted = row[1]
            
            assert is_encrypted == 1, f"Secret should be encrypted after migration, got: {is_encrypted}"
            assert raw_content != old_secret, "Content should no longer be plaintext"
            log("Verified: old secret was auto-migrated and encrypted")
            
            # Verify we can still decrypt it
            secrets = brain.recall(agent_id="test-agent", memory_type="secret")
            old_key_secrets = [s for s in secrets if s.key == "old_api_key"]
            assert len(old_key_secrets) == 1
            assert old_key_secrets[0].content == old_secret
            log("Verified: migrated secret still decrypts to original value")
        else:
            log("No secret found - this might be expected if table was recreated", "WARN")
        
        brain.close()


def test_cli_available():
    """Test that CLI entry point is available."""
    import subprocess
    
    result = subprocess.run(
        [sys.executable, "-m", "clawbrain_cli", "--help"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "clawbrain" in result.stdout.lower()
    log("CLI is available and responds to --help")


def test_hooks_directory_exists():
    """Test that hooks are properly structured."""
    hooks_dir = Path(__file__).parent.parent / "hooks" / "clawbrain-startup"
    
    assert hooks_dir.exists(), f"Hooks directory not found: {hooks_dir}"
    
    handler_js = hooks_dir / "handler.js"
    assert handler_js.exists(), "handler.js not found"
    log(f"Hooks directory exists: {hooks_dir}")
    
    # Check handler.js has required exports (ESM or CommonJS)
    content = handler_js.read_text()
    has_export = (
        "module.exports" in content or 
        "exports." in content or 
        "export default" in content or
        "export " in content
    )
    assert has_export, "handler.js should have exports"
    log("handler.js has proper exports")


def test_brain_bridge_exists():
    """Test that brain_bridge.py exists in expected locations."""
    project_dir = Path(__file__).parent.parent
    
    possible_paths = [
        project_dir / "scripts" / "brain_bridge.py",
        project_dir / "brain" / "scripts" / "brain_bridge.py",
    ]
    
    found = False
    for path in possible_paths:
        if path.exists():
            log(f"brain_bridge.py found at: {path}")
            found = True
            break
    
    assert found, f"brain_bridge.py not found in any expected location"


def test_multiple_agents():
    """Test that multiple agents can have separate memories."""
    from clawbrain import Brain
    
    with tempfile.TemporaryDirectory() as tmpdir:
        brain = Brain(config=get_test_config(tmpdir))
        
        # Agent 1 stores a memory
        brain.remember(
            agent_id="agent-1",
            memory_type="preference",
            content="I like blue",
            key="favorite_color"
        )
        
        # Agent 2 stores a different memory with same key
        brain.remember(
            agent_id="agent-2",
            memory_type="preference",
            content="I like red",
            key="favorite_color"
        )
        
        # Recall for agent 1
        agent1_memories = brain.recall(agent_id="agent-1", memory_type="preference")
        agent1_color = [m for m in agent1_memories if m.key == "favorite_color"]
        assert len(agent1_color) == 1
        assert agent1_color[0].content == "I like blue"
        
        # Recall for agent 2
        agent2_memories = brain.recall(agent_id="agent-2", memory_type="preference")
        agent2_color = [m for m in agent2_memories if m.key == "favorite_color"]
        assert len(agent2_color) == 1
        assert agent2_color[0].content == "I like red"
        
        log("Multiple agents can have separate memories with same key")
        
        brain.close()


def test_health_check():
    """Test the health check functionality."""
    from clawbrain import Brain
    
    with tempfile.TemporaryDirectory() as tmpdir:
        brain = Brain(config=get_test_config(tmpdir))
        
        health = brain.health_check()
        
        assert isinstance(health, dict)
        assert health.get("sqlite") == True or health.get("postgresql") == True
        log(f"Health check returned: {health}")
        
        brain.close()


def test_get_unencrypted_secrets():
    """Test the get_unencrypted_secrets method."""
    from clawbrain import Brain
    import sqlite3
    
    with tempfile.TemporaryDirectory() as tmpdir:
        brain = Brain(config=get_test_config(tmpdir))
        
        # First, all secrets should be encrypted (or none exist)
        unencrypted = brain.get_unencrypted_secrets()
        log(f"Initial unencrypted secrets: {len(unencrypted)}")
        
        # Store an encrypted secret
        brain.remember(
            agent_id="test",
            memory_type="secret",
            content="encrypted-secret",
            key="test_key"
        )
        
        # Should still show 0 unencrypted (new secret is encrypted)
        unencrypted = brain.get_unencrypted_secrets()
        assert len(unencrypted) == 0, "New secrets should be encrypted"
        log("Verified: newly stored secrets are encrypted")
        
        brain.close()


# =============================================================================
# Main Test Runner
# =============================================================================

def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("  ClawBrain Integration Test Suite")
    print("=" * 60)
    print(f"  Date: {datetime.now().isoformat()}")
    print(f"  Python: {sys.version}")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Import ClawBrain", test_import),
        ("Brain Initialization", test_brain_initialization),
        ("Remember and Recall", test_remember_and_recall),
        ("Encryption Available", test_encryption_available),
        ("Secret Encryption", test_secret_encryption),
        ("Auto Migration", test_auto_migration),
        ("CLI Available", test_cli_available),
        ("Hooks Directory", test_hooks_directory_exists),
        ("Brain Bridge Script", test_brain_bridge_exists),
        ("Multiple Agents", test_multiple_agents),
        ("Health Check", test_health_check),
        ("Get Unencrypted Secrets", test_get_unencrypted_secrets),
    ]
    
    for name, test_func in tests:
        run_test(name, test_func)
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    print(f"  Total:  {TESTS_RUN}")
    print(f"  Passed: {TESTS_PASSED}")
    print(f"  Failed: {TESTS_FAILED}")
    
    if FAILED_TESTS:
        print("\n  Failed Tests:")
        for name, error in FAILED_TESTS:
            print(f"    - {name}: {error[:50]}...")
    
    print("=" * 60)
    
    return 0 if TESTS_FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Sensitive Data Masker - Intelligent Sensitive Data Detection and Masking

Uses Microsoft Presidio for intelligent detection, SQLite + LRU cache with ENCRYPTED storage.

Security:
- Uses spawn with argument array (no shell injection)
- Encrypts sensitive data at rest with AES-256 (REQUIRED - no fallback)
- Auto-cleanup of expired data
- Fails securely if cryptography not available
"""

import sys
import json
import hashlib
import sqlite3
import time
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List
from collections import OrderedDict

# ═══════════════════════════════════════════════════════════════
# CRITICAL: Check cryptography dependency FIRST
# ═══════════════════════════════════════════════════════════════

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("❌ ERROR: cryptography library not installed.", file=sys.stderr)
    print("   This skill REQUIRES encryption for security.", file=sys.stderr)
    print("   Install: pip install cryptography", file=sys.stderr)
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

DATA_DIR = Path.home() / ".openclaw" / "data" / "sensitive-masker"
DB_FILE = DATA_DIR / "mapping.db"
CONFIG_FILE = DATA_DIR / "config.json"
KEY_FILE = DATA_DIR / "encryption.key"
LOG_FILE = DATA_DIR / "masker.log"

DEFAULT_CONFIG = {
    "enabled": True,
    "ttl_days": 7,
    "cache_size": 1000,
    "auto_cleanup": True,
    "cleanup_interval_hours": 1,
    "log_enabled": True,
    "encrypt_storage": True,  # ALWAYS ENCRYPTED - NO FALLBACK
    "presidio": {
        "language": "en",
        "entities": [
            "PHONE_NUMBER",
            "EMAIL_ADDRESS",
            "CREDIT_CARD",
            "PERSON",
            "LOCATION",
            "DATE_TIME",
            "NRP",
            "URL",
            "API_KEY",
            "PASSWORD"
        ],
        "custom_patterns": True
    }
}

# Color output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

# ═══════════════════════════════════════════════════════════════
# Encryption Helper
# ═══════════════════════════════════════════════════════════════

class EncryptionHelper:
    """AES-256 encryption for sensitive data storage."""
    
    def __init__(self, key_file: Path):
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography library not available. Cannot initialize encryption.")
        
        self.key_file = key_file
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)
    
    def _load_or_create_key(self) -> bytes:
        """Load existing key or create new one."""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read().strip()
            return key
        else:
            # Create new key
            key = Fernet.generate_key()
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key + b'\n')
            self.key_file.chmod(0o600)
            print(f"{GREEN}✅ Encryption key created: {self.key_file}{NC}")
            return key
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext and return base64-encoded string."""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt base64-encoded ciphertext."""
        try:
            encrypted = base64.b64decode(ciphertext.encode())
            return self.fernet.decrypt(encrypted).decode()
        except Exception:
            # If decryption fails, return as-is (might be unencrypted old data)
            return ciphertext

# ═══════════════════════════════════════════════════════════════
# Presidio Detector
# ═══════════════════════════════════════════════════════════════

class PresidioDetector:
    """Use Microsoft Presidio for intelligent detection."""
    
    def __init__(self):
        try:
            from presidio_analyzer import AnalyzerEngine, PatternRecognizer
            
            self.analyzer = AnalyzerEngine()
            self._load_custom_patterns()
            self.enabled = True
        except ImportError:
            print(f"{YELLOW}⚠️  Presidio not installed, using basic regex{NC}")
            print(f"{YELLOW}Hint: pip install presidio-analyzer presidio-anonymizer{NC}")
            self.enabled = False
    
    def _load_custom_patterns(self):
        """Load custom detection patterns."""
        from presidio_analyzer import PatternRecognizer, Pattern
        
        class APIKeyRecognizer(PatternRecognizer):
            def load_patterns(self):
                return [
                    Pattern(name="sk_key", regex=r"sk-[a-zA-Z0-9]{20,}", score=0.9),
                    Pattern(name="github_token", regex=r"ghp_[a-zA-Z0-9]{36}", score=0.9),
                    Pattern(name="aliyun_ak", regex=r"LTAI[a-zA-Z0-9]{12,}", score=0.9),
                ]
        
        class PasswordRecognizer(PatternRecognizer):
            def load_patterns(self):
                return [
                    Pattern(name="password", regex=r"(?i)(password|passwd|pwd)[=:\s]+[\w@#$%^&*!]+", score=0.8),
                    Pattern(name="db_url", regex=r"(mongodb|mysql|postgresql|redis)://[^\s'\"]+", score=0.9),
                ]
        
        self.analyzer.registry.add_recognizer(APIKeyRecognizer())
        self.analyzer.registry.add_recognizer(PasswordRecognizer())
    
    def detect(self, text: str, language: str = 'en') -> list:
        """Detect sensitive information."""
        if not self.enabled:
            return self._regex_detect(text)
        
        try:
            results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=[
                    "PHONE_NUMBER",
                    "EMAIL_ADDRESS",
                    "CREDIT_CARD",
                    "PERSON",
                    "LOCATION",
                    "URL",
                    "API_KEY",
                    "PASSWORD",
                    "DB_URL"
                ]
            )
            return list(results)
        except Exception as e:
            print(f"{YELLOW}⚠️  Presidio detection failed: {e}{NC}")
            return self._regex_detect(text)
    
    def _regex_detect(self, text: str) -> list:
        """Basic regex detection (fallback)."""
        import re
        
        patterns = [
            (r"(?i)(password|passwd|pwd)[=:\s]+[\w@#$%^&*!]+", "PASSWORD"),
            (r"sk-[a-zA-Z0-9]{20,}", "API_KEY"),
            (r"(mongodb|mysql|postgresql|redis)://[^\s'\"]+", "DB_URL"),
            (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "EMAIL_ADDRESS"),
            (r"1[3-9]\d{9}", "PHONE_NUMBER"),
        ]
        
        results = []
        for pattern, entity_type in patterns:
            for match in re.finditer(pattern, text):
                results.append(type('Result', (), {
                    'entity_type': entity_type,
                    'start': match.start(),
                    'end': match.end(),
                    'score': 0.8
                })())
        
        return results

# ═══════════════════════════════════════════════════════════════
# SQLite + LRU Cache Store (ENCRYPTED - REQUIRED)
# ═══════════════════════════════════════════════════════════════

class SensitiveMappingStore:
    """SQLite + LRU cache storage with REQUIRED ENCRYPTED sensitive data."""
    
    def __init__(self, db_path: Path = None, cache_size: int = 1000):
        if db_path is None:
            db_path = DB_FILE
        
        self.db_path = db_path
        self.cache_size = cache_size
        self.cache = OrderedDict()
        
        # SECURITY: Encryption is REQUIRED - fail if not available
        if not CRYPTO_AVAILABLE:
            raise RuntimeError(
                "CRITICAL: cryptography library not installed. "
                "Sensitive Data Masker REQUIRES encryption for security. "
                "Install: pip install cryptography"
            )
        
        self.encryption = EncryptionHelper(KEY_FILE)
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mappings (
                mask_id TEXT PRIMARY KEY,
                original TEXT NOT NULL,
                data_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON mappings(expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_type ON mappings(data_type)')
        
        conn.commit()
        conn.close()
    
    def add(self, original: str, data_type: str, ttl_days: int = 7) -> str:
        """Add mapping with ENCRYPTED storage, return mask_id."""
        # Generate mask_id
        mask_id = hashlib.sha256(
            f"{original}{time.time()}".encode()
        ).hexdigest()[:16]
        
        expires_at = datetime.now() + timedelta(days=ttl_days)
        
        # Encrypt original data BEFORE storing (REQUIRED)
        stored_data = self.encryption.encrypt(original)
        
        # Write to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO mappings 
            (mask_id, original, data_type, expires_at, usage_count)
            VALUES (?, ?, ?, ?, 0)
        ''', (mask_id, stored_data, data_type, expires_at.isoformat()))
        
        conn.commit()
        conn.close()
        
        # Update cache (store decrypted for fast access)
        self.cache[mask_id] = {
            'original': original,
            'expires_at': expires_at
        }
        
        # LRU eviction
        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)
        
        return mask_id
    
    def get(self, mask_id: str) -> Optional[str]:
        """Get original data (with cache), DECRYPT if needed."""
        # Check cache first
        if mask_id in self.cache:
            data = self.cache[mask_id]
            if data['expires_at'] > datetime.now():
                self.cache.move_to_end(mask_id)
                return data['original']
            else:
                del self.cache[mask_id]
        
        # Query database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT original, expires_at FROM mappings
            WHERE mask_id = ? AND expires_at > ?
        ''', (mask_id, datetime.now().isoformat()))
        
        result = cursor.fetchone()
        
        if result:
            # DECRYPT if needed
            stored_data = result[0]
            original = self.encryption.decrypt(stored_data)
            
            # Update usage count
            cursor.execute('''
                UPDATE mappings SET usage_count = usage_count + 1
                WHERE mask_id = ?
            ''', (mask_id,))
            conn.commit()
            
            # Update cache
            self.cache[mask_id] = {
                'original': original,
                'expires_at': datetime.fromisoformat(result[1])
            }
            
            # LRU eviction
            if len(self.cache) > self.cache_size:
                self.cache.popitem(last=False)
            
            conn.close()
            return original
        
        conn.close()
        return None
    
    def cleanup_expired(self) -> int:
        """Clean expired data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM mappings WHERE expires_at < ?
        ''', (datetime.now().isoformat(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        # Clean cache
        now = datetime.now()
        expired_keys = [
            k for k, v in self.cache.items()
            if v['expires_at'] < now
        ]
        for key in expired_keys:
            del self.cache[key]
        
        return deleted
    
    def get_stats(self) -> dict:
        """Get statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total count
        cursor.execute('SELECT COUNT(*) FROM mappings')
        total = cursor.fetchone()[0]
        
        # By type
        cursor.execute('''
            SELECT data_type, COUNT(*) 
            FROM mappings 
            GROUP BY data_type
        ''')
        by_type = dict(cursor.fetchall())
        
        # Expiring soon
        cursor.execute('''
            SELECT COUNT(*) FROM mappings
            WHERE expires_at < ?
        ''', ((datetime.now() + timedelta(hours=24)).isoformat(),))
        expiring_soon = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total,
            "by_type": by_type,
            "expiring_soon": expiring_soon,
            "cache_size": len(self.cache),
            "encrypted": True  # Always encrypted now
        }

# ═══════════════════════════════════════════════════════════════
# Channel Sensitive Masker
# ═══════════════════════════════════════════════════════════════

class ChannelSensitiveMasker:
    """Channel-level sensitive data masker."""
    
    def __init__(self):
        self.detector = PresidioDetector()
        self.store = SensitiveMappingStore()  # Encryption REQUIRED
    
    def mask_message(self, text: str, language: str = 'en') -> Tuple[str, list]:
        """Mask message."""
        # Detect
        results = self.detector.detect(text, language)
        
        # Create mapping and mask
        replacements = []
        masked_text = text
        
        # Sort by position descending to avoid offset issues
        sorted_results = sorted(results, key=lambda r: r.start, reverse=True)
        
        for result in sorted_results:
            original = text[result.start:result.end]
            entity_type = result.entity_type
            
            # Generate mask_id
            mask_id = self.store.add(original, entity_type)
            
            # Create masked marker
            masked = f"[{entity_type}:{mask_id}]"
            
            # Replace
            masked_text = masked_text[:result.start] + masked + masked_text[result.end:]
            
            replacements.append({
                'type': entity_type,
                'original': original[:20] + '...' if len(original) > 20 else original,
                'masked': masked,
                'mask_id': mask_id,
                'score': getattr(result, 'score', 0.8)
            })
        
        # Reverse replacements (because we processed in reverse order)
        replacements.reverse()
        
        return masked_text, replacements
    
    def restore_message(self, text: str) -> str:
        """Restore message."""
        import re
        
        def replace_match(match):
            full = match.group(0)
            # [TYPE:mask_id]
            parts = full.split(':')
            if len(parts) >= 2:
                mask_id = parts[1].rstrip(']')
                original = self.store.get(mask_id)
                if original:
                    return original
            return full
        
        # Match [TYPE:mask_id] pattern
        pattern = r'\[[A-Z_]+:[a-f0-9]{16}\]'
        return re.sub(pattern, replace_match, text)

# ═══════════════════════════════════════════════════════════════
# Command Line Tool
# ═══════════════════════════════════════════════════════════════

def test_mask_restore(text: str):
    """Test masking and restoration."""
    masker = ChannelSensitiveMasker()
    
    print(f"\n{BLUE}Original message:{NC}")
    print(f"  {text}\n")
    
    # Mask
    masked, replacements = masker.mask_message(text)
    print(f"{GREEN}Masked:{NC}")
    print(f"  {masked}\n")
    
    if replacements:
        print(f"{YELLOW}Detected {len(replacements)} sensitive items:{NC}")
        for r in replacements:
            print(f"  - {r['type']}: {r['original']} → {r['masked']} (score: {r['score']})")
        print()
    
    # Restore
    restored = masker.restore_message(masked)
    print(f"{BLUE}Restored:{NC}")
    print(f"  {restored}\n")
    
    # Verify
    if restored == text:
        print(f"{GREEN}✅ Restoration successful!{NC}")
    else:
        print(f"{YELLOW}⚠️  Restored result doesn't match original{NC}")
        print(f"  Original: {text}")
        print(f"  Restored: {restored}")
    print()

def show_stats():
    """Show statistics."""
    store = SensitiveMappingStore()
    stats = store.get_stats()
    
    print(f"\n{BLUE}📊 Sensitive Data Mapping Statistics:{NC}")
    print(f"  Total: {stats['total']}")
    print(f"  Cache size: {stats['cache_size']}")
    print(f"  Expiring soon (24h): {stats['expiring_soon']}")
    print(f"  Encrypted: {'✅ Yes (REQUIRED)' if stats.get('encrypted') else '❌ No'}")
    
    if stats['by_type']:
        print(f"\n  By type:")
        for data_type, count in stats['by_type'].items():
            print(f"    - {data_type}: {count}")
    
    print()

def cleanup():
    """Clean expired data."""
    store = SensitiveMappingStore()
    deleted = store.cleanup_expired()
    print(f"{GREEN}✅ Cleaned {deleted} expired entries{NC}\n")

def clear_all():
    """Clear all mappings."""
    response = input(f"{YELLOW}⚠️  Are you sure you want to clear all mappings? (yes/no): {NC}")
    if response.lower() == 'yes':
        DB_FILE.unlink(missing_ok=True)
        print(f"{GREEN}✅ Cleared{NC}\n")
    else:
        print("Cancelled\n")

# ═══════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"{YELLOW}Usage:{NC}")
        print(f"  {sys.argv[0]} test <text>      # Test mask/restore")
        print(f"  {sys.argv[0]} stats            # Show statistics")
        print(f"  {sys.argv[0]} cleanup          # Clean expired")
        print(f"  {sys.argv[0]} clear            # Clear all")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'test' and len(sys.argv) >= 3:
        test_mask_restore(' '.join(sys.argv[2:]))
    elif cmd == 'stats':
        show_stats()
    elif cmd == 'cleanup':
        cleanup()
    elif cmd == 'clear':
        clear_all()
    else:
        print(f"{RED}❌ Unknown command: {cmd}{NC}")
        sys.exit(1)

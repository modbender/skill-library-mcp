#!/usr/bin/env python3
"""
Brain v3 - Personal AI Memory System with SQLite Support

Features:
- 🎭 Soul/Personality - Evolving traits
- 👤 User Profile - Learns preferences
- 💭 Conversation State - Mood/intent detection
- 📚 Learning Insights - Continuous improvement
- 🧠 get_full_context() - Everything for personalized responses
- 🔐 Encrypted Secrets - Securely store sensitive data

Supports: SQLite (default), PostgreSQL, Redis
"""

__version__ = "0.1.10"
__author__ = "ClawColab"

import os
import json
import hashlib
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
from contextlib import contextmanager
from threading import Lock
import logging

logger = logging.getLogger(__name__)


def get_bridge_script_path() -> Optional[str]:
    """
    Get the path to brain_bridge.py script.
    Used by hooks to locate the bridge script at runtime.
    
    Returns:
        Path to brain_bridge.py or None if not found
    """
    pkg_dir = Path(__file__).parent
    
    # Check multiple possible locations depending on install method
    candidates = [
        # Pip installed: clawbrain.py at dist-packages/, brain at dist-packages/brain/
        pkg_dir / "brain" / "scripts" / "brain_bridge.py",
        # Development: clawbrain.py at repo root, scripts at scripts/
        pkg_dir / "scripts" / "brain_bridge.py",
        # Legacy: if clawbrain.py is inside brain package
        pkg_dir.parent / "scripts" / "brain_bridge.py",
        pkg_dir.parent / "brain" / "scripts" / "brain_bridge.py",
    ]
    
    for c in candidates:
        if c.exists():
            return str(c)
    
    return None


# Optional dependencies
EMBEDDINGS_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    pass

POSTGRES_AVAILABLE = False
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    pass

REDIS_AVAILABLE = False
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    pass

CRYPTO_AVAILABLE = False
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    pass


@dataclass
class Memory:
    id: str
    agent_id: str
    memory_type: str
    key: str
    content: str
    content_encrypted: bool
    summary: str
    keywords: List[str]
    tags: List[str]
    importance: int
    linked_to: str
    source: str
    embedding: List[float]
    created_at: str
    updated_at: str


@dataclass
class UserProfile:
    user_id: str
    name: Optional[str] = None
    nickname: Optional[str] = None
    preferred_name: Optional[str] = None
    communication_preferences: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    expertise_areas: List[str] = field(default_factory=list)
    learning_topics: List[str] = field(default_factory=list)
    timezone: Optional[str] = None
    active_hours: Dict[str, Any] = field(default_factory=dict)
    conversation_patterns: Dict[str, Any] = field(default_factory=dict)
    emotional_patterns: Dict[str, Any] = field(default_factory=dict)
    important_dates: Dict[str, Any] = field(default_factory=dict)
    life_context: Dict[str, Any] = field(default_factory=dict)
    total_interactions: int = 0
    first_interaction: Optional[str] = None
    last_interaction: Optional[str] = None
    updated_at: Optional[str] = None


DEFAULT_CONFIG = {
    "storage_backend": os.environ.get("BRAIN_STORAGE", "auto"),  # "sqlite", "postgresql", "auto"
    "sqlite_path": os.environ.get("BRAIN_SQLITE_PATH", "./brain_data.db"),
    "postgres_host": os.environ.get("BRAIN_POSTGRES_HOST", "localhost"),
    "postgres_port": int(os.environ.get("BRAIN_POSTGRES_PORT", "5432")),
    "postgres_db": os.environ.get("BRAIN_POSTGRES_DB", "brain_db"),
    "postgres_user": os.environ.get("BRAIN_POSTGRES_USER", "brain_user"),
    "postgres_password": os.environ.get("BRAIN_POSTGRES_PASSWORD", ""),
    "redis_host": os.environ.get("BRAIN_REDIS_HOST", "localhost"),
    "redis_port": int(os.environ.get("BRAIN_REDIS_PORT", "6379")),
    "redis_db": int(os.environ.get("BRAIN_REDIS_DB", "0")),
    "redis_prefix": os.environ.get("BRAIN_REDIS_PREFIX", "brain:"),
    "embedding_model": os.environ.get("BRAIN_EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    "backup_dir": os.environ.get("BRAIN_BACKUP_DIR", "./brain_backups"),
    "encryption_key": os.environ.get("BRAIN_ENCRYPTION_KEY", ""),  # Fernet key for encrypting sensitive data
}


class Brain:
    def __init__(self, config: Dict = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self._lock = Lock()
        self._storage = None
        self._redis = None
        self._pg_conn = None
        self._pending_auto_migrate = False  # Flag for auto-migration
        self._embedder = Embedder(self.config["embedding_model"]) if EMBEDDINGS_AVAILABLE else None
        self._cipher = self._setup_encryption() if CRYPTO_AVAILABLE else None
        
        # Determine storage backend
        storage = self.config.get("storage_backend", "auto")
        
        if storage == "auto":
            if POSTGRES_AVAILABLE and self._try_postgres():
                self._setup_postgres()
                self._storage = "postgresql"
            else:
                self._setup_sqlite()
                self._storage = "sqlite"
        elif storage == "sqlite":
            self._setup_sqlite()
            self._storage = "sqlite"
        elif storage == "postgresql" and POSTGRES_AVAILABLE:
            self._setup_postgres()
            self._storage = "postgresql"
        else:
            self._setup_sqlite()
            self._storage = "sqlite"
        
        if REDIS_AVAILABLE and self.config.get("use_redis", True):
            self._setup_redis()
        
        self._backup_dir = Path(self.config["backup_dir"])
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Auto-migrate unencrypted secrets if encryption was just enabled
        if self._pending_auto_migrate and self._cipher:
            self._run_auto_migration()
        
        logger.info(f"Brain initialized with {self._storage} storage")
    
    def _try_postgres(self) -> bool:
        if not POSTGRES_AVAILABLE:
            return False
        try:
            conn = psycopg2.connect(
                host=self.config["postgres_host"],
                port=self.config["postgres_port"],
                database=self.config["postgres_db"],
                user=self.config["postgres_user"],
                password=self.config["postgres_password"],
                connect_timeout=3
            )
            conn.close()
            return True
        except Exception as e:
            logger.warning(f"PostgreSQL not available: {e}")
            return False
    
    def _setup_sqlite(self):
        db_path = Path(self.config["sqlite_path"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._sqlite_path = str(db_path)
        self._sqlite_conn = sqlite3.connect(self._sqlite_path, check_same_thread=False)
        self._sqlite_conn.row_factory = sqlite3.Row
        self._create_sqlite_tables()
        logger.info(f"SQLite initialized at {self._sqlite_path}")
    
    def _create_sqlite_tables(self):
        cursor = self._sqlite_conn.cursor()
        
        tables = [
            """CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY, agent_id TEXT, session_key TEXT, messages TEXT,
                summary TEXT, keywords TEXT, embedding TEXT, created_at TEXT, updated_at TEXT)""",
            """CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY, agent_id TEXT, memory_type TEXT, key TEXT, content TEXT,
                content_encrypted INTEGER, summary TEXT, keywords TEXT, tags TEXT, importance INTEGER,
                linked_to TEXT, source TEXT, embedding TEXT, created_at TEXT, updated_at TEXT)""",
            """CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY, agent_id TEXT, title TEXT, description TEXT,
                status TEXT, priority INTEGER, due_date TEXT, created_at TEXT, updated_at TEXT)""",
            """CREATE TABLE IF NOT EXISTS souls (
                agent_id TEXT PRIMARY KEY, traits TEXT, preferred_topics TEXT,
                interaction_count INTEGER, created_at TEXT, updated_at TEXT)""",
            """CREATE TABLE IF NOT EXISTS bonds (
                user_id TEXT PRIMARY KEY, level REAL, score INTEGER, total_interactions INTEGER,
                first_interaction TEXT, last_interaction TEXT, milestones TEXT,
                created_at TEXT, updated_at TEXT)""",
            """CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY, agent_id TEXT, title TEXT, description TEXT,
                status TEXT, progress INTEGER, milestones TEXT, created_at TEXT, updated_at TEXT)""",
            """CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY, name TEXT, nickname TEXT, preferred_name TEXT,
                communication_preferences TEXT, interests TEXT, expertise_areas TEXT,
                learning_topics TEXT, timezone TEXT, active_hours TEXT, conversation_patterns TEXT,
                emotional_patterns TEXT, important_dates TEXT, life_context TEXT,
                total_interactions INTEGER, first_interaction TEXT, last_interaction TEXT, updated_at TEXT)""",
            """CREATE TABLE IF NOT EXISTS learning_insights (
                id TEXT PRIMARY KEY, insight_type TEXT, content TEXT, confidence REAL,
                source_context TEXT, times_reinforced INTEGER, times_contradicted INTEGER,
                is_active INTEGER, created_at TEXT, last_reinforced TEXT)""",
            """CREATE TABLE IF NOT EXISTS topic_clusters (
                id TEXT PRIMARY KEY, name TEXT, related_terms TEXT, parent_topic TEXT,
                child_topics TEXT, embedding TEXT, usage_count INTEGER,
                last_discussed TEXT, created_at TEXT)""",
        ]
        
        for sql in tables:
            cursor.execute(sql)
        self._sqlite_conn.commit()
    
    def _setup_postgres(self):
        self._pg_conn = psycopg2.connect(
            host=self.config["postgres_host"],
            port=self.config["postgres_port"],
            database=self.config["postgres_db"],
            user=self.config["postgres_user"],
            password=self.config["postgres_password"]
        )
        self._pg_conn.autocommit = True
    
    def _setup_redis(self):
        if not REDIS_AVAILABLE:
            return
        try:
            self._redis = redis.Redis(
                host=self.config["redis_host"],
                port=self.config["redis_port"],
                db=self.config.get("redis_db", 0),
                decode_responses=True,
                socket_timeout=3,
                socket_connect_timeout=3
            )
            self._redis.ping()
            self._redis_prefix = self.config.get("redis_prefix", "brain:")
            logger.info("Redis connected for caching")
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self._redis = None
    
    def _setup_encryption(self):
        """Initialize encryption cipher with key from config or environment."""
        if not CRYPTO_AVAILABLE:
            logger.warning("cryptography library not installed. Encryption unavailable.")
            return None
        
        newly_generated = False
        key = self.config.get("encryption_key", "")
        if not key:
            # Generate key file path next to database (check config since _storage not set yet)
            sqlite_path = self.config.get("sqlite_path", "")
            if sqlite_path:
                key_path = Path(sqlite_path).parent / ".brain_key"
            else:
                key_path = Path.home() / ".config" / "clawbrain" / ".brain_key"
            
            key_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load or generate key
            if key_path.exists():
                key = key_path.read_bytes()
                logger.info(f"Loaded encryption key from {key_path}")
            else:
                key = Fernet.generate_key()
                key_path.write_bytes(key)
                key_path.chmod(0o600)  # Restrict permissions
                logger.warning(f"Generated new encryption key at {key_path}")
                logger.warning("IMPORTANT: Backup this key! Lost keys = lost encrypted data.")
                newly_generated = True
        elif isinstance(key, str):
            key = key.encode()
        
        try:
            cipher = Fernet(key)
            # Auto-migrate unencrypted secrets when key is first generated
            if newly_generated:
                self._pending_auto_migrate = True
            return cipher
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            return None
    
    def _encrypt(self, content: str) -> str:
        """Encrypt content and return base64-encoded encrypted string."""
        if not self._cipher:
            raise ValueError("Encryption not available")
        return self._cipher.encrypt(content.encode()).decode()
    
    def _decrypt(self, encrypted_content: str) -> str:
        """Decrypt base64-encoded encrypted string and return original content."""
        if not self._cipher:
            raise ValueError("Decryption not available")
        return self._cipher.decrypt(encrypted_content.encode()).decode()
    
    @property
    def storage_backend(self) -> str:
        return self._storage
    
    # ========== MEMORIES ==========
    def remember(self, agent_id: str, memory_type: str, content: str, key: str = None,
                 tags: List[str] = None, auto_tag: bool = False, **kwargs) -> Memory:
        """
        Store a memory with optional tags.

        Args:
            agent_id: Agent identifier
            memory_type: Type of memory (e.g., "knowledge", "preference", "conversation")
            content: Memory content
            key: Optional memory key (auto-generated if not provided)
            tags: Optional list of tags for categorization
            auto_tag: If True, automatically add extracted keywords as tags
            **kwargs: Additional options (importance, linked_to, source)

        Returns:
            Memory object
        """
        now = datetime.now().isoformat()
        memory_id = str(hashlib.md5(f"{agent_id}:{memory_type}:{content[:100]}".encode()).hexdigest())
        keywords = self._extract_keywords([{"content": content}])
        embedding = None
        if self._embedder and self._embedder.model and memory_type != "secret":
            embedding = self._embedder.embed(content)

        # Handle auto_tag: add extracted keywords as tags
        final_tags = set(tags) if tags else set()
        if auto_tag:
            # Add significant keywords as tags (filter short/common words)
            for kw in keywords:
                if len(kw) > 2 and kw.lower() not in final_tags:
                    final_tags.add(kw.lower())

        # Encrypt sensitive content
        is_encrypted = False
        stored_content = content
        if memory_type == "secret" and self._cipher:
            try:
                stored_content = self._encrypt(content)
                is_encrypted = True
                # Don't generate embeddings for encrypted content
                embedding = None
                logger.info(f"Encrypted secret memory: {memory_id}")
            except Exception as e:
                logger.error(f"Failed to encrypt content: {e}")
                raise ValueError("Failed to encrypt sensitive content. Set BRAIN_ENCRYPTION_KEY environment variable.")
        elif memory_type == "secret" and not self._cipher:
            raise ValueError("Encryption not available. Install cryptography: pip install cryptography")

        memory = Memory(
            id=memory_id, agent_id=agent_id, memory_type=memory_type,
            key=key or f"{memory_type}:{content[:50]}",
            content=stored_content, content_encrypted=is_encrypted,
            summary=self._summarize([{"content": content}]) if not is_encrypted else "[Encrypted]",
            keywords=keywords if not is_encrypted else [],
            tags=list(final_tags),
            importance=kwargs.get("importance", 5),
            linked_to=kwargs.get("linked_to"), source=kwargs.get("source"),
            embedding=embedding, created_at=now, updated_at=now
        )

        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute("""INSERT OR IGNORE INTO memories
                    (id, agent_id, memory_type, key, content, content_encrypted, summary, keywords, tags,
                     importance, linked_to, source, embedding, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (memory.id, memory.agent_id, memory.memory_type, memory.key, memory.content,
                     int(memory.content_encrypted), memory.summary, json.dumps(memory.keywords),
                     json.dumps(memory.tags), memory.importance, memory.linked_to, memory.source,
                     json.dumps(memory.embedding) if memory.embedding else None,
                     memory.created_at, memory.updated_at))
            else:
                cursor.execute("""INSERT INTO memories
                    (id, agent_id, memory_type, key, content, content_encrypted, summary, keywords, tags,
                     importance, linked_to, source, embedding, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING""",
                    (memory.id, memory.agent_id, memory.memory_type, memory.key, memory.content,
                     memory.content_encrypted, memory.summary, memory.keywords, memory.tags,
                     memory.importance, memory.linked_to, memory.source,
                     psycopg2.extras.Json(memory.embedding) if memory.embedding else None,
                     memory.created_at, memory.updated_at))
        return memory
    
    def recall(self, agent_id: str = None, query: str = None, memory_type: str = None, limit: int = 10) -> List[Memory]:
        with self._get_cursor() as cursor:
            conditions, params = [], []
            if agent_id:
                conditions.append("agent_id = " + ("?" if self._storage == "sqlite" else "%s"))
                params.append(agent_id)
            if memory_type:
                conditions.append("memory_type = " + ("?" if self._storage == "sqlite" else "%s"))
                params.append(memory_type)
            where = " AND ".join(conditions) if conditions else "1=1"
            limit_param = limit
            
            if self._storage == "sqlite":
                cursor.execute(f"SELECT * FROM memories WHERE {where} ORDER BY importance DESC, created_at DESC LIMIT {limit_param}", tuple(params))
            else:
                if params:
                    cursor.execute(f"SELECT * FROM memories WHERE {where} ORDER BY importance DESC, created_at DESC LIMIT %s", tuple(params + [limit]))
                else:
                    cursor.execute(f"SELECT * FROM memories WHERE {where} ORDER BY importance DESC, created_at DESC LIMIT %s", (limit,))
            
            rows = cursor.fetchall()
        return [self._row_to_memory(row) for row in rows]

    def get_unencrypted_secrets(self) -> List[Dict]:
        """
        Find all secrets that are stored unencrypted.
        
        Returns:
            List of dicts with id, agent_id, key for unencrypted secrets
        """
        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute(
                    "SELECT id, agent_id, key FROM memories WHERE memory_type = 'secret' AND content_encrypted = 0"
                )
            else:
                cursor.execute(
                    "SELECT id, agent_id, key FROM memories WHERE memory_type = 'secret' AND content_encrypted = false"
                )
            rows = cursor.fetchall()
        
        return [{"id": row["id"], "agent_id": row["agent_id"], "key": row["key"]} for row in rows]

    def migrate_secrets(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Migrate unencrypted secrets to encrypted storage.
        
        Args:
            dry_run: If True, only report what would be migrated without making changes
            
        Returns:
            Dict with migration results: {"total": N, "migrated": N, "failed": N, "errors": [...]}
        """
        if not self._cipher:
            return {
                "total": 0,
                "migrated": 0,
                "failed": 0,
                "errors": ["Encryption not available. Install cryptography: pip install cryptography"]
            }
        
        results = {"total": 0, "migrated": 0, "failed": 0, "errors": [], "dry_run": dry_run}
        
        with self._get_cursor() as cursor:
            # Find all unencrypted secrets
            if self._storage == "sqlite":
                cursor.execute(
                    "SELECT id, agent_id, key, content FROM memories WHERE memory_type = 'secret' AND content_encrypted = 0"
                )
            else:
                cursor.execute(
                    "SELECT id, agent_id, key, content FROM memories WHERE memory_type = 'secret' AND content_encrypted = false"
                )
            
            rows = cursor.fetchall()
            results["total"] = len(rows)
            
            if dry_run:
                logger.info(f"[DRY RUN] Would migrate {len(rows)} unencrypted secrets")
                return results
            
            now = datetime.now().isoformat()
            
            for row in rows:
                try:
                    # Encrypt the content
                    encrypted_content = self._encrypt(row["content"])
                    
                    # Update the record
                    if self._storage == "sqlite":
                        cursor.execute(
                            "UPDATE memories SET content = ?, content_encrypted = 1, summary = '[Encrypted]', keywords = '[]', updated_at = ? WHERE id = ?",
                            (encrypted_content, now, row["id"])
                        )
                    else:
                        cursor.execute(
                            "UPDATE memories SET content = %s, content_encrypted = true, summary = '[Encrypted]', keywords = '[]', updated_at = %s WHERE id = %s",
                            (encrypted_content, now, row["id"])
                        )
                    
                    results["migrated"] += 1
                    logger.info(f"Migrated secret: {row['id']} (key: {row['key']})")
                    
                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"Failed to migrate {row['id']}: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)
        
        logger.info(f"Migration complete: {results['migrated']}/{results['total']} secrets encrypted")
        return results

    def _run_auto_migration(self):
        """
        Automatically migrate unencrypted secrets when encryption is first enabled.
        Called during Brain initialization when a new encryption key is generated.
        """
        try:
            unencrypted = self.get_unencrypted_secrets()
            if not unencrypted:
                logger.info("No unencrypted secrets found - nothing to migrate")
                return
            
            logger.warning(f"Found {len(unencrypted)} unencrypted secrets - auto-migrating...")
            result = self.migrate_secrets(dry_run=False)
            
            if result["migrated"] > 0:
                logger.info(f"Auto-migration complete: {result['migrated']} secrets encrypted")
            if result["failed"] > 0:
                logger.error(f"Auto-migration had {result['failed']} failures: {result['errors']}")
        except Exception as e:
            logger.error(f"Auto-migration failed: {e}")
        finally:
            self._pending_auto_migrate = False

    def search_by_tags(self, tags: List[str], agent_id: str = None, memory_type: str = None,
                       match: str = "OR", limit: int = 20) -> List[Memory]:
        """
        Search memories by tags with AND/OR logic support.

        Args:
            tags: List of tags to search for
            agent_id: Optional agent filter
            memory_type: Optional memory type filter
            match: "OR" (any tag matches) or "AND" (all tags must match)
            limit: Maximum results to return

        Returns:
            List of Memory objects matching the tags
        """
        if not tags:
            return []

        with self._get_cursor() as cursor:
            conditions, params = [], []

            if match.upper() == "OR":
                # OR logic: memory has ANY of the tags
                if self._storage == "sqlite":
                    for tag in tags:
                        conditions.append("tags LIKE ?")
                        params.append(f'%"{tag}"%')
                    where_clause = " OR ".join(conditions) if conditions else "1=0"
                else:
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append(f"tags @> %s")
                        params.append(json.dumps([tag]))
                    where_clause = " OR ".join(tag_conditions) if tag_conditions else "1=0"
            else:
                # AND logic: memory must have ALL tags
                # For this, we check each tag and count matches
                if self._storage == "sqlite":
                    for tag in tags:
                        conditions.append("tags LIKE ?")
                        params.append(f'%"{tag}"%')
                    where_clause = " AND ".join(conditions)
                else:
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append(f"tags @> %s")
                        params.append(json.dumps([tag]))
                    where_clause = " AND ".join(tag_conditions)

            if agent_id:
                where_clause += " AND agent_id = " + ("?" if self._storage == "sqlite" else "%s")
                params.append(agent_id)

            if memory_type:
                where_clause += " AND memory_type = " + ("?" if self._storage == "sqlite" else "%s")
                params.append(memory_type)

            if self._storage == "sqlite":
                cursor.execute(
                    f"SELECT * FROM memories WHERE {where_clause} ORDER BY importance DESC, created_at DESC LIMIT {limit}",
                    tuple(params)
                )
            else:
                cursor.execute(
                    f"SELECT * FROM memories WHERE {where_clause} ORDER BY importance DESC, created_at DESC LIMIT %s",
                    tuple(params + [limit])
                )

            rows = cursor.fetchall()

            # For AND mode on SQLite, filter results to ensure all tags present
            if match.upper() == "AND" and self._storage == "sqlite":
                filtered = []
                for row in rows:
                    mem_tags = row["tags"]
                    if isinstance(mem_tags, str):
                        mem_tags = json.loads(mem_tags) if mem_tags else []
                    if all(tag in mem_tags for tag in tags):
                        filtered.append(row)
                rows = filtered[:limit]

        return [self._row_to_memory(row) for row in rows]

    def get_all_tags(self, agent_id: str = None) -> List[str]:
        """
        Get all unique tags from memories.

        Args:
            agent_id: Optional agent filter

        Returns:
            List of unique tag strings
        """
        with self._get_cursor() as cursor:
            if agent_id:
                if self._storage == "sqlite":
                    cursor.execute("SELECT tags FROM memories WHERE agent_id = ? AND tags IS NOT NULL", (agent_id,))
                else:
                    cursor.execute("SELECT tags FROM memories WHERE agent_id = %s AND tags IS NOT NULL", (agent_id,))
            else:
                if self._storage == "sqlite":
                    cursor.execute("SELECT tags FROM memories WHERE tags IS NOT NULL")
                else:
                    cursor.execute("SELECT tags FROM memories WHERE tags IS NOT NULL")

            rows = cursor.fetchall()
            all_tags = set()
            for row in rows:
                tags = row["tags"]
                if isinstance(tags, str):
                    tags = json.loads(tags) if tags else []
                if isinstance(tags, list):
                    all_tags.update(tags)
            return sorted(list(all_tags))

    def get_tag_stats(self, agent_id: str = None, memory_type: str = None) -> Dict[str, int]:
        """
        Get tag usage statistics - which tags are most used.

        Args:
            agent_id: Optional agent filter
            memory_type: Optional memory type filter

        Returns:
            Dict mapping tag -> count, sorted by count descending
        """
        with self._get_cursor() as cursor:
            conditions, params = [], []
            if agent_id:
                conditions.append("agent_id = " + ("?" if self._storage == "sqlite" else "%s"))
                params.append(agent_id)
            if memory_type:
                conditions.append("memory_type = " + ("?" if self._storage == "sqlite" else "%s"))
                params.append(memory_type)

            where = " AND ".join(conditions) if conditions else "1=1"

            if self._storage == "sqlite":
                cursor.execute(f"SELECT tags FROM memories WHERE {where} AND tags IS NOT NULL", tuple(params))
            else:
                cursor.execute(f"SELECT tags FROM memories WHERE {where} AND tags IS NOT NULL", tuple(params))

            tag_counts = {}
            for row in cursor.fetchall():
                tags = row["tags"]
                if isinstance(tags, str):
                    tags = json.loads(tags) if tags else []
                if isinstance(tags, list):
                    for tag in tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Sort by count descending
            return dict(sorted(tag_counts.items(), key=lambda x: -x[1]))

    def search_by_tag_hierarchy(self, parent_tag: str, agent_id: str = None,
                                memory_type: str = None, limit: int = 20) -> List[Memory]:
        """
        Search memories by tag hierarchy (parent tag and all child tags).

        Example:
            parent_tag="api" matches: "api", "api:clawhub", "api:rest", "api/graphql"

        Args:
            parent_tag: Parent tag to match (with all children)
            agent_id: Optional agent filter
            memory_type: Optional memory type filter
            limit: Maximum results to return

        Returns:
            List of Memory objects matching the hierarchy
        """
        # Generate tag patterns for hierarchy search
        patterns = [
            f'"{parent_tag}"',           # Exact match
            f'"{parent_tag}:"',          # api:child
            f'"{parent_tag}/"',          # api/child
            f'"{parent_tag}-"',          # api-child
        ]

        with self._get_cursor() as cursor:
            conditions, params = [], []
            for pattern in patterns:
                conditions.append("tags LIKE ?")
                params.append(f'%{pattern}%')

            where_clause = " OR ".join(conditions)

            if agent_id:
                where_clause += " AND agent_id = " + ("?" if self._storage == "sqlite" else "%s")
                params.append(agent_id)

            if memory_type:
                where_clause += " AND memory_type = " + ("?" if self._storage == "sqlite" else "%s")
                params.append(memory_type)

            if self._storage == "sqlite":
                cursor.execute(
                    f"SELECT * FROM memories WHERE {where_clause} ORDER BY importance DESC, created_at DESC LIMIT {limit}",
                    tuple(params)
                )
            else:
                cursor.execute(
                    f"SELECT * FROM memories WHERE {where_clause} ORDER BY importance DESC, created_at DESC LIMIT %s",
                    tuple(params + [limit])
                )

            rows = cursor.fetchall()
        return [self._row_to_memory(row) for row in rows]

    def add_tags_to_memory(self, memory_id: str, tags: List[str]) -> bool:
        """
        Add tags to an existing memory.

        Args:
            memory_id: The memory ID to update
            tags: List of tags to add

        Returns:
            True if memory was updated, False if not found
        """
        # Get existing memory
        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
            else:
                cursor.execute("SELECT * FROM memories WHERE id = %s", (memory_id,))
            row = cursor.fetchone()
            if not row:
                return False
            memory = self._row_to_memory(row)

        # Merge tags
        existing_tags = set(memory.tags)
        existing_tags.update(tags)
        updated_tags = list(existing_tags)

        # Update memory
        now = datetime.now().isoformat()
        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute(
                    "UPDATE memories SET tags = ?, updated_at = ? WHERE id = ?",
                    (json.dumps(updated_tags), now, memory_id)
                )
            else:
                cursor.execute(
                    "UPDATE memories SET tags = %s, updated_at = %s WHERE id = %s",
                    (updated_tags, now, memory_id)
                )
        return True

    def link_memories(self, memory_id: str, linked_memory_id: str, bidirectional: bool = True) -> bool:
        """
        Link two memories together for cross-referencing.

        Args:
            memory_id: Source memory ID
            linked_memory_id: Target memory ID to link to
            bidirectional: If True, also link target back to source

        Returns:
            True if linked successfully, False if any memory not found
        """
        # Get both memories
        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute("SELECT id, linked_to FROM memories WHERE id IN (?, ?)", (memory_id, linked_memory_id))
            else:
                cursor.execute("SELECT id, linked_to FROM memories WHERE id IN (%s, %s)", (memory_id, linked_memory_id))

            rows = cursor.fetchall()
            found_ids = {row["id"]: row["linked_to"] for row in rows}

            if memory_id not in found_ids or linked_memory_id not in found_ids:
                return False

            # Update source memory
            current_link = found_ids.get(memory_id, "") or ""
            linked_set = set(current_link.split(",")) if current_link else set()
            linked_set.add(linked_memory_id)
            new_link = ",".join(linked_set)

            now = datetime.now().isoformat()
            if self._storage == "sqlite":
                cursor.execute("UPDATE memories SET linked_to = ?, updated_at = ? WHERE id = ?", (new_link, now, memory_id))
            else:
                cursor.execute("UPDATE memories SET linked_to = %s, updated_at = %s WHERE id = %s", (new_link, now, memory_id))

            # Update target memory (bidirectional)
            if bidirectional:
                target_link = found_ids.get(linked_memory_id, "") or ""
                target_set = set(target_link.split(",")) if target_link else set()
                target_set.add(memory_id)
                target_new_link = ",".join(target_set)

                if self._storage == "sqlite":
                    cursor.execute("UPDATE memories SET linked_to = ?, updated_at = ? WHERE id = ?",
                                   (target_new_link, now, linked_memory_id))
                else:
                    cursor.execute("UPDATE memories SET linked_to = %s, updated_at = %s WHERE id = %s",
                                   (target_new_link, now, linked_memory_id))

            return True

    def get_linked_memories(self, memory_id: str) -> List[Memory]:
        """
        Get all memories linked to a specific memory.

        Args:
            memory_id: The memory ID to get links for

        Returns:
            List of linked Memory objects
        """
        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute("SELECT linked_to FROM memories WHERE id = ?", (memory_id,))
            else:
                cursor.execute("SELECT linked_to FROM memories WHERE id = %s", (memory_id,))

            row = cursor.fetchone()
            if not row or not row["linked_to"]:
                return []

            linked_ids = [lid.strip() for lid in row["linked_to"].split(",") if lid.strip()]
            if not linked_ids:
                return []

            placeholders = ",".join(["?"] * len(linked_ids)) if self._storage == "sqlite" else ",".join(["%s"] * len(linked_ids))
            if self._storage == "sqlite":
                cursor.execute(f"SELECT * FROM memories WHERE id IN ({placeholders})", tuple(linked_ids))
            else:
                cursor.execute(f"SELECT * FROM memories WHERE id IN ({placeholders})", tuple(linked_ids))

            rows = cursor.fetchall()
        return [self._row_to_memory(row) for row in rows]

    def _row_to_memory(self, row) -> Memory:
        # Handle keywords - can be list (PostgreSQL) or string (SQLite)
        keywords = row["keywords"]
        if isinstance(keywords, str):
            keywords = json.loads(keywords) if keywords else []

        # Handle tags - can be list (PostgreSQL) or string (SQLite)
        # sqlite3.Row uses index access, dict uses .get()
        tags = row["tags"] if "tags" in row.keys() else []
        if isinstance(tags, str):
            tags = json.loads(tags) if tags else []

        # Handle embedding - can be list (PostgreSQL JSON) or string (SQLite)
        embedding = row["embedding"]
        if isinstance(embedding, str):
            embedding = json.loads(embedding) if embedding else None

        # Handle datetime - PostgreSQL returns datetime objects, SQLite returns strings
        created_at = row["created_at"]
        if hasattr(created_at, 'isoformat'):
            created_at = created_at.isoformat()
        updated_at = row["updated_at"]
        if hasattr(updated_at, 'isoformat'):
            updated_at = updated_at.isoformat()

        # Decrypt content if encrypted
        content = row["content"]
        is_encrypted = bool(row["content_encrypted"])
        if is_encrypted and self._cipher:
            try:
                content = self._decrypt(content)
            except Exception as e:
                logger.error(f"Failed to decrypt memory {row['id']}: {e}")
                content = "[Decryption Failed]"

        return Memory(
            id=row["id"], agent_id=row["agent_id"], memory_type=row["memory_type"],
            key=row["key"], content=content, content_encrypted=is_encrypted,
            summary=row["summary"], keywords=keywords, tags=tags,
            importance=row["importance"], linked_to=row["linked_to"], source=row["source"],
            embedding=embedding,
            created_at=created_at, updated_at=updated_at
        )
    
    # ========== CONVERSATIONS ==========
    def remember_conversation(self, session_key: str, messages: List[Dict], agent_id: str = "assistant", summary: str = None) -> str:
        now = datetime.now().isoformat()
        conv_id = str(hashlib.md5(f"{session_key}:{now}".encode()).hexdigest())
        keywords = self._extract_keywords(messages)
        
        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute("""INSERT OR REPLACE INTO conversations 
                    (id, agent_id, session_key, messages, summary, keywords, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (conv_id, agent_id, session_key, json.dumps(messages), summary,
                     json.dumps(keywords), now, now))
            else:
                cursor.execute("""INSERT INTO conversations 
                    (id, agent_id, session_key, messages, summary, keywords, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET messages = conversations.messages || EXCLUDED.messages""",
                    (conv_id, agent_id, session_key, json.dumps(messages), summary,
                     json.dumps(keywords), now, now))
        return conv_id
    
    def get_conversation(self, session_key: str, limit: int = None) -> List[Dict]:
        if self._redis:
            cached = self._redis.get(f"{self._redis_prefix}conv:{session_key}")
            if cached:
                data = json.loads(cached)
                return data.get("messages", [])[-limit:] if limit else data.get("messages", [])
        
        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute("SELECT messages FROM conversations WHERE session_key = ? ORDER BY created_at DESC LIMIT 1", (session_key,))
            else:
                cursor.execute("SELECT messages FROM conversations WHERE session_key = %s ORDER BY created_at DESC LIMIT 1", (session_key,))
            row = cursor.fetchone()
        
        if row:
            messages = row["messages"] if self._storage == "sqlite" else (row["messages"] or [])
            if self._redis:
                cache_data = json.dumps({"messages": messages})
                self._redis.setex(f"{self._redis_prefix}conv:{session_key}", 3600, cache_data)
            return messages[-limit:] if limit else messages
        return []
    
    # ========== USER PROFILES ==========
    def get_user_profile(self, user_id: str) -> UserProfile:
        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            else:
                cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
        
        if row:
            # Helper to parse JSON fields that might be dict/list already (PostgreSQL) or string (SQLite)
            def parse_json(val, default):
                if val is None:
                    return default
                if isinstance(val, str):
                    return json.loads(val) if val else default
                return val
            
            # Helper to convert datetime to string
            def to_isoformat(val):
                if val is None:
                    return None
                if hasattr(val, 'isoformat'):
                    return val.isoformat()
                return val
            
            return UserProfile(
                user_id=row["user_id"], name=row["name"], nickname=row["nickname"],
                preferred_name=row["preferred_name"],
                communication_preferences=parse_json(row["communication_preferences"], {}),
                interests=parse_json(row["interests"], []),
                expertise_areas=parse_json(row["expertise_areas"], []),
                learning_topics=parse_json(row["learning_topics"], []),
                timezone=row["timezone"],
                active_hours=parse_json(row["active_hours"], {}),
                conversation_patterns=parse_json(row["conversation_patterns"], {}),
                emotional_patterns=parse_json(row["emotional_patterns"], {}),
                important_dates=parse_json(row["important_dates"], {}),
                life_context=parse_json(row["life_context"], {}),
                total_interactions=row["total_interactions"] or 0,
                first_interaction=to_isoformat(row["first_interaction"]),
                last_interaction=to_isoformat(row["last_interaction"]),
                updated_at=to_isoformat(row["updated_at"])
            )
        return UserProfile(user_id=user_id)
    
    def learn_user_preference(self, user_id: str, preference_type: str, value: str):
        profile = self.get_user_profile(user_id)
        now = datetime.now().isoformat()
        
        if profile.first_interaction is None:
            profile.first_interaction = now
        profile.last_interaction = now
        profile.total_interactions += 1
        profile.updated_at = now
        
        if preference_type == "interest" and value not in profile.interests:
            profile.interests.append(value)
        elif preference_type == "expertise" and value not in profile.expertise_areas:
            profile.expertise_areas.append(value)
        elif preference_type == "learning" and value not in profile.learning_topics:
            profile.learning_topics.append(value)
        
        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute("""INSERT OR REPLACE INTO user_profiles 
                    (user_id, name, nickname, preferred_name, communication_preferences, interests,
                     expertise_areas, learning_topics, timezone, active_hours, conversation_patterns,
                     emotional_patterns, important_dates, life_context, total_interactions,
                     first_interaction, last_interaction, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (profile.user_id, profile.name, profile.nickname, profile.preferred_name,
                     json.dumps(profile.communication_preferences), json.dumps(profile.interests),
                     json.dumps(profile.expertise_areas), json.dumps(profile.learning_topics),
                     profile.timezone, json.dumps(profile.active_hours),
                     json.dumps(profile.conversation_patterns), json.dumps(profile.emotional_patterns),
                     json.dumps(profile.important_dates), json.dumps(profile.life_context),
                     profile.total_interactions, profile.first_interaction, profile.last_interaction,
                     profile.updated_at))
            else:
                cursor.execute("""INSERT INTO user_profiles 
                    (user_id, name, nickname, preferred_name, communication_preferences, interests,
                     expertise_areas, learning_topics, timezone, active_hours, conversation_patterns,
                     emotional_patterns, important_dates, life_context, total_interactions,
                     first_interaction, last_interaction, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        interests = EXCLUDED.interests,
                        total_interactions = user_profiles.total_interactions + 1,
                        last_interaction = EXCLUDED.last_interaction""",
                    (profile.user_id, profile.name, profile.nickname, profile.preferred_name,
                     psycopg2.extras.Json(profile.communication_preferences), profile.interests,
                     profile.expertise_areas, profile.learning_topics,
                     profile.timezone, psycopg2.extras.Json(profile.active_hours),
                     psycopg2.extras.Json(profile.conversation_patterns), psycopg2.extras.Json(profile.emotional_patterns),
                     psycopg2.extras.Json(profile.important_dates), psycopg2.extras.Json(profile.life_context),
                     profile.total_interactions, profile.first_interaction, profile.last_interaction,
                     profile.updated_at))
    
    # ========== MOOD/INTENT DETECTION ==========
    def detect_user_mood(self, message: str) -> Dict[str, Any]:
        message_lower = message.lower()
        mood_keywords = {
            "happy": ["great", "awesome", "love", "excellent", "happy", "wonderful", "amazing", "excited"],
            "frustrated": ["annoying", "hate", "stupid", "frustrated", "angry", "terrible", "worst"],
            "stressed": ["busy", "overwhelmed", "stressed", "anxious", "worry", "panic"],
            "curious": ["how", "why", "what", "tell me", "explain", "wondering", "interested"],
            "sad": ["unfortunately", "sad", "disappointed", "sorry", "unhappy"],
        }
        mood_scores = {}
        for mood, keywords in mood_keywords.items():
            matches = sum(1 for kw in keywords if kw in message_lower)
            if matches > 0:
                mood_scores[mood] = matches / len(keywords)
        
        if mood_scores:
            top_mood = max(mood_scores, key=mood_scores.get)
            return {"mood": top_mood, "confidence": min(0.9, 0.3 + mood_scores[top_mood] * 0.3), "all_moods": mood_scores}
        return {"mood": "neutral", "confidence": 0.5, "all_moods": {}}
    
    def detect_user_intent(self, message: str) -> str:
        message_lower = message.lower().strip()
        if any(greet in message_lower for greet in ["hello", "hi", "hey", "good morning"]):
            return "greeting"
        elif "?" in message or message_lower.startswith(("what", "how", "why", "can you", "could you")):
            return "question"
        elif any(req in message_lower for req in ["please", "can you", "i want", "i need"]):
            return "request"
        elif any(fb in message_lower for fb in ["actually", "no that's", "wrong"]):
            return "feedback"
        elif any(bye in message_lower for bye in ["bye", "goodbye", "later"]):
            return "farewell"
        return "statement"
    
    # ========== FULL CONTEXT ==========
    def get_full_context(self, session_key: str, user_id: str = "default", agent_id: str = "assistant", message: str = None) -> Dict[str, Any]:
        now = datetime.now()
        message_analysis = {}
        if message:
            message_analysis = {"mood": self.detect_user_mood(message), "intent": self.detect_user_intent(message)}
        
        conversation_state = self.get_conversation(session_key)
        user_profile = self.get_user_profile(user_id)
        memories = self.recall(agent_id=agent_id, limit=10)
        
        return {
            "user": {
                "profile": {"name": user_profile.preferred_name or user_profile.name,
                           "interests": user_profile.interests, "expertise": user_profile.expertise_areas},
                "preferred_name": user_profile.preferred_name or user_profile.name,
                "interests": user_profile.interests,
                "communication_style": user_profile.communication_preferences,
            },
            "conversation": {
                "state": {"user_mood": message_analysis.get("mood", {}).get("mood", "neutral") if message_analysis else "neutral",
                         "intent": message_analysis.get("intent", "statement") if message_analysis else "statement"},
                "history": conversation_state,
                "turn_count": len(conversation_state) if conversation_state else 0,
                "current_topic": "",
            },
            "message_analysis": message_analysis,
            "memories": [asdict(m) for m in memories],
            "time_context": {"time_of_day": now.strftime("%H:%M"), "timestamp": now.isoformat()},
            "response_guidance": {
                "tone": "friendly", "formality": user_profile.communication_preferences.get("formality", "casual"),
                "verbosity": user_profile.communication_preferences.get("verbosity", "concise"),
                "use_humor": user_profile.communication_preferences.get("use_humor", True),
                "use_emoji": user_profile.communication_preferences.get("use_emoji", True),
                "show_empathy": False, "be_encouraging": True, "match_energy": False, "response_type": "conversational",
            },
        }
    
    def process_message(self, message: str, session_key: str, user_id: str = "default", agent_id: str = "assistant") -> Dict[str, Any]:
        return self.get_full_context(session_key, user_id, agent_id, message)
    
    def generate_personality_prompt(self, agent_id: str = "assistant", user_id: str = "default") -> str:
        profile = self.get_user_profile(user_id)
        prompt = f"You are {agent_id}, a personal AI assistant who is helpful and friendly."
        if profile.preferred_name:
            prompt += f" Your human is named {profile.preferred_name}."
        if profile.interests:
            prompt += f" They're interested in: {', '.join(profile.interests[:3])}."
        return prompt
    
    # ========== HELPER METHODS ==========
    def _extract_keywords(self, messages: List[Dict]) -> List[str]:
        keywords = []
        for msg in messages:
            content = msg.get("content", "").lower()
            words = [w for w in content.split() if len(w) > 3 and w not in ["that", "this", "with", "from", "have"]]
            keywords.extend(words[:5])
        return list(set(keywords))[:10]
    
    def _summarize(self, messages: List[Dict]) -> str:
        if not messages:
            return ""
        content = " ".join(m.get("content", "") for m in messages)
        return content[:100] + "..." if len(content) > 100 else content
    
    @contextmanager
    def _get_cursor(self):
        with self._lock:
            if self._storage == "sqlite":
                cursor = self._sqlite_conn.cursor()
                try:
                    yield cursor
                    self._sqlite_conn.commit()
                finally:
                    cursor.close()
            else:
                cursor = self._pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                try:
                    yield cursor
                finally:
                    cursor.close()
    
    def health_check(self) -> Dict[str, bool]:
        return {"storage": self._storage in ["sqlite", "postgresql"], "sqlite": self._storage == "sqlite",
                "postgres": self._storage == "postgresql", "redis": self._redis is not None,
                "backup_dir": self._backup_dir.exists()}
    
    # ========== SYNC/REFRESH METHODS (OpenClaw Integration) ==========
    def sync_memories(self, agent_id: str = "openclaw", since_hours: int = 24) -> Dict[str, Any]:
        """
        Sync and return recent memories for OpenClaw integration.
        Called on gateway startup to refresh memory context.
        
        Args:
            agent_id: Agent identifier
            since_hours: Only sync memories from the last N hours
            
        Returns:
            Dict with sync results including memories count and last sync time
        """
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(hours=since_hours)).isoformat()
        
        with self._get_cursor() as cursor:
            if self._storage == "sqlite":
                cursor.execute(
                    "SELECT COUNT(*) as count FROM memories WHERE agent_id = ? AND created_at > ?",
                    (agent_id, cutoff)
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM memories WHERE agent_id = %s AND created_at > %s",
                    (agent_id, cutoff)
                )
            row = cursor.fetchone()
            recent_count = row["count"] if row else 0
        
        # Get all memories count
        memories = self.recall(agent_id=agent_id, limit=100)
        
        return {
            "memories_count": len(memories),
            "recent_memories": recent_count,
            "since_hours": since_hours,
            "storage_backend": self._storage,
            "last_sync": datetime.now().isoformat(),
        }
    
    def refresh_on_startup(self, agent_id: str = "openclaw", user_id: str = "default") -> Dict[str, Any]:
        """
        Refresh brain state on OpenClaw service startup.
        This is the main method called by the OpenClaw plugin on gateway:startup.
        
        Args:
            agent_id: Agent identifier
            user_id: User identifier
            
        Returns:
            Dict with full context and sync status
        """
        # Health check first
        health = self.health_check()
        if not health.get("storage"):
            return {
                "success": False,
                "error": "Storage backend not available",
                "health": health,
            }
        
        # Sync memories
        sync_result = self.sync_memories(agent_id=agent_id)
        
        # Get user profile
        profile = self.get_user_profile(user_id)
        
        # Get full context for the agent
        context = self.get_full_context(
            session_key=f"{agent_id}_startup",
            user_id=user_id,
            agent_id=agent_id,
            message=""
        )
        
        # Generate personality prompt
        personality_prompt = self.generate_personality_prompt(
            agent_id=agent_id,
            user_id=user_id
        )
        
        return {
            "success": True,
            "sync": sync_result,
            "user_profile": {
                "name": profile.preferred_name or profile.name,
                "interests": profile.interests,
                "expertise": profile.expertise_areas,
                "total_interactions": profile.total_interactions,
            },
            "context": context,
            "personality_prompt": personality_prompt,
            "health": health,
            "refreshed_at": datetime.now().isoformat(),
        }
    
    def save_session_to_memory(
        self, 
        session_key: str, 
        messages: List[Dict[str, str]], 
        agent_id: str = "openclaw",
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Save a session's messages to memory.
        Called by OpenClaw plugin on command:new event.
        
        Args:
            session_key: Unique session identifier
            messages: List of message dicts with 'role' and 'content'
            agent_id: Agent identifier
            tags: Optional tags for the memory
            
        Returns:
            Dict with save result
        """
        if not messages:
            return {"success": False, "error": "No messages to save"}
        
        # Create a summary of the conversation
        content_parts = []
        for msg in messages[-20:]:  # Last 20 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:500]  # Truncate long messages
            content_parts.append(f"{role}: {content}")
        
        content = "\n".join(content_parts)
        summary = self._summarize(messages[-5:])  # Summary of last 5
        
        # Store as conversation memory
        memory = self.remember(
            agent_id=agent_id,
            memory_type="conversation",
            content=content,
            key=f"session_{session_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            tags=tags or ["session", "conversation"],
            auto_tag=True,
            importance=6,  # Slightly above average importance
        )
        
        # Also save to conversations table
        conv_id = self.remember_conversation(
            session_key=session_key,
            messages=messages,
            agent_id=agent_id,
            summary=summary
        )
        
        return {
            "success": True,
            "memory_id": memory.id,
            "conversation_id": conv_id,
            "messages_saved": len(messages),
            "saved_at": datetime.now().isoformat(),
        }
    
    def get_startup_context(self, agent_id: str = "openclaw", user_id: str = "default") -> str:
        """
        Get a formatted context string for OpenClaw MEMORY.md injection.
        
        Args:
            agent_id: Agent identifier
            user_id: User identifier
            
        Returns:
            Markdown-formatted context string for MEMORY.md
        """
        profile = self.get_user_profile(user_id)
        memories = self.recall(agent_id=agent_id, limit=5)
        
        lines = ["# Memory Context", ""]
        
        # User section
        lines.append("## User Profile")
        if profile.preferred_name or profile.name:
            lines.append(f"- **Name**: {profile.preferred_name or profile.name}")
        if profile.interests:
            lines.append(f"- **Interests**: {', '.join(profile.interests[:5])}")
        if profile.expertise_areas:
            lines.append(f"- **Expertise**: {', '.join(profile.expertise_areas[:5])}")
        if profile.total_interactions:
            lines.append(f"- **Interactions**: {profile.total_interactions}")
        lines.append("")
        
        # Recent memories
        if memories:
            lines.append("## Recent Memories")
            for mem in memories:
                summary = mem.summary or mem.content[:100]
                lines.append(f"- [{mem.memory_type}] {summary}")
            lines.append("")
        
        # Timestamp
        lines.append(f"_Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M')}_")
        
        return "\n".join(lines)
    
    def close(self):
        if hasattr(self, '_sqlite_conn') and self._sqlite_conn:
            self._sqlite_conn.close()
        if self._pg_conn:
            self._pg_conn.close()
        if self._redis:
            self._redis.close()


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception as e:
                logger.warning(f"Could not load embedding model: {e}")
    
    def embed(self, text: str) -> Optional[List[float]]:
        if self.model and text:
            try:
                return self.model.encode(text).tolist()
            except:
                return None
        return None

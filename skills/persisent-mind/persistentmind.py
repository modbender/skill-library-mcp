#!/usr/bin/env python3
"""
PersistentMind v1.0.0
Persistent, searchable, context-aware memory for AI agents and workflows.

Free and open-source (MIT Licensed)
No external dependencies. Works locally — no API keys required.

Features:
  - Store and retrieve memories with semantic tags
  - Context-scoped memory (project, session, global)
  - Automatic relevance scoring and decay
  - Memory consolidation — merge duplicates
  - Full-text search with ranking
  - Export/import for team sharing
"""

import json
import os
import re
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum


class MemoryScope(str, Enum):
    GLOBAL = "global"        # Persists across all projects and sessions
    PROJECT = "project"      # Scoped to a specific project
    SESSION = "session"      # Temporary, current session only


class MemoryType(str, Enum):
    FACT = "fact"                    # Factual information
    PREFERENCE = "preference"        # User preferences and settings
    PROCEDURE = "procedure"          # How to do something (steps)
    CONTEXT = "context"              # Background context
    CORRECTION = "correction"        # Something that was wrong + the fix
    RELATIONSHIP = "relationship"    # How things relate to each other
    REMINDER = "reminder"            # Something to remember for later


@dataclass
class Memory:
    """A single memory entry"""
    id: str
    timestamp: str
    content: str
    memory_type: str           # MemoryType value
    scope: str                 # MemoryScope value
    tags: List[str]
    project: Optional[str] = None
    session_id: Optional[str] = None
    source: str = "user"       # "user", "agent", "auto"
    importance: float = 5.0    # 1-10 scale
    access_count: int = 0
    last_accessed: Optional[str] = None
    related_ids: List[str] = field(default_factory=list)
    expires_at: Optional[str] = None   # ISO datetime, None = never expires
    archived: bool = False


@dataclass
class MemorySearchResult:
    """A search result with relevance score"""
    memory: Memory
    relevance_score: float
    matched_fields: List[str]


class PersistentMind:
    """
    Persistent, searchable memory for AI agents and Claude Code workflows.

    Designed for:
    - Remembering user preferences across sessions
    - Storing project context that agents need repeatedly
    - Capturing corrections so mistakes aren't repeated
    - Building a knowledge base that improves over time

    All data is stored locally in JSON files. Zero external dependencies.
    """

    def __init__(
        self,
        storage_path: str = ".persistentmind",
        project: Optional[str] = None,
        session_id: Optional[str] = None,
        auto_cleanup_days: int = 90,
    ):
        """
        Initialize the memory manager.

        Args:
            storage_path: Directory for local storage
            project: Current project name (for project-scoped memories)
            session_id: Current session ID (auto-generated if not provided)
            auto_cleanup_days: Auto-archive memories not accessed in this many days
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.project = project
        self.session_id = session_id or self._generate_id("session")
        self.auto_cleanup_days = auto_cleanup_days

        self.memories_file = self.storage_path / "memories.json"
        self.memories: List[Memory] = self._load_memories()

        # Auto-cleanup expired memories on init
        self._cleanup_expired()

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def remember(
        self,
        content: str,
        memory_type: str = MemoryType.FACT,
        scope: str = MemoryScope.PROJECT,
        tags: Optional[List[str]] = None,
        importance: float = 5.0,
        project: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        source: str = "user",
    ) -> Memory:
        """
        Store a new memory.

        Args:
            content: The information to remember
            memory_type: Type of memory (fact, preference, procedure, etc.)
            scope: global / project / session
            tags: List of searchable tags
            importance: 1-10 importance score (10 = critical)
            project: Project name (defaults to current project)
            expires_in_days: Auto-expire after this many days (None = permanent)
            source: "user", "agent", or "auto"

        Returns:
            Memory object
        """
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()

        memory = Memory(
            id=self._generate_id("mem"),
            timestamp=datetime.now().isoformat(),
            content=content,
            memory_type=memory_type,
            scope=scope,
            tags=tags or self._auto_extract_tags(content),
            project=project or self.project,
            session_id=self.session_id if scope == MemoryScope.SESSION else None,
            source=source,
            importance=max(1.0, min(10.0, importance)),
            expires_at=expires_at,
        )

        # Check for near-duplicate and warn
        similar = self._find_similar(content)
        if similar:
            print(f"ℹ️  Similar memory exists (ID: {similar.id}). Storing anyway. Consider using update_memory() instead.")

        self.memories.append(memory)
        self._save_memories()
        print(f"✅ Memory stored: {memory.id} [{memory_type}]")
        return memory

    def recall(
        self,
        query: str,
        scope_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        project_filter: Optional[str] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> List[MemorySearchResult]:
        """
        Search memories by content, tags, or type.

        Args:
            query: Search term(s)
            scope_filter: Filter by scope (global/project/session)
            type_filter: Filter by memory type
            project_filter: Filter by project name
            limit: Max results to return
            min_importance: Only return memories >= this importance

        Returns:
            List of MemorySearchResult sorted by relevance
        """
        candidates = [m for m in self.memories if not m.archived]

        if scope_filter:
            candidates = [m for m in candidates if m.scope == scope_filter]
        if type_filter:
            candidates = [m for m in candidates if m.memory_type == type_filter]
        if project_filter:
            candidates = [m for m in candidates if m.project == project_filter]
        if min_importance > 0:
            candidates = [m for m in candidates if m.importance >= min_importance]

        # Score each candidate
        scored = []
        query_terms = query.lower().split()
        for memory in candidates:
            score, matched = self._score_memory(memory, query_terms)
            if score > 0:
                scored.append(MemorySearchResult(memory=memory, relevance_score=score, matched_fields=matched))

        # Sort by relevance then importance
        scored.sort(key=lambda x: (x.relevance_score, x.memory.importance), reverse=True)
        results = scored[:limit]

        # Update access count
        for result in results:
            result.memory.access_count += 1
            result.memory.last_accessed = datetime.now().isoformat()
        self._save_memories()

        return results

    def recall_by_type(self, memory_type: str, limit: int = 20) -> List[Memory]:
        """Get all memories of a specific type."""
        results = [m for m in self.memories if m.memory_type == memory_type and not m.archived]
        return sorted(results, key=lambda m: m.importance, reverse=True)[:limit]

    def recall_by_tag(self, tag: str, limit: int = 20) -> List[Memory]:
        """Get all memories with a specific tag."""
        tag_lower = tag.lower()
        results = [m for m in self.memories if any(t.lower() == tag_lower for t in m.tags) and not m.archived]
        return sorted(results, key=lambda m: m.importance, reverse=True)[:limit]

    def get_context(self, project: Optional[str] = None, max_tokens_estimate: int = 2000) -> str:
        """
        Get a formatted context block of the most relevant memories.
        Designed to be injected into AI prompts.

        Args:
            project: Project to get context for (defaults to current)
            max_tokens_estimate: Rough token limit for context block

        Returns:
            Formatted string ready for prompt injection
        """
        proj = project or self.project
        memories = [m for m in self.memories if not m.archived and (
            m.scope == MemoryScope.GLOBAL or
            (m.scope == MemoryScope.PROJECT and m.project == proj) or
            (m.scope == MemoryScope.SESSION and m.session_id == self.session_id)
        )]

        # Sort: corrections first (most important), then by importance desc
        memories.sort(key=lambda m: (
            0 if m.memory_type == MemoryType.CORRECTION else 1,
            -m.importance
        ))

        lines = ["# Relevant Memory Context\n"]
        char_budget = max_tokens_estimate * 4  # rough 4 chars/token estimate
        used = 0

        for m in memories:
            type_icon = {
                "fact": "📌", "preference": "⚙️", "procedure": "📋",
                "context": "🗂️", "correction": "⚠️", "relationship": "🔗", "reminder": "🔔"
            }.get(m.memory_type, "•")
            line = f"{type_icon} [{m.memory_type.upper()}] {m.content}"
            if m.tags:
                line += f" (tags: {', '.join(m.tags)})"
            line += "\n"

            used += len(line)
            if used > char_budget:
                lines.append(f"... ({len(memories) - len(lines) + 1} more memories truncated)")
                break
            lines.append(line)

        return "\n".join(lines)

    def update_memory(self, memory_id: str, content: str = None, importance: float = None, tags: List[str] = None) -> Optional[Memory]:
        """Update an existing memory."""
        for memory in self.memories:
            if memory.id == memory_id:
                if content:
                    memory.content = content
                if importance is not None:
                    memory.importance = max(1.0, min(10.0, importance))
                if tags is not None:
                    memory.tags = tags
                self._save_memories()
                print(f"✅ Memory updated: {memory_id}")
                return memory
        print(f"⚠️  Memory not found: {memory_id}")
        return None

    def forget(self, memory_id: str, permanent: bool = False) -> bool:
        """
        Archive (soft-delete) or permanently delete a memory.

        Args:
            memory_id: ID of memory to forget
            permanent: If True, permanently delete. Default is archive.
        """
        for i, memory in enumerate(self.memories):
            if memory.id == memory_id:
                if permanent:
                    self.memories.pop(i)
                    print(f"🗑️  Memory permanently deleted: {memory_id}")
                else:
                    memory.archived = True
                    print(f"📦 Memory archived: {memory_id}")
                self._save_memories()
                return True
        return False

    def consolidate(self, dry_run: bool = True) -> List[Dict]:
        """
        Find near-duplicate memories and suggest consolidation.

        Args:
            dry_run: If True, only report duplicates. If False, merge them.

        Returns:
            List of duplicate groups found
        """
        active = [m for m in self.memories if not m.archived]
        groups = []
        checked = set()

        for i, mem in enumerate(active):
            if mem.id in checked:
                continue
            group = [mem]
            for j, other in enumerate(active[i + 1:], i + 1):
                if other.id in checked:
                    continue
                if self._similarity_score(mem.content, other.content) > 0.6:
                    group.append(other)
                    checked.add(other.id)

            if len(group) > 1:
                groups.append({
                    "count": len(group),
                    "memories": [{"id": m.id, "content": m.content[:80]} for m in group],
                    "suggested_merge": group[0].content,
                })
                if not dry_run:
                    # Keep highest importance, archive the rest
                    keeper = max(group, key=lambda m: m.importance)
                    for m in group:
                        if m.id != keeper.id:
                            m.archived = True
                    print(f"🔀 Merged {len(group)} memories into {keeper.id}")

        if not dry_run:
            self._save_memories()

        return groups

    # ------------------------------------------------------------------
    # Stats & export
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict:
        """Get memory statistics."""
        active = [m for m in self.memories if not m.archived]
        by_type: Dict[str, int] = {}
        by_scope: Dict[str, int] = {}
        for m in active:
            by_type[m.memory_type] = by_type.get(m.memory_type, 0) + 1
            by_scope[m.scope] = by_scope.get(m.scope, 0) + 1

        return {
            "total_memories": len(active),
            "archived": len([m for m in self.memories if m.archived]),
            "by_type": by_type,
            "by_scope": by_scope,
            "avg_importance": round(sum(m.importance for m in active) / len(active), 2) if active else 0,
            "most_accessed": sorted(active, key=lambda m: m.access_count, reverse=True)[:3],
        }

    def format_summary(self) -> str:
        """Format a human-readable memory summary."""
        stats = self.get_stats()
        recent = sorted([m for m in self.memories if not m.archived],
                        key=lambda m: m.timestamp, reverse=True)[:5]

        output = f"""
╔═══════════════════════════════════════════════════════════════╗
║               MEMORY MANAGER — SUMMARY                        ║
╚═══════════════════════════════════════════════════════════════╝

🧠 Total Active Memories: {stats['total_memories']}  |  Archived: {stats['archived']}
   Avg Importance: {stats['avg_importance']}/10

📊 BY TYPE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for t, count in stats["by_type"].items():
            output += f"  • {t:<20} {count}\n"

        output += f"""
📋 RECENT MEMORIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for m in recent:
            output += f"  [{m.memory_type}] {m.content[:70]}{'...' if len(m.content) > 70 else ''}\n"

        return output

    def export_memories(self, output_file: str = "memories_export.json", include_archived: bool = False):
        """Export memories to a JSON file for sharing or backup."""
        to_export = self.memories if include_archived else [m for m in self.memories if not m.archived]
        data = {
            "exported_at": datetime.now().isoformat(),
            "total": len(to_export),
            "memories": [asdict(m) for m in to_export],
        }
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"📁 Exported {len(to_export)} memories to {output_file}")

    def import_memories(self, input_file: str, overwrite_duplicates: bool = False):
        """Import memories from a JSON export file."""
        with open(input_file) as f:
            data = json.load(f)

        existing_ids = {m.id for m in self.memories}
        imported = 0
        skipped = 0
        for item in data.get("memories", []):
            if item["id"] in existing_ids:
                if overwrite_duplicates:
                    self.memories = [m for m in self.memories if m.id != item["id"]]
                else:
                    skipped += 1
                    continue
            self.memories.append(Memory(**item))
            imported += 1

        self._save_memories()
        print(f"📥 Imported {imported} memories ({skipped} skipped as duplicates)")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _score_memory(self, memory: Memory, query_terms: List[str]) -> Tuple[float, List[str]]:
        """Score a memory against query terms. Returns (score, matched_fields)."""
        score = 0.0
        matched = []

        content_lower = memory.content.lower()
        tags_lower = [t.lower() for t in memory.tags]
        type_lower = memory.memory_type.lower()

        for term in query_terms:
            if term in content_lower:
                score += 2.0
                if "content" not in matched:
                    matched.append("content")
            if any(term in tag for tag in tags_lower):
                score += 1.5
                if "tags" not in matched:
                    matched.append("tags")
            if term in type_lower:
                score += 0.5
                if "type" not in matched:
                    matched.append("type")

        if score > 0:
            # Boost by importance
            score *= (memory.importance / 5.0)
            # Boost corrections (critical to surface)
            if memory.memory_type == MemoryType.CORRECTION:
                score *= 1.3
            # Decay by recency (older = slight penalty)
            days_old = (datetime.now() - datetime.fromisoformat(memory.timestamp)).days
            if days_old > 30:
                score *= max(0.5, 1.0 - (days_old / 365) * 0.3)

        return round(score, 4), matched

    def _find_similar(self, content: str) -> Optional[Memory]:
        """Find an existing memory with similar content."""
        for m in self.memories:
            if not m.archived and self._similarity_score(content, m.content) > 0.8:
                return m
        return None

    def _similarity_score(self, a: str, b: str) -> float:
        """Simple word-overlap similarity score."""
        words_a = set(re.sub(r'[^a-z0-9\s]', '', a.lower()).split())
        words_b = set(re.sub(r'[^a-z0-9\s]', '', b.lower()).split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)

    def _auto_extract_tags(self, content: str) -> List[str]:
        """Auto-extract likely tags from content."""
        # Extract capitalized words, tech terms, and quoted phrases
        tags = []
        # Quoted phrases
        tags += re.findall(r'"([^"]+)"', content)
        # Capitalized proper nouns (skip start of sentence)
        words = content.split()
        for i, word in enumerate(words[1:], 1):
            clean = re.sub(r'[^a-zA-Z0-9]', '', word)
            if clean and clean[0].isupper() and len(clean) > 2:
                tags.append(clean.lower())
        # Common tech patterns
        tech = re.findall(r'\b(?:api|sdk|python|js|ts|react|claude|gpt|gemini|openai|anthropic|github|docker|aws|gcp)\b', content.lower())
        tags += tech
        return list(dict.fromkeys(tags))[:8]  # dedupe, max 8 tags

    def _cleanup_expired(self):
        """Archive expired and stale memories."""
        now = datetime.now()
        changed = False
        for memory in self.memories:
            if memory.archived:
                continue
            if memory.expires_at and datetime.fromisoformat(memory.expires_at) < now:
                memory.archived = True
                changed = True
            elif memory.last_accessed and self.auto_cleanup_days:
                last = datetime.fromisoformat(memory.last_accessed)
                if (now - last).days > self.auto_cleanup_days and memory.scope == MemoryScope.SESSION:
                    memory.archived = True
                    changed = True
        if changed:
            self._save_memories()

    def _load_memories(self) -> List[Memory]:
        if not self.memories_file.exists():
            return []
        try:
            with open(self.memories_file) as f:
                return [Memory(**item) for item in json.load(f)]
        except Exception as e:
            print(f"Warning: Could not load memories: {e}")
            return []

    def _save_memories(self):
        with open(self.memories_file, "w") as f:
            json.dump([asdict(m) for m in self.memories], f, indent=2)

    def _generate_id(self, prefix: str) -> str:
        import uuid
        return f"{prefix}_{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Example / demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mm = PersistentMind(project="my-app")

    # Store different types of memories
    mm.remember(
        "User prefers concise responses under 200 words",
        memory_type=MemoryType.PREFERENCE,
        scope=MemoryScope.GLOBAL,
        importance=8.0,
        tags=["response-style", "user-preference"]
    )

    mm.remember(
        "The database uses PostgreSQL 16. Connection string is in .env as DATABASE_URL",
        memory_type=MemoryType.FACT,
        scope=MemoryScope.PROJECT,
        importance=9.0,
        tags=["database", "postgresql", "config"]
    )

    mm.remember(
        "Never use wildcard imports — the linter will fail the CI check",
        memory_type=MemoryType.CORRECTION,
        scope=MemoryScope.PROJECT,
        importance=10.0,
        tags=["linting", "ci", "imports"]
    )

    mm.remember(
        "To run migrations: poetry run alembic upgrade head",
        memory_type=MemoryType.PROCEDURE,
        scope=MemoryScope.PROJECT,
        importance=7.0,
        tags=["alembic", "migrations", "database"]
    )

    # Search
    print("\n🔍 Search: 'database'")
    results = mm.recall("database")
    for r in results:
        print(f"  [{r.relevance_score:.2f}] {r.memory.content[:60]}...")

    # Get context for prompt injection
    print("\n📋 CONTEXT BLOCK (for prompt injection):")
    print(mm.get_context())

    # Summary
    print(mm.format_summary())

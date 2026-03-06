"""
OASIS Forum - Thread-safe discussion board with persistence
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field

# Persistence directory (relative to project root)
_this_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_this_dir)
DISCUSSIONS_DIR = os.path.join(_project_root, "data", "oasis_discussions")


@dataclass
class TimelineEvent:
    """A timestamped event in the discussion lifecycle."""
    elapsed: float          # seconds since discussion started
    event: str              # e.g. "start", "agent_call", "agent_done", "round", "conclude"
    agent: str = ""         # expert name (if applicable)
    detail: str = ""        # extra info

    def to_dict(self) -> dict:
        return {"elapsed": round(self.elapsed, 2), "event": self.event,
                "agent": self.agent, "detail": self.detail}

    @classmethod
    def from_dict(cls, d: dict) -> "TimelineEvent":
        return cls(**d)


@dataclass
class Post:
    """A single post / reply in a discussion thread."""
    id: int
    author: str
    content: str
    reply_to: int | None = None
    upvotes: int = 0
    downvotes: int = 0
    timestamp: float = field(default_factory=time.time)
    elapsed: float = 0.0    # seconds since discussion started
    voters: dict[str, str] = field(default_factory=dict)  # voter_name -> "up"/"down"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "author": self.author, "content": self.content,
            "reply_to": self.reply_to, "upvotes": self.upvotes,
            "downvotes": self.downvotes, "timestamp": self.timestamp,
            "elapsed": round(self.elapsed, 2),
            "voters": self.voters,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Post":
        d2 = dict(d)
        d2.setdefault("elapsed", 0.0)
        return cls(**d2)


class DiscussionForum:
    """
    Thread-safe shared discussion board for a single topic.
    All experts read/write through this instance concurrently.
    """

    def __init__(self, topic_id: str, question: str, user_id: str = "anonymous", max_rounds: int = 5):
        self.topic_id = topic_id
        self.question = question
        self.user_id = user_id
        self.max_rounds = max_rounds
        self.current_round = 0
        self.posts: list[Post] = []
        self.timeline: list[TimelineEvent] = []
        self.conclusion: str | None = None
        self.status = "pending"
        self.discussion: bool = True    # True=讨论模式, False=执行模式
        self.created_at = time.time()
        self._start_time: float = 0.0   # set when discussion actually starts
        self._lock = asyncio.Lock()
        self._counter = 0

    def start_clock(self):
        """Mark the discussion start time (T=0 for all elapsed calculations)."""
        self._start_time = time.time()
        self.log_event("start", detail="Discussion started")

    def elapsed(self) -> float:
        """Seconds since start_clock(), or 0 if not started."""
        if self._start_time <= 0:
            return 0.0
        return time.time() - self._start_time

    def log_event(self, event: str, agent: str = "", detail: str = ""):
        """Append a timestamped event to the timeline."""
        ev = TimelineEvent(elapsed=self.elapsed(), event=event, agent=agent, detail=detail)
        self.timeline.append(ev)
        print(f"  [OASIS] ⏱ T+{ev.elapsed:.1f}s  {event}"
              + (f"  [{agent}]" if agent else "")
              + (f"  {detail}" if detail else ""))

    # ── Serialisation ──

    def to_dict(self) -> dict:
        return {
            "topic_id": self.topic_id,
            "question": self.question,
            "user_id": self.user_id,
            "max_rounds": self.max_rounds,
            "current_round": self.current_round,
            "posts": [p.to_dict() for p in self.posts],
            "timeline": [e.to_dict() for e in self.timeline],
            "conclusion": self.conclusion,
            "status": self.status,
            "discussion": self.discussion,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DiscussionForum":
        forum = cls(
            topic_id=d["topic_id"],
            question=d["question"],
            user_id=d.get("user_id", "anonymous"),
            max_rounds=d.get("max_rounds", 5),
        )
        forum.current_round = d.get("current_round", 0)
        forum.conclusion = d.get("conclusion")
        forum.status = d.get("status", "concluded")
        forum.discussion = d.get("discussion", True)
        forum.created_at = d.get("created_at", 0)
        forum.posts = [Post.from_dict(p) for p in d.get("posts", [])]
        forum.timeline = [TimelineEvent.from_dict(e) for e in d.get("timeline", [])]
        forum._counter = max((p.id for p in forum.posts), default=0)
        return forum

    # ── Persistence ──

    def _storage_path(self) -> str:
        user_dir = os.path.join(DISCUSSIONS_DIR, self.user_id)
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, f"{self.topic_id}.json")

    def save(self):
        """Persist current state to disk."""
        path = self._storage_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_all(cls) -> dict[str, "DiscussionForum"]:
        """Load all persisted discussions from disk. Returns {topic_id: forum}."""
        result: dict[str, DiscussionForum] = {}
        if not os.path.isdir(DISCUSSIONS_DIR):
            return result
        for user_dir_name in os.listdir(DISCUSSIONS_DIR):
            user_dir = os.path.join(DISCUSSIONS_DIR, user_dir_name)
            if not os.path.isdir(user_dir):
                continue
            for fname in os.listdir(user_dir):
                if not fname.endswith(".json"):
                    continue
                try:
                    with open(os.path.join(user_dir, fname), "r", encoding="utf-8") as f:
                        data = json.load(f)
                    forum = cls.from_dict(data)
                    result[forum.topic_id] = forum
                except Exception as e:
                    print(f"[OASIS] ⚠️ Failed to load {fname}: {e}")
        return result

    async def publish(self, author: str, content: str, reply_to: int | None = None) -> Post:
        """Publish a new post to the forum (thread-safe)."""
        async with self._lock:
            self._counter += 1
            post = Post(
                id=self._counter,
                author=author,
                content=content,
                reply_to=reply_to,
                elapsed=self.elapsed(),
            )
            self.posts.append(post)
            return post

    async def vote(self, voter: str, post_id: int, direction: str):
        """Vote on a post. Each voter can only vote once per post, cannot vote on own posts."""
        async with self._lock:
            post = self._find(post_id)
            if post and voter != post.author and voter not in post.voters:
                post.voters[voter] = direction
                if direction == "up":
                    post.upvotes += 1
                else:
                    post.downvotes += 1

    async def browse(self, viewer: str | None = None, exclude_self: bool = False) -> list[Post]:
        """Browse all posts. Optionally exclude the viewer's own posts."""
        async with self._lock:
            if exclude_self and viewer:
                return [p for p in self.posts if p.author != viewer]
            return list(self.posts)

    async def get_top_posts(self, n: int = 3) -> list[Post]:
        """Get the top N posts ranked by net upvotes."""
        async with self._lock:
            return sorted(
                self.posts,
                key=lambda p: p.upvotes - p.downvotes,
                reverse=True,
            )[:n]

    async def get_post_count(self) -> int:
        """Get total number of posts."""
        async with self._lock:
            return len(self.posts)

    def _find(self, post_id: int) -> Post | None:
        """Find a post by ID (caller must hold lock)."""
        return next((p for p in self.posts if p.id == post_id), None)

"""
Prompt cache — avoids regenerating stories/audio for same or similar prompts.
Uses simple hash for exact matches + optional fuzzy matching.
"""
import hashlib
import json
import database as db

def hash_prompt(prompt: str, child_name: str, language: str) -> str:
    """Normalize and hash a prompt for cache lookup."""
    normalized = " ".join(prompt.lower().strip().split())
    key = f"{normalized}|{child_name.lower()}|{language}"
    return hashlib.sha256(key.encode()).hexdigest()[:32]

async def get_cached(prompt: str, child_name: str, language: str) -> dict | None:
    """Check if we have a cached story for this prompt."""
    h = hash_prompt(prompt, child_name, language)
    rs = await db.execute(
        "SELECT story_json FROM prompt_cache WHERE prompt_hash = ? AND child_name = ? AND language = ?",
        [h, child_name.lower(), language]
    )
    if rs.rows and rs.rows[0][0]:
        return json.loads(rs.rows[0][0])
    return None

async def set_cached(prompt: str, child_name: str, language: str, story: dict):
    """Cache a generated story for this prompt."""
    h = hash_prompt(prompt, child_name, language)
    try:
        await db.execute(
            "INSERT OR REPLACE INTO prompt_cache (prompt_hash, prompt_text, child_name, language, story_json) VALUES (?, ?, ?, ?, ?)",
            [h, prompt, child_name.lower(), language, json.dumps(story, ensure_ascii=False)]
        )
    except Exception:
        pass  # Cache miss is fine, don't break the flow

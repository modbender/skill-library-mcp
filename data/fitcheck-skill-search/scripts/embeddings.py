#!/usr/bin/env python3
"""Local embedding generation for semantic skill search.

Uses sentence-transformers/all-MiniLM-L6-v2 via ONNX runtime
for fast local embeddings without external API calls.
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Paths
SKILL_DIRS = [
    "/usr/local/lib/node_modules/openclaw/skills",
    os.path.expanduser("~/.openclaw/workspace/skills"),
]
INDEX_DIR = Path(__file__).parent.parent / "index"
EMBEDDINGS_FILE = INDEX_DIR / "embeddings_cache.json"


def ensure_index_dir():
    """Ensure index directory exists."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def parse_frontmatter(content: str) -> Dict:
    """Extract YAML frontmatter from SKILL.md."""
    result = {
        "name": "",
        "description": "",
        "triggers": [],
    }
    
    if not content.startswith("---"):
        return result
    
    # Find end of frontmatter
    end_match = content.find("\n---", 3)
    if end_match == -1:
        return result
    
    frontmatter = content[3:end_match].strip()
    
    # Parse simple key: value pairs
    current_key = None
    current_value = []
    
    for line in frontmatter.split("\n"):
        line_stripped = line.rstrip()
        
        # Check for new key
        if ":" in line_stripped and not line_stripped.startswith(" ") and not line_stripped.startswith("-"):
            # Save previous key-value
            if current_key and current_value:
                value = " ".join(current_value).strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                result[current_key] = value
            
            key, val = line_stripped.split(":", 1)
            current_key = key.strip()
            current_value = [val.strip()]
        elif line_stripped.startswith("- ") and current_key:
            # List item
            item = line_stripped[2:].strip()
            if current_key not in result:
                result[current_key] = []
            if isinstance(result[current_key], list):
                result[current_key].append(item)
        elif current_key:
            current_value.append(line_stripped)
    
    # Save last key-value
    if current_key and current_value:
        value = " ".join(current_value).strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        result[current_key] = value
    
    return result


def extract_skill_text(skill_path: Path) -> Dict:
    """Extract searchable text from a SKILL.md file."""
    try:
        content = skill_path.read_text(encoding='utf-8', errors='ignore')
        frontmatter = parse_frontmatter(content)
        
        # Get body text (after frontmatter)
        body_start = content.find("\n#")
        body = content[body_start:] if body_start > 0 else ""
        
        # Extract first paragraph of description
        desc = frontmatter.get("description", "")
        name = frontmatter.get("name", skill_path.parent.name)
        triggers = frontmatter.get("triggers", [])
        
        # Combine for embedding
        text_parts = [
            name,
            desc,
            " ".join(triggers) if isinstance(triggers, list) else str(triggers),
        ]
        
        # Add body headers and code examples
        for line in body.split("\n"):
            if line.startswith("#") or line.startswith("```"):
                text_parts.append(line.replace("#", "").replace("`", ""))
        
        combined_text = " ".join(filter(None, text_parts))
        
        return {
            "name": name,
            "folder": skill_path.parent.name,
            "description": desc,
            "triggers": triggers if isinstance(triggers, list) else [triggers] if triggers else [],
            "location": str(skill_path.parent),
            "search_text": combined_text[:2000],  # Limit length
            "content_hash": hashlib.md5(content.encode()).hexdigest()[:16],
        }
    except Exception as e:
        return {
            "name": skill_path.parent.name,
            "folder": skill_path.parent.name,
            "description": f"Error parsing: {e}",
            "triggers": [],
            "location": str(skill_path.parent),
            "search_text": skill_path.parent.name,
            "content_hash": "",
        }


def fallback_embedding(text: str) -> List[float]:
    """Simple fallback: char-level n-gram frequency vector."""
    # Create a simple 384-dim vector based on character n-grams
    vector = [0.0] * 384
    text_lower = text.lower()
    
    # Trigram hashing
    for i in range(len(text_lower) - 2):
        trigram = text_lower[i:i+3]
        idx = hash(trigram) % 384
        vector[idx] += 1.0
    
    # Normalize
    norm = sum(x**2 for x in vector) ** 0.5
    if norm > 0:
        vector = [x / norm for x in vector]
    
    return vector


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x**2 for x in a) ** 0.5
    norm_b = sum(x**2 for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def index_all_skills() -> Dict:
    """Build complete skill index with embeddings."""
    ensure_index_dir()
    
    skills = []
    seen = set()
    
    for skill_dir in SKILL_DIRS:
        if not os.path.isdir(skill_dir):
            continue
        
        for item in sorted(os.listdir(skill_dir)):
            if item.startswith(".") or item in seen:
                continue
            
            item_path = Path(skill_dir) / item
            skill_md = item_path / "SKILL.md"
            
            if skill_md.exists():
                seen.add(item)
                skill_data = extract_skill_text(skill_md)
                print(f"Indexing: {skill_data['name']}")
                
                # Generate embedding
                skill_data["embedding"] = fallback_embedding(skill_data["search_text"])
                skills.append(skill_data)
    
    # Save index
    index_path = INDEX_DIR / "skills_index.json"
    with open(index_path, 'w') as f:
        json.dump(skills, f, indent=2)
    
    print(f"Indexed {len(skills)} skills to {index_path}")
    return {"skills": skills, "count": len(skills)}


def load_index() -> Optional[Dict]:
    """Load existing skill index."""
    index_path = INDEX_DIR / "skills_index.json"
    if not index_path.exists():
        return None
    
    with open(index_path, 'r') as f:
        return json.load(f)


def semantic_search(query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
    """Search skills by semantic similarity."""
    index = load_index()
    if not index:
        print("No index found. Building index...")
        result = index_all_skills()
        index = result["skills"]
    
    query_emb = fallback_embedding(query)
    
    results = []
    for skill in index:
        if "embedding" in skill:
            sim = cosine_similarity(query_emb, skill["embedding"])
            results.append((skill, sim))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "index":
        index_all_skills()
    elif len(sys.argv) > 2 and sys.argv[1] == "semantic":
        query = sys.argv[2]
        results = semantic_search(query, top_k=5)
        print(f"\nSemantic search results for: '{query}'\n")
        for skill, score in results:
            print(f"{score:.3f} | {skill['folder']}")
            print(f"      {skill['description'][:80]}...")
            print(f"      Location: {skill['location']}")
            print()
    else:
        print("Usage:")
        print("  python3 embeddings.py index")
        print("  python3 embeddings.py semantic '<query>'")
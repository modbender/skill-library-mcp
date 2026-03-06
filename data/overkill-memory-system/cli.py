#!/usr/bin/env python3
"""
Ultimate Unified Memory System CLI
Implements 6-tier memory architecture with WAL protocol
Neuroscience Integration: Hippocampus (importance), Amygdala (emotions), VTA (value)
ACC-Error Integration: Error pattern tracking
Vestige Integration: Cognitive memory with spaced repetition
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Import integrations
try:
    import acc_error
except ImportError:
    acc_error = None
    
try:
    import vestige
except ImportError:
    vestige = None

try:
    import jarvis_diary
except ImportError:
    jarvis_diary = None

try:
    import basal_ganglia
except ImportError:
    basal_ganglia = None

try:
    import insula
except ImportError:
    insula = None

# Import speed optimizations
try:
    import speed
except ImportError:
    speed = None

# Import file search (optional tier)
try:
    import file_search
except ImportError:
    file_search = None

# Import knowledge graph
try:
    import knowledge_graph
except ImportError:
    knowledge_graph = None

# Import self-improving
try:
    import self_improving
except ImportError:
    self_improving = None

# Import self-reflection
try:
    import self_reflection
except ImportError:
    self_reflection = None

# Paths
MEMORY_BASE = Path.home() / ".openclaw" / "memory"
SESSION_STATE = MEMORY_BASE / "SESSION-STATE.md"
MEMORY_MD = MEMORY_BASE / "MEMORY.md"
CRON_INBOX = MEMORY_BASE / "cron-inbox.md"
PLATFORM_POSTS = MEMORY_BASE / "platform-posts.md"
STRATEGY_NOTES = MEMORY_BASE / "strategy-notes.md"
HEARTBEAT_STATE = MEMORY_BASE / "heartbeat-state.json"
DIARY_DIR = MEMORY_BASE / "diary"
DAILY_DIR = MEMORY_BASE / "daily"
CHROMA_DIR = MEMORY_BASE / "chroma"

# Neuroscience skill paths
HIPPOCAMPUS_INDEX = MEMORY_BASE / "index.json"
AMYGDALA_STATE = MEMORY_BASE / "emotional-state.json"
VTA_STATE = MEMORY_BASE / "reward-state.json"

# Git-Notes COLD tier storage
GIT_NOTES_DIR = MEMORY_BASE / "git-notes"
GIT_NOTES_INDEX = GIT_NOTES_DIR / "index.json"

# BLOOM FILTER & CACHE for hybrid search
BLOOM_FILTER_FILE = MEMORY_BASE / "bloom-filter.json"
CACHE_DIR = MEMORY_BASE / "search-cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Ensure directories exist
MEMORY_BASE.mkdir(parents=True, exist_ok=True)
DIARY_DIR.mkdir(parents=True, exist_ok=True)
DAILY_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
GIT_NOTES_DIR.mkdir(parents=True, exist_ok=True)


def init_files():
    """Initialize all memory files"""
    files = [
        (SESSION_STATE, "# Session State\n\nLast Updated: {}\n\n## WAL Buffer\n\n".format(datetime.now().isoformat())),
        (MEMORY_MD, "# Memory - Long-term Curated\n\n## Key Facts\n\n- (Add important facts here)\n\n## Decisions\n\n- (Add important decisions here)\n\n## Preferences\n\n- (Add user preferences here)\n\n## Lessons Learned\n\n- (Add lessons learned here)\n\n"),
        (CRON_INBOX, "# Cron Inbox\n\n## Cross-session Messages\n\n"),
        (PLATFORM_POSTS, "# Platform Posts\n\n## Tracked Posts\n\n"),
        (STRATEGY_NOTES, "# Strategy Notes\n\n## Adaptive Learning\n\n"),
    ]
    
    for path, default_content in files:
        if not path.exists():
            path.write_text(default_content)
            print(f"Created: {path}")
    
    # Initialize heartbeat state
    if not HEARTBEAT_STATE.exists():
        json.dump({"lastChecks": {}}, HEARTBEAT_STATE.open("w"))
        print(f"Created: {HEARTBEAT_STATE}")
    
    print("Memory system initialized!")


# ============================================================================
# HYBRID SEARCH: INTENT DETECTION
# ============================================================================

def detect_intent(query: str) -> dict:
    """
    Detect user intent from query to optimize search strategy.
    
    Detects: preference, error, important, recent, project, general
    
    Args:
        query: User search query
    
    Returns:
        Dictionary with detected intent and confidence
    """
    query_lower = query.lower()
    
    # Intent patterns
    intent_patterns = {
        "preference": [
            "prefer", "like", "want", "wish", "should", "better", "favorite",
            "always", "never", "usually", "custom", "setting", "config"
        ],
        "error": [
            "error", "bug", "fail", "wrong", "broken", "issue", "problem",
            "crash", "exception", "not working", "fix", "debug"
        ],
        "important": [
            "important", "critical", "key", "remember", "don't forget",
            "must", "essential", "vital", "note", "reminder"
        ],
        "recent": [
            "recent", "latest", "last", "yesterday", "today", "new",
            "just", "recently", "current", "update"
        ],
        "project": [
            "project", "code", "build", "deploy", "release", "feature",
            "implementation", "api", "database", "infrastructure"
        ],
        "general": []  # Fallback
    }
    
    # Score each intent
    intent_scores = {}
    for intent, patterns in intent_patterns.items():
        if not patterns:  # Skip empty general list
            continue
        score = sum(1 for p in patterns if p in query_lower)
        if score > 0:
            intent_scores[intent] = score
    
    # Determine primary intent
    if intent_scores:
        primary_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(1.0, intent_scores[primary_intent] / 3.0)
    else:
        primary_intent = "general"
        confidence = 0.5
    
    return {
        "primary": primary_intent,
        "confidence": round(confidence, 2),
        "all_scores": intent_scores,
        "query": query
    }


def get_tier_weights(intent: dict) -> dict:
    """
    Get tier weights based on detected intent.
    Early weighting allows prioritizing certain tiers based on query intent.
    
    Args:
        intent: Output from detect_intent()
    
    Returns:
        Dictionary of tier weights (0.0-1.0)
    """
    primary = intent["primary"]
    
    # Default weights (balanced)
    default_weights = {
        "hot": 0.2,       # Session state
        "bloom": 0.1,    # Bloom filter check
        "cache": 0.15,   # Search cache
        "mem0": 0.2,     # Mem0 semantic search
        "curated": 0.15, # MEMORY.md
        "cold": 0.1,     # Daily files
        "git_notes": 0.1, # Git-notes
        "diary": 0.1,    # Jarvis diary
        "strategy_notes": 0.1  # Strategy notes
    }
    
    # Intent-specific weights
    intent_weights = {
        "preference": {
            "curated": 0.35,
            "hot": 0.15,
            "cache": 0.15,
            "mem0": 0.15,
            "bloom": 0.05,
            "cold": 0.1,
            "git_notes": 0.05,
            "diary": 0.0,
            "strategy_notes": 0.0
        },
        "error": {
            "hot": 0.35,
            "git_notes": 0.15,
            "cache": 0.1,
            "mem0": 0.1,
            "bloom": 0.0,
            "curated": 0.05,
            "diary": 0.0,
            "strategy_notes": 0.25
        },
        "important": {
            "curated": 0.35,
            "hot": 0.2,
            "git_notes": 0.15,
            "mem0": 0.15,
            "cache": 0.1,
            "cold": 0.03,
            "bloom": 0.02,
            "diary": 0.0,
            "strategy_notes": 0.0
        },
        "recent": {
            "hot": 0.3,
            "cold": 0.3,
            "cache": 0.15,
            "mem0": 0.15,
            "bloom": 0.05,
            "curated": 0.03,
            "git_notes": 0.02,
            "diary": 0.05,
            "strategy_notes": 0.0
        },
        "project": {
            "git_notes": 0.3,
            "cold": 0.25,
            "mem0": 0.2,
            "cache": 0.1,
            "hot": 0.1,
            "bloom": 0.03,
            "curated": 0.02,
            "diary": 0.0,
            "strategy_notes": 0.0
        },
        "general": default_weights
    }
    
    return intent_weights.get(primary, default_weights)


# ============================================================================
# HYBRID SEARCH: BLOOM FILTER
# ============================================================================

def _load_bloom_filter() -> dict:
    """Load bloom filter state."""
    if BLOOM_FILTER_FILE.exists():
        try:
            with open(BLOOM_FILTER_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"entries": set(), "size": 10000}

def _save_bloom_filter(bloom_data: dict):
    """Save bloom filter state."""
    # Convert set to list for JSON
    save_data = {k: list(v) if isinstance(v, set) else v for k, v in bloom_data.items()}
    with open(BLOOM_FILTER_FILE, "w") as f:
        json.dump(save_data, f)

def bloom_check(query: str) -> dict:
    """
    Check if query likely has results in memory using bloom filter.
    Fast pre-check (~1ms) to skip expensive searches.
    
    Args:
        query: Search query
    
    Returns:
        Dictionary with check result and metadata
    """
    bloom_data = _load_bloom_filter()
    entries = set(bloom_data.get("entries", []))
    
    # Simple hash-based membership check
    query_hash = str(hash(query.lower()))
    likely_found = any(query_hash[:4] in entry for entry in entries)
    
    return {
        "query": query,
        "likely_found": likely_found,
        "check_time_ms": 1.0,
        "bloom_size": len(entries)
    }

def bloom_add(query: str):
    """Add query to bloom filter after successful search."""
    bloom_data = _load_bloom_filter()
    entries = set(bloom_data.get("entries", []))
    
    query_hash = str(hash(query.lower()))
    entries.add(query_hash)
    
    # Keep only recent entries
    if len(entries) > bloom_data.get("size", 10000):
        entries = set(list(entries)[-5000:])
    
    bloom_data["entries"] = entries
    _save_bloom_filter(bloom_data)


# ============================================================================
# HYBRID SEARCH: CACHE
# ============================================================================

def cache_get(query: str) -> dict:
    """
    Get cached search results if available and fresh.
    
    Args:
        query: Search query
    
    Returns:
        Cached result or None
    """
    query_hash = str(hash(query.lower()))
    cache_file = CACHE_DIR / f"{query_hash}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                cached = json.load(f)
            
            # Check freshness (5 minutes)
            cached_time = datetime.fromisoformat(cached.get("cached_at", "2000-01-01"))
            age_seconds = (datetime.now() - cached_time).total_seconds()
            
            if age_seconds < 300:  # 5 minutes
                return {
                    "hit": True,
                    "results": cached.get("results", []),
                    "age_seconds": age_seconds,
                    "source": "cache"
                }
        except:
            pass
    
    return {"hit": False}

def cache_set(query: str, results: dict):
    """Cache search results."""
    query_hash = str(hash(query.lower()))
    cache_file = CACHE_DIR / f"{query_hash}.json"
    
    cache_data = {
        "query": query,
        "results": results,
        "cached_at": datetime.now().isoformat()
    }
    
    with open(cache_file, "w") as f:
        json.dump(cache_data, f)


# ============================================================================
# HYBRID SEARCH: MEM0 INTEGRATION
# ============================================================================

def mem0_search(query: str, limit: int = 10) -> dict:
    """
    Search using Mem0 semantic memory.
    This is the PRIMARY search tier - runs BEFORE other tiers.
    
    Args:
        query: Search query
        limit: Max results to return
    
    Returns:
        Mem0 search results with semantic scores
    """
    try:
        # Try to import and use mem0
        from mem0 import Memory
        
        # Initialize mem0 client (uses MEMORY_BASE for storage)
        mem = Memory()
        
        # Search semantic memory
        results = mem.search(query=query, limit=limit)
        
        if results and len(results) > 0:
            return {
                "hit": True,
                "results": results,
                "search_time_ms": 22.0,  # Typical mem0 latency
                "source": "mem0"
            }
        else:
            return {
                "hit": False,
                "results": [],
                "search_time_ms": 25.0,
                "source": "mem0"
            }
            
    except ImportError:
        # mem0 not installed
        return {
            "hit": False,
            "results": [],
            "error": "mem0 not installed",
            "search_time_ms": 1.0,
            "source": "mem0"
        }
    except Exception as e:
        # Mem0 search failed
        return {
            "hit": False,
            "results": [],
            "error": str(e),
            "search_time_ms": 50.0,
            "source": "mem0"
        }


# ============================================================================
# HYBRID SEARCH: MAIN FUNCTION
# ============================================================================

def hybrid_search(query: str, mode: str = "hybrid") -> dict:
    """
    Main hybrid search function implementing the full search pipeline.
    
    Pipeline:
    1. Check bloom filter (fast pre-check)
    2. Check cache (fast)
    3. Query Mem0 FIRST (semantic - primary tier)
    4. If hit: rank + return (~22ms)
    5. If miss: query remaining tiers in parallel
    6. Merge + rank with neuroscience
    
    Args:
        query: Search query
        mode: "hybrid" (default), "fast" (cache only), "full" (all tiers)
    
    Returns:
        Complete search results with timing and scoring
    """
    import time
    start_time = time.time()
    
    result = {
        "query": query,
        "mode": mode,
        "tiers_checked": [],
        "timing": {},
        "results": []
    }
    
    # Step 1: Intent detection for early weighting
    intent = detect_intent(query)
    weights = get_tier_weights(intent)
    result["intent"] = intent
    result["tier_weights"] = weights
    
    # Step 1b: Ultra-Hot tier check (normalized query, sub-ms)
    if speed:
        ultra_hot_start = time.time()
        ultra_hot_results = speed.get_ultra_hot(query)
        result["timing"]["ultra_hot_ms"] = (time.time() - ultra_hot_start) * 1000
        
        if ultra_hot_results is not None:
            result["results"] = ultra_hot_results
            result["source"] = "ultra_hot"
            result["tiers_checked"].append("ultra_hot")
            result["timing"]["total_ms"] = (time.time() - start_time) * 1000
            return result
        result["tiers_checked"].append("ultra_hot")
    
    # Step 2: Bloom filter check
    bloom_start = time.time()
    bloom_result = bloom_check(query)
    result["timing"]["bloom_ms"] = (time.time() - bloom_start) * 1000
    result["tiers_checked"].append("bloom")
    result["bloom"] = bloom_result
    
    # Step 3: Cache check
    cache_start = time.time()
    cache_result = cache_get(query)
    result["timing"]["cache_ms"] = (time.time() - cache_start) * 1000
    
    # FAST MODE: Return cache only
    if mode == "fast":
        if cache_result.get("hit"):
            result["results"] = cache_result.get("results", [])
            result["timing"]["total_ms"] = (time.time() - start_time) * 1000
            result["source"] = "cache"
            result["tiers_checked"].append("cache")
            return result
        else:
            result["results"] = []
            result["timing"]["total_ms"] = (time.time() - start_time) * 1000
            result["source"] = "cache_miss"
            return result
    
    # Step 4: Mem0 search (PRIMARY - runs FIRST)
    mem0_start = time.time()
    mem0_result = mem0_search(query)
    result["timing"]["mem0_ms"] = (time.time() - mem0_start) * 1000
    result["tiers_checked"].append("mem0")
    
    # If Mem0 hit and we have results, rank and return quickly (~22ms)
    if mem0_result.get("hit") and mem0_result.get("results"):
        result["results"] = mem0_result.get("results", [])
        result["source"] = "mem0"
        result["mem0"] = mem0_result
        
        # Add neuroscience scoring to results
        result["results"] = _rank_with_neuroscience(result["results"], query)
        
        # Apply confidence early exit (speed optimization)
        if speed:
            result["results"] = speed.rank_with_confidence(result["results"])
            result["results"] = speed.truncate_results(result["results"])
        
        result["timing"]["total_ms"] = (time.time() - start_time) * 1000
        
        # Update bloom filter
        bloom_add(query)
        
        # Cache the results (with normalized query for better hits)
        if speed:
            normalized_query = speed.normalize_query(query)
            cache_set(normalized_query, result["results"])
        else:
            cache_set(query, result["results"])
        
        return result
    
    # Step 5: Mem0 miss - query remaining tiers in parallel
    result["mem0"] = mem0_result
    result["source"] = "mem0_miss"
    
    # Query remaining tiers
    tier_results = {}
    
    # HOT tier - Session state
    if SESSION_STATE.exists():
        content = SESSION_STATE.read_text()
        if query.lower() in content.lower():
            tier_results["hot"] = [{
                "source": "hot",
                "content": content,
                "preview": content[:300]
            }]
    
    # CURATED tier - MEMORY.md
    if MEMORY_MD.exists():
        content = MEMORY_MD.read_text()
        if query.lower() in content.lower():
            tier_results["curated"] = [{
                "source": "curated",
                "content": content,
                "preview": content[:300]
            }]
    
    # COLD tier - Daily files
    cold_results = []
    for daily_file in DAILY_DIR.glob("*.md"):
        try:
            content = daily_file.read_text()
            if query.lower() in content.lower():
                cold_results.append({
                    "source": "cold",
                    "file": str(daily_file.name),
                    "content": content,
                    "preview": content[:300]
                })
        except:
            pass
    if cold_results:
        tier_results["cold"] = cold_results
    
    # Git-notes
    notes_index = _load_git_notes_index()
    notes_results = []
    for key, note in notes_index.get("notes", {}).items():
        if query.lower() in key.lower() or query.lower() in note.get("value", "").lower():
            notes_results.append({
                "source": "git_notes",
                "key": key,
                "content": note.get("value", ""),
                "preview": note.get("value", "")[:300]
            })
    if notes_results:
        tier_results["git_notes"] = notes_results
    
    # Diary tier - Jarvis diary entries
    if jarvis_diary:
        diary_search_results = jarvis_diary.search_diary(query, max_results=5)
        if diary_search_results.get("total_matches", 0) > 0:
            diary_results = []
            for entry in diary_search_results.get("results", []):
                diary_results.append({
                    "source": "diary",
                    "date": entry.get("date", ""),
                    "timestamp": entry.get("timestamp", ""),
                    "content": entry.get("full_content", ""),
                    "preview": entry.get("content_preview", "")[:300],
                    "importance": entry.get("importance", 0.5),
                    "emotions": entry.get("emotions", [])
                })
            tier_results["diary"] = diary_results
    
    # Strategy notes tier
    if jarvis_diary:
        strategy_search_results = jarvis_diary.search_strategy(query, max_results=5)
        if strategy_search_results.get("total_matches", 0) > 0:
            strategy_results = []
            for entry in strategy_search_results.get("results", []):
                strategy_results.append({
                    "source": "strategy_notes",
                    "section": entry.get("section", ""),
                    "content": entry.get("content", ""),
                    "preview": entry.get("preview", "")[:300]
                })
            tier_results["strategy_notes"] = strategy_results
    
    # FILE SEARCH tier - Fast file search using fd/rg (optional)
    if file_search and file_search.has_fd_rg():
        file_search_results = file_search.fast_file_search(query, MEMORY_BASE, limit=20)
        if file_search_results:
            formatted_results = []
            for fs in file_search_results:
                formatted_results.append({
                    "source": "file_search",
                    "file": fs.get("path", ""),
                    "line": fs.get("line", 0),
                    "content": fs.get("content", ""),
                    "preview": fs.get("content", "")[:300] if fs.get("content") else fs.get("path", ""),
                    "score": fs.get("score", 0.5)
                })
            tier_results["file_search"] = formatted_results
    
    # Merge all results
    all_results = []
    for tier, tier_data in tier_results.items():
        weight = weights.get(tier, 0.1)
        for item in tier_data:
            item["tier"] = tier
            item["weight"] = weight
            all_results.append(item)
    
    # FULL MODE: Query ALL tiers (skip optimization)
    if mode == "full":
        result["tiers_checked"].extend(["hot", "curated", "cold", "git_notes", "diary", "file_search"])
    
    # Rank with neuroscience
    result["results"] = _rank_with_neuroscience(all_results, query)
    
    # Apply confidence early exit (speed optimization)
    if speed:
        result["results"] = speed.rank_with_confidence(result["results"])
        result["results"] = speed.truncate_results(result["results"])
    
    result["tier_results"] = tier_results
    
    # Timing
    result["timing"]["total_ms"] = (time.time() - start_time) * 1000
    
    # Cache results (with normalized query for better hits)
    if result["results"]:
        if speed:
            normalized_query = speed.normalize_query(query)
            cache_set(normalized_query, result["results"])
            # Also cache in ultra-hot
            speed.set_ultra_hot(query, result["results"])
        else:
            cache_set(query, result["results"])
        bloom_add(query)
    
    return result


def _rank_with_neuroscience(results: list, query: str) -> list:
    """
    Rank search results using neuroscience scoring.
    Combines: relevance, importance (Hippocampus), value (VTA), emotion (Amygdala)
    
    Final Score = (Base Relevance × 0.4) + (Importance × 0.3) + (Value × 0.2) + (Emotion Match × 0.1)
    """
    if not results:
        return []
    
    query_lower = query.lower()
    
    # Get habit boost for this query
    habit_boost = 0.0
    if basal_ganglia:
        habit_boost = basal_ganglia.get_habit_boost(query)
    
    for result in results:
        content = result.get("content", result.get("preview", ""))
        
        # Base relevance (simple keyword match)
        query_words = set(query_lower.split())
        content_lower = content.lower()
        matches = sum(1 for w in query_words if w in content_lower)
        base_relevance = min(1.0, matches / max(1, len(query_words)))
        
        # Neuroscience analysis
        neuro = analyze_text_neuroscience(content, include_scoring=False)
        
        # Extract scores
        importance = neuro.get("hippocampus", {}).get("importance", 0.5)
        value = neuro.get("vta", {}).get("value", 0.5)
        emotion_intensity = neuro.get("amygdala", {}).get("intensity", 0.5)
        
        # Apply tier weight
        tier_weight = result.get("weight", 0.1)
        
        # Calculate final score
        final_score = (
            (base_relevance * 0.4) +
            (importance * 0.3) +
            (value * 0.2) +
            (emotion_intensity * 0.1)
        )
        
        # Boost by tier weight
        final_score = final_score * (0.5 + tier_weight)
        
        # Apply habit boost (Basal Ganglia)
        if habit_boost > 0:
            final_score = final_score * (1.0 + habit_boost)
        
        result["neuroscience"] = {
            "importance": importance,
            "value": value,
            "emotion_intensity": emotion_intensity,
            "base_relevance": base_relevance,
            "tier_weight": tier_weight,
            "habit_boost": habit_boost
        }
        result["final_score"] = round(final_score, 4)
    
    # Sort by final_score descending
    results.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    
    return results


# ============================================================================
# NEUROSCIENCE INTEGRATION FUNCTIONS
# ============================================================================

# Valid neuroscience values
VALID_EMOTIONS = ["joy", "sadness", "anger", "fear", "curiosity", "connection", "accomplishment", "fatigue"]
VALID_REWARDS = ["accomplishment", "social", "curiosity", "connection", "creative", "competence"]


# ============================================================================
# HIPPOCAMPUS (Importance Scoring)
# ============================================================================

def calculate_hippocampus_importance(content: str, memory_history: list = None) -> dict:
    """
    Calculate importance score (0-1) based on neuroscience principles:
    - Frequency of mention (how often similar concepts appear)
    - User corrections (explicit feedback indicating importance)
    - Emotional weight (emotional content is more memorable)
    - Recency (recent events matter more)
    
    Args:
        content: The text content to analyze
        memory_history: Optional list of past memories to check frequency
    
    Returns:
        Dictionary with importance breakdown and final score
    """
    content_lower = content.lower()
    word_count = len(content.split())
    
    # 1. Frequency of Mention (0-1)
    # Check if similar topics appear in memory history
    frequency_score = 0.3  # default baseline
    if memory_history:
        keywords = set(content_lower.split()[:10])  # First 10 words as keywords
        mention_count = 0
        for mem in memory_history:
            mem_lower = mem.get("content", "").lower()
            if any(k in mem_lower for k in keywords if len(k) > 3):
                mention_count += 1
        # More mentions = higher importance (up to 1.0)
        frequency_score = min(1.0, 0.3 + (mention_count * 0.15))
    
    # 2. User Corrections (0-1)
    # Keywords that indicate user corrections/feedback
    correction_patterns = [
        "remember", "actually", "correction", "not", "wrong", "instead", 
        "important", "don't forget", "make sure", "note that", "btw", 
        "by the way", "reminder", "highlight", "key point", "critical"
    ]
    correction_count = sum(1 for p in correction_patterns if p in content_lower)
    correction_score = min(1.0, 0.2 + (correction_count * 0.2))
    
    # 3. Emotional Weight (0-1)
    # Emotional content is more memorable
    emotions = detect_emotions(content)
    emotional_weight = len(emotions) * 0.15  # Each emotion adds weight
    emotion_score = min(1.0, 0.1 + emotional_weight)
    
    # 4. Recency (0-1)
    # Default to recent unless specified otherwise
    # For CLI input, assume recent (0.7 baseline)
    recency_score = 0.7
    
    # Calculate weighted importance
    importance = (
        (frequency_score * 0.25) +
        (correction_score * 0.25) +
        (emotion_score * 0.25) +
        (recency_score * 0.25)
    )
    
    return {
        "importance": round(importance, 3),
        "breakdown": {
            "frequency": round(frequency_score, 3),
            "correction": round(correction_score, 3),
            "emotional_weight": round(emotion_score, 3),
            "recency": round(recency_score, 3)
        },
        "detected_emotions": emotions,
        "word_count": word_count
    }


# ============================================================================
# AMYGdala (Emotional Tagging)
# ============================================================================

def calculate_amygdala_emotional_intensity(emotions: list) -> dict:
    """
    Calculate emotional intensity (0-1) based on detected emotions.
    
    Args:
        emotions: List of detected emotion strings
    
    Returns:
        Dictionary with intensity score and emotional profile
    """
    if not emotions:
        return {
            "intensity": 0.0,
            "primary_emotion": None,
            "emotional_profile": {},
            "valence": 0.0,
            "arousal": 0.0
        }
    
    # Emotion intensity weights (how "strong" each emotion felt)
    emotion_intensity = {
        "joy": 0.9,
        "accomplishment": 0.85,
        "anger": 0.8,
        "fear": 0.75,
        "sadness": 0.6,
        "curiosity": 0.7,
        "connection": 0.65,
        "fatigue": 0.4
    }
    
    # Calculate intensity (average of detected emotions)
    intensities = [emotion_intensity.get(e, 0.5) for e in emotions]
    avg_intensity = sum(intensities) / len(intensities)
    
    # Find primary (strongest) emotion
    primary = max(emotions, key=lambda e: emotion_intensity.get(e, 0.5))
    
    # Emotional dimensions (valence: positive/negative, arousal: high/low)
    valence_map = {
        "joy": 0.8, "accomplishment": 0.7, "curiosity": 0.6, "connection": 0.6,
        "anger": -0.6, "fear": -0.5, "sadness": -0.7, "fatigue": -0.3
    }
    arousal_map = {
        "joy": 0.7, "accomplishment": 0.6, "anger": 0.9, "fear": 0.8,
        "sadness": 0.3, "curiosity": 0.5, "connection": 0.4, "fatigue": 0.2
    }
    
    valence = sum(valence_map.get(e, 0) for e in emotions) / len(emotions)
    arousal = sum(arousal_map.get(e, 0) for e in emotions) / len(emotions)
    
    return {
        "intensity": round(avg_intensity, 3),
        "primary_emotion": primary,
        "emotional_profile": {e: emotion_intensity.get(e, 0.5) for e in emotions},
        "valence": round(valence, 3),  # -1 (negative) to +1 (positive)
        "arousal": round(arousal, 3),  # 0 (calm) to 1 (aroused)
        "emotions_detected": emotions
    }


def tag_with_amygdala(content: str) -> dict:
    """
    Full amygdala emotional tagging pipeline.
    
    Returns:
        Complete emotional analysis
    """
    emotions = detect_emotions(content)
    intensity_data = calculate_amygdala_emotional_intensity(emotions)
    
    return {
        "content_preview": content[:100],
        "emotions": emotions,
        "intensity": intensity_data["intensity"],
        "primary_emotion": intensity_data["primary_emotion"],
        "valence": intensity_data["valence"],
        "arousal": intensity_data["arousal"],
        "emotional_profile": intensity_data["emotional_profile"],
        "tagged_at": datetime.now().isoformat()
    }


# ============================================================================
# VTA (Value Scoring)
# ============================================================================

def calculate_vta_value(content: str, reward_type: str = None, intensity: float = 0.5,
                         user_feedback: str = None, task_completed: bool = None,
                         goal_alignment: float = None) -> dict:
    """
    Calculate value score based on VTA (Ventral Tegmental Area) reward pathways.
    
    Args:
        content: The content to score
        reward_type: Primary reward type (auto-detected if None)
        intensity: Base intensity (0-1)
        user_feedback: Optional user feedback text
        task_completed: Whether a task was completed
        goal_alignment: Alignment with goals (0-1)
    
    Returns:
        Dictionary with value score and reward breakdown
    """
    # Reward type weights (dopamine response strength)
    reward_weights = {
        "accomplishment": 0.9,
        "competence": 0.85,
        "social": 0.8,
        "connection": 0.8,
        "creative": 0.75,
        "curiosity": 0.7
    }
    
    # Auto-detect reward type from content if not provided
    if not reward_type:
        reward_type = detect_reward_type_from_content(content)
    
    base_weight = reward_weights.get(reward_type, 0.5)
    
    # 1. User Feedback Modifier (0-1)
    feedback_score = 0.5  # baseline
    if user_feedback:
        positive_patterns = ["good", "great", "thanks", "perfect", "awesome", "love", "excellent"]
        negative_patterns = ["bad", "wrong", "terrible", "hate", "disappointed", "fail"]
        fb_lower = user_feedback.lower()
        if any(p in fb_lower for p in positive_patterns):
            feedback_score = 0.9
        elif any(p in fb_lower for p in negative_patterns):
            feedback_score = 0.2
    
    # 2. Task Completion (0 or 1)
    task_score = 0.5
    if task_completed is not None:
        task_score = 1.0 if task_completed else 0.2
    
    # 3. Goal Alignment (0-1)
    goal_score = goal_alignment if goal_alignment is not None else 0.6
    
    # Calculate final value
    value = (
        (base_weight * intensity * 0.4) +
        (feedback_score * 0.2) +
        (task_score * 0.2) +
        (goal_score * 0.2)
    )
    
    return {
        "value": round(value, 3),
        "reward_type": reward_type,
        "base_weight": base_weight,
        "breakdown": {
            "reward_strength": round(base_weight * intensity, 3),
            "user_feedback": round(feedback_score, 3),
            "task_completion": round(task_score, 3),
            "goal_alignment": round(goal_score, 3)
        },
        "detected_from_content": reward_type if not reward_type else False
    }


def detect_reward_type_from_content(content: str) -> str:
    """Auto-detect reward type from content."""
    content_lower = content.lower()
    
    reward_indicators = {
        "accomplishment": ["completed", "finished", "done", "shipped", "success", "achieved", "fixed", "solved"],
        "competence": ["expert", "skill", "learned", "mastered", "improved", "better", "efficient"],
        "social": ["team", "colleague", "meeting", "together", "share", "discuss"],
        "connection": ["friend", "family", "bond", "reconnect", "welcome", "good to"],
        "creative": ["create", "design", "invent", "art", "idea", "novel", "imagine"],
        "curiosity": ["wonder", "explore", "discover", "learn", "research", "?"]
    }
    
    for reward_type, indicators in reward_indicators.items():
        if any(ind in content_lower for ind in indicators):
            return reward_type
    
    return "curiosity"  # Default


# ============================================================================
# COMBINED NEUROSCIENCE ANALYSIS
# ============================================================================

def analyze_text_neuroscience(content: str, include_scoring: bool = True) -> dict:
    """
    Full neuroscience analysis of text.
    
    Args:
        content: Text to analyze
        include_scoring: Include final combined score
    
    Returns:
        Complete neuroscience analysis
    """
    # Hippocampus - Importance
    importance_data = calculate_hippocampus_importance(content)
    
    # Amygdala - Emotions
    emotions = detect_emotions(content)
    amygdala_data = calculate_amygdala_emotional_intensity(emotions)
    
    # VTA - Value
    vta_data = calculate_vta_value(content)
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "content_preview": content[:100],
        "hippocampus": importance_data,
        "amygdala": amygdala_data,
        "vta": vta_data
    }
    
    if include_scoring:
        # Final Score = (Base Relevance × 0.4) + (Importance × 0.3) + (Value × 0.2) + (Emotion Match × 0.1)
        # For text analysis, base relevance is assumed to be 1.0 (perfect match to query)
        base_relevance = 1.0
        importance = importance_data["importance"]
        value = vta_data["value"]
        emotion_match = amygdala_data["intensity"]
        
        final_score = (
            (base_relevance * 0.4) +
            (importance * 0.3) +
            (value * 0.2) +
            (emotion_match * 0.1)
        )
        
        result["final_score"] = round(final_score, 3)
        result["scoring_formula"] = {
            "base_relevance": {"weight": 0.4, "value": base_relevance},
            "importance": {"weight": 0.3, "value": importance},
            "value": {"weight": 0.2, "value": value},
            "emotion_match": {"weight": 0.1, "value": emotion_match}
        }
    
    return result


def get_neuroscience_stats() -> dict:
    """Get comprehensive neuroscience statistics."""
    stats = {
        "timestamp": datetime.now().isoformat(),
        "system": "overkill-memory-system",
        "components": {}
    }
    
    # Hippocampus stats
    stats["components"]["hippocampus"] = {
        "name": "Importance Scoring",
        "factors": ["frequency", "correction", "emotional_weight", "recency"],
        "status": "active"
    }
    
    # Amygdala stats
    stats["components"]["amygdala"] = {
        "name": "Emotional Tagging",
        "detectable_emotions": VALID_EMOTIONS,
        "dimensions": ["valence", "arousal", "intensity"],
        "status": "active"
    }
    
    # VTA stats
    stats["components"]["vta"] = {
        "name": "Value Scoring",
        "reward_types": VALID_REWARDS,
        "factors": ["user_feedback", "task_completion", "goal_alignment"],
        "status": "active"
    }
    
    # Count tagged memories
    total_tagged = 0
    emotion_distribution = {}
    
    for neuro_file in MEMORY_BASE.glob("**/*.neuro.json"):
        try:
            with open(neuro_file) as f:
                data = json.load(f)
            memories = data.get("memories", [])
            total_tagged += len(memories)
            for mem in memories:
                for emotion in mem.get("emotions", []):
                    emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
        except:
            pass
    
    stats["memory_stats"] = {
        "total_neuro_tagged": total_tagged,
        "emotion_distribution": emotion_distribution
    }
    
    return stats


def search_with_neuroscience_scoring(query: str) -> dict:
    """
    Search memories with full neuroscience scoring.
    
    Final Score = (Base Relevance × 0.4) + (Importance × 0.3) + (Value × 0.2) + (Emotion Match × 0.1)
    """
    results = {
        "query": query,
        "scoring_mode": "neuroscience",
        "results": []
    }
    
    query_lower = query.lower()
    
    # Get habit boost for this query
    habit_boost = 0.0
    if basal_ganglia:
        habit_boost = basal_ganglia.get_habit_boost(query)
    
    # Search through all tiers
    search_paths = [
        ("session", SESSION_STATE),
        ("curated", MEMORY_MD),
        ("inbox", CRON_INBOX),
        ("daily", DAILY_DIR),
        ("diary", DIARY_DIR)
    ]
    
    for tier_name, path in search_paths:
        if tier_name in ["daily", "diary"]:
            # Directory - glob for files
            if path.exists():
                for file in path.glob("*.md"):
                    try:
                        content = file.read_text()
                        if query_lower in content.lower():
                            # Full neuroscience analysis
                            analysis = analyze_text_neuroscience(content)
                            results["results"].append({
                                "source": str(file),
                                "tier": tier_name,
                                "content_preview": content[:200],
                                **analysis
                            })
                    except:
                        pass
        else:
            # Single file
            if path.exists():
                try:
                    content = path.read_text()
                    if query_lower in content.lower():
                        analysis = analyze_text_neuroscience(content)
                        results["results"].append({
                            "source": str(path),
                            "tier": tier_name,
                            "content_preview": content[:200],
                            **analysis
                        })
                except:
                    pass
    
    # Sort by final_score descending
    results["results"].sort(key=lambda x: x.get("final_score", 0), reverse=True)
    
    # Apply habit boost to all results
    if habit_boost > 0:
        for result in results["results"]:
            result["final_score"] = round(result["final_score"] * (1.0 + habit_boost), 4)
            result["habit_boost"] = habit_boost
        # Re-sort after applying habit boost
        results["results"].sort(key=lambda x: x.get("final_score", 0), reverse=True)
    
    results["habit_boost"] = habit_boost
    
    return results


def get_importance_from_index(content: str) -> float:
    """Read importance score from hippocampus index.json for related memories."""
    if not HIPPOCAMPUS_INDEX.exists():
        return 0.5  # Default importance
    
    try:
        with open(HIPPOCAMPUS_INDEX) as f:
            data = json.load(f)
        
        # Find memories with similar content
        memories = data.get("memories", [])
        content_lower = content.lower()
        
        # Check for keyword matches with existing memories
        for mem in memories:
            mem_content = mem.get("content", "").lower()
            if any(word in content_lower for word in mem_content.split()[:5]):
                return mem.get("importance", 0.5)
        
        return 0.5  # Default
    except Exception:
        return 0.5


def detect_emotions(content: str) -> list:
    """Detect emotions from content using keyword patterns."""
    content_lower = content.lower()
    detected = []
    
    emotion_patterns = {
        "joy": ["happy", "great", "wonderful", "awesome", "love", "excited", "celebrate", "🎉", "❤️", "thanks", "thank you"],
        "sadness": ["sad", "sorry", "unfortunately", "disappointed", "miss", "lost", "failed"],
        "anger": ["angry", "frustrated", "annoyed", "irritated", "hate", "terrible", "awful"],
        "fear": ["worried", "anxious", "afraid", "nervous", "scared", "concerned", "uncertain"],
        "curiosity": ["wonder", "interesting", "curious", "explore", "discover", "learn", "?", "how", "why"],
        "connection": ["friend", "bond", "together", "miss you", "welcome", "nice to", "good to"],
        "accomplishment": ["completed", "finished", "done", "shipped", "success", "achieved", "won", "fixed"],
        "fatigue": ["tired", "exhausted", "drained", "burned out", "need rest", "sleepy"]
    }
    
    for emotion, patterns in emotion_patterns.items():
        if any(p in content_lower for p in patterns):
            if emotion not in detected:
                detected.append(emotion)
    
    return detected


def get_current_emotional_state() -> dict:
    """Get current emotional state from amygdala."""
    if not AMYGDALA_STATE.exists():
        return {"valence": 0.1, "arousal": 0.3, "connection": 0.4, "curiosity": 0.5, "energy": 0.5}
    
    try:
        with open(AMYGDALA_STATE) as f:
            return json.load(f).get("dimensions", {})
    except Exception:
        return {"valence": 0.1, "arousal": 0.3, "connection": 0.4, "curiosity": 0.5, "energy": 0.5}


def get_current_drive() -> float:
    """Get current motivation drive from VTA."""
    if not VTA_STATE.exists():
        return 0.5  # Baseline drive
    
    try:
        with open(VTA_STATE) as f:
            data = json.load(f)
        return data.get("drive", 0.5)
    except Exception:
        return 0.5


def compute_value_score(reward_type: str, intensity: float = 0.5) -> float:
    """Compute value/motivation score based on reward type."""
    reward_weights = {
        "accomplishment": 0.9,
        "social": 0.8,
        "curiosity": 0.7,
        "connection": 0.8,
        "creative": 0.75,
        "competence": 0.85
    }
    weight = reward_weights.get(reward_type, 0.5)
    return weight * intensity


def add_neuroscience_metadata(content: str, importance: float = None, emotions: list = None, 
                               reward_type: str = None, reward_intensity: float = 0.5) -> dict:
    """
    Add neuroscience metadata to a memory.
    
    Args:
        content: The memory content
        importance: Importance score (0.0-1.0), auto-detected if None
        emotions: List of emotions, auto-detected if None
        reward_type: VTA reward type, auto-detected if None
        reward_intensity: Intensity for reward calculation
    
    Returns:
        Dictionary with neuroscience metadata
    """
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "importance": importance if importance is not None else get_importance_from_index(content),
        "emotions": emotions if emotions is not None else detect_emotions(content),
        "value": None,
        "source": "cli"
    }
    
    # Add VTA value if reward_type provided or detected
    if reward_type:
        metadata["value"] = {
            "type": reward_type,
            "score": compute_value_score(reward_type, reward_intensity),
            "intensity": reward_intensity
        }
    elif reward_type is None and metadata["emotions"]:
        # Auto-detect reward from emotions
        emotion_to_reward = {
            "accomplishment": "accomplishment",
            "joy": "social",
            "connection": "connection",
            "curiosity": "curiosity"
        }
        for emotion in metadata["emotions"]:
            if emotion in emotion_to_reward:
                metadata["value"] = {
                    "type": emotion_to_reward[emotion],
                    "score": compute_value_score(emotion_to_reward[emotion], 0.5),
                    "intensity": 0.5,
                    "auto_detected": True
                }
                break
    
    return metadata


def tag_memory_with_neuroscience(file_path: str, content: str, importance: float = None,
                                  emotions: list = None, reward_type: str = None,
                                  reward_intensity: float = 0.5) -> dict:
    """Tag a stored memory file with neuroscience metadata."""
    metadata = add_neuroscience_metadata(content, importance, emotions, reward_type, reward_intensity)
    
    # Store metadata in a companion .neuro.json file
    neuro_path = Path(str(file_path).replace(".md", ".neuro.json"))
    
    existing = {}
    if neuro_path.exists():
        try:
            with open(neuro_path) as f:
                existing = json.load(f)
        except:
            pass
    
    existing["memories"] = existing.get("memories", [])
    existing["memories"].append({
        "content_preview": content[:100],
        **metadata
    })
    existing["lastUpdated"] = datetime.now().isoformat()
    
    with open(neuro_path, "w") as f:
        json.dump(existing, f, indent=2)
    
    return metadata


def analyze_existing_memories() -> dict:
    """Analyze all existing memories and add neuroscience tags."""
    results = {"analyzed": 0, "tagged": 0, "errors": 0, "by_tier": {}}
    
    # Analyze daily files
    daily_path = DAILY_DIR
    if daily_path.exists():
        results["by_tier"]["daily"] = {"analyzed": 0, "tagged": 0}
        for md_file in daily_path.glob("*.md"):
            try:
                content = md_file.read_text()
                metadata = tag_memory_with_neuroscience(str(md_file), content)
                results["by_tier"]["daily"]["analyzed"] += 1
                results["by_tier"]["daily"]["tagged"] += 1
                results["tagged"] += 1
            except Exception as e:
                results["errors"] += 1
            results["analyzed"] += 1
    
    # Analyze diary files
    diary_path = DIARY_DIR
    if diary_path.exists():
        results["by_tier"]["diary"] = {"analyzed": 0, "tagged": 0}
        for md_file in diary_path.glob("*.md"):
            try:
                content = md_file.read_text()
                metadata = tag_memory_with_neuroscience(str(md_file), content)
                results["by_tier"]["diary"]["analyzed"] += 1
                results["by_tier"]["diary"]["tagged"] += 1
                results["tagged"] += 1
            except Exception as e:
                results["errors"] += 1
            results["analyzed"] += 1
    
    return results


def search_with_importance_weighting(query: str) -> dict:
    """
    Search memories with importance weighting (Hippocampus integration).
    Higher importance memories are ranked higher.
    """
    results = {"query": query, "importance_weighted": True, "results": []}
    
    # Load hippocampus index for importance scores
    importance_map = {}
    if HIPPOCAMPUS_INDEX.exists():
        try:
            with open(HIPPOCAMPUS_INDEX) as f:
                data = json.load(f)
            for mem in data.get("memories", []):
                importance_map[mem.get("content", "")[:50].lower()] = mem.get("importance", 0.5)
        except:
            pass
    
    # Search through tiers
    for daily_file in DAILY_DIR.glob("*.md"):
        if query.lower() in daily_file.read_text().lower():
            content = daily_file.read_text()
            # Try to find importance from index
            importance = 0.5
            for key, val in importance_map.items():
                if key in content.lower():
                    importance = val
                    break
            
            results["results"].append({
                "source": str(daily_file),
                "importance": importance,
                "content_preview": content[:200]
            })
    
    # Sort by importance descending
    results["results"].sort(key=lambda x: x["importance"], reverse=True)
    
    return results


def get_neuroscience_summary() -> dict:
    """Get a summary of neuroscience state across all systems."""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "hippocampus": {},
        "amygdala": {},
        "vta": {}
    }
    
    # Hippocampus - importance stats
    if HIPPOCAMPUS_INDEX.exists():
        try:
            with open(HIPPOCAMPUS_INDEX) as f:
                data = json.load(f)
            memories = data.get("memories", [])
            importance_scores = [m.get("importance", 0) for m in memories]
            summary["hippocampus"] = {
                "total_memories": len(memories),
                "avg_importance": sum(importance_scores) / len(importance_scores) if importance_scores else 0,
                "core_memories": len([s for s in importance_scores if s >= 0.7])
            }
        except Exception as e:
            summary["hippocampus"]["error"] = str(e)
    
    # Amygdala - emotional state
    if AMYGDALA_STATE.exists():
        try:
            with open(AMYGDALA_STATE) as f:
                data = json.load(f)
            summary["amygdala"] = data.get("dimensions", {})
        except Exception as e:
            summary["amygdala"]["error"] = str(e)
    
    # VTA - motivation state
    if VTA_STATE.exists():
        try:
            with open(VTA_STATE) as f:
                data = json.load(f)
            summary["vta"] = {
                "drive": data.get("drive", 0.5),
                "seeking": data.get("seeking", []),
                "anticipating": data.get("anticipating", [])
            }
        except Exception as e:
            summary["vta"]["error"] = str(e)
    
    return summary


# ============================================================================
# MEMORY FUNCTIONS
# ============================================================================


def search(query: str):
    """Search all memory tiers"""
    results = {"query": query, "tiers": {}}
    
    # HOT tier - SESSION-STATE.md
    if SESSION_STATE.exists():
        content = SESSION_STATE.read_text()
        if query.lower() in content.lower():
            results["tiers"]["hot"] = {"source": str(SESSION_STATE), "matches": ["Query found in session state"]}
    
    # CURATED tier - MEMORY.md
    if MEMORY_MD.exists():
        content = MEMORY_MD.read_text()
        if query.lower() in content.lower():
            results["tiers"]["curated"] = {"source": str(MEMORY_MD), "matches": ["Query found in curated memory"]}
    
    # COLD tier - daily files
    daily_matches = []
    for daily_file in DAILY_DIR.glob("*.md"):
        if query.lower() in daily_file.read_text().lower():
            daily_matches.append(str(daily_file.name))
    if daily_matches:
        results["tiers"]["cold"] = {"source": str(DAILY_DIR), "matches": daily_matches}
    
    # Cron inbox
    if CRON_INBOX.exists():
        content = CRON_INBOX.read_text()
        if query.lower() in content.lower():
            results["tiers"]["inbox"] = {"source": str(CRON_INBOX), "matches": ["Query found in cron inbox"]}
    
    print(json.dumps(results, indent=2))


def wal_write(category: str, content: str, importance: float = None, emotions: str = None, 
              reward_type: str = None, reward_intensity: float = 0.5):
    """Write to WAL (Write-Ahead Log) with neuroscience metadata"""
    timestamp = datetime.now().isoformat()
    
    # Parse emotions if provided as string
    emotion_list = None
    if emotions:
        emotion_list = [e.strip() for e in emotions.split(",") if e.strip() in VALID_EMOTIONS]
    
    # Add neuroscience metadata
    neuro_meta = add_neuroscience_metadata(
        content, 
        importance=importance, 
        emotions=emotion_list, 
        reward_type=reward_type,
        reward_intensity=reward_intensity
    )
    
    # Format entry with neuroscience metadata
    neuro_tags = ""
    if neuro_meta["importance"]:
        neuro_tags += f" [importance: {neuro_meta['importance']:.2f}]"
    if neuro_meta["emotions"]:
        neuro_tags += f" [emotions: {', '.join(neuro_meta['emotions'])}]"
    if neuro_meta["value"]:
        neuro_tags += f" [value: {neuro_meta['value']['type']}:{neuro_meta['value']['score']:.2f}]"
    
    entry = f"\n### [{timestamp}] {category}{neuro_tags}\n{content}\n"
    
    with SESSION_STATE.open("a") as f:
        f.write(entry)
    
    print(f"WAL entry written to {SESSION_STATE}")
    if neuro_tags:
        print(f"  🧠 Neuroscience: {neuro_tags}")


def wal_read():
    """Read session state"""
    if SESSION_STATE.exists():
        print(SESSION_STATE.read_text())
    else:
        print("No session state found")


def inbox_read():
    """Read cron inbox"""
    if CRON_INBOX.exists():
        print(CRON_INBOX.read_text())
    else:
        print("No inbox found")


def inbox_write(content: str, importance: float = None, emotions: str = None,
                reward_type: str = None, reward_intensity: float = 0.5):
    """Write to cron inbox with neuroscience metadata"""
    timestamp = datetime.now().isoformat()
    
    # Parse emotions if provided as string
    emotion_list = None
    if emotions:
        emotion_list = [e.strip() for e in emotions.split(",") if e.strip() in VALID_EMOTIONS]
    
    # Add neuroscience metadata
    neuro_meta = add_neuroscience_metadata(
        content,
        importance=importance,
        emotions=emotion_list,
        reward_type=reward_type,
        reward_intensity=reward_intensity
    )
    
    # Format entry with neuroscience metadata
    neuro_tags = ""
    if neuro_meta["importance"]:
        neuro_tags += f" [importance: {neuro_meta['importance']:.2f}]"
    if neuro_meta["emotions"]:
        neuro_tags += f" [emotions: {', '.join(neuro_meta['emotions'])}]"
    if neuro_meta["value"]:
        neuro_tags += f" [value: {neuro_meta['value']['type']}:{neuro_meta['value']['score']:.2f}]"
    
    entry = f"\n### [{timestamp}]{neuro_tags}\n{content}\n"
    
    with CRON_INBOX.open("a") as f:
        f.write(entry)
    
    print(f"Inbox entry written to {CRON_INBOX}")
    if neuro_tags:
        print(f"  🧠 Neuroscience: {neuro_tags}")


def diary_write(content: str, importance: float = None, emotions: str = None,
                reward_type: str = None, reward_intensity: float = 0.5):
    """Write to personal diary with neuroscience metadata"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    diary_file = DIARY_DIR / f"{date_str}.md"
    
    # Parse emotions if provided as string
    emotion_list = None
    if emotions:
        emotion_list = [e.strip() for e in emotions.split(",") if e.strip() in VALID_EMOTIONS]
    
    # Add neuroscience metadata
    neuro_meta = add_neuroscience_metadata(
        content,
        importance=importance,
        emotions=emotion_list,
        reward_type=reward_type,
        reward_intensity=reward_intensity
    )
    
    if not diary_file.exists():
        diary_file.write_text(f"# Diary - {date_str}\n\n")
    
    timestamp = datetime.now().isoformat()
    
    # Format entry with neuroscience metadata
    neuro_tags = ""
    if neuro_meta["importance"]:
        neuro_tags += f" *importance: {neuro_meta['importance']:.2f}*"
    if neuro_meta["emotions"]:
        neuro_tags += f" *emotions: {', '.join(neuro_meta['emotions'])}*"
    if neuro_meta["value"]:
        neuro_tags += f" *value: {neuro_meta['value']['type']} ({neuro_meta['value']['score']:.2f})*"
    
    entry = f"\n## {timestamp}{neuro_tags}\n\n{content}\n"
    
    with diary_file.open("a") as f:
        f.write(entry)
    
    print(f"Diary entry written to {diary_file}")
    if neuro_tags:
        print(f"  🧠 Neuroscience: {neuro_tags}")


def stats():
    """Show memory statistics"""
    stats = {
        "memory_base": str(MEMORY_BASE),
        "tiers": {}
    }
    
    # HOT
    if SESSION_STATE.exists():
        stats["tiers"]["hot"] = {
            "file": str(SESSION_STATE),
            "size_bytes": SESSION_STATE.stat().st_size,
            "modified": datetime.fromtimestamp(SESSION_STATE.stat().st_mtime).isoformat()
        }
    
    # CURATED
    if MEMORY_MD.exists():
        stats["tiers"]["curated"] = {
            "file": str(MEMORY_MD),
            "size_bytes": MEMORY_MD.stat().st_size
        }
    
    # Cold - daily files
    daily_files = list(DAILY_DIR.glob("*.md"))
    stats["tiers"]["cold"] = {
        "directory": str(DAILY_DIR),
        "file_count": len(daily_files)
    }
    
    # Diary
    diary_files = list(DIARY_DIR.glob("*.md"))
    stats["tiers"]["diary"] = {
        "directory": str(DIARY_DIR),
        "entry_count": len(diary_files)
    }
    
    # Inbox
    if CRON_INBOX.exists():
        stats["tiers"]["inbox"] = {
            "file": str(CRON_INBOX),
            "size_bytes": CRON_INBOX.stat().st_size
        }
    
    # Git-Notes (COLD tier)
    if GIT_NOTES_INDEX.exists():
        notes_index = _load_git_notes_index()
        stats["tiers"]["cold_git_notes"] = {
            "directory": str(GIT_NOTES_DIR),
            "note_count": len(notes_index.get("notes", {}))
        }
    
    print(json.dumps(stats, indent=2))


def cleanup(days: int):
    """Clean old memories"""
    cutoff = datetime.now() - timedelta(days=days)
    cleaned = []
    
    # Clean daily files
    for daily_file in DAILY_DIR.glob("*.md"):
        file_time = datetime.fromtimestamp(daily_file.stat().st_mtime)
        if file_time < cutoff:
            daily_file.unlink()
            cleaned.append(str(daily_file))
    
    # Clean diary files
    for diary_file in DIARY_DIR.glob("*.md"):
        file_time = datetime.fromtimestamp(diary_file.stat().st_mtime)
        if file_time < cutoff:
            diary_file.unlink()
            cleaned.append(str(diary_file))
    
    print(f"Cleaned {len(cleaned)} files older than {days} days")
    if cleaned:
        for f in cleaned:
            print(f"  - {f}")


# ============================================================================
# GIT-NOTES (COLD TIER) FUNCTIONS
# ============================================================================

def _load_git_notes_index() -> dict:
    """Load the git-notes index file."""
    if GIT_NOTES_INDEX.exists():
        try:
            with open(GIT_NOTES_INDEX) as f:
                return json.load(f)
        except Exception:
            pass
    return {"notes": {}}

def _save_git_notes_index(index: dict):
    """Save the git-notes index file."""
    with open(GIT_NOTES_INDEX, "w") as f:
        json.dump(index, f, indent=2)

def git_notes_add(key: str, value: str, tags: str = None):
    """Add a structured note to git-notes (COLD tier)."""
    # Parse tags
    tag_list = []
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    # Create note structure
    note = {
        "key": key,
        "value": value,
        "tags": tag_list,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Load index and add note
    index = _load_git_notes_index()
    index["notes"][key] = note
    _save_git_notes_index(index)
    
    print(f"✓ Added note: {key}")
    if tag_list:
        print(f"  Tags: {', '.join(tag_list)}")
    print(f"  Value: {value[:100]}{'...' if len(value) > 100 else ''}")

def git_notes_get(key: str):
    """Get a note by key from git-notes."""
    index = _load_git_notes_index()
    
    if key in index["notes"]:
        note = index["notes"][key]
        print(json.dumps(note, indent=2))
    else:
        print(f"Note not found: {key}")
        # Show similar keys
        similar = [k for k in index["notes"].keys() if key.lower() in k.lower()]
        if similar:
            print(f"Similar keys: {', '.join(similar[:5])}")

def git_notes_search(query: str):
    """Search notes by query in key, value, or tags."""
    index = _load_git_notes_index()
    query_lower = query.lower()
    
    results = []
    for key, note in index["notes"].items():
        # Search in key, value, and tags
        if (query_lower in key.lower() or 
            query_lower in note.get("value", "").lower() or
            any(query_lower in tag.lower() for tag in note.get("tags", []))):
            results.append({
                "key": key,
                "score": (
                    3 if query_lower in key.lower() else
                    2 if query_lower in " ".join(note.get("tags", [])).lower() else
                    1
                ),
                "note": note
            })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    if results:
        print(f"Found {len(results)} result(s) for '{query}':\n")
        for r in results:
            note = r["note"]
            print(f"## {note['key']}")
            print(f"   Value: {note['value'][:80]}{'...' if len(note['value']) > 80 else ''}")
            if note.get("tags"):
                print(f"   Tags: {', '.join(note['tags'])}")
            print(f"   Created: {note['created_at']}")
            print()
    else:
        print(f"No results found for '{query}'")

def git_notes_list(tag: str = None):
    """List all notes, optionally filtered by tag."""
    index = _load_git_notes_index()
    
    notes = list(index["notes"].values())
    
    # Filter by tag if provided
    if tag:
        tag_lower = tag.lower()
        notes = [n for n in notes if any(tag_lower in t.lower() for t in n.get("tags", []))]
    
    if notes:
        print(f"📋 {len(notes)} note(s):\n")
        for note in notes:
            tags_str = f" [{', '.join(note['tags'])}]" if note.get("tags") else ""
            print(f"• {note['key']}{tags_str}")
            print(f"  {note['value'][:60]}{'...' if len(note['value']) > 60 else ''}")
            print(f"  Created: {note['created_at'][:10]}")
            print()
    else:
        filter_msg = f" with tag '{tag}'" if tag else ""
        print(f"No notes found{filter_msg}")


def main():
    parser = argparse.ArgumentParser(
        description="Ultimate Unified Memory System CLI with Neuroscience Integration"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # search
    search_parser = subparsers.add_parser("search", help="Search all memory tiers")
    search_parser.add_argument("query", nargs="?", default="", help="Search query")
    search_parser.add_argument("--fast", action="store_true", 
                               help="Fast mode: cache only search")
    search_parser.add_argument("--full", action="store_true", 
                               help="Full mode: search all tiers (no optimization)")
    search_parser.add_argument("--hybrid", action="store_true", 
                               help="Hybrid mode: default - uses bloom, cache, mem0 first, then falls back")
    search_parser.add_argument("--weighted", action="store_true", 
                               help="Use importance-weighted search (Hippocampus)")
    search_parser.add_argument("--neuro", action="store_true", 
                               help="Use full neuroscience scoring (Hippocampus + Amygdala + VTA)")
    
    subparsers.add_parser("init", help="Initialize memory system")
    
    # neuroscience commands
    neuro_parser = subparsers.add_parser("neuro", help="Neuroscience operations")
    neuro_sub = neuro_parser.add_subparsers(dest="neuro_command")
    
    # neuro stats
    neuro_sub.add_parser("stats", help="Show neuroscience statistics")
    
    # neuro analyze
    neuro_analyze_parser = neuro_sub.add_parser("analyze", help="Analyze text for neuroscience")
    neuro_analyze_parser.add_argument("text", nargs="?", default="", help="Text to analyze")
    neuro_analyze_parser.add_argument("--full", action="store_true", help="Include full scoring breakdown")
    
    # legacy neuro-summary
    subparsers.add_parser("neuro-summary", help="Get neuroscience state summary (legacy)")
    
    analyze_parser = subparsers.add_parser("analyze", help="Analyze existing memories")
    analyze_parser.add_argument("--dry-run", action="store_true", help="Show what would be tagged")
    
    # wal
    wal_parser = subparsers.add_parser("wal", help="Write-Ahead Log operations")
    wal_sub = wal_parser.add_subparsers(dest="wal_command")
    wal_sub.add_parser("read", help="Read session state")
    wal_write_parser = wal_sub.add_parser("write", help="Write to WAL")
    wal_write_parser.add_argument("--category", required=True, help="Category")
    wal_write_parser.add_argument("--content", required=True, help="Content")
    wal_write_parser.add_argument("--importance", type=float, default=None, 
                          help="Importance score 0.0-1.0 (Hippocampus)")
    wal_write_parser.add_argument("--emotions", type=str, default=None,
                          help=f"Comma-separated emotions: {', '.join(VALID_EMOTIONS)}")
    wal_write_parser.add_argument("--value", dest="reward_type", type=str, default=None,
                          help=f"Reward type: {', '.join(VALID_REWARDS)}")
    wal_write_parser.add_argument("--intensity", type=float, default=0.5,
                          help="Reward intensity 0.0-1.0 (default: 0.5)")
    
    # inbox
    inbox_parser = subparsers.add_parser("inbox", help="Cron inbox operations")
    inbox_sub = inbox_parser.add_subparsers(dest="inbox_command")
    inbox_sub.add_parser("read", help="Read inbox")
    inbox_write_parser = inbox_sub.add_parser("write", help="Write to inbox")
    inbox_write_parser.add_argument("--content", required=True, help="Content")
    inbox_write_parser.add_argument("--importance", type=float, default=None,
                           help="Importance score 0.0-1.0 (Hippocampus)")
    inbox_write_parser.add_argument("--emotions", type=str, default=None,
                           help=f"Comma-separated emotions: {', '.join(VALID_EMOTIONS)}")
    inbox_write_parser.add_argument("--value", dest="reward_type", type=str, default=None,
                           help=f"Reward type: {', '.join(VALID_REWARDS)}")
    inbox_write_parser.add_argument("--intensity", type=float, default=0.5,
                           help="Reward intensity 0.0-1.0 (default: 0.5)")
    
    # diary
    diary_parser = subparsers.add_parser("diary", help="Personal diary")
    diary_sub = diary_parser.add_subparsers(dest="diary_command")
    diary_write_parser = diary_sub.add_parser("write", help="Write diary entry")
    diary_write_parser.add_argument("--content", required=True, help="Content")
    diary_write_parser.add_argument("--importance", type=float, default=None,
                           help="Importance score 0.0-1.0 (Hippocampus)")
    diary_write_parser.add_argument("--emotions", type=str, default=None,
                           help=f"Comma-separated emotions: {', '.join(VALID_EMOTIONS)}")
    diary_write_parser.add_argument("--value", dest="reward_type", type=str, default=None,
                           help=f"Reward type: {', '.join(VALID_REWARDS)}")
    diary_write_parser.add_argument("--intensity", type=float, default=0.5,
                           help="Reward intensity 0.0-1.0 (default: 0.5)")
    
    # diary search
    diary_search_parser = diary_sub.add_parser("search", help="Search diary entries")
    diary_search_parser.add_argument("query", help="Search query")
    
    # diary today
    diary_sub.add_parser("today", help="Show today's diary entry")
    
    # diary add (simple version)
    diary_add_parser = diary_sub.add_parser("add", help="Add simple diary entry")
    diary_add_parser.add_argument("content", help="Entry content (supports multi-word)")
    diary_add_parser.add_argument("--importance", type=float, default=0.5, help="Importance 0-1")
    diary_add_parser.add_argument("--emotions", type=str, help="Comma-separated emotions")
    
    # diary stats
    diary_sub.add_parser("stats", help="Show diary statistics")
    
    # stats
    subparsers.add_parser("stats", help="Show memory statistics")
    
    # cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean old memories")
    cleanup_parser.add_argument("--days", type=int, default=30, help="Days to keep")
    
    # git-notes (COLD tier)
    git_notes_parser = subparsers.add_parser("git-notes", help="Git-Notes COLD tier operations")
    git_notes_sub = git_notes_parser.add_subparsers(dest="git_notes_command")
    
    # git-notes add
    git_notes_add_parser = git_notes_sub.add_parser("add", help="Add a note")
    git_notes_add_parser.add_argument("--key", required=True, help="Note key")
    git_notes_add_parser.add_argument("--value", required=True, help="Note value")
    git_notes_add_parser.add_argument("--tags", type=str, default=None, help="Comma-separated tags")
    
    # git-notes get
    git_notes_get_parser = git_notes_sub.add_parser("get", help="Get a note by key")
    git_notes_get_parser.add_argument("key", help="Note key")
    
    # git-notes search
    git_notes_search_parser = git_notes_sub.add_parser("search", help="Search notes")
    git_notes_search_parser.add_argument("query", help="Search query")
    
    # git-notes list
    git_notes_list_parser = git_notes_sub.add_parser("list", help="List all notes")
    git_notes_list_parser.add_argument("--tag", type=str, default=None, help="Filter by tag")
    
    # error (ACC-Error integration)
    error_parser = subparsers.add_parser("error", help="ACC-Error pattern tracking")
    error_sub = error_parser.add_subparsers(dest="error_command")
    
    # error track
    error_track_parser = error_sub.add_parser("track", help="Track an error")
    error_track_parser.add_argument("description", help="Error description")
    error_track_parser.add_argument("--pattern", "-p", help="Pattern name")
    error_track_parser.add_argument("--context", "-c", help="Additional context")
    error_track_parser.add_argument("--mitigation", "-m", help="How to avoid")
    
    # error patterns
    error_sub.add_parser("patterns", help="Get active error patterns")
    
    # error corrections
    error_sub.add_parser("corrections", help="Get user corrections (lessons learned)")
    
    # error search
    error_search_parser = error_sub.add_parser("search", help="Search error patterns")
    error_search_parser.add_argument("query", help="Search query")
    
    # vestige (Cognitive memory)
    vestige_parser = subparsers.add_parser("vestige", help="Vestige cognitive memory")
    vestige_sub = vestige_parser.add_subparsers(dest="vestige_command")
    
    # vestige search
    vestige_search_parser = vestige_sub.add_parser("search", help="Search vestige memories")
    vestige_search_parser.add_argument("query", help="Search query")
    vestige_search_parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    
    # vestige ingest
    vestige_ingest_parser = vestige_sub.add_parser("ingest", help="Ingest content into memory")
    vestige_ingest_parser.add_argument("content", help="Content to remember")
    vestige_ingest_parser.add_argument("--tags", "-t", help="Comma-separated tags")
    vestige_ingest_parser.add_argument("--importance", "-i", type=float, default=0.5, help="Importance 0-1")
    
    # vestige promote
    vestige_promote_parser = vestige_sub.add_parser("promote", help="Strengthen a memory")
    vestige_promote_parser.add_argument("memory_id", help="Memory ID")
    
    # vestige demote
    vestige_demote_parser = vestige_sub.add_parser("demote", help="Weaken a memory")
    vestige_demote_parser.add_argument("memory_id", help="Memory ID")
    
    # vestige stats
    vestige_sub.add_parser("stats", help="Get vestige statistics")
    
    # habit (Basal Ganglia - habit learning)
    habit_parser = subparsers.add_parser("habit", help="Basal Ganglia habit learning")
    habit_sub = habit_parser.add_subparsers(dest="habit_command")
    
    # habit track
    habit_track_parser = habit_sub.add_parser("track", help="Track a habit (repeated action)")
    habit_track_parser.add_argument("action", help="The action/query to track")
    
    # habit list
    habit_sub.add_parser("list", help="List all learned habits")
    
    # habit disable
    habit_disable_parser = habit_sub.add_parser("disable", help="Disable a habit")
    habit_disable_parser.add_argument("habit_id", help="Habit ID to disable")
    
    # habit enable
    habit_enable_parser = habit_sub.add_parser("enable", help="Enable a previously disabled habit")
    habit_enable_parser.add_argument("habit_id", help="Habit ID to enable")
    
    # habit delete
    habit_delete_parser = habit_sub.add_parser("delete", help="Delete a habit permanently")
    habit_delete_parser.add_argument("habit_id", help="Habit ID to delete")
    
    # habit stats
    habit_sub.add_parser("stats", help="Get habit learning statistics")
    
    # insula (internal state)
    if insula:
        state_parser = subparsers.add_parser("state", help="Insula internal state management")
        state_sub = state_parser.add_subparsers(dest="state_command")
        
        # state set
        state_set_parser = state_sub.add_parser("set", help="Set internal state value")
        state_set_parser.add_argument("key_value", help="Key=value pair (e.g., energy=low)")
        
        # state show
        state_sub.add_parser("show", help="Show current internal state")
        
        # state detect
        state_detect_parser = state_sub.add_parser("detect", help="Detect state from conversation")
        state_detect_parser.add_argument("conversation", nargs="?", default="", help="Conversation text to analyze")
    
    # file search (optional fast tier using fd/rg)
    file_parser = subparsers.add_parser("file", help="Fast file search using fd/rg")
    file_sub = file_parser.add_subparsers(dest="file_command")
    
    # file search - by name
    file_name_parser = file_sub.add_parser("search", help="Search files by name")
    file_name_parser.add_argument("pattern", help="File name pattern")
    file_name_parser.add_argument("--path", default=None, help="Path to search (default: memory)")
    
    # file search - by content
    file_content_parser = file_sub.add_parser("content", help="Search file contents")
    file_content_parser.add_argument("query", help="Content query")
    file_content_parser.add_argument("--path", default=None, help="Path to search (default: memory)")
    file_content_parser.add_argument("--limit", type=int, default=50, help="Max results")
    
    # file search - fast combined
    file_fast_parser = file_sub.add_parser("fast", help="Fast combined search (name + content)")
    file_fast_parser.add_argument("query", help="Search query")
    file_fast_parser.add_argument("--path", default=None, help="Path to search (default: memory)")
    file_fast_parser.add_argument("--limit", type=int, default=30, help="Max results")
    
    # file status - check fd/rg availability
    file_sub.add_parser("status", help="Check fd/rg availability")
    
    # kg (knowledge graph)
    kg_parser = subparsers.add_parser("kg", help="Knowledge Graph operations")
    kg_sub = kg_parser.add_subparsers(dest="kg_command")
    
    # kg add
    kg_add_parser = kg_sub.add_parser("add", help="Add a fact to knowledge graph")
    kg_add_parser.add_argument("--entity", required=True, help="Entity name")
    kg_add_parser.add_argument("--category", required=True, help="Fact category")
    kg_add_parser.add_argument("--fact", required=True, help="The fact statement")
    
    # kg search
    kg_search_parser = kg_sub.add_parser("search", help="Search knowledge graph")
    kg_search_parser.add_argument("query", help="Search query")
    
    # kg list
    kg_sub.add_parser("list", help="List all entities")
    
    # improve (Self-Improving integration)
    improve_parser = subparsers.add_parser("improve", help="Self-improvement logging")
    improve_sub = improve_parser.add_subparsers(dest="improve_command")
    
    # improve error
    improve_error_parser = improve_sub.add_parser("error", help="Log an error")
    improve_error_parser.add_argument("text", help="Error description")
    improve_error_parser.add_argument("--context", "-c", help="Context or details")
    
    # improve correct
    improve_correct_parser = improve_sub.add_parser("correct", help="Log a user correction")
    improve_correct_parser.add_argument("text", help="Correction text")
    improve_correct_parser.add_argument("--context", "-c", help="Context or details")
    
    # improve request
    improve_request_parser = improve_sub.add_parser("request", help="Log a feature request")
    improve_request_parser.add_argument("text", help="Feature description")
    improve_request_parser.add_argument("--reason", "-r", help="Reason or justification")
    
    # improve better
    improve_better_parser = improve_sub.add_parser("better", help="Log a best practice")
    improve_better_parser.add_argument("text", help="Best practice description")
    improve_better_parser.add_argument("--context", "-c", help="Context or details")
    
    # improve list
    improve_sub.add_parser("list", help="List all learnings")
    
    # reflect (Self-Reflection)
    reflect_parser = subparsers.add_parser("reflect", help="Self-reflection operations")
    reflect_sub = reflect_parser.add_subparsers(dest="reflect_command")
    
    # reflect task
    reflect_task_parser = reflect_sub.add_parser("task", help="Reflect on a completed task")
    reflect_task_parser.add_argument("task", help="Task description")
    reflect_task_parser.add_argument("--outcome", required=True, help="Outcome (success/partial/failure)")
    reflect_task_parser.add_argument("--notes", default="", help="Additional notes")
    
    # reflect daily
    reflect_sub.add_parser("daily", help="Perform daily review")
    
    # reflect weekly
    reflect_sub.add_parser("weekly", help="Perform weekly review")
    
    # reflect list
    reflect_list_parser = reflect_sub.add_parser("list", help="List recent reflections")
    reflect_list_parser.add_argument("--days", type=int, default=7, help="Number of days to look back")
    
    args = parser.parse_args()
    
    # Track search queries as habits (Basal Ganglia automatic learning)
    if args.command == "search" and args.query and basal_ganglia:
        basal_ganglia.track_habit(args.query)
    
    if args.command == "init":
        init_files()
    elif args.command == "search":
        if hasattr(args, 'fast') and args.fast:
            # FAST MODE: cache only
            results = hybrid_search(args.query, mode="fast")
            print(json.dumps(results, indent=2))
        elif hasattr(args, 'full') and args.full:
            # FULL MODE: all tiers
            results = hybrid_search(args.query, mode="full")
            print(json.dumps(results, indent=2))
        elif hasattr(args, 'neuro') and args.neuro:
            results = search_with_neuroscience_scoring(args.query)
            print(json.dumps(results, indent=2))
        elif hasattr(args, 'weighted') and args.weighted:
            results = search_with_importance_weighting(args.query)
            print(json.dumps(results, indent=2))
        else:
            # Default: HYBRID mode
            results = hybrid_search(args.query, mode="hybrid")
            print(json.dumps(results, indent=2))
    elif args.command == "neuro":
        if args.neuro_command == "stats":
            stats_data = get_neuroscience_stats()
            print(json.dumps(stats_data, indent=2))
        elif args.neuro_command == "analyze":
            if not args.text:
                print("Error: Please provide text to analyze")
                print("Usage: overkill-memory-system neuro analyze \"your text here\"")
            else:
                analysis = analyze_text_neuroscience(args.text, include_scoring=args.full if hasattr(args, 'full') else True)
                print(json.dumps(analysis, indent=2))
    elif args.command == "neuro-summary":
        summary = get_neuroscience_summary()
        print(json.dumps(summary, indent=2))
    elif args.command == "analyze":
        results = analyze_existing_memories()
        print(json.dumps(results, indent=2))
    elif args.command == "wal":
        if args.wal_command == "read":
            wal_read()
        elif args.wal_command == "write":
            wal_write(
                args.category, 
                args.content,
                importance=args.importance,
                emotions=args.emotions,
                reward_type=args.reward_type,
                reward_intensity=args.intensity
            )
    elif args.command == "inbox":
        if args.inbox_command == "read":
            inbox_read()
        elif args.inbox_command == "write":
            inbox_write(
                args.content,
                importance=args.importance,
                emotions=args.emotions,
                reward_type=args.reward_type,
                reward_intensity=args.intensity
            )
    elif args.command == "diary":
        if args.diary_command == "write":
            diary_write(
                args.content,
                importance=args.importance,
                emotions=args.emotions,
                reward_type=args.reward_type,
                reward_intensity=args.intensity
            )
        elif args.diary_command == "search":
            if jarvis_diary:
                jarvis_diary.cli_search(args.query)
            else:
                print("Error: jarvis_diary module not available")
        elif args.diary_command == "today":
            if jarvis_diary:
                jarvis_diary.cli_today()
            else:
                print("Error: jarvis_diary module not available")
        elif args.diary_command == "add":
            if jarvis_diary:
                emotions = args.emotions.split(",") if args.emotions else None
                jarvis_diary.cli_add(args.content, args.importance, emotions)
            else:
                print("Error: jarvis_diary module not available")
        elif args.diary_command == "stats":
            if jarvis_diary:
                jarvis_diary.cli_stats()
            else:
                print("Error: jarvis_diary module not available")
    elif args.command == "stats":
        stats()
    elif args.command == "cleanup":
        cleanup(args.days)
    elif args.command == "git-notes":
        if args.git_notes_command == "add":
            git_notes_add(args.key, args.value, args.tags)
        elif args.git_notes_command == "get":
            git_notes_get(args.key)
        elif args.git_notes_command == "search":
            git_notes_search(args.query)
        elif args.git_notes_command == "list":
            git_notes_list(args.tag)
    elif args.command == "error":
        if acc_error is None:
            print("Error: acc_error module not available")
            print("Make sure acc_error.py is in the same directory as cli.py")
        elif args.error_command == "track":
            result = acc_error.track_error(
                args.description,
                pattern=args.pattern,
                context=args.context,
                mitigation=args.mitigation
            )
            print(json.dumps(result, indent=2))
        elif args.error_command == "patterns":
            result = acc_error.get_patterns()
            print(json.dumps(result, indent=2))
        elif args.error_command == "corrections":
            result = acc_error.get_corrections()
            print(json.dumps(result, indent=2))
        elif args.error_command == "search":
            result = acc_error.search(args.query)
            print(json.dumps(result, indent=2))
    elif args.command == "vestige":
        if vestige is None:
            print("Error: vestige module not available")
            print("Make sure vestige.py is in the same directory as cli.py")
            print("Install vestige-mcp: https://github.com/samvallad33/vestige")
        elif args.vestige_command == "search":
            result = vestige.search(args.query, args.limit)
            print(json.dumps(result, indent=2))
        elif args.vestige_command == "ingest":
            tags = args.tags.split(',') if args.tags else None
            result = vestige.ingest(args.content, tags, args.importance)
            print(json.dumps(result, indent=2))
        elif args.vestige_command == "promote":
            result = vestige.promote(args.memory_id)
            print(json.dumps(result, indent=2))
        elif args.vestige_command == "demote":
            result = vestige.demote(args.memory_id)
            print(json.dumps(result, indent=2))
        elif args.vestige_command == "stats":
            result = vestige.stats()
            print(json.dumps(result, indent=2))
    elif args.command == "habit":
        if basal_ganglia is None:
            print("Error: basal_ganglia module not available")
            print("Make sure basal_ganglia.py is in the same directory as cli.py")
        elif args.habit_command == "track":
            result = basal_ganglia.track_habit(args.action)
            print(json.dumps(result, indent=2))
        elif args.habit_command == "list":
            result = basal_ganglia.list_habits()
            print(json.dumps(result, indent=2))
        elif args.habit_command == "disable":
            result = basal_ganglia.disable_habit(args.habit_id)
            print(json.dumps(result, indent=2))
        elif args.habit_command == "enable":
            result = basal_ganglia.enable_habit(args.habit_id)
            print(json.dumps(result, indent=2))
        elif args.habit_command == "delete":
            result = basal_ganglia.delete_habit(args.habit_id)
            print(json.dumps(result, indent=2))
        elif args.habit_command == "stats":
            result = basal_ganglia.get_habit_stats()
            print(json.dumps(result, indent=2))
    
    elif args.command == "state" and insula:
        state = insula.get_state()
        
        if args.state_command == "set":
            # Parse key=value
            key_value = args.key_value
            if "=" not in key_value:
                print("Error: Use format key=value (e.g., energy=low)")
                sys.exit(1)
            
            key, value = key_value.split("=", 1)
            
            # Map CLI keys to function params
            key_map = {
                "energy": "energy",
                "curiosity": "curiosity", 
                "mood": "mood",
                "fatigue": "fatigue"
            }
            
            if key not in key_map:
                print(f"Error: Invalid key '{key}'. Valid keys: {', '.join(key_map.keys())}")
                sys.exit(1)
            
            # Convert fatigue to float
            kwargs = {}
            if key == "fatigue":
                try:
                    kwargs[key_map[key]] = float(value)
                except ValueError:
                    print("Error: fatigue must be a number between 0.0 and 1.0")
                    sys.exit(1)
            else:
                kwargs[key_map[key]] = value
            
            result = state.set_state(**kwargs)
            print(json.dumps(result, indent=2))
        
        elif args.state_command == "show":
            result = state.get_state()
            print(json.dumps(result, indent=2))
        
        elif args.state_command == "detect":
            if not args.conversation:
                # Read from recent conversation (WAL/session)
                session_state = MEMORY_BASE / "memory" / "SESSION-STATE.md"
                if session_state.exists():
                    args.conversation = session_state.read_text()[:2000]
                else:
                    print("Error: No conversation text provided")
                    sys.exit(1)
            
            detected = state.detect_state_from_context(args.conversation)
            current = state.get_state()
            print("Detected:", json.dumps(detected, indent=2))
            print("Current state:", json.dumps(current, indent=2))
    
    elif args.command == "file":
        if file_search is None:
            print("Error: file_search module not available")
            print("Make sure file_search.py is in the same directory as cli.py")
        elif args.file_command == "status":
            has_tools = file_search.has_fd_rg()
            print(json.dumps({
                "fd_available": shutil.which("fd") is not None,
                "rg_available": shutil.which("rg") is not None,
                "fast_mode_available": has_tools,
                "memory_path": str(MEMORY_BASE)
            }, indent=2))
        elif args.file_command == "search":
            search_path = Path(args.path) if args.path else MEMORY_BASE
            results = file_search.search_by_name(args.pattern, search_path)
            print(file_search.format_search_results(results))
        elif args.file_command == "content":
            search_path = Path(args.path) if args.path else MEMORY_BASE
            results = file_search.search_by_content(args.query, search_path, args.limit)
            print(file_search.format_search_results(results))
        elif args.file_command == "fast":
            search_path = Path(args.path) if args.path else MEMORY_BASE
            results = file_search.fast_file_search(args.query, search_path, args.limit)
            print(file_search.format_search_results(results))
    
    elif args.command == "kg":
        if knowledge_graph is None:
            print("Error: knowledge_graph module not available")
            print("Make sure knowledge_graph.py is in the same directory as cli.py")
        elif args.kg_command == "add":
            knowledge_graph.cli_add(args.entity, args.category, args.fact)
        elif args.kg_command == "search":
            knowledge_graph.cli_search(args.query)
        elif args.kg_command == "list":
            knowledge_graph.cli_list()
    
    elif args.command == "improve":
        if self_improving is None:
            print("Error: self_improving module not available")
            print("Make sure self_improving.py is in the same directory as cli.py")
        elif args.improve_command == "error":
            self_improving.cli_log_error(args.text, args.context or "")
        elif args.improve_command == "correct":
            self_improving.cli_log_correction(args.text, args.context or "")
        elif args.improve_command == "request":
            self_improving.cli_log_feature_request(args.text, args.reason or "")
        elif args.improve_command == "better":
            self_improving.cli_log_best_practice(args.text, args.context or "")
        elif args.improve_command == "list":
            self_improving.cli_list_learnings()
    
    elif args.command == "reflect":
        if self_reflection is None:
            print("Error: self_reflection module not available")
            print("Make sure self_reflection.py is in the same directory as cli.py")
        elif args.reflect_command == "task":
            result = self_reflection.cli_reflect_task(args.task, args.outcome, args.notes)
            print(json.dumps(result, indent=2))
        elif args.reflect_command == "daily":
            result = self_reflection.cli_daily_review()
            print(json.dumps(result, indent=2))
        elif args.reflect_command == "weekly":
            result = self_reflection.cli_weekly_review()
            print(json.dumps(result, indent=2))
        elif args.reflect_command == "list":
            result = self_reflection.cli_list_reflections(args.days)
            print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

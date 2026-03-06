#!/usr/bin/env python3
"""
Advanced Multi-Store Memory System

A sophisticated memory architecture inspired by cognitive science, featuring:
- Episodic Memory: Events with emotional context and decay
- Semantic Memory: Facts and knowledge extracted from episodes  
- Procedural Memory: Learned behavioral patterns and correlations
- Working Memory: Current context and attention mechanism

Implements Ebbinghaus forgetting curve, consolidation, and reflection.
"""

import json
import math
import os
import re
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class MemorySystem:
    """Advanced multi-store memory system for autonomous AI consciousness."""
    
    def __init__(self, base_dir: str = "memory_store", config: Optional[Dict] = None):
        """Initialize the memory system.
        
        Args:
            base_dir: Directory to store memory files
            config: Configuration options (decay rates, capacities, etc.)
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Default configuration
        self.config = {
            "working_memory_capacity": 50,
            "episodic_decay_rate": 0.5,  # Base decay rate per day
            "semantic_reinforcement_threshold": 3,  # Repetitions needed for semantic extraction
            "consolidation_importance_threshold": 0.3,
            "forget_threshold": 0.1,
            "max_recall_results": 100
        }
        if config:
            self.config.update(config)
        
        # Memory stores
        self.episodic_path = self.base_dir / "episodic.json"
        self.semantic_path = self.base_dir / "semantic.json"
        self.procedural_path = self.base_dir / "procedural.json"
        self.working_path = self.base_dir / "working.json"
        self.meta_path = self.base_dir / "meta.json"
        
        # Initialize empty stores if they don't exist
        for path in [self.episodic_path, self.semantic_path, self.procedural_path, 
                     self.working_path]:
            if not path.exists():
                with open(path, 'w') as f:
                    json.dump([], f)
        
        # Initialize meta file as dict
        if not self.meta_path.exists():
            with open(self.meta_path, 'w') as f:
                json.dump({}, f)
    
    def _load_store(self, path: Path) -> List[Dict]:
        """Load a memory store from disk."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_store(self, path: Path, data: List[Dict]) -> None:
        """Save a memory store to disk."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _get_timestamp(self) -> float:
        """Get current UTC timestamp."""
        return datetime.now(timezone.utc).timestamp()
    
    def _calculate_decay(self, timestamp: float, decay_rate: float, reinforcement_count: int = 0) -> float:
        """Calculate memory strength using Ebbinghaus forgetting curve.
        
        Strength = e^(-t * decay_rate / (1 + reinforcement_count))
        
        Args:
            timestamp: When memory was created/last accessed
            decay_rate: Base decay rate
            reinforcement_count: Number of times memory was reinforced
            
        Returns:
            Current memory strength (0-1)
        """
        days_passed = (self._get_timestamp() - timestamp) / 86400.0  # seconds to days
        effective_decay = decay_rate / (1 + reinforcement_count * 0.5)
        return math.exp(-days_passed * effective_decay)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for keyword matching."""
        # Convert to lowercase, split on non-alphanumeric, filter empty
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [t for t in tokens if len(t) > 2]  # Filter short words
    
    def _calculate_tf_idf_score(self, query_tokens: List[str], content: str, corpus: List[str]) -> float:
        """Calculate TF-IDF-like relevance score."""
        content_tokens = self._tokenize(content)
        if not content_tokens:
            return 0.0
        
        score = 0.0
        corpus_size = len(corpus)
        
        for token in query_tokens:
            # Term frequency in this document
            tf = content_tokens.count(token) / len(content_tokens)
            
            # Document frequency in corpus
            df = sum(1 for doc in corpus if token in self._tokenize(doc))
            
            # Inverse document frequency
            idf = math.log(corpus_size / max(1, df)) if corpus_size > 0 else 0
            
            score += tf * idf
        
        return score
    
    def encode(self, event: str, emotion: str = "neutral", importance: float = 0.5, 
               context: Optional[Dict] = None) -> str:
        """Store a new episodic memory.
        
        Args:
            event: Description of the event
            emotion: Emotional valence (e.g., "happy", "sad", "frustrated", "excited")
            importance: Importance score 0-1
            context: Additional context metadata
            
        Returns:
            Memory ID
        """
        memory_id = str(uuid.uuid4())
        timestamp = self._get_timestamp()
        
        memory = {
            "id": memory_id,
            "timestamp": timestamp,
            "content": event,
            "emotion": emotion,
            "importance": max(0.0, min(1.0, importance)),  # Clamp to [0,1]
            "decay_rate": self.config["episodic_decay_rate"],
            "reinforcement_count": 0,
            "last_accessed": timestamp,
            "context": context or {}
        }
        
        # Add to episodic memory
        episodic = self._load_store(self.episodic_path)
        episodic.append(memory)
        self._save_store(self.episodic_path, episodic)
        
        # Add to working memory (maintain capacity)
        working = self._load_store(self.working_path)
        working.append(memory)
        if len(working) > self.config["working_memory_capacity"]:
            working = working[-self.config["working_memory_capacity"]:]
        self._save_store(self.working_path, working)
        
        return memory_id
    
    def recall(self, query: str, memory_type: str = "all", limit: int = 10) -> List[Dict]:
        """Semantic search across memories.
        
        Args:
            query: Search query
            memory_type: "episodic", "semantic", "procedural", "working", or "all"
            limit: Maximum number of results
            
        Returns:
            List of relevant memories, sorted by relevance
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        
        results = []
        stores_to_search = []
        
        if memory_type == "all":
            stores_to_search = ["episodic", "semantic", "procedural", "working"]
        else:
            stores_to_search = [memory_type]
        
        for store_type in stores_to_search:
            if store_type == "episodic":
                memories = self._load_store(self.episodic_path)
                corpus = [m["content"] for m in memories]
            elif store_type == "semantic":
                memories = self._load_store(self.semantic_path)
                corpus = [m["content"] for m in memories]
            elif store_type == "procedural":
                memories = self._load_store(self.procedural_path)
                corpus = [f"{m['action']} -> {m['outcome']}" for m in memories]
            elif store_type == "working":
                memories = self._load_store(self.working_path)
                corpus = [m["content"] for m in memories]
            else:
                continue
            
            for memory in memories:
                if store_type == "procedural":
                    content = f"{memory['action']} -> {memory['outcome']}"
                else:
                    content = memory["content"]
                
                # Calculate relevance score
                tf_idf_score = self._calculate_tf_idf_score(query_tokens, content, corpus)
                
                # For episodic memories, factor in decay
                if store_type == "episodic":
                    strength = self._calculate_decay(
                        memory["timestamp"], 
                        memory["decay_rate"], 
                        memory["reinforcement_count"]
                    )
                    score = tf_idf_score * strength
                else:
                    score = tf_idf_score
                
                if score > 0:
                    memory_with_score = memory.copy()
                    memory_with_score["relevance_score"] = score
                    memory_with_score["memory_type"] = store_type
                    results.append(memory_with_score)
                
                # Update last_accessed for episodic memories
                if store_type == "episodic" and score > 0:
                    memory["last_accessed"] = self._get_timestamp()
        
        # Sort by relevance and apply limit
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        limited_results = results[:min(limit, self.config["max_recall_results"])]
        
        # Save updated episodic memories (last_accessed updates)
        if "episodic" in stores_to_search:
            episodic = self._load_store(self.episodic_path)
            self._save_store(self.episodic_path, episodic)
        
        return limited_results
    
    def consolidate(self) -> Dict[str, Any]:
        """Consolidate memories: decay, reinforce, and extract semantic knowledge.
        
        Returns:
            Consolidation statistics
        """
        stats = {
            "memories_processed": 0,
            "memories_decayed": 0,
            "memories_forgotten": 0,
            "semantic_extracted": 0,
            "procedural_updated": 0
        }
        
        # Load all stores
        episodic = self._load_store(self.episodic_path)
        semantic = self._load_store(self.semantic_path)
        procedural = self._load_store(self.procedural_path)
        
        # Process episodic memories
        surviving_episodic = []
        pattern_counts = defaultdict(int)
        
        for memory in episodic:
            stats["memories_processed"] += 1
            
            # Calculate current strength
            strength = self._calculate_decay(
                memory["timestamp"],
                memory["decay_rate"],
                memory["reinforcement_count"]
            )
            
            # Check if memory survives
            if strength < self.config["forget_threshold"]:
                stats["memories_forgotten"] += 1
                continue
            elif strength < 0.5:
                stats["memories_decayed"] += 1
            
            # Track patterns for semantic extraction
            tokens = self._tokenize(memory["content"])
            for token in tokens:
                pattern_counts[token] += 1
            
            surviving_episodic.append(memory)
        
        # Extract new semantic memories from patterns
        semantic_tokens = set()
        for sem_mem in semantic:
            semantic_tokens.update(self._tokenize(sem_mem["content"]))
        
        for token, count in pattern_counts.items():
            if (count >= self.config["semantic_reinforcement_threshold"] and 
                token not in semantic_tokens):
                
                semantic_memory = {
                    "id": str(uuid.uuid4()),
                    "timestamp": self._get_timestamp(),
                    "content": token,
                    "category": "pattern",
                    "strength": min(1.0, count / 10.0),  # Normalize strength
                    "source_count": count,
                    "cross_references": []
                }
                semantic.append(semantic_memory)
                stats["semantic_extracted"] += 1
        
        # Update procedural memories based on recent outcomes
        # (This would need integration with the actual activity logging system)
        
        # Save consolidated memories
        self._save_store(self.episodic_path, surviving_episodic)
        self._save_store(self.semantic_path, semantic)
        self._save_store(self.procedural_path, procedural)
        
        # Update metadata
        meta = {
            "last_consolidation": self._get_timestamp(),
            "consolidation_stats": stats
        }
        with open(self.meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
        
        return stats
    
    def reflect(self) -> Dict[str, Any]:
        """Meta-cognition: analyze memory patterns and generate insights.
        
        Returns:
            Reflection insights
        """
        episodic = self._load_store(self.episodic_path)
        semantic = self._load_store(self.semantic_path)
        procedural = self._load_store(self.procedural_path)
        
        insights = {
            "memory_summary": {
                "episodic_count": len(episodic),
                "semantic_count": len(semantic),
                "procedural_count": len(procedural)
            },
            "emotional_patterns": defaultdict(int),
            "temporal_patterns": {},
            "importance_distribution": {},
            "decay_analysis": {}
        }
        
        if not episodic:
            return insights
        
        # Emotional pattern analysis
        for memory in episodic:
            insights["emotional_patterns"][memory["emotion"]] += 1
        
        # Temporal pattern analysis
        timestamps = [m["timestamp"] for m in episodic]
        if timestamps:
            earliest = min(timestamps)
            latest = max(timestamps)
            timespan_days = (latest - earliest) / 86400.0
            insights["temporal_patterns"] = {
                "timespan_days": timespan_days,
                "memories_per_day": len(episodic) / max(1, timespan_days),
                "most_recent": datetime.fromtimestamp(latest, timezone.utc).isoformat(),
                "oldest": datetime.fromtimestamp(earliest, timezone.utc).isoformat()
            }
        
        # Importance distribution
        importance_values = [m["importance"] for m in episodic]
        if importance_values:
            insights["importance_distribution"] = {
                "mean": sum(importance_values) / len(importance_values),
                "high_importance_count": sum(1 for i in importance_values if i > 0.7),
                "low_importance_count": sum(1 for i in importance_values if i < 0.3)
            }
        
        # Decay analysis
        current_time = self._get_timestamp()
        strong_memories = 0
        weak_memories = 0
        
        for memory in episodic:
            strength = self._calculate_decay(
                memory["timestamp"],
                memory["decay_rate"],
                memory["reinforcement_count"]
            )
            if strength > 0.5:
                strong_memories += 1
            elif strength < 0.2:
                weak_memories += 1
        
        insights["decay_analysis"] = {
            "strong_memories": strong_memories,
            "weak_memories": weak_memories,
            "consolidation_needed": weak_memories > strong_memories
        }
        
        return insights
    
    def forget(self, threshold: float = None) -> int:
        """Remove memories below importance threshold.
        
        Args:
            threshold: Importance threshold (uses config default if None)
            
        Returns:
            Number of memories removed
        """
        if threshold is None:
            threshold = self.config["forget_threshold"]
        
        episodic = self._load_store(self.episodic_path)
        before_count = len(episodic)
        
        # Keep only memories above threshold or with high reinforcement
        surviving = []
        for memory in episodic:
            strength = self._calculate_decay(
                memory["timestamp"],
                memory["decay_rate"],
                memory["reinforcement_count"]
            )
            
            if (memory["importance"] >= threshold or 
                strength >= threshold or 
                memory["reinforcement_count"] > 2):
                surviving.append(memory)
        
        self._save_store(self.episodic_path, surviving)
        return before_count - len(surviving)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics for dashboard display.
        
        Returns:
            Comprehensive memory statistics
        """
        episodic = self._load_store(self.episodic_path)
        semantic = self._load_store(self.semantic_path)
        procedural = self._load_store(self.procedural_path)
        working = self._load_store(self.working_path)
        
        # Load metadata
        try:
            with open(self.meta_path, 'r') as f:
                meta = json.load(f)
                # Ensure meta is a dict, not a list
                if not isinstance(meta, dict):
                    meta = {}
        except (FileNotFoundError, json.JSONDecodeError):
            meta = {}
        
        current_time = self._get_timestamp()
        
        # Analyze episodic memory health
        strong_count = 0
        total_importance = 0
        emotion_dist = defaultdict(int)
        
        for memory in episodic:
            strength = self._calculate_decay(
                memory["timestamp"],
                memory["decay_rate"],
                memory["reinforcement_count"]
            )
            if strength > 0.5:
                strong_count += 1
            
            total_importance += memory["importance"]
            emotion_dist[memory["emotion"]] += 1
        
        avg_importance = total_importance / max(1, len(episodic))
        
        # Calculate memory efficiency
        total_memories = len(episodic) + len(semantic) + len(procedural)
        working_utilization = len(working) / self.config["working_memory_capacity"]
        
        return {
            "store_sizes": {
                "episodic": len(episodic),
                "semantic": len(semantic),
                "procedural": len(procedural),
                "working": len(working),
                "total": total_memories
            },
            "memory_health": {
                "strong_episodic_memories": strong_count,
                "average_importance": round(avg_importance, 3),
                "working_memory_utilization": round(working_utilization, 2),
                "consolidation_needed": strong_count < len(episodic) * 0.3
            },
            "emotional_distribution": dict(emotion_dist),
            "system_config": self.config,
            "last_consolidation": meta.get("last_consolidation"),
            "last_consolidation_stats": meta.get("consolidation_stats")
        }
    
    def add_procedural_memory(self, action: str, outcome: str, context: Optional[Dict] = None,
                            mood: Optional[str] = None) -> str:
        """Add a procedural memory (action -> outcome mapping).
        
        Args:
            action: The action taken
            outcome: The result/outcome
            context: Additional context
            mood: Mood during the action
            
        Returns:
            Memory ID
        """
        procedural = self._load_store(self.procedural_path)
        
        memory_id = str(uuid.uuid4())
        memory = {
            "id": memory_id,
            "timestamp": self._get_timestamp(),
            "action": action,
            "outcome": outcome,
            "context": context or {},
            "mood": mood,
            "success_score": 1.0 if "success" in outcome.lower() else 0.5,
            "reinforcement_count": 1
        }
        
        # Check if similar action exists and reinforce it
        for existing in procedural:
            if existing["action"].lower() == action.lower():
                existing["reinforcement_count"] += 1
                existing["timestamp"] = self._get_timestamp()
                self._save_store(self.procedural_path, procedural)
                return existing["id"]
        
        procedural.append(memory)
        self._save_store(self.procedural_path, procedural)
        return memory_id


def main():
    """CLI interface for memory system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Multi-Store Memory System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Encode command
    encode_parser = subparsers.add_parser("encode", help="Store a new memory")
    encode_parser.add_argument("event", help="Event description")
    encode_parser.add_argument("--emotion", default="neutral", help="Emotional valence")
    encode_parser.add_argument("--importance", type=float, default=0.5, help="Importance (0-1)")
    
    # Recall command
    recall_parser = subparsers.add_parser("recall", help="Search memories")
    recall_parser.add_argument("query", help="Search query")
    recall_parser.add_argument("--type", default="all", 
                              choices=["episodic", "semantic", "procedural", "working", "all"])
    recall_parser.add_argument("--limit", type=int, default=5, help="Max results")
    
    # Consolidate command
    subparsers.add_parser("consolidate", help="Run memory consolidation")
    
    # Stats command
    subparsers.add_parser("stats", help="Show memory statistics")
    
    # Reflect command
    subparsers.add_parser("reflect", help="Run reflection analysis")
    
    # Forget command
    forget_parser = subparsers.add_parser("forget", help="Remove low-importance memories")
    forget_parser.add_argument("--threshold", type=float, help="Importance threshold")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize memory system
    memory = MemorySystem()
    
    if args.command == "encode":
        memory_id = memory.encode(args.event, args.emotion, args.importance)
        print(f"Encoded memory: {memory_id}")
        
    elif args.command == "recall":
        results = memory.recall(args.query, args.type, args.limit)
        print(f"Found {len(results)} memories:")
        for i, mem in enumerate(results, 1):
            score = mem.get("relevance_score", 0)
            mem_type = mem.get("memory_type", "unknown")
            content = mem.get("content", mem.get("action", ""))
            print(f"{i}. [{mem_type}] {content} (score: {score:.3f})")
            
    elif args.command == "consolidate":
        stats = memory.consolidate()
        print("Consolidation completed:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    elif args.command == "stats":
        stats = memory.get_stats()
        print("Memory System Statistics:")
        print(json.dumps(stats, indent=2))
        
    elif args.command == "reflect":
        insights = memory.reflect()
        print("Reflection Insights:")
        print(json.dumps(insights, indent=2))
        
    elif args.command == "forget":
        removed = memory.forget(args.threshold)
        print(f"Removed {removed} memories")


if __name__ == "__main__":
    main()
# SimpleMem Python Wrapper for OpenClaw

import os
import json
from pathlib import Path

# Try to import simplemem
try:
    from simplemem import SimpleMemSystem, set_config, SimpleMemConfig
    SIMPLEMEM_AVAILABLE = True
except ImportError:
    SIMPLEMEM_AVAILABLE = False


class SimpleMemWrapper:
    """Wrapper para usar SimpleMem desde OpenClaw"""
    
    def __init__(self, data_dir=None, api_key=None):
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.system = None
        
        if SIMPLEMEM_AVAILABLE and self.api_key:
            try:
                config = SimpleMemConfig()
                config.openai_api_key = self.api_key
                config.lancedb_path = str(self.data_dir / "lancedb")
                set_config(config)
                self.system = SimpleMemSystem()
                print(f"SimpleMem initialized at {self.data_dir}")
            except Exception as e:
                print(f"SimpleMem init failed: {e}")
                self.system = None
    
    def add(self, content, user_id="osiris", metadata=None):
        """Agregar un recuerdo"""
        if self.system and self.api_key and self.api_key != "test":
            try:
                self.system.add(content, user_id=user_id)
                return True
            except Exception as e:
                print(f"SimpleMem add failed: {e}")
        
        # Fallback to JSON storage
        memories_file = self.data_dir / "memories.json"
        if memories_file.exists():
            with open(memories_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
        else:
            memories = {}
        
        if user_id not in memories:
            memories[user_id] = []
        
        memory = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": str(Path(__file__).stat().st_mtime)
        }
        memories[user_id].append(memory)
        
        with open(memories_file, 'w', encoding='utf-8') as f:
            json.dump(memories, f, ensure_ascii=False, indent=2)
        return True
    
    def retrieve(self, query, user_id="osiris", limit=5):
        """Recuperar recuerdos relacionados"""
        if self.system and self.api_key and self.api_key != "test":
            try:
                results = self.system.retrieve(query, user_id=user_id, top_k=limit)
                return [{"content": r.content, "score": r.score} for r in results]
            except Exception as e:
                print(f"SimpleMem retrieve failed: {e}")
        
        # Fallback to JSON search
        memories_file = self.data_dir / "memories.json"
        if not memories_file.exists():
            return []
        
        with open(memories_file, 'r', encoding='utf-8') as f:
            memories = json.load(f)
        
        user_memories = memories.get(user_id, [])
        query_words = set(query.lower().split())
        
        results = []
        for mem in user_memories:
            content_words = set(mem["content"].lower().split())
            score = len(query_words & content_words)
            if score > 0:
                results.append({**mem, "score": score})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def search(self, query, limit=10):
        """Búsqueda global"""
        return self.retrieve(query, user_id="osiris", limit=limit)
    
    def stats(self):
        """Estadísticas de memoria"""
        memories_file = self.data_dir / "memories.json"
        if memories_file.exists():
            with open(memories_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            total = sum(len(v) for v in memories.values())
            return {
                "total_memories": total,
                "categories": {k: len(v) for k, v in memories.items()},
                "simplemem_active": self.system is not None
            }
        return {"total_memories": 0, "simplemem_active": self.system is not None}


# Funciones CLI simples
if __name__ == "__main__":
    import sys
    
    # Get API key from args or env
    api_key = os.getenv("OPENAI_API_KEY", "")
    wrapper = SimpleMemWrapper(api_key=api_key)
    
    if len(sys.argv) < 2:
        print("Usage: python simplemem.py <add|search|retrieve|stats> [args]")
        print("Environment: OPENAI_API_KEY required for full SimpleMem features")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "add":
        content = " ".join(sys.argv[2:])
        wrapper.add(content)
        print(f"Added: {content}")
    
    elif command == "search" or command == "retrieve":
        query = " ".join(sys.argv[2:])
        results = wrapper.retrieve(query)
        for r in results:
            print(f"[{r.get('score', 0)}] {r['content']}")
    
    elif command == "stats":
        print(wrapper.stats())

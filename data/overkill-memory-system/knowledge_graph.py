#!/usr/bin/env python3
"""
Knowledge Graph Module
Simple entity-fact storage system for atomic knowledge
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Path for knowledge storage
KNOWLEDGE_DIR = Path.home() / ".openclaw" / "memory" / "knowledge"
ITEMS_FILE = KNOWLEDGE_DIR / "items.json"

# Ensure directory exists
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)


def _load_items() -> dict:
    """Load items from JSON file"""
    if ITEMS_FILE.exists():
        try:
            return json.loads(ITEMS_FILE.read_text())
        except json.JSONDecodeError:
            return {"entities": {}, "facts": []}
    return {"entities": {}, "facts": []}


def _save_items(data: dict):
    """Save items to JSON file"""
    ITEMS_FILE.write_text(json.dumps(data, indent=2))


def add_fact(entity: str, category: str, fact: str) -> dict:
    """
    Add an atomic fact to the knowledge graph.
    
    Args:
        entity: The entity name (e.g., "Python", "Cody")
        category: The category of fact (e.g., "skill", "preference", "project")
        fact: The fact statement
    
    Returns:
        Dictionary with success status and added fact
    """
    data = _load_items()
    
    # Normalize entity
    entity_lower = entity.lower()
    
    # Add entity to index if not exists
    if entity_lower not in data["entities"]:
        data["entities"][entity_lower] = {
            "name": entity,
            "categories": set(),
            "fact_count": 0
        }
    
    # Add category to entity
    if category not in data["entities"][entity_lower]["categories"]:
        data["entities"][entity_lower]["categories"].add(category)
    
    # Create fact entry
    fact_entry = {
        "id": len(data["facts"]) + 1,
        "entity": entity,
        "category": category,
        "fact": fact,
        "timestamp": datetime.now().isoformat()
    }
    
    data["facts"].append(fact_entry)
    data["entities"][entity_lower]["fact_count"] += 1
    
    # Convert sets to lists for JSON
    for e in data["entities"].values():
        e["categories"] = list(e["categories"])
    
    _save_items(data)
    
    return {
        "success": True,
        "fact": fact_entry
    }


def search_kg(query: str) -> list:
    """
    Search facts in the knowledge graph.
    
    Args:
        query: Search query (matches against entity, category, or fact)
    
    Returns:
        List of matching facts
    """
    data = _load_items()
    query_lower = query.lower()
    
    results = []
    for fact in data["facts"]:
        # Search in entity, category, and fact text
        if (query_lower in fact["entity"].lower() or
            query_lower in fact["category"].lower() or
            query_lower in fact["fact"].lower()):
            results.append(fact)
    
    return results


def list_entities() -> list:
    """
    List all entities in the knowledge graph.
    
    Returns:
        List of entity dictionaries with name, categories, and fact count
    """
    data = _load_items()
    
    entities = []
    for entity_key, entity_data in data["entities"].items():
        entities.append({
            "name": entity_data["name"],
            "categories": list(entity_data.get("categories", [])),
            "fact_count": entity_data.get("fact_count", 0)
        })
    
    # Sort by fact count descending
    entities.sort(key=lambda x: x["fact_count"], reverse=True)
    
    return entities


def get_facts_by_entity(entity: str) -> list:
    """Get all facts for a specific entity"""
    data = _load_items()
    entity_lower = entity.lower()
    
    return [f for f in data["facts"] if f["entity"].lower() == entity_lower]


def get_facts_by_category(category: str) -> list:
    """Get all facts in a specific category"""
    data = _load_items()
    category_lower = category.lower()
    
    return [f for f in data["facts"] if f["category"].lower() == category_lower]


# CLI helper functions
def cli_add(entity: str, category: str, fact: str):
    """CLI wrapper for add_fact"""
    result = add_fact(entity, category, fact)
    if result["success"]:
        print(f"Added fact for '{entity}' in category '{category}': {fact}")
    return result


def cli_search(query: str):
    """CLI wrapper for search_kg"""
    results = search_kg(query)
    if results:
        print(f"Found {len(results)} result(s):\n")
        for i, fact in enumerate(results, 1):
            print(f"{i}. [{fact['category']}] {fact['entity']}: {fact['fact']}")
            print(f"   Added: {fact['timestamp']}\n")
    else:
        print(f"No results found for: {query}")
    return results


def cli_list():
    """CLI wrapper for list_entities"""
    entities = list_entities()
    if entities:
        print(f"Entities in knowledge graph:\n")
        for ent in entities:
            print(f"- {ent['name']} ({ent['fact_count']} facts)")
            if ent['categories']:
                print(f"  Categories: {', '.join(ent['categories'])}")
    else:
        print("No entities in knowledge graph yet.")
    return entities


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: knowledge_graph.py <command> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        if len(sys.argv) < 5:
            print("Usage: knowledge_graph.py add <entity> <category> <fact>")
            sys.exit(1)
        cli_add(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: knowledge_graph.py search <query>")
            sys.exit(1)
        cli_search(sys.argv[2])
    elif cmd == "list":
        cli_list()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

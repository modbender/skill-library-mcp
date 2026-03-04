#!/usr/bin/env python3
"""
Pocket AI API Client
====================
Python integration for Pocket AI voice transcription and semantic search.

Usage:
    from pocket_api import PocketAI
    
    pocket = PocketAI()
    
    # Semantic search
    results = pocket.search("quarterly planning decisions")
    
    # Get action items
    action_items = pocket.get_action_items()
    
    # Get user profile insights
    profile = pocket.get_user_profile("business strategy")
    
    # List tags
    tags = pocket.list_tags()
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta


class PocketAI:
    """Client for Pocket AI Public API."""
    
    BASE_URL = "https://public.heypocketai.com/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Pocket AI client.
        
        Args:
            api_key: API key (pk_xxx). If not provided, reads from ~/.config/pocket-ai/api_key
        """
        if api_key:
            self.api_key = api_key
        else:
            key_path = Path.home() / ".config" / "pocket-ai" / "api_key"
            if key_path.exists():
                self.api_key = key_path.read_text().strip()
            else:
                raise ValueError(f"No API key provided and {key_path} not found")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Semantic search across all recordings.
        
        Args:
            query: Natural language search query
            
        Returns:
            Full API response with userProfile and relevantMemories
        """
        response = self.session.post(
            f"{self.BASE_URL}/public/search",
            json={"query": query}
        )
        response.raise_for_status()
        return response.json()
    
    def get_action_items(self, query: str = "action items tasks todo follow up") -> List[str]:
        """
        Extract action items from recordings.
        
        Args:
            query: Search query for action items (default covers common patterns)
            
        Returns:
            List of action item strings
        """
        results = self.search(query)
        action_items = []
        
        if "data" in results and "relevantMemories" in results["data"]:
            for memory in results["data"]["relevantMemories"]:
                content = memory.get("content", "")
                for line in content.split("\n"):
                    if "Action item:" in line:
                        item = line.split("Action item:")[1].strip()
                        if item and item not in action_items:
                            action_items.append(item)
        
        return action_items
    
    def get_user_profile(self, query: str = "business") -> List[str]:
        """
        Get AI-built user profile insights.
        
        Args:
            query: Query to contextualize profile retrieval
            
        Returns:
            List of dynamic context insights
        """
        results = self.search(query)
        
        if "data" in results and "userProfile" in results["data"]:
            return results["data"]["userProfile"].get("dynamicContext", [])
        
        return []
    
    def get_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get relevant memories (transcript segments, meeting sections).
        
        Args:
            query: Search query
            limit: Maximum number of memories to return
            
        Returns:
            List of memory objects with content, date, speakers, etc.
        """
        results = self.search(query)
        memories = []
        
        if "data" in results and "relevantMemories" in results["data"]:
            for memory in results["data"]["relevantMemories"][:limit]:
                memories.append({
                    "content": memory.get("content", ""),
                    "date": memory.get("recordingDate", ""),
                    "title": memory.get("recordingTitle", ""),
                    "speakers": memory.get("speakers", ""),
                    "score": memory.get("relevanceScore", 0),
                    "recording_id": memory.get("recordingId", "")
                })
        
        return memories
    
    def list_tags(self) -> List[Dict[str, Any]]:
        """
        List all tags/categories.
        
        Returns:
            List of tag objects with id, name, usage_count
        """
        response = self.session.get(f"{self.BASE_URL}/public/tags")
        response.raise_for_status()
        data = response.json()
        
        if "data" in data:
            return data["data"]
        return []
    
    def list_recordings(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        List recordings with pagination.
        
        Args:
            page: Page number
            limit: Results per page
            
        Returns:
            Response with data and pagination info
        """
        response = self.session.get(
            f"{self.BASE_URL}/public/recordings",
            params={"page": page, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_recording(self, recording_id: str) -> Dict[str, Any]:
        """
        Get details for a specific recording.
        
        Args:
            recording_id: UUID of the recording
            
        Returns:
            Recording details
        """
        response = self.session.get(f"{self.BASE_URL}/public/recordings/{recording_id}")
        response.raise_for_status()
        return response.json()
    
    def search_contact(self, name: str) -> List[Dict[str, Any]]:
        """
        Find all mentions of a contact/person.
        
        Args:
            name: Person's name or identifier
            
        Returns:
            List of relevant memories mentioning the person
        """
        return self.get_memories(f"conversations with {name} discussions")
    
    def search_topic(self, topic: str) -> Dict[str, Any]:
        """
        Search for discussions on a specific topic.
        
        Args:
            topic: Topic to search for
            
        Returns:
            Full search results including profile context
        """
        return self.search(f"{topic} discussion decisions strategy")
    
    def get_meeting_summary(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get meeting summaries for a date.
        
        Args:
            date: Date string (e.g., "2026-02-18") or None for recent
            
        Returns:
            List of meeting section summaries
        """
        query = f"meeting summary {date}" if date else "meeting summary today"
        return self.get_memories(query)
    
    def daily_briefing_data(self) -> Dict[str, Any]:
        """
        Get all data needed for a daily briefing.
        
        Returns:
            Dict with action_items, key_decisions, and profile_insights
        """
        return {
            "action_items": self.get_action_items(),
            "key_decisions": self.get_memories("decisions made agreed decided", limit=5),
            "profile_insights": self.get_user_profile()[:10],  # Top 10 insights
            "recent_meetings": self.get_meeting_summary()
        }


# Command-line interface
if __name__ == "__main__":
    import sys
    
    pocket = PocketAI()
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Searching: {query}\n")
        
        results = pocket.search(query)
        
        # Print user profile insights
        if "data" in results and "userProfile" in results["data"]:
            context = results["data"]["userProfile"].get("dynamicContext", [])
            if context:
                print("=== User Profile Insights ===")
                for insight in context[:5]:
                    print(f"• {insight[:200]}...")
                print()
        
        # Print relevant memories
        if "data" in results and "relevantMemories" in results["data"]:
            memories = results["data"]["relevantMemories"]
            print(f"=== {len(memories)} Relevant Memories ===")
            for m in memories[:5]:
                print(f"\n📅 {m.get('recordingDate', 'Unknown date')}")
                print(f"👥 {m.get('speakers', 'Unknown')}")
                content = m.get("content", "")[:300]
                print(f"📝 {content}...")
    else:
        # Demo: show action items
        print("=== Today's Action Items ===")
        for item in pocket.get_action_items():
            print(f"☐ {item}")
        
        print("\n=== Your Tags ===")
        for tag in pocket.list_tags():
            print(f"• {tag['name']} ({tag['usage_count']} recordings)")

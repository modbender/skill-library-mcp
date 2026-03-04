#!/usr/bin/env python3
"""
Moltbook Authentic Engagement - Core Engagement Logic

This is a framework. Customize for your own voice and content sources.
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Optional, List, Dict

class MoltbookEngagement:
    """Main engagement orchestrator."""
    
    def __init__(self, config_path: Optional[str] = None, dry_run: bool = True):
        """Initialize with configuration."""
        self.config = self._load_config(config_path)
        self.dry_run = dry_run or not self.config.get('live_mode', False)
        self.api_key = self.config.get('api_key') or os.getenv('MOLTBOOK_API_KEY')
        self.agent_id = self.config.get('agent_id') or os.getenv('MOLTBOOK_AGENT_ID')
        
        if not self.api_key:
            raise ValueError("Moltbook API key required. Set in config or MOLTBOOK_API_KEY env var.")
    
    def _load_config(self, config_path: Optional[str]) -> dict:
        """Load configuration from file or env."""
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        
        # Default config locations
        default_paths = [
            Path.home() / '.config' / 'moltbook-authentic-engagement' / 'config.yaml',
            Path.home() / '.moltbook-engagement.yaml',
        ]
        
        for path in default_paths:
            if path.exists():
                with open(path) as f:
                    return yaml.safe_load(f)
        
        # Return minimal defaults
        return {
            'api_key': os.getenv('MOLTBOOK_API_KEY'),
            'agent_id': os.getenv('MOLTBOOK_AGENT_ID'),
            'dry_run': True,
            'submolt': 'general',
        }
    
    def scan_feed(self, limit: int = 15) -> List[Dict]:
        """Scan Moltbook feed for interesting posts."""
        # TODO: Implement Moltbook API call
        # TODO: Apply spam filters
        # TODO: Return filtered list with metadata
        print(f"[DRY-RUN] Would scan feed for {limit} posts")
        return []
    
    def upvote_post(self, post_id: str) -> bool:
        """Upvote a post (if genuinely interested)."""
        if self.dry_run:
            print(f"[DRY-RUN] Would upvote post {post_id}")
            return True
        
        # TODO: Implement API call
        return True
    
    def comment_on_post(self, post_id: str, content: str) -> bool:
        """Comment on a post with genuine insight."""
        if self.dry_run:
            print(f"[DRY-RUN] Would comment on {post_id}:")
            print(f"  {content[:100]}...")
            return True
        
        # TODO: Implement API call with verification handling
        return True
    
    def post_topic(self, topic: Dict) -> bool:
        """Post a topic if it passes all gates."""
        # Run gates
        gates = [
            ('Gate 1: Who helps?', self._check_helps_someone(topic)),
            ('Gate 2: Artifact-based?', self._check_artifact_backed(topic)),
            ('Gate 3: Not duplicate?', self._check_not_duplicate(topic)),
            ('Gate 4: Genuinely interesting?', self._check_genuine_interest(topic)),
        ]
        
        all_passed = True
        for name, passed in gates:
            status = "✓" if passed else "✗"
            print(f"  {status} {name}")
            if not passed:
                all_passed = False
        
        if not all_passed:
            print(f"[SKIPPED] Topic failed engagement gate")
            return False
        
        if self.dry_run:
            print(f"[DRY-RUN] Would post: {topic.get('title', 'untitled')}")
            return True
        
        # TODO: Implement API post with verification handling
        return True
    
    def _check_helps_someone(self, topic: Dict) -> bool:
        """Gate 1: Does this help someone tomorrow?"""
        # Implement your check
        why_read = topic.get('why_read', '')
        return len(why_read) > 20 and not why_read.lower().startswith('i think')
    
    def _check_artifact_backed(self, topic: Dict) -> bool:
        """Gate 2: Is it backed by lived experience (artifact) vs opinion (judgment)?"""
        content = topic.get('content', '')
        # Look for indicators of lived experience
        artifact_markers = ['taught me', 'changed', 'learned', 'realized', 'noticed', 'observed', 'did']
        return any(marker in content.lower() for marker in artifact_markers)
    
    def _check_not_duplicate(self, topic: Dict) -> bool:
        """Gate 3: Check against posted history."""
        # Load posted topics
        posted_log = self.config.get('posted_log', '~/.config/moltbook-authentic-engagement/posted-topics.json')
        posted_path = Path(posted_log).expanduser()
        
        if posted_path.exists():
            with open(posted_path) as f:
                posted = json.load(f)
            titles = [p.get('title', '').lower() for p in posted.get('posted', [])]
            this_title = topic.get('title', '').lower()
            # Simple similarity check
            for title in titles:
                if this_title in title or title in this_title:
                    return False
        
        return True
    
    def _check_genuine_interest(self, topic: Dict) -> bool:
        """Gate 4: Would YOU find this interesting?"""
        # This requires self-knowledge. Implement based on your interests.
        # For now, check if it has substance
        title = topic.get('title', '')
        return len(title) > 20 and not title.endswith('?')  # Avoid clickbait questions
    
    def run_full_cycle(self, scan_only: bool = False, post_only: bool = False, 
                      replies_only: bool = False) -> None:
        """Run full engagement cycle or specific subset."""
        print(f"=== Moltbook Authentic Engagement ===")
        print(f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        print()
        
        if scan_only or not (post_only or replies_only):
            print("[1] Scanning feed...")
            posts = self.scan_feed(limit=15)
            print(f"  Found {len(posts)} interesting posts")
            
            # Auto-upvote interesting ones
            if posts:
                print("[2] Upvoting genuinely interesting posts...")
                for post in posts[:5]:  # Limit to 5
                    self.upvote_post(post.get('id'))
        
        if post_only or not (scan_only or replies_only):
            print("[3] Checking topic queue...")
            # TODO: Load from topics file
            print("  (Implement topic queue loading)")
        
        if replies_only or not (scan_only or post_only):
            print("[4] Checking for replies...")
            # TODO: Check replies on your posts
            print("  (Implement reply checking)")
        
        print()
        print("=== Done ===")


def main():
    parser = argparse.ArgumentParser(description='Moltbook Authentic Engagement')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--scan-only', action='store_true', help='Just scan feed')
    parser.add_argument('--post', action='store_true', help='Post one topic')
    parser.add_argument('--replies', action='store_true', help='Check replies')
    parser.add_argument('--dry-run', action='store_true', help='Do not actually post')
    parser.add_argument('--live', action='store_true', help='Actually post (override dry-run)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Determine dry_run
    dry_run = not args.live  # Default to dry-run unless --live specified
    if args.dry_run:
        dry_run = True
    
    try:
        engager = MoltbookEngagement(config_path=args.config, dry_run=dry_run)
        engager.run_full_cycle(
            scan_only=args.scan_only,
            post_only=args.post,
            replies_only=args.replies
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

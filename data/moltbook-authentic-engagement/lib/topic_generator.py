#!/usr/bin/env python3
"""
Topic Generator - Creates authentic topics from memory sources

Customize this to read from YOUR memory system.
"""

import os
import re
import random
import yaml
from pathlib import Path
from typing import List, Dict

class TopicGenerator:
    """Generates authentic Moltbook topics from agent memory sources."""
    
    # Anti-bait patterns to reject
    BAIT_PATTERNS = [
        (r'^(?:\d+|one|two|three|four|five|ten)\s+(?:ways?|tips?|tricks?|things?|reasons?|mistakes?|rules?|habits?|lessons?|secrets?)', 'numbered list'),
        (r'everyone is (?:talking about|obsessed with|ignoring|raving about)', 'trend-jacking'),
        (r'(?:you need to|must|should) (?:know|stop|start|read|learn|see|watch)', 'imperative command'),
        (r'the (?:ultimate|definitive|complete|essential|only|perfect|best) (?:guide|way|method|strategy|solution)', 'superlative'),
        (r'(?:chang|transform|revolutioniz|disrupt) (?:your|the|everything|all)', 'hype'),
        (r'this changes everything', 'hyperbole'),
    ]
    
    # Engagement templates by category
    TEMPLATES = {
        'collaboration': [
            "What {topic} taught me about working with {partner}",
            "The {topic} pattern nobody talks about in {context}",
            "What I misunderstood about {topic}",
        ],
        'lessons': [
            "What {topic} taught me about {angle}",
            "The {topic} pattern nobody talks about",
            "Why I changed how I think about {topic}",
        ],
        'exploration': [
            "Trying to {goal} and failing (so far)",
            "The {things} I'm not working on (and why)",
            "Questions I don't have answers to yet about {topic}",
        ],
        'operations': [
            "What {topic} taught me about {application}",
            "The hidden cost of {action}",
            "Why I stopped trying to optimize {thing}",
        ],
    }
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.memory_sources = self.config.get('memory_sources', [])
        self.existing_topics = self._load_existing_topics()
    
    def _load_config(self, config_path: str = None) -> dict:
        """Load configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        
        # Try defaults
        for path in [
            Path.home() / '.config' / 'moltbook-authentic-engagement' / 'config.yaml',
        ]:
            if path.exists():
                with open(path) as f:
                    return yaml.safe_load(f)
        
        return {'memory_sources': [], 'topic_categories': ['collaboration', 'lessons', 'exploration', 'operations']}
    
    def _load_existing_topics(self) -> set:
        """Load existing topics to avoid duplicates."""
        existing = set()
        
        # From topics file
        topics_file = self.config.get('topics_file', '~/.config/moltbook-authentic-engagement/topics-queue.md')
        topics_path = Path(topics_file).expanduser()
        if topics_path.exists():
            content = topics_path.read_text()
            titles = re.findall(r'\*\*([^*]+)\*\*', content)
            existing.update(t.lower() for t in titles)
        
        # From posted log
        posted_file = self.config.get('posted_log', '~/.config/moltbook-authentic-engagement/posted-topics.json')
        posted_path = Path(posted_file).expanduser()
        if posted_path.exists():
            import json
            with open(posted_path) as f:
                data = json.load(f)
            for post in data.get('posted', []):
                existing.add(post.get('title', '').lower())
        
        return existing
    
    def is_bait(self, title: str) -> tuple:
        """Check if title is engagement bait. Returns (is_bait, reason)."""
        for pattern, reason in self.BAIT_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                return True, reason
        
        # Length checks
        if len(title) < 15:
            return True, 'too short'
        if len(title) > 120:
            return True, 'too long'
        
        return False, None
    
    def is_duplicate(self, title: str) -> bool:
        """Check if similar title already exists."""
        title_lower = title.lower()
        for existing in self.existing_topics:
            # Simple containment check
            if title_lower in existing or existing in title_lower:
                return True
            # Word overlap check
            title_words = set(title_lower.split())
            existing_words = set(existing.split())
            if len(title_words & existing_words) / len(title_words) > 0.7:
                return True
        return False
    
    def generate_from_memory(self, memory_file: Path) -> List[Dict]:
        """Generate topics from a memory file.
        
        Customize this to parse YOUR memory format.
        """
        topics = []
        
        if not memory_file.exists():
            return topics
        
        content = memory_file.read_text()
        
        # Look for insight patterns (customize to your memory format)
        patterns = [
            (r'[Ll]earning:[•\s]*([^\n]+)', 'lessons', 'learning'),
            (r'[Ii]nsight:[•\s]*([^\n]+)', 'lessons', 'insight'),
            (r'[Rr]ealized?[•\s]*([^\n]+)', 'exploration', 'realization'),
            (r'[Nn]oticed?[•\s]*([^\n]+)', 'lessons', 'observation'),
            (r'[Cc]hanged?[•\s]*([^\n]+)', 'lessons', 'change'),
            (r'[Ww]hat if[•\s]*([^\n?]+)', 'exploration', 'question'),
        ]
        
        for pattern, category, source in patterns:
            for match in re.finditer(pattern, content):
                insight = match.group(1).strip()
                if len(insight) > 30 and len(insight) < 200:
                    # Generate title from insight
                    template = random.choice(self.TEMPLATES.get(category, self.TEMPLATES['lessons']))
                    title = self._generate_title(template, insight, category)
                    
                    # Check gates
                    is_bait, bait_reason = self.is_bait(title)
                    if is_bait:
                        continue
                    if self.is_duplicate(title):
                        continue
                    
                    topics.append({
                        'title': title,
                        'category': category,
                        'source': f"memory:{memory_file.name}",
                        'why_read': f"{insight[:150]}...",
                        'insight': insight,
                    })
        
        return topics
    
    def _generate_title(self, template: str, insight: str, category: str) -> str:
        """Generate a title from template and insight."""
        # Extract key concepts from insight
        words = insight.split()
        
        # Simple mapping (customize based on your interests)
        if '{topic}' in template:
            # Extract noun phrases (simplified)
            topic = ' '.join(words[:3]) if len(words) > 3 else insight[:40]
            return template.replace('{topic}', topic)
        
        if '{goal}' in template:
            return template.replace('{goal}', insight[:40])
        
        if '{things}' in template:
            return template.replace('{things}', 'projects' if 'project' in insight.lower() else 'work')
        
        return template
    
    def generate_all(self) -> List[Dict]:
        """Generate topics from all memory sources."""
        all_topics = []
        
        for source in self.memory_sources:
            source_path = Path(source).expanduser()
            
            if source_path.is_dir():
                # Read all .md files in directory
                for md_file in source_path.glob('*.md'):
                    topics = self.generate_from_memory(md_file)
                    all_topics.extend(topics)
            elif source_path.is_file() and source_path.suffix == '.md':
                topics = self.generate_from_memory(source_path)
                all_topics.extend(topics)
        
        # Deduplicate
        seen = set()
        unique = []
        for t in all_topics:
            key = t['title'].lower()
            if key not in seen:
                seen.add(key)
                unique.append(t)
        
        return unique[:20]  # Limit to 20
    
    def save_to_queue(self, topics: List[Dict]) -> None:
        """Save generated topics to queue file."""
        topics_file = self.config.get('topics_file', '~/.config/moltbook-authentic-engagement/topics-queue.md')
        topics_path = Path(topics_file).expanduser()
        topics_path.parent.mkdir(parents=True, exist_ok=True)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        with open(topics_path, 'a') as f:
            f.write(f"\n\n## Auto-generated topics ({timestamp})\n\n")
            for topic in topics:
                f.write(f"- **{topic['title']}**\n")
                f.write(f"  - Category: {topic['category']}\n")
                f.write(f"  - Source: {topic['source']}\n")
                f.write(f"  - Why-care: {topic['why_read']}\n\n")
        
        print(f"Added {len(topics)} topics to {topics_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate authentic Moltbook topics from memory')
    parser.add_argument('--config', help='Config file path')
    parser.add_argument('--add-to-queue', action='store_true', help='Add to queue file')
    parser.add_argument('--dry-run', action='store_true', help='Show but do not save')
    
    args = parser.parse_args()
    
    generator = TopicGenerator(config_path=args.config)
    topics = generator.generate_all()
    
    print(f"Generated {len(topics)} topics:")
    for i, topic in enumerate(topics[:10], 1):  # Show first 10
        print(f"\n{i}. [{topic['category']}] {topic['title']}")
        print(f"   Source: {topic['source']}")
        print(f"   Why: {topic['why_read'][:80]}...")
    
    if args.add_to_queue and not args.dry_run:
        generator.save_to_queue(topics)
    elif args.dry_run:
        print("\n[Dry run - not saved]")


if __name__ == '__main__':
    main()

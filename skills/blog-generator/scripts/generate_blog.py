#!/usr/bin/env python3
"""
Generate Blog - Cron-ready script for automated blog post generation.

This script is designed to run via cron jobs and generates blog posts
from journal analysis with proper error handling and logging.
"""

import argparse
import json
import sys
from pathlib import Path

# Import blog generator
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from scripts.blog_generator import BlogGenerator
except ImportError:
    print("Error: Could not import BlogGenerator.", file=sys.stderr)
    sys.exit(1)


def main():
    default_humanizer = Path("/Users/ghost/Downloads/humanizer-1.0.0")
    default_visual_explainer = Path("/Users/ghost/.openclaw/workspace/skills/visual-explainer-main")
    parser = argparse.ArgumentParser(description="Generate X-format blog articles as HTML. Humanizer runs between generations.")
    parser.add_argument("--days", type=int, default=7, help="Days of journal history to analyze (default: 7)")
    parser.add_argument("--max-topics", type=int, default=3, help="Maximum topics to generate (default: 3)")
    parser.add_argument("--format", choices=["x", "classic"], default="x", help="Article format: x (default) or classic")
    parser.add_argument("--humanizer-path", type=str, default=str(default_humanizer), help="Humanizer run between generations")
    parser.add_argument("--no-humanize", action="store_true", help="Skip humanizer")
    parser.add_argument("--visual-explainer-path", type=str, default=str(default_visual_explainer), help="Header from visual-explainer")
    parser.add_argument("--output-dir", "-o", type=str, default="", help="Directory to save HTML articles")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--openclaw-home", type=str, help="OpenClaw home directory (default: ~/.openclaw)")
    args = parser.parse_args()
    
    openclaw_home = Path(args.openclaw_home) if args.openclaw_home else Path.home() / ".openclaw"
    humanizer_path = Path(args.humanizer_path)
    visual_explainer_path = Path(args.visual_explainer_path)
    output_dir = Path(args.output_dir) if args.output_dir else None
    
    generator = BlogGenerator(openclaw_home, output_dir=output_dir)
    
    try:
        # Scan journal entries
        topics = generator.scan_journal_entries(days_back=args.days)
        
        if not topics:
            if args.json:
                print(json.dumps({
                    "status": "no_topics",
                    "message": "No topics found in journal entries",
                    "days_analyzed": args.days
                }))
            else:
                print(f"No topics found in journal entries from the last {args.days} days.")
            return 0
        
        # Identify high-value topics
        high_value_topics = generator.identify_high_value_topics(topics, max_topics=args.max_topics)
        
        if not high_value_topics:
            if args.json:
                print(json.dumps({
                    "status": "no_high_value_topics",
                    "message": "No high-value topics identified",
                    "topics_found": len(topics)
                }))
            else:
                print(f"Found {len(topics)} topics but none met the high-value threshold.")
            return 0
        
        # Generate blog posts
        generated_posts = []
        for topic in high_value_topics:
            try:
                blog_post = generator.generate_blog_post(topic, format=args.format)
                if not getattr(args, "no_humanize", False) and humanizer_path.exists():
                    lines = blog_post.split("\n")
                    title_lines, body_lines, footer_lines = [], [], []
                    state = "title"
                    for line in lines:
                        if state == "title" and line.strip().startswith("# "):
                            title_lines.append(line)
                            state = "body"
                            continue
                        if state == "body" and line.strip() == "---":
                            footer_lines.append(line)
                            state = "footer"
                            continue
                        (title_lines if state == "title" else body_lines if state == "body" else footer_lines).append(line)
                    body_text = "\n".join(body_lines).strip()
                    if body_text:
                        humanized = generator.run_humanizer(body_text, humanizer_path)
                        if humanized:
                            blog_post = "\n".join(title_lines) + "\n\n" + humanized + "\n\n" + "\n".join(footer_lines)
                blog_file = generator.save_blog_post(blog_post, topic, visual_explainer_path=visual_explainer_path)
                generated_posts.append({
                    'topic': {
                        'type': topic.get('type'),
                        'value_score': topic.get('value_score', 0),
                        'source': topic.get('source')
                    },
                    'blog_file': str(blog_file),
                    'title': blog_post.split('\n')[0].replace('# ', '')
                })
            except Exception as e:
                print(f"Error generating blog post for topic: {e}", file=sys.stderr)
                continue
        
        if not generated_posts:
            if args.json:
                print(json.dumps({
                    "status": "generation_failed",
                    "message": "Failed to generate any blog posts",
                    "topics_attempted": len(high_value_topics)
                }))
            else:
                print("Failed to generate any blog posts.")
            return 1
        
        if args.json:
            output = {
                'status': 'success',
                'topics_found': len(topics),
                'high_value_topics': len(high_value_topics),
                'blog_posts_generated': len(generated_posts),
                'posts': generated_posts
            }
            print(json.dumps(output, indent=2))
        else:
            print("=" * 70)
            print("BLOG POST GENERATION REPORT")
            print("=" * 70)
            print(f"\nJournal entries analyzed: Last {args.days} days")
            print(f"Topics found: {len(topics)}")
            print(f"High-value topics identified: {len(high_value_topics)}")
            print(f"Blog posts generated: {len(generated_posts)}\n")
            
            for i, post in enumerate(generated_posts, 1):
                print(f"{i}. {post['title']}")
                print(f"   Saved to: {post['blog_file']}")
                print(f"   Value Score: {post['topic']['value_score']}\n")
            
            print("=" * 70)
        
        return 0
    
    except Exception as e:
        error_msg = f"Error generating blog posts: {e}"
        if args.json:
            print(json.dumps({
                "status": "error",
                "error": str(e)
            }))
        else:
            print(error_msg, file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

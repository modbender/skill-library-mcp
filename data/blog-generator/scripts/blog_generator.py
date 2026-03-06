#!/usr/bin/env python3
"""
Blog Generator - Analyzes journal entries and chat history to identify high-value topics
and generate blog posts.

Scans journal entries, chat history, and recent activity to find interesting topics,
researches search volume/keywords, and generates blog posts.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import subprocess
import html as html_module


class BlogGenerator:
    def __init__(self, openclaw_home: Path, output_dir: Optional[Path] = None):
        self.openclaw_home = openclaw_home
        self.journal_dir = openclaw_home / "journal"
        self.blogs_dir = Path(output_dir) if output_dir else openclaw_home / "blogs"
        self.blogs_dir.mkdir(parents=True, exist_ok=True)
        
        # High-value keywords related to OpenClaw
        self.high_value_keywords = [
            "openclaw gateway",
            "openclaw setup",
            "openclaw configuration",
            "openclaw skills",
            "openclaw troubleshooting",
            "gateway auth",
            "gateway restart",
            "gateway disconnected",
            "agent swarm",
            "subagent",
            "cursor chat history",
            "openclaw cron",
            "openclaw automation",
        ]
        
    def scan_journal_entries(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scan journal entries from the last N days for interesting topics."""
        topics = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        if not self.journal_dir.exists():
            return topics
        
        # Scan chat analysis files
        for journal_file in self.journal_dir.glob("chat_analysis_*.md"):
            try:
                file_time = self._extract_timestamp_from_filename(journal_file.name)
                if file_time and file_time >= cutoff_date:
                    content = journal_file.read_text()
                    extracted = self._extract_topics_from_content(content, journal_file.name)
                    topics.extend(extracted)
            except Exception as e:
                print(f"Error reading {journal_file}: {e}", file=sys.stderr)
        
        # Scan other markdown files in journal
        for journal_file in self.journal_dir.rglob("*.md"):
            if "chat_analysis" in journal_file.name:
                continue  # Already processed
            try:
                stat = journal_file.stat()
                file_time = datetime.fromtimestamp(stat.st_mtime)
                if file_time >= cutoff_date:
                    content = journal_file.read_text()
                    extracted = self._extract_topics_from_content(content, journal_file.name)
                    topics.extend(extracted)
            except Exception as e:
                continue
        
        return topics

    def scan_skill_dirs(self, skill_paths: List[Path]) -> List[Dict[str, Any]]:
        """Build topics from skill directories (SKILL.md + optional README). One topic per skill."""
        topics = []
        for path in skill_paths:
            path = Path(path)
            if not path.exists():
                continue
            skill_md = path / "SKILL.md"
            readme = path / "README.md"
            name = path.name.replace("-", " ").replace("_", " ").title()
            description = ""
            body = ""
            if skill_md.exists():
                text = skill_md.read_text()
                # Frontmatter description (YAML)
                fm_match = re.search(r"description:\s*['\"]?([^'\n]+?)['\"]?(?:\n|$)", text[:2000], re.IGNORECASE | re.DOTALL)
                if fm_match:
                    description = fm_match.group(1).strip().replace("\n", " ")[:300]
                else:
                    for line in text.split("\n")[:25]:
                        if line.strip().lower().startswith("description:"):
                            description = line.split(":", 1)[-1].strip().strip("'\"").replace("\n", " ")[:300]
                            break
                # Body: first 800 chars after first # heading
                lines = text.split("\n")
                started = False
                for line in lines:
                    if line.strip().startswith("# "):
                        started = True
                        body += line.strip() + " "
                        continue
                    if started:
                        body += line.strip() + " "
                        if len(body) >= 800:
                            break
            if not description and readme.exists():
                description = readme.read_text()[:300].replace("\n", " ")
            content = f"{name}. {description} {body}".strip()[:1200]
            if not content:
                content = f"Skill: {name} at {path}"
            # Prefer slug from path name for output filename
            skill_slug = path.name.replace(" ", "-").replace("_", "-").lower()
            skill_slug = re.sub(r"[^\w\-]+", "", skill_slug)[:50]
            topics.append({
                "type": "discovery",
                "content": content,
                "source": str(path),
                "value_score": 5,
                "skill_slug": skill_slug or None,
            })
        return topics
    
    def _extract_timestamp_from_filename(self, filename: str) -> Optional[datetime]:
        """Extract timestamp from filename like chat_analysis_2026-02-17_123045.md"""
        try:
            match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{6})', filename)
            if match:
                date_str = match.group(1)
                time_str = match.group(2)
                dt_str = f"{date_str} {time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except:
            pass
        return None
    
    def _extract_topics_from_content(self, content: str, source: str) -> List[Dict[str, Any]]:
        """Extract interesting topics from journal content."""
        topics = []
        
        # Look for discoveries, obstacles, and solutions
        discovery_pattern = r'##\s*🔍\s*Key\s*Discoveries\s*\n(.*?)(?=##|$)'
        obstacle_pattern = r'##\s*⚠️\s*Obstacles\s*Encountered\s*\n(.*?)(?=##|$)'
        solution_pattern = r'##\s*✅\s*Solutions\s*Found\s*\n(.*?)(?=##|$)'
        
        discoveries = re.findall(discovery_pattern, content, re.DOTALL | re.IGNORECASE)
        obstacles = re.findall(obstacle_pattern, content, re.DOTALL | re.IGNORECASE)
        solutions = re.findall(solution_pattern, content, re.DOTALL | re.IGNORECASE)
        
        # Extract topics from discoveries
        for disc_text in discoveries:
            lines = disc_text.split('\n')
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    topics.append({
                        'type': 'discovery',
                        'content': line.strip()[:500],
                        'source': source,
                        'value_score': self._score_topic_value(line)
                    })
        
        # Extract topics from obstacles (high value - problems people face)
        for obs_text in obstacles:
            lines = obs_text.split('\n')
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    topics.append({
                        'type': 'obstacle',
                        'content': line.strip()[:500],
                        'source': source,
                        'value_score': self._score_topic_value(line) + 2  # Obstacles are higher value
                    })
        
        # Extract topics from solutions (very high value - how to solve problems)
        for sol_text in solutions:
            lines = sol_text.split('\n')
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    topics.append({
                        'type': 'solution',
                        'content': line.strip()[:500],
                        'source': source,
                        'value_score': self._score_topic_value(line) + 3  # Solutions are highest value
                    })
        
        return topics
    
    def _score_topic_value(self, content: str) -> int:
        """Score a topic based on keywords and content quality."""
        score = 0
        content_lower = content.lower()
        
        # Check for high-value keywords
        for keyword in self.high_value_keywords:
            if keyword.lower() in content_lower:
                score += 2
        
        # Check for problem-solving language
        problem_words = ['error', 'failed', 'issue', 'problem', 'fix', 'solution', 'how to', 'troubleshoot']
        for word in problem_words:
            if word in content_lower:
                score += 1
        
        # Check for technical depth
        if len(content) > 100:
            score += 1
        
        return score
    
    def identify_high_value_topics(self, topics: List[Dict[str, Any]], max_topics: int = 5) -> List[Dict[str, Any]]:
        """Identify the highest value topics for blog posts."""
        # Sort by value score
        sorted_topics = sorted(topics, key=lambda x: x.get('value_score', 0), reverse=True)
        
        # Group similar topics
        unique_topics = []
        seen_content = set()
        
        for topic in sorted_topics:
            # Create a signature from the content (first 100 chars)
            signature = topic['content'][:100].lower().strip()
            if signature not in seen_content:
                seen_content.add(signature)
                unique_topics.append(topic)
                if len(unique_topics) >= max_topics:
                    break
        
        return unique_topics
    
    def research_keyword(self, keyword: str) -> Dict[str, Any]:
        """Research a keyword for search volume and competition (placeholder - can be enhanced)."""
        # This is a placeholder - in a real implementation, you'd use an API like:
        # - Google Keyword Planner API
        # - Ahrefs API
        # - SEMrush API
        # For now, we'll use heuristics
        
        keyword_lower = keyword.lower()
        search_volume_score = 0
        
        # High-volume indicators
        if any(kw in keyword_lower for kw in ['how to', 'tutorial', 'guide', 'setup', 'install']):
            search_volume_score += 3
        
        if 'error' in keyword_lower or 'fix' in keyword_lower or 'troubleshoot' in keyword_lower:
            search_volume_score += 2
        
        if 'openclaw' in keyword_lower:
            search_volume_score += 1  # Niche but valuable
        
        return {
            'keyword': keyword,
            'estimated_volume': 'medium' if search_volume_score >= 3 else 'low',
            'competition': 'low',  # OpenClaw is niche
            'value_score': search_volume_score
        }
    
    def generate_blog_post(self, topic: Dict[str, Any], format: str = "x") -> str:
        """Generate a blog post from a topic. format: 'x' = X/Twitter long-form (Manus style), 'classic' = overview/problem/solution."""
        content_type = topic.get('type', 'general')
        content = topic.get('content', '')
        if format == "x":
            return self._generate_x_article(topic, content, content_type)
        # Classic format
        title = self._extract_title_from_content(content, content_type)
        blog_post = f"""# {title}

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview

{self._generate_overview(content, content_type)}

## The Problem

{self._generate_problem_section(content, content_type)}

## The Solution

{self._generate_solution_section(content, content_type)}

## Key Takeaways

{self._generate_takeaways(content, content_type)}

## Related Topics

{self._generate_related_topics(content)}

---

*This post was automatically generated from journal analysis. Source: {topic.get('source', 'unknown')}*
"""
        return blog_post

    def _generate_x_article(self, topic: Dict[str, Any], content: str, content_type: str) -> str:
        """Generate an X (Twitter) long-form article in Manus style: punchy hook, short paragraphs, urgency, stakes."""
        hook = self._x_hook(content, content_type)
        big_fact = self._x_big_fact(content, content_type)
        two_types = self._x_two_types(content, content_type)
        what_it_is = self._x_what_it_is(content, content_type)
        pivot = self._x_pivot(content, content_type)
        concrete = self._x_concrete(content, content_type)
        stakes = self._x_stakes(content, content_type)
        closing = self._x_closing(content, content_type)
        parts = [p for p in [hook, big_fact, two_types, what_it_is, pivot, concrete, stakes, closing] if p]
        body = "\n\n".join(parts)
        title = hook.split(":")[0].strip() if ":" in hook else hook[:60]
        return f"""# {title}

{body}

---

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Source: {topic.get('source', 'unknown')}*
"""

    def _x_hook(self, content: str, content_type: str) -> str:
        """Punchy one-line hook ending with colon."""
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.strip().startswith("#")][:2]
        core = " ".join(lines)[:200] if lines else "This changes how we work."
        # Extract a bold claim
        if content_type == "obstacle":
            return "a lot of people are about to hit the same wall—and most won't see it coming:"
        if content_type == "solution":
            return "the fix is simpler than everyone thinks, and almost nobody is doing it right:"
        return "what's happening right now is bigger than most people realize:"

    def _x_big_fact(self, content: str, content_type: str) -> str:
        """Big fact + 'if you think X you're missing Y'."""
        fact = content.strip()[:300].replace("\n", " ")
        if len(fact) < 50:
            fact = "The shift from manual work to automated workflows is accelerating."
        return f"{fact}—and if you think this is just \"another tool\" you're completely missing what's actually happening."

    def _x_two_types(self, content: str, content_type: str) -> str:
        """Two types of people framing."""
        return """there are two types of people right now:

people who think this is something you use when you need help, asking it questions and copying answers into your work—and people who understand it as something that executes entire workflows while they're doing something else

the gap between those two is about to get very obvious."""

    def _x_what_it_is(self, content: str, content_type: str) -> str:
        """Contrast: isn't X—it's Y."""
        return "this isn't another helper that gives you better responses—it's the kind of change that replaces whole job categories when adoption hits critical mass."

    def _x_pivot(self, content: str, content_type: str) -> str:
        """'And here's where it gets [scary/interesting]'."""
        return "and here's where it gets real for anyone in the same space:"

    def _x_concrete(self, content: str, content_type: str) -> str:
        """Concrete capabilities / facts, short sentences."""
        lines = [l.strip() for l in content.split("\n") if l.strip() and len(l.strip()) > 20][:5]
        if not lines:
            return "the people who figure out how to let the system do the actual work—instead of getting better at \"using the tool\"—will pull ahead. everyone else will spend months wondering what happened."
        bullets = " ".join(lines[:3])
        return f"{bullets}\n\nthe people who build systems where the work gets done automatically will own the next phase; everyone else will be months behind."

    def _x_stakes(self, content: str, content_type: str) -> str:
        """Urgency: right now, not in 5 years."""
        return "and the best part is almost nobody was expecting it this soon. this isn't coming in five years—it's happening right now."

    def _x_closing(self, content: str, content_type: str) -> str:
        """Closing stakes."""
        return "most people scrolling past this won't understand until they're already replaced. the industry will look different after this."
    
    def _extract_title_from_content(self, content: str, content_type: str) -> str:
        """Extract or generate a title from content."""
        # Try to find a question or statement
        lines = content.split('\n')
        for line in lines[:3]:
            line = line.strip()
            if not line:
                continue
            
            # Remove markdown formatting
            line = re.sub(r'^\d+\.\s*', '', line)
            line = re.sub(r'\*\*', '', line)
            line = re.sub(r'`', '', line)
            
            if len(line) > 20 and len(line) < 100:
                # Capitalize first letter
                title = line[0].upper() + line[1:] if line else "OpenClaw Topic"
                # Ensure it ends properly
                if not title.endswith(('.', '!', '?')):
                    title += ": A Practical Guide"
                return title
        
        # Fallback title based on type
        if content_type == 'obstacle':
            return "Common OpenClaw Issues and How to Resolve Them"
        elif content_type == 'solution':
            return "Solving OpenClaw Configuration Challenges"
        elif content_type == 'discovery':
            return "OpenClaw Tips and Best Practices"
        else:
            return "OpenClaw Insights and Solutions"
    
    def _generate_overview(self, content: str, content_type: str) -> str:
        """Generate overview section."""
        if content_type == 'obstacle':
            return f"In this post, we'll explore a common issue encountered with OpenClaw and provide practical solutions. Based on recent analysis, this problem appears frequently and has a clear resolution path."
        elif content_type == 'solution':
            return f"This guide walks through a proven solution for an OpenClaw configuration or usage challenge. The approach has been tested and documented from real-world usage."
        else:
            return f"This post covers an interesting discovery or insight about using OpenClaw effectively. The information comes from analyzing recent usage patterns and journal entries."
    
    def _generate_problem_section(self, content: str, content_type: str) -> str:
        """Generate problem section."""
        if content_type == 'obstacle':
            # Extract the problem from content
            problem_lines = [line.strip() for line in content.split('\n')[:3] if line.strip()]
            problem_text = ' '.join(problem_lines[:2])
            return f"{problem_text}\n\nThis issue can be frustrating and may prevent you from using OpenClaw effectively. Understanding the root cause is the first step toward resolution."
        else:
            return "While working with OpenClaw, users may encounter various challenges related to configuration, gateway connectivity, or skill management. This post addresses one such challenge."
    
    def _generate_solution_section(self, content: str, content_type: str) -> str:
        """Generate solution section."""
        if content_type == 'solution':
            # Extract solution from content
            solution_lines = [line.strip() for line in content.split('\n')[:5] if line.strip()]
            solution_text = '\n\n'.join(solution_lines[:3])
            return f"{solution_text}\n\n### Step-by-Step Guide\n\n1. Identify the specific issue you're experiencing\n2. Follow the solution approach outlined above\n3. Verify the fix works as expected\n4. Document any additional steps needed for your setup"
        else:
            return "To resolve this issue, follow these steps:\n\n1. Check your OpenClaw configuration\n2. Review recent logs for error messages\n3. Consult the relevant skill documentation\n4. If needed, restart the gateway or relevant services\n\nFor specific guidance, refer to the OpenClaw documentation or community resources."
    
    def _generate_takeaways(self, content: str, content_type: str) -> str:
        """Generate key takeaways."""
        takeaways = [
            "Always check logs when encountering issues",
            "Keep your OpenClaw installation updated",
            "Review skill documentation for best practices",
            "Consider using gateway-guard for automatic recovery"
        ]
        
        return '\n'.join([f"- {takeaway}" for takeaway in takeaways[:4]])
    
    def _generate_related_topics(self, content: str) -> str:
        """Generate related topics section."""
        related = []
        content_lower = content.lower()
        
        if 'gateway' in content_lower:
            related.append("- [Gateway Configuration Guide](#)")
            related.append("- [Troubleshooting Gateway Issues](#)")
        
        if 'skill' in content_lower or 'agent' in content_lower:
            related.append("- [OpenClaw Skills Overview](#)")
            related.append("- [Creating Custom Skills](#)")
        
        if 'cron' in content_lower or 'schedule' in content_lower:
            related.append("- [Setting Up Cron Jobs](#)")
            related.append("- [Automation Best Practices](#)")
        
        if not related:
            related = [
                "- [OpenClaw Documentation](#)",
                "- [Community Resources](#)"
            ]
        
        return '\n'.join(related[:4])
    
    def save_blog_post(
        self,
        blog_post: str,
        topic: Dict[str, Any],
        visual_explainer_path: Optional[Path] = None,
    ) -> Path:
        """Save blog post to blogs directory as HTML only (X-article format, header from visual-explainer)."""
        title = blog_post.split('\n')[0].replace('# ', '').strip()
        filename = topic.get("skill_slug") or self._slugify(title)
        timestamp = datetime.now().strftime("%Y%m%d")
        blog_file = self.blogs_dir / f"{timestamp}_{filename}.html"
        counter = 1
        while blog_file.exists():
            blog_file = self.blogs_dir / f"{timestamp}_{filename}_{counter}.html"
            counter += 1
        html_content = self.render_to_html(blog_post, topic, visual_explainer_path)
        blog_file.write_text(html_content)
        return blog_file

    def _html_escape(self, s: str) -> str:
        """Escape text for safe HTML."""
        return html_module.escape(s, quote=True)

    def _call_visual_explainer(
        self,
        section: str,
        text: str,
        topic: Dict[str, Any],
        visual_explainer_path: Path,
        title_override: Optional[str] = None,
    ) -> Optional[str]:
        """Call visual-explainer skill; return HTML snippet or image tag, or None. For section 'header' only."""
        script_names = ("generate_header.py", "generate.py", "explain.py", "visual_explainer.py") if section == "header" else ("generate.py", "explain.py", "visual_explainer.py")
        title = title_override or (text.split("\n")[0][:200] if text else "")
        for script_name in script_names:
            script = visual_explainer_path / "scripts" / script_name
            if not script.exists():
                script = visual_explainer_path / script_name
            if not script.exists():
                continue
            try:
                payload = json.dumps({
                    "section": section,
                    "text": text[:2000],
                    "topic_type": topic.get("type", "general"),
                    "title": title,
                })
                proc = subprocess.run(
                    [sys.executable, str(script)],
                    input=payload,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    env={**os.environ},
                    cwd=str(visual_explainer_path),
                )
                if proc.returncode != 0 or not proc.stdout:
                    continue
                out = json.loads(proc.stdout)
                if out.get("image_path"):
                    rel = out["image_path"]
                    return f'<figure class="visual-explainer"><img src="{self._html_escape(rel)}" alt="{self._html_escape(section)}" loading="lazy" /></figure>'
                if out.get("html_snippet"):
                    return out["html_snippet"]
            except (json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError, Exception):
                continue
        return None

    def _md_paragraphs_to_html(self, body: str) -> str:
        """Convert markdown-style body (double newline = paragraph) to HTML. ## lines become <h2>, rest <p>."""
        parts = []
        for block in body.split("\n\n"):
            block = block.strip()
            if not block:
                continue
            lines = block.split("\n")
            if len(lines) == 1:
                line = lines[0]
                if line.startswith("## "):
                    parts.append(f"<h2>{self._html_escape(line.replace('## ', '').strip())}</h2>")
                else:
                    parts.append(f"<p>{self._html_escape(line)}</p>")
                continue
            # Multiple lines: emit h2 for ## lines, then <p> for the rest
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.strip().startswith("## "):
                    parts.append(f"<h2>{self._html_escape(line.replace('## ', '').strip())}</h2>")
                    i += 1
                    continue
                para_lines = []
                while i < len(lines) and not lines[i].strip().startswith("## "):
                    para_lines.append(self._html_escape(lines[i]))
                    i += 1
                if para_lines:
                    parts.append("<p>" + "<br>\n".join(para_lines) + "</p>")
        return "\n".join(parts)

    def render_to_html(
        self,
        blog_post: str,
        topic: Dict[str, Any],
        visual_explainer_path: Optional[Path] = None,
    ) -> str:
        """Render to HTML for X articles: header from visual-explainer only, then title + body (no interlaced visuals)."""
        lines = blog_post.split("\n")
        title = ""
        body_blocks = []
        footer = ""
        state = "title"
        for line in lines:
            if state == "title" and line.strip().startswith("# "):
                title = self._html_escape(line.replace("# ", "").strip())
                state = "body"
                continue
            if state == "body" and line.strip() == "---":
                state = "footer"
                footer += line + "\n"
                continue
            if state == "title":
                pass
            elif state == "body":
                body_blocks.append(line)
            else:
                footer += line + "\n"
        body_text = "\n".join(body_blocks)
        body_html = self._md_paragraphs_to_html(body_text)
        footer_html = self._html_escape(footer.strip()).replace("\n", "<br>\n")
        # Single header from visual-explainer only (no interlaced Mermaid or other visuals)
        header_html = ""
        if visual_explainer_path and visual_explainer_path.exists():
            header_snippet = self._call_visual_explainer(
                "header",
                title + "\n\n" + body_text[:800],
                topic,
                visual_explainer_path,
                title_override=title,
            )
            if header_snippet:
                header_html = header_snippet
        if not header_html:
            header_html = f'<header class="ve-article-header"><h1 class="ve-article-header__title">{title}</h1></header>'
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<style>
  :root {{ --bg: #0f0f12; --text: #e4e4e7; --muted: #71717a; --accent: #a78bfa; }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; max-width: 720px; margin: 0 auto; padding: 2rem; }}
  .article p {{ margin-bottom: 1rem; }}
  .footer {{ margin-top: 2rem; font-size: 0.875rem; color: var(--muted); }}
  .ve-article-header {{ margin-bottom: 1.5rem; }}
  .ve-article-header__title {{ font-size: 1.75rem; font-weight: 700; color: var(--text); margin: 0; }}
  .ve-article-header__summary {{ margin: 0.5rem 0 0; color: var(--muted); font-size: 1rem; }}
  figure.visual-explainer {{ margin: 0 0 1.5rem; }}
  figure.visual-explainer img {{ max-width: 100%; height: auto; border-radius: 8px; }}
</style>
</head>
<body>
<article class="article">
  {header_html}
  <div class="article-body">{body_html}</div>
  <div class="footer">{footer_html}</div>
</article>
</body>
</html>"""

    def run_humanizer(self, text: str, humanizer_path: Path) -> Optional[str]:
        """Run humanizer script on text; return humanized text or None on failure."""
        script = humanizer_path / "scripts" / "humanize.py"
        if not script.exists():
            return None
        try:
            proc = subprocess.run(
                [sys.executable, str(script), "--humanizer-path", str(humanizer_path)],
                input=text,
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ},
            )
            if proc.returncode == 0 and proc.stdout:
                return proc.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        return None
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text[:50]  # Limit length


def main():
    default_humanizer = Path("/Users/ghost/Downloads/humanizer-1.0.0")
    default_visual_explainer = Path("/Users/ghost/.openclaw/workspace/skills/visual-explainer-main")
    parser = argparse.ArgumentParser(description="Generate X-format blog articles as HTML. Humanizer runs between generations.")
    parser.add_argument("--days", type=int, default=7, help="Days of journal history to analyze (default: 7)")
    parser.add_argument("--max-topics", type=int, default=3, help="Maximum topics to generate (default: 3)")
    parser.add_argument("--format", choices=["x", "classic"], default="x", help="Article format: x = X long-form (default), classic = overview/problem/solution")
    parser.add_argument("--humanizer-path", type=str, default=str(default_humanizer), help=f"Run humanizer between generations (default: {default_humanizer})")
    parser.add_argument("--no-humanize", action="store_true", help="Skip humanizer pass")
    parser.add_argument("--visual-explainer-path", type=str, default=str(default_visual_explainer), help=f"Header from visual-explainer (default: {default_visual_explainer})")
    parser.add_argument("--output-dir", "-o", type=str, default="", help="Directory to save HTML articles (default: openclaw_home/blogs)")
    parser.add_argument("--skill-dirs", type=str, nargs="*", default=None, help="Generate from skill dirs (paths to SKILL.md); one article per skill, skips journal")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--openclaw-home", type=str, help="OpenClaw home directory (default: ~/.openclaw)")
    args = parser.parse_args()
    
    openclaw_home = Path(args.openclaw_home) if args.openclaw_home else Path.home() / ".openclaw"
    humanizer_path = Path(args.humanizer_path)
    visual_explainer_path = Path(args.visual_explainer_path) if args.visual_explainer_path else None
    output_dir = Path(args.output_dir) if args.output_dir else None
    
    generator = BlogGenerator(openclaw_home, output_dir=output_dir)
    
    try:
        if getattr(args, "skill_dirs", None):
            # Generate from skill directories (one article per skill)
            skill_paths = [Path(p) for p in args.skill_dirs]
            topics = generator.scan_skill_dirs(skill_paths)
            high_value_topics = topics
        else:
            # Scan journal entries
            topics = generator.scan_journal_entries(days_back=args.days)
            if not topics:
                if args.json:
                    print(json.dumps({"status": "no_topics", "message": "No topics found in journal entries"}))
                else:
                    print("No topics found in journal entries from the specified time period.")
                return
            high_value_topics = generator.identify_high_value_topics(topics, max_topics=args.max_topics)

        if not high_value_topics:
            if args.json:
                print(json.dumps({"status": "no_high_value_topics", "message": "No high-value topics identified"}))
            else:
                print("No high-value topics identified.")
            return
        
        # Generate blog posts (X-article format, HTML only). Run humanizer between each generation.
        generated_posts = []
        for topic in high_value_topics:
            blog_post = generator.generate_blog_post(topic, format=args.format)
            # Run humanizer between generations (unless --no-humanize)
            if not getattr(args, "no_humanize", False) and humanizer_path.exists():
                lines = blog_post.split("\n")
                title_line = []
                body_lines = []
                footer_lines = []
                state = "title"
                for line in lines:
                    if state == "title" and line.strip().startswith("# "):
                        title_line.append(line)
                        state = "body"
                        continue
                    if state == "body" and line.strip() == "---":
                        footer_lines.append(line)
                        state = "footer"
                        continue
                    if state == "title":
                        title_line.append(line)
                    elif state == "body":
                        body_lines.append(line)
                    else:
                        footer_lines.append(line)
                body_text = "\n".join(body_lines).strip()
                if body_text:
                    humanized = generator.run_humanizer(body_text, humanizer_path)
                    if humanized:
                        blog_post = "\n".join(title_line) + "\n\n" + humanized + "\n\n" + "\n".join(footer_lines)
            blog_file = generator.save_blog_post(blog_post, topic, visual_explainer_path=visual_explainer_path)
            generated_posts.append({
                'topic': topic,
                'blog_file': str(blog_file),
                'title': blog_post.split('\n')[0].replace('# ', '')
            })
        
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
            print(f"\nTopics analyzed: {len(topics)}")
            print(f"High-value topics identified: {len(high_value_topics)}")
            print(f"Blog posts generated: {len(generated_posts)}\n")
            
            for i, post in enumerate(generated_posts, 1):
                print(f"{i}. {post['title']}")
                print(f"   Saved to: {post['blog_file']}\n")
            
            print("=" * 70)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

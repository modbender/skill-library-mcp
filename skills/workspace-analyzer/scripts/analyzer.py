#!/usr/bin/env python3
"""
Workspace Analyzer for OpenClaw
Scans, analyzes, and reports on workspace health.

Success Criteria:
1. Dynamic - works for any OpenClaw workspace
2. No sensitive info - read-only, no secrets
3. Well documented
4. Agent-focused output (JSON)
"""

import os
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Default workspace root
DEFAULT_ROOT = os.path.expanduser("~/.openclaw/workspace")

# Patterns for dynamic core file detection
PATTERNS = {
    "kai_core": {
        "location": "root",
        "files": ["SOUL.md", "OPERATING.md", "AGENTS.md", "HEARTBEAT.md", 
                  "CORE_PRINCIPLES.md", "USER.md", "LEARNINGS.md", 
                  "WORKING_MEMORY.md", "IDENTITY.md", "TOOLS.md", "KNOWLEDGE_GRAPH.md",
                  "SUB_CONSCIOUS.md"],
        "patterns": ["*.md"],  # All .md in root
        "exclude": ["projects/", "node_modules/"]
    },
    "sub_conscious": {
        "location": "root",
        "files": ["SUB_CONSCIOUS.md"],
        "patterns": ["SUB_CONSCIOUS.md"],
        "exclude": []
    },
    "mission_control": {
        "location": "mission_control/",
        "patterns": ["*GUIDELINES.md", "DATABASE_*.md", "AGENT_CREATION_*.md"],
        "exclude": ["shared-context/", "agents/"]
    },
    "agent_cores": {
        "location": "mission_control/agents/",
        "patterns": ["SOUL.md", "OPERATING.md", "AGENTS.md", "HEARTBEAT.md",
                     "CORE_PRINCIPLES.md", "USER.md", "LEARNINGS.md", 
                     "WORKING_MEMORY.md", "IDENTITY.md", "TOOLS.md"],
        "folder_pattern": "*"  # Matches any agent folder
    },
    "skills": {
        "location": "skills/",
        "patterns": ["*/SKILL.md"],
        "exclude": ["mocs/"]
    }
}

# Category-specific thresholds (lines)
THRESHOLDS = {
    "kai_core": {
        "bloat_warning": 400,
        "bloat_critical": 600
    },
    "sub_conscious": {
        "bloat_warning": 100,
        "bloat_critical": 200
    },
    "mission_control": {
        "bloat_warning": 500,
        "bloat_critical": 800
    },
    "agent_cores": {
        "bloat_warning": 300,
        "bloat_critical": 500
    },
    "skills": {
        "bloat_warning": 600,
        "bloat_critical": 1000
    },
    "memory": {
        "bloat_warning": 500,
        "bloat_critical": 800
    },
    "docs": {
        "bloat_warning": 400,
        "bloat_critical": 600
    },
    "default": {
        "bloat_warning": 400,
        "bloat_critical": 800
    },
    # Global thresholds
    "orphan_days": 30,         # File not modified in X days = orphan warning
    "duplicate_size_kb": 5,    # Consider duplicate if files are >X KB and similar
    "duplicate_ratio": 0.9,    # Files are duplicates if content similarity >X%
}


def get_all_markdown_files(root: str) -> List[Path]:
    """Get all markdown files, excluding node_modules and projects."""
    md_files = []
    root_path = Path(root)
    
    for path in root_path.rglob("*.md"):
        # Exclude patterns
        excluded = False
        for exclude in ["node_modules", "projects/", ".git"]:
            if exclude in str(path):
                excluded = True
                break
        
        if not excluded:
            md_files.append(path)
    
    return md_files


def detect_core_files(root: str, md_files: List[Path]) -> Dict[str, Any]:
    """Dynamically detect core files based on location patterns."""
    root_path = Path(root)
    detected = {
        "kai_core": {"files": [], "count": 0},
        "mission_control": {"files": [], "count": 0},
        "agent_cores": {"files": [], "agents": [], "count": 0},
        "skills": {"files": [], "count": 0}
    }
    
    for md_file in md_files:
        rel_path = md_file.relative_to(root_path)
        path_str = str(rel_path)
        
        # KAI core: root *.md files
        if path_str.count('/') == 0 and path_str.endswith('.md'):
            if not path_str.startswith('.'):
                detected["kai_core"]["files"].append(path_str)
        
        # Mission Control guidelines
        elif 'mission_control/' in path_str:
            # Check if it's in agents subfolder (agent core)
            if '/agents/' in path_str:
                # Extract agent name
                parts = path_str.split('/')
                if len(parts) >= 3:
                    agent_name = parts[2]
                    if agent_name not in detected["agent_cores"]["agents"]:
                        detected["agent_cores"]["agents"].append(agent_name)
                    detected["agent_cores"]["files"].append(path_str)
            
            # Guidelines (not in agents)
            elif any(p in path_str for p in ['GUIDELINES', 'DATABASE_', 'AGENT_CREATION']):
                detected["mission_control"]["files"].append(path_str)
        
        # Skills
        elif path_str.startswith('skills/') and path_str.endswith('/SKILL.md'):
            detected["skills"]["files"].append(path_str)
    
    # Count totals
    detected["kai_core"]["count"] = len(detected["kai_core"]["files"])
    detected["mission_control"]["count"] = len(detected["mission_control"]["files"])
    detected["agent_cores"]["count"] = len(detected["agent_cores"]["files"])
    detected["skills"]["count"] = len(detected["skills"]["files"])
    
    return detected


def get_category_from_path(path_str: str) -> str:
    """Determine category from file path."""
    if path_str.count('/') == 0:
        return "kai_core"
    elif '/agents/' in path_str:
        return "agent_cores"
    elif 'mission_control/' in path_str and not '/agents/' in path_str:
        return "mission_control"
    elif path_str.startswith('skills/'):
        return "skills"
    elif path_str.startswith('memory/'):
        return "memory"
    elif path_str.startswith('docs/'):
        return "docs"
    else:
        return "default"


def analyze_file(file_path: Path, root: str) -> Dict[str, Any]:
    """Analyze a single file for issues."""
    stats = os.stat(file_path)
    rel_path = str(file_path.relative_to(Path(root)))
    category = get_category_from_path(rel_path)
    
    # Get category-specific thresholds
    thresholds = THRESHOLDS.get(category, THRESHOLDS["default"])
    
    analysis = {
        "path": str(file_path),
        "relative_path": rel_path,
        "category": category,
        "size_bytes": stats.st_size,
        "size_kb": round(stats.st_size / 1024, 2),
        "modified_days_ago": (datetime.now() - datetime.fromtimestamp(stats.st_mtime)).days,
        "line_count": 0,
        "sections": [],
        "wiki_links": [],
        "issues": []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            analysis["line_count"] = len(lines)
            
            # Extract sections (## headers)
            sections = []
            for line in lines:
                if line.strip().startswith('##'):
                    sections.append(line.strip().replace('##', '').strip())
            analysis["sections"] = sections
            
            # Extract wiki-links [[...]]
            wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
            analysis["wiki_links"] = wiki_links
            
            # Check for issues using category-specific thresholds
            line_count = len(lines)
            bloat_critical = thresholds.get("bloat_critical", THRESHOLDS["default"]["bloat_critical"])
            bloat_warning = thresholds.get("bloat_warning", THRESHOLDS["default"]["bloat_warning"])
            
            # Bloat warnings (category-specific)
            if line_count > bloat_critical:
                analysis["issues"].append({
                    "type": "BLOAT_CRITICAL",
                    "severity": "CRITICAL",
                    "msg": f"{line_count} lines - critical bloat (threshold: {bloat_critical})"
                })
            elif line_count > bloat_warning:
                analysis["issues"].append({
                    "type": "BLOAT_WARNING",
                    "severity": "WARN",
                    "msg": f"{line_count} lines - consider splitting (threshold: {bloat_warning})"
                })
            
            # Orphan warning
            if analysis["modified_days_ago"] > THRESHOLDS["orphan_days"]:
                analysis["issues"].append({
                    "type": "ORPHAN_WARNING",
                    "severity": "INFO",
                    "msg": f"Not modified in {analysis['modified_days_ago']} days"
                })
    
    except Exception as e:
        analysis["issues"].append({
            "type": "READ_ERROR",
            "severity": "ERROR",
            "msg": str(e)
        })
    
    return analysis


def detect_duplicates(all_analysis: Dict) -> List[Dict]:
    """Detect potential duplicate files based on similar names and sizes."""
    duplicates = []
    files_by_name = {}
    
    # Group files by similar base names
    for file_path, analysis in all_analysis.items():
        # Get base name without date prefix and extension
        basename = os.path.basename(file_path)
        # Remove date patterns like 2026-02-XX- or XXXX-XX-XX
        import re
        cleaned = re.sub(r'^\d{4}-\d{2}-\d{2}(-\d+)?[-_]?', '', basename)
        cleaned = re.sub(r'^\d+-', '', cleaned)  # Remove leading numbers
        cleaned = cleaned.replace('.md', '')
        
        if cleaned not in files_by_name:
            files_by_name[cleaned] = []
        files_by_name[cleaned].append({
            "path": file_path,
            "size_kb": analysis.get("size_kb", 0),
            "line_count": analysis.get("line_count", 0)
        })
    
    # Find groups with multiple files
    for name, files in files_by_name.items():
        if len(files) > 1:
            # Check if sizes are similar (within 50%)
            sizes = [f["size_kb"] for f in files]
            if sizes and max(sizes) > 0:
                ratio = min(sizes) / max(sizes) if max(sizes) > 0 else 0
                if ratio > 0.5:  # More than 50% similar
                    duplicates.append({
                        "type": "POTENTIAL_DUPLICATE",
                        "severity": "WARN",
                        "name": name,
                        "files": files,
                        "msg": f"Found {len(files)} files with similar name '{name}'"
                    })
    
    return duplicates


def detect_broken_links(all_analysis: Dict) -> List[Dict]:
    """Detect potentially broken wiki-links."""
    broken_links = []
    
    # Build set of all valid file paths (without extensions)
    valid_paths = set()
    for file_path in all_analysis.keys():
        # Add various forms of the path
        basename = os.path.basename(file_path)
        valid_paths.add(basename)
        valid_paths.add(basename.replace('.md', ''))
        # Add relative path variations
        valid_paths.add(file_path)
        valid_paths.add(file_path.replace('.md', ''))
    
    # Check each file's wiki-links
    for file_path, analysis in all_analysis.items():
        for link in analysis.get("wiki_links", []):
            # Clean the link
            link_clean = link.strip()
            link_clean = link_clean.replace('.md', '')
            
            # Check if link could be valid
            is_broken = True
            for valid in valid_paths:
                valid_clean = valid.replace('.md', '')
                if link_clean.lower() == valid_clean.lower():
                    is_broken = False
                    break
            
            # Only flag if it looks like an internal link (not a URL)
            if is_broken and not link.startswith('http') and not '/' in link:
                broken_links.append({
                    "type": "POTENTIAL_BROKEN_LINK",
                    "severity": "INFO",
                    "file": file_path,
                    "link": link,
                    "msg": f"Wiki-link '[[{link}]]' may not match any file"
                })
    
    return broken_links


# Topics that should have single source of truth
SINGLE_SOURCE_TOPICS = {
    "skill_graph": {
        "keywords": ["skill graph", "skill_graph", "skill-graph"],
        "expected_file": "SUB_CONSCIOUS.md",
        "description": "Skill graph navigation and traversal"
    },
    "memory_architecture": {
        "keywords": ["memory architecture", "tiered retrieval", "memory decay", "conflict resolution"],
        "expected_file": "OPERATING.md",
        "description": "Memory management and retrieval"
    },
    "message_reactions": {
        "keywords": ["message reaction", "react to", "telegram emoji"],
        "expected_file": "SUB_CONSCIOUS.md",
        "description": "Message reaction behaviors"
    },
    "image_handling": {
        "keywords": ["image handling", "understand_image", "analyze image"],
        "expected_file": "OPERATING.md",
        "description": "Image analysis procedures"
    },
    "session_bootstrap": {
        "keywords": ["session bootstrap", "session start", "every session"],
        "expected_file": "AGENTS.md",
        "description": "Session initialization"
    },
    "self_improving": {
        "keywords": ["self improving", "correction", "pattern detection"],
        "expected_file": "self-improving/memory.md",
        "description": "Behavioral learning and corrections"
    }
}


def validate_single_source(all_analysis: Dict) -> Dict[str, Dict]:
    """Validate that each topic exists in only one place.
    
    Only checks core KAI files (kai_core, sub_conscious), not skills or memory.
    Skills are expected to reference these topics.
    """
    topic_locations = {}
    
    # Only check core files (not skills, memory, docs)
    CORE_FILE_PREFIXES = ["SOUL.md", "OPERATING.md", "AGENTS.md", "HEARTBEAT.md", 
                          "CORE_PRINCIPLES.md", "USER.md", "LEARNINGS.md",
                          "WORKING_MEMORY.md", "IDENTITY.md", "TOOLS.md", 
                          "KNOWLEDGE_GRAPH.md", "SUB_CONSCIOUS.md"]
    
    # Scan each file for topic keywords
    for file_path, analysis in all_analysis.items():
        # Skip non-core files (skills, memory, docs)
        basename = os.path.basename(file_path)
        is_core = basename in CORE_FILE_PREFIXES
        is_root = "/" not in file_path or file_path.startswith("SUB_CONSCIOUS") or file_path.startswith("self-improving/")
        
        # Only validate core files
        if not (is_core or is_root):
            continue
            
        content = analysis.get("content", "").lower()
        sections = analysis.get("sections", [])
        
        # Check content and sections for each topic
        for topic, config in SINGLE_SOURCE_TOPICS.items():
            found = False
            
            # Check keywords in content (only if substantial)
            content_length = len(content.split())
            if content_length > 50:  # Skip very short files
                for keyword in config["keywords"]:
                    if keyword.lower() in content:
                        found = True
                        break
            
            # Check if topic appears in sections
            for section in sections:
                section_lower = section.lower()
                for keyword in config["keywords"]:
                    if keyword.lower() in section_lower:
                        found = True
                        break
                if found:
                    break
            
            if found:
                if topic not in topic_locations:
                    topic_locations[topic] = {
                        "status": "PASS" if len(topic_locations.get(topic, {}).get("files", [])) == 0 else "FAIL",
                        "files": [],
                        "expected_file": config["expected_file"],
                        "description": config["description"],
                        "severity": "CRITICAL"
                    }
                topic_locations[topic]["files"].append(file_path)
                topic_locations[topic]["status"] = "FAIL"
    
    # Build recommendations from validation
    recommendations = []
    for topic, data in topic_locations.items():
        if data["status"] == "FAIL" and len(data["files"]) > 1:
            # Filter to only core files that shouldn't have duplicates
            problem_files = [f for f in data["files"] if f.startswith("SUB_CONSCIOUS") or 
                           f in ["SOUL.md", "OPERATING.md", "AGENTS.md", "HEARTBEAT.md"]]
            if len(problem_files) > 1:
                recommendations.append({
                    "action": "FIX_DUPLICATE_CONTENT",
                    "topic": topic,
                    "files": problem_files,
                    "severity": "CRITICAL",
                    "description": f"'{topic}' found in {len(problem_files)} core files",
                    "recommendation": f"Consolidate to {data['expected_file']}, reference from others"
                })
    
    return {
        "validation": topic_locations,
        "recommendations": recommendations
    }


def generate_recommendations(core_files: Dict, all_analysis: Dict) -> List[Dict]:
    """Generate recommendations based on analysis."""
    recommendations = []
    
    # Check for bloat
    for file_path, analysis in all_analysis.items():
        for issue in analysis.get("issues", []):
            if "BLOAT" in issue["type"]:
                recommendations.append({
                    "action": "REVIEW_BLOAT",
                    "file": file_path,
                    "category": analysis.get("category", "unknown"),
                    "reason": issue["msg"],
                    "severity": issue["severity"]
                })
            elif "ORPHAN" in issue["type"]:
                recommendations.append({
                    "action": "REVIEW_ORPHAN",
                    "file": file_path,
                    "reason": issue["msg"],
                    "severity": "INFO"
                })
    
    # Detect duplicates
    duplicates = detect_duplicates(all_analysis)
    for dup in duplicates:
        recommendations.append({
            "action": "CHECK_DUPLICATE",
            "name": dup["name"],
            "files": [f["path"] for f in dup["files"]],
            "reason": dup["msg"],
            "severity": dup["severity"]
        })
    
    # Detect broken links
    broken_links = detect_broken_links(all_analysis)
    for bl in broken_links[:10]:  # Limit to first 10
        recommendations.append({
            "action": "CHECK_BROKEN_LINK",
            "file": bl["file"],
            "link": bl["link"],
            "reason": bl["msg"],
            "severity": "INFO"
        })
    
    # Validate single source of truth
    single_source = validate_single_source(all_analysis)
    for rec in single_source.get("recommendations", []):
        recommendations.append(rec)
    
    # Check core files health
    for category, data in core_files.items():
        if data["count"] == 0 and category != "skills":  # Skills optional
            recommendations.append({
                "action": "CHECK_MISSING",
                "category": category,
                "reason": f"No {category} files detected",
                "severity": "WARN"
            })
    
    return recommendations


def analyze_workspace(root: str, quick: bool = False) -> Dict[str, Any]:
    """Main analysis function."""
    
    # Get all markdown files
    md_files = get_all_markdown_files(root)
    
    # Detect core files dynamically
    core_files = detect_core_files(root, md_files)
    
    # Analyze files
    all_analysis = {}
    
    if not quick:
        # Full analysis
        for md_file in md_files:
            analysis = analyze_file(md_file, root)
            all_analysis[str(md_file.relative_to(Path(root)))] = analysis
    else:
        # Quick - structure only
        for md_file in md_files:
            stats = os.stat(md_file)
            all_analysis[str(md_file.relative_to(Path(root)))] = {
                "path": str(md_file),
                "size_kb": round(stats.st_size / 1024, 2),
                "modified_days_ago": (datetime.now() - datetime.fromtimestamp(stats.st_mtime)).days,
                "line_count": "skipped (quick mode)",
                "issues": []
            }
    
    # Generate recommendations
    recommendations = generate_recommendations(core_files, all_analysis)
    
    # Validate single source of truth
    single_source_result = validate_single_source(all_analysis)
    
    # Build output
    output = {
        "scan_info": {
            "root": root,
            "timestamp": datetime.now().isoformat(),
            "files_scanned": len(md_files),
            "quick_mode": quick
        },
        "core_files_detected": core_files,
        "analysis": all_analysis,
        "single_source_validation": single_source_result.get("validation", {}),
        "recommendations": recommendations,
        "summary": {
            "total_files": len(md_files),
            "total_issues": sum(len(a.get("issues", [])) for a in all_analysis.values()),
            "total_recommendations": len(recommendations)
        }
    }
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Analyze OpenClaw workspace for maintenance needs"
    )
    parser.add_argument(
        "--root", 
        default=DEFAULT_ROOT,
        help=f"Workspace root path (default: {DEFAULT_ROOT})"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick scan (structure only, no content analysis)"
    )
    parser.add_argument(
        "--output",
        help="Output file (default: stdout)"
    )
    
    args = parser.parse_args()
    
    # Run analysis
    result = analyze_workspace(args.root, args.quick)
    
    # Output
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(f"Analysis saved to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()

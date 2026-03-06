#!/usr/bin/env python3
"""
Experience Query Tool

Query experiences by tech stack, context, or keyword.
Supports progressive loading - only returns relevant experiences.
Supports auto-detection from project files (package.json, go.mod, pom.xml, etc.)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Import project detector
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from detect_project import detect_project
    HAS_DETECTOR = True
except ImportError:
    HAS_DETECTOR = False


def load_index(experience_dir: Path) -> dict:
    """Load the experience index."""
    index_path = experience_dir / 'index.json'
    if not index_path.exists():
        return {
            'version': '2.0.0',
            'index': {'tech_stacks': [], 'contexts': [], 'total_experiences': 0},
            'preferences': [],
            'fixes': []
        }
    
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_tech_experience(experience_dir: Path, tech: str) -> dict | None:
    """Load experience for a specific tech stack."""
    tech_file = experience_dir / 'tech' / f'{tech.lower()}.json'
    if not tech_file.exists():
        return None
    
    with open(tech_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_context_experience(experience_dir: Path, context: str) -> dict | None:
    """Load experience for a specific context trigger."""
    context_file = experience_dir / 'contexts' / f'{context.lower()}.json'
    if not context_file.exists():
        return None
    
    with open(context_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def search_experiences(experience_dir: Path, keyword: str) -> list:
    """Search experiences by keyword across all files."""
    results = []
    keyword_lower = keyword.lower()
    
    # Search in index
    index = load_index(experience_dir)
    
    for pref in index.get('preferences', []):
        if keyword_lower in pref.lower():
            results.append({'type': 'preference', 'content': pref})
    
    for fix in index.get('fixes', []):
        if keyword_lower in fix.lower():
            results.append({'type': 'fix', 'content': fix})
    
    # Search in tech files
    tech_dir = experience_dir / 'tech'
    if tech_dir.exists():
        for tech_file in tech_dir.glob('*.json'):
            with open(tech_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for pattern in data.get('patterns', []):
                if keyword_lower in pattern.lower():
                    results.append({
                        'type': 'pattern',
                        'tech': tech_file.stem,
                        'content': pattern
                    })
    
    return results


def query_by_project(experience_dir: Path, project_dir: str) -> dict:
    """
    Auto-detect project tech stack and load relevant experiences.
    
    Args:
        experience_dir: Experience storage directory
        project_dir: Project directory to analyze
    
    Returns:
        dict with detected tech and relevant experiences
    """
    if not HAS_DETECTOR:
        return {'error': 'Project detector not available'}
    
    # Import here to avoid unbound error
    from detect_project import detect_project as dp
    
    # Detect project tech stack
    detection = dp(project_dir)
    
    if 'error' in detection:
        return detection
    
    result = {
        'detected': detection,
        'experiences': {
            'preferences': [],
            'fixes': [],
            'patterns': {}
        }
    }
    
    # Load index for preferences and fixes
    index = load_index(experience_dir)
    result['experiences']['preferences'] = index.get('preferences', [])
    result['experiences']['fixes'] = index.get('fixes', [])
    
    # Load experiences for each detected tech
    all_tech = detection.get('base_tech', []) + detection.get('frameworks', []) + detection.get('tools', [])
    
    for tech in all_tech:
        tech_exp = load_tech_experience(experience_dir, tech)
        if tech_exp:
            result['experiences']['patterns'][tech] = tech_exp.get('patterns', [])
    
    return result


def format_output(data: dict | list, format_type: str = 'json') -> str:
    """Format output based on type."""
    if format_type == 'json':
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif format_type == 'markdown':
        if isinstance(data, list):
            return '\n'.join(f'- {item}' for item in data)
        elif isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, list):
                    lines.append(f'\n### {key.capitalize()}')
                    for item in value:
                        lines.append(f'- {item}')
                else:
                    lines.append(f'**{key}**: {value}')
            return '\n'.join(lines)
    return str(data)


def main():
    parser = argparse.ArgumentParser(
        description='Query programming experiences progressively',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query_experience.py --tech react
  python query_experience.py --context when_testing
  python query_experience.py --search "跨域"
  python query_experience.py --project /path/to/project  # Auto-detect and load
  python query_experience.py --list-tech
  python query_experience.py --summary
        """
    )
    
    parser.add_argument(
        '--tech', '-t',
        help='Query experiences for a specific tech stack'
    )
    parser.add_argument(
        '--context', '-c',
        help='Query experiences for a specific context trigger'
    )
    parser.add_argument(
        '--search', '-s',
        help='Search experiences by keyword'
    )
    parser.add_argument(
        '--project', '-p',
        help='Auto-detect project tech stack and load relevant experiences'
    )
    parser.add_argument(
        '--list-tech',
        action='store_true',
        help='List all available tech stacks'
    )
    parser.add_argument(
        '--list-contexts',
        action='store_true',
        help='List all available context triggers'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show experience summary'
    )
    parser.add_argument(
        '--experience-dir',
        default=os.path.join(os.path.dirname(__file__), '..', 'experience'),
        help='Experience directory path'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'markdown'],
        default='json',
        help='Output format'
    )
    
    args = parser.parse_args()
    experience_dir = Path(args.experience_dir)
    
    if not experience_dir.exists():
        print(f"Error: Experience directory not found: {experience_dir}", file=sys.stderr)
        sys.exit(1)
    
    index = load_index(experience_dir)
    
    if args.summary:
        summary = {
            'version': index.get('version', 'unknown'),
            'last_updated': index.get('last_updated'),
            'total_experiences': index.get('index', {}).get('total_experiences', 0),
            'tech_stacks': len(index.get('index', {}).get('tech_stacks', [])),
            'contexts': len(index.get('index', {}).get('contexts', [])),
            'preferences': len(index.get('preferences', [])),
            'fixes': len(index.get('fixes', []))
        }
        print(format_output(summary, args.format))
        return
    
    if args.list_tech:
        tech_stacks = index.get('index', {}).get('tech_stacks', [])
        print(format_output(tech_stacks, args.format))
        return
    
    if args.list_contexts:
        contexts = index.get('index', {}).get('contexts', [])
        print(format_output(contexts, args.format))
        return
    
    if args.tech:
        result = load_tech_experience(experience_dir, args.tech)
        if result:
            print(format_output(result, args.format))
        else:
            print(f"No experience found for tech: {args.tech}", file=sys.stderr)
            sys.exit(1)
        return
    
    if args.context:
        result = load_context_experience(experience_dir, args.context)
        if result:
            print(format_output(result, args.format))
        else:
            print(f"No experience found for context: {args.context}", file=sys.stderr)
            sys.exit(1)
        return
    
    if args.search:
        results = search_experiences(experience_dir, args.search)
        if results:
            print(format_output(results, args.format))
        else:
            print(f"No results found for: {args.search}", file=sys.stderr)
        return
    
    if args.project:
        result = query_by_project(experience_dir, args.project)
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(format_output(result, args.format))
        return
    
    # Default: show preferences and fixes (commonly needed)
    output = {
        'preferences': index.get('preferences', []),
        'fixes': index.get('fixes', [])
    }
    print(format_output(output, args.format))


if __name__ == '__main__':
    main()

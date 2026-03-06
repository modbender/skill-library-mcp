#!/usr/bin/env python3
"""
ACC-Error Integration for overkill-memory-system
Interfaces with acc-error-memory skill to track and search error patterns.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

# Paths - acc-error-memory uses ~/.openclaw/workspace/memory/
WORKSPACE = os.environ.get('WORKSPACE', os.path.expanduser('~/.openclaw/workspace'))
ACC_STATE_FILE = Path(WORKSPACE) / 'memory' / 'acc-state.json'
ACC_SKILL_DIR = Path.home() / '.openclaw' / 'workspace-cody' / 'skills' / 'acc-error-memory'
ACC_SCRIPTS_DIR = ACC_SKILL_DIR / 'scripts'


def _ensure_state_file() -> dict:
    """Ensure ACC state file exists and return its contents."""
    if not ACC_STATE_FILE.exists():
        return {"version": "2.0", "activePatterns": {}, "resolved": {}, "stats": {}}
    try:
        with open(ACC_STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"version": "2.0", "activePatterns": {}, "resolved": {}, "stats": {}}


def _save_state(state: dict):
    """Save ACC state file."""
    ACC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ACC_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def search(query: str) -> dict:
    """
    Search error patterns for matching entries.
    
    Args:
        query: Search query to match against patterns, contexts, and mitigations
    
    Returns:
        Dictionary with search results
    """
    state = _ensure_state_file()
    query_lower = query.lower()
    results = {"query": query, "active": [], "resolved": [], "matches": 0}
    
    # Search active patterns
    for name, data in state.get('activePatterns', {}).items():
        if (query_lower in name.lower() or 
            query_lower in data.get('context', '').lower() or
            query_lower in data.get('mitigation', '').lower()):
            results["active"].append({
                "pattern": name,
                **data
            })
            results["matches"] += 1
    
    # Search resolved patterns
    for name, data in state.get('resolved', {}).items():
        if (query_lower in name.lower() or 
            query_lower in data.get('context', '').lower() or
            query_lower in data.get('lesson', {}).get('mitigation', '').lower()):
            results["resolved"].append({
                "pattern": name,
                **data
            })
            results["matches"] += 1
    
    return results


def track_error(description: str, pattern: Optional[str] = None, 
                context: Optional[str] = None, mitigation: Optional[str] = None) -> dict:
    """
    Track an error in the ACC system.
    
    Args:
        description: Error description (used as context if not provided)
        pattern: Optional pattern name (auto-detected from description if None)
        context: Additional context about the error
        mitigation: How to avoid this error in the future
    
    Returns:
        Result dictionary with status
    """
    # Auto-detect pattern from description if not provided
    if not pattern:
        pattern = _auto_detect_pattern(description)
    
    # Use description as context if not provided
    if not context:
        context = description
    
    state = _ensure_state_file()
    active = state.setdefault('activePatterns', {})
    resolved = state.setdefault('resolved', {})
    stats = state.setdefault('stats', {})
    
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    
    # Check for regression (pattern was previously resolved)
    regression = False
    if pattern in resolved:
        print(f"⚠️ REGRESSION: '{pattern}' was resolved but occurred again!")
        old_data = resolved.pop(pattern)
        old_lesson = old_data.get('lesson', {})
        old_mitigation = old_lesson.get('mitigation', '') if isinstance(old_lesson, dict) else old_data.get('lessonLearned', '')
        
        active[pattern] = {
            'count': old_data.get('count', 0) + 1,
            'severity': 'critical',
            'firstSeen': old_data.get('firstSeen', now),
            'lastSeen': now,
            'context': context or old_data.get('context', ''),
            'mitigation': mitigation or old_mitigation,
            'regression': True,
            'previouslyResolvedOn': old_data.get('resolvedOn'),
        }
        stats['totalRegressions'] = stats.get('totalRegressions', 0) + 1
        regression = True
        result = {
            "status": "regression_logged",
            "pattern": pattern,
            "count": active[pattern]['count'],
            "severity": "critical"
        }
    elif pattern in active:
        # Existing pattern - increment
        data = active[pattern]
        data['count'] = data.get('count', 0) + 1
        data['lastSeen'] = now
        if context:
            data['context'] = context
        if mitigation:
            data['mitigation'] = mitigation
        
        # Update severity
        count = data['count']
        if count >= 3:
            data['severity'] = 'critical'
        elif count >= 2:
            data['severity'] = 'warning'
        
        result = {
            "status": "pattern_updated",
            "pattern": pattern,
            "count": count,
            "severity": data['severity']
        }
    else:
        # New pattern
        active[pattern] = {
            'count': 1,
            'severity': 'normal',
            'firstSeen': now,
            'lastSeen': now,
            'context': context,
            'mitigation': mitigation or 'be more careful'
        }
        result = {
            "status": "new_pattern",
            "pattern": pattern,
            "count": 1,
            "severity": "normal"
        }
    
    stats['totalErrorsLogged'] = stats.get('totalErrorsLogged', 0) + 1
    state['lastUpdated'] = now
    
    _save_state(state)
    
    return result


def _auto_detect_pattern(description: str) -> str:
    """Auto-detect pattern type from error description."""
    desc_lower = description.lower()
    
    patterns = {
        'factual_error': ['wrong', 'incorrect', 'false', 'not true', 'misspoke'],
        'context_missed': ['missed', 'forgot', 'didn\'t know', 'didn\'t remember', 'ignored'],
        'tone_mismatch': ['tone', 'manner', 'rude', 'too aggressive', 'too passive'],
        'format_error': ['format', 'wrong format', 'should be', 'invalid'],
        'command_error': ['command', 'wrong command', 'should run', 'failed'],
        'permission_error': ['permission', 'access', 'denied', 'authorized'],
        'version_error': ['version', 'outdated', 'old version', 'newer'],
    }
    
    for pattern_name, keywords in patterns.items():
        if any(kw in desc_lower for kw in keywords):
            return pattern_name
    
    # Default: use sanitized description as pattern name
    import re
    sanitized = re.sub(r'[^a-z0-9\s]', '', desc_lower)
    sanitized = '_'.join(sanitized.split()[:3])
    return sanitized[:50] or 'unknown_error'


def get_corrections() -> dict:
    """
    Get user corrections (resolved patterns with lessons learned).
    
    Returns:
        Dictionary of corrections/lessons from resolved patterns
    """
    state = _ensure_state_file()
    resolved = state.get('resolved', {})
    
    corrections = {}
    for name, data in resolved.items():
        lesson = data.get('lesson', {})
        if isinstance(lesson, dict):
            corrections[name] = {
                'context': data.get('context', ''),
                'mitigation': lesson.get('mitigation', ''),
                'insight': lesson.get('insight', ''),
                'resolutionType': lesson.get('resolutionType', ''),
                'daysClear': data.get('daysClear', 0)
            }
        else:
            corrections[name] = {
                'context': data.get('context', ''),
                'lesson': str(lesson),
                'daysClear': data.get('daysClear', 0)
            }
    
    return {
        "corrections": corrections,
        "total": len(corrections)
    }


def get_patterns() -> dict:
    """
    Get all active error patterns.
    
    Returns:
        Dictionary of active patterns with their severity and counts
    """
    state = _ensure_state_file()
    active = state.get('activePatterns', {})
    
    patterns = {}
    for name, data in active.items():
        patterns[name] = {
            'count': data.get('count', 0),
            'severity': data.get('severity', 'normal'),
            'context': data.get('context', ''),
            'mitigation': data.get('mitigation', ''),
            'firstSeen': data.get('firstSeen', ''),
            'lastSeen': data.get('lastSeen', ''),
            'regression': data.get('regression', False)
        }
    
    # Count by severity
    severity_counts = {'normal': 0, 'warning': 0, 'critical': 0}
    for p in patterns.values():
        sev = p['severity']
        if sev in severity_counts:
            severity_counts[sev] += 1
    
    return {
        "patterns": patterns,
        "total": len(patterns),
        "by_severity": severity_counts,
        "stats": state.get('stats', {})
    }


def get_state() -> dict:
    """Get full ACC state for debugging."""
    return _ensure_state_file()


# CLI interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="ACC-Error Integration")
    subparsers = parser.add_subparsers(dest="command")
    
    # search
    search_parser = subparsers.add_parser("search", help="Search error patterns")
    search_parser.add_argument("query", help="Search query")
    
    # track
    track_parser = subparsers.add_parser("track", help="Track an error")
    track_parser.add_argument("--description", "-d", required=True, help="Error description")
    track_parser.add_argument("--pattern", "-p", help="Pattern name")
    track_parser.add_argument("--context", "-c", help="Additional context")
    track_parser.add_argument("--mitigation", "-m", help="How to avoid")
    
    # corrections
    subparsers.add_parser("corrections", help="Get user corrections")
    
    # patterns
    subparsers.add_parser("patterns", help="Get error patterns")
    
    # state
    subparsers.add_parser("state", help="Get full state")
    
    args = parser.parse_args()
    
    if args.command == "search":
        result = search(args.query)
        print(json.dumps(result, indent=2))
    elif args.command == "track":
        result = track_error(args.description, args.pattern, args.context, args.mitigation)
        print(json.dumps(result, indent=2))
    elif args.command == "corrections":
        result = get_corrections()
        print(json.dumps(result, indent=2))
    elif args.command == "patterns":
        result = get_patterns()
        print(json.dumps(result, indent=2))
    elif args.command == "state":
        result = get_state()
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

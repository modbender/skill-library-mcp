#!/usr/bin/env python3
"""
Build extraction cache from RLM state.pkl for kirk-content-pipeline.

This script extracts data from RLM state (single or multi-doc) and creates
a structured JSON cache with context labels and auto-generated attribution map.

Features:
- Auto-extracts 'tag' from PDF filenames (e.g., "GFHK - Memory.pdf" → "GFHK")
- Auto-generates topics with key_metrics from extractions
- Optionally loads manual cross-doc synthesis descriptions

Usage:
    # Auto-discovery (recommended) - searches common locations
    python3 build_extraction_cache.py \
        --output draft/YYYY-MM-DD-topic-assets/rlm-extraction-cache.json

    # Multi-doc auto-discovery
    python3 build_extraction_cache.py \
        --multi \
        --output draft/YYYY-MM-DD-topic-assets/rlm-extraction-cache.json

    # Manual path (override auto-discovery)
    python3 build_extraction_cache.py \
        --state-dir ~/.claude/rlm_state \
        --output cache.json

    # With manual cross-doc synthesis
    python3 build_extraction_cache.py \
        --multi \
        --output cache.json \
        --synthesis cross-doc-synthesis.json

Auto-discovery searches these locations (in order):
    Single-doc: ~/.claude/rlm_state, ~/.claude/skills/rlm-repl/scripts/.claude/rlm_state, etc.
    Multi-doc: ~/.claude/rlm_state, ~/.claude/skills/rlm-repl-multi/state, etc.

Manual synthesis format (optional):
    {
      "dual_squeeze_thesis": {
        "description": "Memory + ABF shortage = dual bottleneck",
        "components": [
          {"topic": "Memory Pricing", "source": "gfhk_memory", "timeframe": "1Q26"},
          {"topic": "Abf Shortage", "source": "goldman_abf", "timeframe": "2H26-2028"}
        ]
      }
    }
"""

import argparse
import json
import pickle
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


def load_rlm_state(state_path: Path) -> Dict[str, Any]:
    """Load RLM state.pkl file.

    Handles v1/v2/v3+ state formats, including LazyContext objects from v3+.
    """
    import sys
    # Add rlm-v3 scripts to sys.path so pickle can resolve LazyContext class
    rlm_v3_dir = Path.home() / '.claude/skills/rlm-v3/scripts'
    if str(rlm_v3_dir) not in sys.path and rlm_v3_dir.exists():
        sys.path.insert(0, str(rlm_v3_dir))
    try:
        with open(state_path, 'rb') as f:
            return pickle.load(f)
    except (AttributeError, ModuleNotFoundError):
        # LazyContext class not importable — fall back to loading without it
        # This means lazy states can't be loaded, but eager states work fine
        import io

        class _LazyContextStub:
            """Stub for when LazyContext can't be imported."""
            def __init__(self):
                self._cache_path = None
                self._path = 'unknown'
                self._loaded_at = 'unknown'

            @property
            def content(self):
                import os as _os
                if self._cache_path and _os.path.isfile(self._cache_path):
                    with open(self._cache_path, 'r') as f:
                        return f.read()
                return ''

            @property
            def path(self):
                return self._path

            @property
            def loaded_at(self):
                return self._loaded_at

            def __setstate__(self, state):
                self._cache_path = state.get('cache_path')
                self._path = state.get('path', 'unknown')
                self._loaded_at = state.get('loaded_at', 'unknown')
                self._metadata = state.get('metadata', {})

        class _StubUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                if name == 'LazyContext':
                    return _LazyContextStub
                return super().find_class(module, name)

        with open(state_path, 'rb') as f:
            return _StubUnpickler(f).load()


def _resolve_context_content(ctx) -> str:
    """Extract content string from a context (dict or LazyContext).

    Handles:
    - v1 dict: ctx['content']
    - v2/v3 dict: ctx['content']
    - v3 LazyContext: ctx.content (property that reads from disk)
    """
    if hasattr(ctx, 'content') and not isinstance(ctx, dict):
        # LazyContext — access .content property
        return ctx.content or ''
    if isinstance(ctx, dict):
        return ctx.get('content', '')
    return str(ctx)


def _resolve_context_path(ctx) -> str:
    """Extract file path from a context (dict or LazyContext)."""
    if hasattr(ctx, 'path') and not isinstance(ctx, dict):
        return ctx.path or 'unknown'
    if isinstance(ctx, dict):
        return ctx.get('path', 'unknown')
    return 'unknown'


def _resolve_context_loaded_at(ctx) -> str:
    """Extract loaded_at from a context (dict or LazyContext)."""
    if hasattr(ctx, 'loaded_at') and not isinstance(ctx, dict):
        return ctx.loaded_at or 'unknown'
    if isinstance(ctx, dict):
        return ctx.get('loaded_at', 'unknown')
    return 'unknown'


def load_rlm_multi_state(state_dir: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load rlm-repl-multi / rlm-v3 state.

    Handles v1 (single context), v2/v3 (named contexts), and v4 (LazyContext).
    """
    state_path = state_dir / 'state.pkl'
    if not state_path.exists():
        return {}

    state = load_rlm_state(state_path)

    # v3/v4: top-level 'contexts' dict (rlm-v3 format)
    if 'contexts' in state and isinstance(state['contexts'], dict) and state['contexts']:
        return state['contexts']

    # v2: globals.contexts (rlm-repl-multi format)
    if 'globals' in state and 'contexts' in state.get('globals', {}):
        return state['globals']['contexts']

    # v1: top-level 'context' (old rlm-repl format)
    context = state.get('context', {})
    if context and 'path' in context:
        name = Path(context['path']).stem
        return {name: state}

    return {}


def extract_context_labels(text: str, window_start: int, window_size: int = 500) -> Dict[str, Any]:
    """
    Extract context labels from text window around a data point.

    Looks for:
    - Product/server type (e.g., "HGX B300 8-GPU server", "GB300 rack")
    - Time periods (e.g., "3Q25", "1Q26E", "FY2026")
    - Figure/table references (e.g., "Figure 2", "Table 1")
    - Units (e.g., "per server", "per rack", "billion", "million")
    """
    start = max(0, window_start - window_size)
    end = min(len(text), window_start + window_size)
    window = text[start:end]

    labels = {
        'product_type': None,
        'time_period': None,
        'figure_ref': None,
        'units': None,
        'scope': None
    }

    # Extract product/server type
    product_patterns = [
        r'(HGX [AB]\d{3} \d+-GPU [Ss]erver)',
        r'(GB\d{3} (?:rack|NVL\d+))',
        r'((?:HGX|GB)\d{3})',
        r'(\d+-GPU server)',
    ]
    for pattern in product_patterns:
        match = re.search(pattern, window)
        if match:
            labels['product_type'] = match.group(1)
            break

    # Extract time period
    time_patterns = [
        r'([1-4]Q\d{2}E?)',  # 3Q25, 1Q26E
        r'(FY\d{4}E?)',      # FY2026E
        r'(\d{4}E)',         # 2026E
        r'(20\d{2})',        # 2025, 2026
    ]
    time_matches = []
    for pattern in time_patterns:
        matches = re.findall(pattern, window)
        time_matches.extend(matches)
    if time_matches:
        # Look for before → after pattern
        if len(time_matches) >= 2:
            labels['time_period'] = f"{time_matches[0]} → {time_matches[1]}"
        else:
            labels['time_period'] = time_matches[0]

    # Extract figure reference
    fig_patterns = [
        r'(Figure \d+)',
        r'(Table \d+)',
        r'(Fig\. \d+)',
    ]
    for pattern in fig_patterns:
        match = re.search(pattern, window, re.IGNORECASE)
        if match:
            labels['figure_ref'] = match.group(1)
            break

    # Extract units
    unit_patterns = [
        r'(per (?:server|rack|unit|quarter|year))',
        r'(\$\w+)',  # $k, $m, $bn
        r'(billion|million|thousand)',
        r'(dollars?|racks?|units?)',
    ]
    for pattern in unit_patterns:
        match = re.search(pattern, window, re.IGNORECASE)
        if match:
            labels['units'] = match.group(1).lower()
            break

    # Extract scope
    scope_patterns = [
        r'(1GW (?:data center|datacenter))',
        r'(per (?:1GW|datacenter|server|rack))',
        r'(total|aggregate|cumulative)',
    ]
    for pattern in scope_patterns:
        match = re.search(pattern, window, re.IGNORECASE)
        if match:
            labels['scope'] = match.group(1)
            break

    return labels


def extract_numbers_with_context(
    content: str,
    source_id: str,
    pdf_path: str
) -> List[Dict[str, Any]]:
    """
    Extract numerical data points with context labels from PDF content.

    This is a basic extraction - in practice, you'd run specific grep queries
    and use those results. This function shows the structure.
    """
    extractions = []
    entry_id = 0

    # Find patterns like "$369k → $408k" or "3,756 → 4,378"
    # This is simplified - real extraction would use targeted grep results
    patterns = [
        r'\$?([\d,]+)k?\s*→\s*\$?([\d,]+)k?',  # $369k → $408k
        r'([\d,]+)\s*→\s*([\d,]+)',             # 3,756 → 4,378
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content):
            entry_id += 1
            match_start = match.start()

            # Extract context labels
            labels = extract_context_labels(content, match_start)

            # Get the matched values
            before_val = match.group(1).replace(',', '')
            after_val = match.group(2).replace(',', '')

            # Try to find what metric this is (look backwards)
            metric_window = content[max(0, match_start - 200):match_start]
            metric_match = re.search(r'([A-Z][A-Za-z0-9\s\-]{3,30}):', metric_window)
            metric = metric_match.group(1).strip() if metric_match else "Unknown"

            extraction = {
                'entry_id': f"{source_id}_{entry_id:03d}",
                'source_id': source_id,
                'pdf_path': pdf_path,
                'metric': metric,
                'product_type': labels['product_type'],
                'time_period': labels['time_period'],
                'figure_ref': labels['figure_ref'],
                'units': labels['units'],
                'scope': labels['scope'],
                'values': {
                    'before': before_val,
                    'after': after_val,
                    'change': None,  # Would calculate if needed
                    'change_pct': None
                },
                'context_snippet': content[max(0, match_start - 100):match_start + 100],
                'char_position': match_start
            }

            extractions.append(extraction)

    return extractions


def extract_tag_from_pdf_name(pdf_name: str) -> str:
    """
    Extract short tag from PDF filename.

    Examples:
        "GFHK - Memory price impact.pdf" → "GFHK"
        "Goldman Sachs ABF shortage.pdf" → "Goldman Sachs"
        "永豐投顧簡報2026_人型機器人.pdf" → "永豐"
    """
    if ' - ' in pdf_name:
        # Split on " - " and take first part
        return pdf_name.split(' - ')[0].strip()
    elif '_' in pdf_name:
        # Split on underscore and take first part
        return pdf_name.split('_')[0].strip()
    else:
        # Take first word or first 20 chars
        first_word = pdf_name.split()[0] if ' ' in pdf_name else pdf_name
        return first_word.replace('.pdf', '').strip()


def build_attribution_map(
    sources: List[Dict[str, Any]],
    extractions: List[Dict[str, Any]],
    manual_synthesis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Auto-generate attribution map from sources and extractions.

    Creates:
    - topics: {topic_name: {primary_source, tag, key_metrics, source_context}}
    - cross_doc_synthesis: Manual synthesis entries if provided
    """
    attribution_map = {
        'topics': {},
        'cross_doc_synthesis': manual_synthesis or {}
    }

    # Group extractions by source_id
    by_source = {}
    for extraction in extractions:
        source_id = extraction['source_id']
        if source_id not in by_source:
            by_source[source_id] = []
        by_source[source_id].append(extraction)

    # Build topic for each source
    for source in sources:
        source_id = source['source_id']
        source_extractions = by_source.get(source_id, [])

        if not source_extractions:
            continue

        # Collect unique metrics
        metrics = set()
        figure_refs = set()
        time_periods = set()

        for ext in source_extractions:
            if ext.get('metric') and ext['metric'] != 'Unknown':
                metrics.add(ext['metric'])
            if ext.get('figure_ref'):
                figure_refs.add(ext['figure_ref'])
            if ext.get('time_period'):
                time_periods.add(ext['time_period'])

        # Determine topic name from source_id or dominant theme
        # For now, use source_id as topic name (can be customized)
        topic_name = source_id.replace('_', ' ').title()

        # Build source context note
        context_parts = []
        if figure_refs:
            context_parts.append(f"Figures: {', '.join(sorted(figure_refs))}")
        if time_periods:
            context_parts.append(f"Time periods: {', '.join(sorted(time_periods))}")

        source_context = '; '.join(context_parts) if context_parts else None

        attribution_map['topics'][topic_name] = {
            'primary_source': source_id,
            'tag': source['tag'],
            'key_metrics': sorted(list(metrics)),
            'source_context': source_context,
            'notes': f"{len(source_extractions)} extractions from this source"
        }

    return attribution_map


def build_cache_from_states(
    states: Dict[str, Dict[str, Any]],
    output_path: Path,
    source_map_path: Optional[Path] = None
) -> None:
    """
    Build extraction cache from RLM states with auto-generated attribution map.

    Args:
        states: Dict of {source_id: state_dict}
        output_path: Where to save cache.json
        source_map_path: Optional path to manual cross-doc synthesis JSON
    """
    cache = {
        'cache_version': '1.0',
        'generated_at': datetime.now().isoformat(),
        'sources': [],
        'extractions': []
    }

    # Process each source
    for source_id, state_or_ctx in states.items():
        # Handle both v1 (full state with 'context' key) and v2+/v3 (context object directly)
        if isinstance(state_or_ctx, dict) and 'context' in state_or_ctx:
            # v1 format: states[id] = full state dict
            ctx = state_or_ctx['context']
        else:
            # v2+/v3 format: states[id] = context dict or LazyContext
            ctx = state_or_ctx

        pdf_path = _resolve_context_path(ctx)
        content = _resolve_context_content(ctx)

        pdf_name = Path(pdf_path).name if pdf_path != 'unknown' else 'unknown'

        # Extract tag from PDF name
        tag = extract_tag_from_pdf_name(pdf_name)

        # Add source info with tag
        source_info = {
            'source_id': source_id,
            'pdf_path': pdf_path,
            'pdf_name': pdf_name,
            'tag': tag,
            'chars_extracted': len(content),
            'loaded_at': _resolve_context_loaded_at(ctx)
        }
        cache['sources'].append(source_info)

        # Extract data with context
        extractions = extract_numbers_with_context(content, source_id, pdf_path)
        cache['extractions'].extend(extractions)

    # Load manual cross-doc synthesis if provided
    manual_synthesis = None
    if source_map_path and source_map_path.exists():
        with open(source_map_path) as f:
            manual_data = json.load(f)
            # If it's the full attribution map format, extract cross_doc_synthesis
            if 'cross_doc_synthesis' in manual_data:
                manual_synthesis = manual_data['cross_doc_synthesis']
            else:
                # Assume the whole file is cross_doc_synthesis
                manual_synthesis = manual_data

    # Auto-generate attribution map
    cache['source_attribution_map'] = build_attribution_map(
        cache['sources'],
        cache['extractions'],
        manual_synthesis
    )

    # Save cache
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(cache, f, indent=2)

    print(f"✓ Cache built: {output_path}")
    print(f"  Sources: {len(cache['sources'])}")
    print(f"  Extractions: {len(cache['extractions'])}")
    print(f"  Topics: {len(cache['source_attribution_map']['topics'])}")


def build_cache_from_grep_results(
    grep_results: List[Dict[str, Any]],
    source_id: str,
    pdf_path: str,
    output_path: Path
) -> None:
    """
    Build cache from explicit grep results (recommended approach).

    Instead of auto-extracting, this takes the results of your targeted
    grep queries and structures them.

    Example usage:
        results = [
            {
                'query': '369|408',
                'matches': [
                    {'match': '369', 'snippet': '...HGX B300...3Q25 ASP...369...', 'char_pos': 1234},
                    {'match': '408', 'snippet': '...1Q26E ASP...408...', 'char_pos': 1250}
                ]
            }
        ]
    """
    cache = {
        'cache_version': '1.0',
        'generated_at': datetime.now().isoformat(),
        'sources': [{
            'source_id': source_id,
            'pdf_path': pdf_path,
            'pdf_name': Path(pdf_path).name
        }],
        'extractions': []
    }

    for result in grep_results:
        for i, match in enumerate(result.get('matches', [])):
            snippet = match.get('snippet', '')
            labels = extract_context_labels(snippet, len(snippet) // 2, window_size=len(snippet))

            extraction = {
                'entry_id': f"{source_id}_{i+1:03d}",
                'source_id': source_id,
                'pdf_path': pdf_path,
                'query': result['query'],
                'matched_text': match.get('match', ''),
                'product_type': labels['product_type'],
                'time_period': labels['time_period'],
                'figure_ref': labels['figure_ref'],
                'units': labels['units'],
                'scope': labels['scope'],
                'context_snippet': snippet,
                'char_position': match.get('char_pos')
            }

            cache['extractions'].append(extraction)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(cache, f, indent=2)

    print(f"✓ Cache built from grep results: {output_path}")
    print(f"  Extractions: {len(cache['extractions'])}")


def find_rlm_state_auto(multi: bool = False) -> Optional[Path]:
    """
    Auto-discover RLM state from common locations.

    Searches in order of likelihood for single-doc or multi-doc state.

    Args:
        multi: If True, search for rlm-repl-multi state, else rlm-repl

    Returns:
        Path to state directory if found, None otherwise
    """
    home = Path.home()

    if multi:
        # Common rlm-repl-multi locations
        search_paths = [
            home / '.claude/rlm_state',  # Most common
            home / '.claude/skills/rlm-v3/scripts/.claude/rlm_state',  # rlm-v3
            home / '.claude/skills/rlm-repl-multi/state',
            home / '.claude/skills/rlm-repl-multi/scripts/state',
            Path('.rlm_state'),  # Local directory
            Path('state'),
        ]
    else:
        # Common rlm-repl / rlm-v3 locations
        search_paths = [
            home / '.claude/rlm_state',
            home / '.claude/skills/rlm-v3/scripts/.claude/rlm_state',  # rlm-v3
            home / '.claude/skills/rlm-repl/scripts/.claude/rlm_state',
            home / '.claude/skills/rlm-repl/state',
            Path('.rlm_state'),
            Path('state'),
        ]

    # Find ALL existing state files and pick the most recently modified one.
    # This ensures the current session's state wins over stale leftovers.
    candidates = []
    for path in search_paths:
        state_file = path / 'state.pkl'
        if state_file.exists():
            mtime = state_file.stat().st_mtime
            candidates.append((mtime, path))

    if not candidates:
        return None

    # Sort by modification time descending (newest first)
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_path = candidates[0][1]

    if len(candidates) > 1:
        print(f"ℹ️  Found {len(candidates)} state locations, using most recent:")
        for mtime, path in candidates:
            from datetime import datetime
            marker = " ← selected" if path == best_path else ""
            print(f"    {path} (modified {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}{marker})")
    else:
        print(f"ℹ️  Auto-discovered state: {best_path}")

    return best_path


def main():
    parser = argparse.ArgumentParser(
        description='Build extraction cache from RLM state for kirk-content-pipeline'
    )
    parser.add_argument(
        '--state-dir',
        type=Path,
        help='RLM state directory (auto-discovers if not specified)'
    )
    parser.add_argument(
        '--multi-state-dir',
        type=Path,
        help='rlm-repl-multi state directory (auto-discovers if not specified)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output path for cache.json'
    )
    parser.add_argument(
        '--synthesis',
        type=Path,
        help='Optional manual cross-doc synthesis JSON (descriptions for synthesized insights)'
    )
    parser.add_argument(
        '--multi',
        action='store_true',
        help='Use rlm-repl-multi state directory instead of rlm-repl'
    )

    args = parser.parse_args()

    # Try to load state(s)
    states = {}
    checked_paths = []

    # Check for rlm-repl-multi state (if --multi flag or --multi-state-dir provided)
    if args.multi or args.multi_state_dir:
        if args.multi_state_dir:
            # Use explicitly provided path
            multi_dir = args.multi_state_dir
        else:
            # Auto-discover
            multi_dir = find_rlm_state_auto(multi=True)

        if multi_dir and multi_dir.exists():
            multi_states = load_rlm_multi_state(multi_dir)
            states.update(multi_states)
            print(f"ℹ️  Loaded {len(multi_states)} contexts from rlm-repl-multi")
        elif multi_dir:
            checked_paths.append(str(multi_dir))

    # Check for single/v3 state (if not multi mode, or if multi found nothing)
    if not states and not args.multi:
        if args.state_dir:
            state_dir = args.state_dir
        else:
            state_dir = find_rlm_state_auto(multi=False)

        if state_dir:
            state_path = state_dir / 'state.pkl'
            if state_path.exists():
                single_state = load_rlm_state(state_path)

                # v3/v4: top-level 'contexts' dict
                if 'contexts' in single_state and isinstance(single_state['contexts'], dict) and single_state['contexts']:
                    ctxs = single_state['contexts']
                    for name, ctx in ctxs.items():
                        pdf_path = _resolve_context_path(ctx)
                        source_id = Path(pdf_path).stem.replace(' ', '_').lower() if pdf_path != 'unknown' else name
                        states[source_id] = ctx
                    print(f"ℹ️  Loaded {len(ctxs)} context(s) from rlm v3+")

                # v2: globals.contexts (rlm-repl-multi format)
                elif 'globals' in single_state and 'contexts' in single_state.get('globals', {}):
                    ctxs = single_state['globals']['contexts']
                    for name, ctx in ctxs.items():
                        pdf_path = _resolve_context_path(ctx)
                        source_id = Path(pdf_path).stem.replace(' ', '_').lower() if pdf_path != 'unknown' else name
                        states[source_id] = ctx
                    print(f"ℹ️  Loaded {len(ctxs)} context(s) from rlm v2")

                # v1: top-level 'context' dict
                elif 'context' in single_state:
                    context = single_state['context']
                    if context and 'path' in context:
                        source_id = Path(context['path']).stem.replace(' ', '_').lower()
                        states[source_id] = single_state
                        print(f"ℹ️  Loaded single context from rlm-repl v1")
            else:
                checked_paths.append(str(state_path))

    if not states:
        print("✗ No RLM state found")
        print("  Auto-discovery searched:")
        # Show all auto-discovery paths
        home = Path.home()
        if args.multi or args.multi_state_dir:
            print("  Multi-doc locations:")
            print(f"    {home / '.claude/rlm_state'}")
            print(f"    {home / '.claude/skills/rlm-v3/scripts/.claude/rlm_state'}")
            print(f"    {home / '.claude/skills/rlm-repl-multi/state'}")
            print(f"    {home / '.claude/skills/rlm-repl-multi/scripts/state'}")
        else:
            print("  Single-doc locations:")
            print(f"    {home / '.claude/rlm_state'}")
            print(f"    {home / '.claude/skills/rlm-v3/scripts/.claude/rlm_state'}")
            print(f"    {home / '.claude/skills/rlm-repl/scripts/.claude/rlm_state'}")
            print(f"    {home / '.claude/skills/rlm-repl/state'}")
        if checked_paths:
            print("  Explicitly checked:")
            for p in checked_paths:
                print(f"    {p}")
        return 1

    # Build cache with auto-generated attribution map
    build_cache_from_states(states, args.output, args.synthesis)

    return 0


if __name__ == '__main__':
    exit(main())

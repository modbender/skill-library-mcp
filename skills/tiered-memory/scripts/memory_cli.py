#!/usr/bin/env python3
"""
Tiered Memory CLI v2.1.0 - EvoClaw Architecture Implementation

Three-tier memory system with LLM-powered search, distillation, and consolidation.
Enhanced with structured metadata extraction, validation, and URL preservation.

Tiers:
  Hot (5KB):  Core memory — identity, owner profile, active context, critical lessons
  Warm (50KB): Scored recent facts with decay — 30-day retention
  Cold (∞):    Turso archive — unlimited, queryable, 10-year retention

Features:
  - LLM-powered tree search and distillation
  - Structured metadata extraction (URLs, commands, paths)
  - Memory completeness validation
  - URL-aware distillation and search
  - Score-based tier placement (>=0.7 Hot, >=0.3 Warm, >=0.05 Cold, <0.05 Frozen)
  - Auto-pruning hot memory (max 20 lessons, 10 events, 10 tasks)
  - Multi-agent support (agent_id scoping)
  - Consolidation modes (quick/daily/monthly/full)
  - Metrics and observability

Usage:
  memory_cli.py store --text "..." --category "..." [--importance 0.7] [--agent-id default]
  memory_cli.py retrieve --query "..." [--llm] [--limit 5] [--agent-id default]
  memory_cli.py distill --text "conversation" [--llm] [--llm-endpoint http://...]
  memory_cli.py consolidate [--mode quick|daily|monthly|full] [--agent-id default]
  memory_cli.py validate [--file PATH] [--agent-id default]
  memory_cli.py extract-metadata --file PATH
  memory_cli.py search-url --url FRAGMENT [--limit 5] [--agent-id default]
  memory_cli.py sync-critical [--agent-id default]
  memory_cli.py metrics [--agent-id default]
  memory_cli.py hot --update key=value [--agent-id default]
  memory_cli.py tree [--show | --add PATH DESC | --remove PATH] [--agent-id default]
"""

import argparse
import json
import os
import sys
import time
import math
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

# ─── Structured Metadata Extraction ───

def extract_structured_metadata(text):
    """
    Extract structured metadata from text: URLs, commands, file paths.
    Returns dict with keys: urls, commands, paths
    """
    metadata = {
        'urls': [],
        'commands': [],
        'paths': []
    }
    
    # Extract URLs - look for http/https or domain patterns
    url_pattern = r'https?://[^\s<>"\')]+|www\.[^\s<>"\')]+|(?:^|\s)([a-z0-9-]+\.(com|org|ai|io|net|dev|app|studio|co)[^\s<>"\')]*)'
    matches = re.finditer(url_pattern, text, re.IGNORECASE | re.MULTILINE)
    for match in matches:
        url = match.group(0).strip()
        if match.lastindex and match.group(match.lastindex):
            # Domain without protocol captured by group
            url = match.group(1)
        # Clean up trailing punctuation
        url = url.rstrip('.,;:!?)')
        # Skip if it looks like a path (starts with /)
        if url.startswith('/'):
            continue
        # Validate URL
        try:
            parsed = urlparse(url if url.startswith('http') else f'https://{url}')
            if parsed.netloc:
                metadata['urls'].append(url if url.startswith('http') else url)
        except:
            pass
    
    # Extract shell commands (lines starting with $ or commands in backticks)
    command_patterns = [
        r'`([^`]+)`',  # Backtick commands
        r'^\$\s+(.+)$',  # Lines starting with $
        r'^(?:sudo\s+)?(?:cd|ls|mkdir|rm|mv|cp|wget|curl|git|docker|npm|pip|python|node|go|rust|cargo|ssh|scp)\s+(.+)$'  # Common commands
    ]
    for pattern in command_patterns:
        for match in re.finditer(pattern, text, re.MULTILINE):
            cmd = match.group(1 if match.lastindex else 0).strip()
            if len(cmd) > 3 and len(cmd) < 200:  # Reasonable command length
                metadata['commands'].append(cmd)
    
    # Extract file paths (Unix-style) - but not URL paths
    path_patterns = [
        r'(/[a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)+)',  # Absolute paths
        r'(~?/[a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)+)',  # Home-relative paths
        r'(\./[a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)*)',  # Relative paths
    ]
    for pattern in path_patterns:
        for match in re.finditer(pattern, text):
            path = match.group(1)
            # Filter out URLs mistakenly matched as paths
            # Check for domain-like patterns (e.g., github.com, docs.comfy.org)
            if not any(x in path for x in ['http://', 'https://', '://']) and \
               not re.search(r'\.(com|org|ai|io|net|dev|app|studio|co)/', path) and \
               len(path) > 5:
                metadata['paths'].append(path)
    
    # Deduplicate
    metadata['urls'] = list(dict.fromkeys(metadata['urls']))[:10]  # Max 10 URLs
    metadata['commands'] = list(dict.fromkeys(metadata['commands']))[:5]  # Max 5 commands
    metadata['paths'] = list(dict.fromkeys(metadata['paths']))[:10]  # Max 10 paths
    
    return metadata


def validate_memory_completeness(daily_notes_path, warm_memory_path=None):
    """
    Validate that daily notes have complete actionable information.
    Returns list of warnings about missing details.
    """
    warnings = []
    
    if not os.path.exists(daily_notes_path):
        return [f"Daily notes file not found: {daily_notes_path}"]
    
    with open(daily_notes_path) as f:
        content = f.read()
    
    # Check for tools mentioned without URLs
    tool_keywords = ['z-image', 'LTX-2', 'ComfyUI', 'SadTalker', 'whisper', 'AnimateDiff', 'Stable Diffusion', 'FLUX']
    for tool in tool_keywords:
        if tool.lower() in content.lower():
            # Check if there's a URL nearby (within 500 chars)
            idx = content.lower().find(tool.lower())
            context = content[max(0, idx-250):idx+250]
            if not re.search(r'https?://|www\.', context, re.IGNORECASE):
                warnings.append(f"Tool '{tool}' mentioned without URL/documentation link")
    
    # Check for commands mentioned without examples
    command_keywords = ['download', 'install', 'configure', 'setup', 'deploy']
    for keyword in command_keywords:
        if keyword in content.lower():
            idx = content.lower().find(keyword)
            context = content[max(0, idx-100):idx+200]
            if not re.search(r'`[^`]+`|\$\s+\w+', context):
                warnings.append(f"Action '{keyword}' mentioned without command example")
    
    # Check for decisions without next steps
    decision_keywords = ['decided', 'chose', 'selected', 'will use']
    for keyword in decision_keywords:
        if keyword in content.lower():
            idx = content.lower().find(keyword)
            context = content[max(0, idx-50):idx+300]
            if not any(word in context.lower() for word in ['next', 'todo', 'action', 'download', 'install', 'configure', 'http']):
                section = content[max(0, idx-100):idx+50]
                warnings.append(f"Decision near '{section[-50:].strip()}...' may lack implementation details")
    
    return warnings

# ─── Configuration ───

def load_config():
    """Load configuration from config.json with sensible defaults."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), 'config.json')
    
    defaults = {
        'agent_id': 'default',
        'hot': {'max_bytes': 5120, 'max_lessons': 20, 'max_events': 10, 'max_tasks': 10},
        'warm': {'max_kb': 50, 'retention_days': 30, 'eviction_threshold': 0.3},
        'cold': {'backend': 'turso', 'retention_years': 10},
        'scoring': {'half_life_days': 30, 'reinforcement_boost': 0.1},
        'tree': {'max_nodes': 50, 'max_depth': 4, 'max_size_bytes': 2048},
        'distillation': {'aggression': 0.7, 'max_distilled_bytes': 100, 'mode': 'rule'},
        'consolidation': {'warm_eviction': 'hourly', 'tree_prune': 'daily', 'tree_rebuild': 'monthly'}
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
                # Merge with defaults
                for key in defaults:
                    if key not in config:
                        config[key] = defaults[key]
                    elif isinstance(defaults[key], dict):
                        for subkey in defaults[key]:
                            if subkey not in config[key]:
                                config[key][subkey] = defaults[key][subkey]
                return config
        except Exception as e:
            print(f"Warning: Failed to load config.json: {e}", file=sys.stderr)
    
    return defaults

CONFIG = load_config()

# ─── Security & Robustness ───

import tempfile
import shutil

# Schema version for compatibility checking
SCHEMA_VERSION = "2.0"

def sanitize_agent_id(agent_id):
    """
    Sanitize agent_id to prevent path traversal attacks.
    Only allows alphanumeric, hyphens, underscores, and 'default'.
    """
    if agent_id == 'default':
        return agent_id
    
    # Remove any path separators and parent directory references
    agent_id = agent_id.replace('/', '').replace('\\', '').replace('..', '')
    
    # Only allow safe characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', agent_id):
        raise ValueError(f"Invalid agent_id: {agent_id}. Only alphanumeric, hyphens, and underscores allowed.")
    
    return agent_id

def atomic_write_json(filepath, data, ensure_version=True):
    """
    Atomically write JSON file using temp file + rename pattern.
    Adds schema version if ensure_version=True and data is a dict.
    """
    # Only add version to dicts (not lists)
    if ensure_version and isinstance(data, dict) and '_schema_version' not in data:
        data = dict(data)  # Copy to avoid mutating original
        data['_schema_version'] = SCHEMA_VERSION
    
    # Write to temp file first
    dir_path = os.path.dirname(filepath)
    os.makedirs(dir_path, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(mode='w', dir=dir_path, delete=False, suffix='.tmp') as tmp:
        json.dump(data, tmp, indent=2)
        tmp_path = tmp.name
    
    try:
        # Atomic rename (on POSIX systems)
        shutil.move(tmp_path, filepath)
    except Exception:
        # Cleanup on failure
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

def load_json_with_version(filepath, expected_version=SCHEMA_VERSION):
    """
    Load JSON file and check schema version.
    Returns (data, is_compatible) tuple.
    """
    if not os.path.exists(filepath):
        return None, True
    
    with open(filepath) as f:
        data = json.load(f)
    
    # Check version if present
    file_version = data.get('_schema_version')
    if file_version and file_version != expected_version:
        print(f"Warning: File {filepath} has version {file_version}, expected {expected_version}", 
              file=sys.stderr)
        return data, False
    
    return data, True

# Turso connection pool (simple implementation)
_turso_pool = {'conn': None, 'last_used': 0, 'ttl': 300}  # 5min TTL

def get_turso_connection(db_url, auth_token):
    """
    Get Turso connection from pool or create new one.
    Reuses connection if less than TTL seconds old.
    """
    global _turso_pool
    
    now = time.time()
    if _turso_pool['conn'] and (now - _turso_pool['last_used']) < _turso_pool['ttl']:
        _turso_pool['last_used'] = now
        return _turso_pool['conn']
    
    # Create new connection
    try:
        import libsql_client
        conn = libsql_client.create_client_sync(url=db_url, auth_token=auth_token)
        _turso_pool['conn'] = conn
        _turso_pool['last_used'] = now
        return conn
    except ImportError:
        print("Error: libsql_client not installed. Run: pip install libsql-client", file=sys.stderr)
        sys.exit(1)

def turso_execute_with_retry(db_url, auth_token, query, params=None, max_retries=3):
    """
    Execute Turso query with exponential backoff retry.
    """
    for attempt in range(max_retries):
        try:
            conn = get_turso_connection(db_url, auth_token)
            if params:
                return conn.execute(query, params)
            else:
                return conn.execute(query)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff: 1s, 2s, 4s
            wait_time = 2 ** attempt
            print(f"Turso query failed (attempt {attempt+1}/{max_retries}): {e}. Retrying in {wait_time}s...",
                  file=sys.stderr)
            time.sleep(wait_time)
            # Invalidate connection on error
            _turso_pool['conn'] = None

# Paths
WORKSPACE = os.environ.get("WORKSPACE", os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
MEMORY_DIR = os.path.join(WORKSPACE, "memory")

def get_agent_paths(agent_id='default'):
    """Get file paths for a specific agent."""
    agent_id = sanitize_agent_id(agent_id)  # Security: prevent path traversal
    agent_dir = os.path.join(MEMORY_DIR, agent_id) if agent_id != 'default' else MEMORY_DIR
    return {
        'warm_file': os.path.join(agent_dir, 'warm-memory.json'),
        'tree_file': os.path.join(agent_dir, 'memory-tree.json'),
        'hot_state_file': os.path.join(agent_dir, 'hot-memory-state.json'),
        'memory_md': os.path.join(WORKSPACE, f'MEMORY-{agent_id}.md' if agent_id != 'default' else 'MEMORY.md'),
        'metrics_file': os.path.join(agent_dir, 'metrics.json'),
        'agent_dir': agent_dir
    }

# ─── Scoring ───

def recency_decay(age_days, half_life=None):
    """Exponential decay: score halves every half_life days."""
    if half_life is None:
        half_life = CONFIG['scoring']['half_life_days']
    return math.exp(-age_days / half_life)

def reinforcement_factor(access_count, boost=None):
    """Reinforcement learning: accessed memories get boosted."""
    if boost is None:
        boost = CONFIG['scoring']['reinforcement_boost']
    return 1.0 + boost * access_count

def calculate_score(importance, created_at, access_count=0):
    """Calculate relevance score: importance × recency × reinforcement."""
    age_days = (time.time() - created_at) / 86400
    decay = recency_decay(age_days)
    reinf = reinforcement_factor(access_count)
    return importance * decay * reinf

def classify_tier(score):
    """Classify score into tier: hot/warm/cold/frozen."""
    if score >= 0.7:
        return 'hot'
    elif score >= 0.3:
        return 'warm'
    elif score >= 0.05:
        return 'cold'
    else:
        return 'frozen'

# ─── Tree Index ───

class MemoryTree:
    """Hierarchical memory index with constraints."""
    
    def __init__(self, tree_file):
        self.tree_file = tree_file
        self.nodes = {}
        self.max_nodes = CONFIG['tree']['max_nodes']
        self.max_depth = CONFIG['tree']['max_depth']
        self.max_size = CONFIG['tree']['max_size_bytes']
        self.load()
    
    def load(self):
        if os.path.exists(self.tree_file):
            with open(self.tree_file) as f:
                self.nodes = json.load(f)
        else:
            self.nodes = {
                'root': {'desc': 'Memory root', 'warm_count': 0, 'cold_count': 0, 
                        'last_access': 0, 'children': []}
            }
    
    def save(self):
        os.makedirs(os.path.dirname(self.tree_file), exist_ok=True)
        
        # Enforce size limit
        serialized = json.dumps(self.nodes)
        if len(serialized) > self.max_size:
            print(f"Warning: Tree size {len(serialized)} exceeds {self.max_size}, pruning...", 
                  file=sys.stderr)
            self._prune_to_fit()
        
        atomic_write_json(self.tree_file, self.nodes, ensure_version=True)
    
    def _prune_to_fit(self):
        """Remove least important nodes to fit size limit."""
        # Score nodes by: warm_count + cold_count + recency
        scored = []
        for path, node in self.nodes.items():
            if path == 'root':
                continue
            score = node.get('warm_count', 0) + node.get('cold_count', 0) * 0.1
            if node.get('last_access', 0) > 0:
                age_days = (time.time() - node['last_access']) / 86400
                score *= recency_decay(age_days, half_life=7)
            scored.append((path, score))
        
        scored.sort(key=lambda x: x[1])
        
        # Remove lowest scored until size fits
        while len(json.dumps(self.nodes)) > self.max_size and scored:
            path_to_remove, _ = scored.pop(0)
            self._remove_node_internal(path_to_remove)
    
    def add_node(self, path, desc):
        """Add a category node to the tree."""
        if len(self.nodes) >= self.max_nodes:
            return False
        
        depth = path.count('/') + 1
        if depth > self.max_depth:
            return False
        
        # Ensure parent exists
        if '/' in path:
            parent_path = path.rsplit('/', 1)[0]
            if parent_path not in self.nodes:
                parent_desc = parent_path.split('/')[-1].replace('_', ' ').title()
                self.add_node(parent_path, parent_desc)
        
        parent_path = path.rsplit('/', 1)[0] if '/' in path else 'root'
        
        if path not in self.nodes:
            self.nodes[path] = {
                'desc': desc[:100],  # Max 100 chars
                'warm_count': 0,
                'cold_count': 0,
                'last_access': 0,
                'children': []
            }
            if parent_path in self.nodes:
                if path not in self.nodes[parent_path].get('children', []):
                    self.nodes[parent_path].setdefault('children', []).append(path)
        
        self.save()
        return True
    
    def remove_node(self, path):
        """Remove a node if it has no data."""
        if path not in self.nodes or path == 'root':
            return False
        
        node = self.nodes[path]
        if node.get('warm_count', 0) > 0 or node.get('cold_count', 0) > 0:
            return False
        
        self._remove_node_internal(path)
        self.save()
        return True
    
    def _remove_node_internal(self, path):
        """Internal removal without save."""
        if path not in self.nodes:
            return
        
        # Remove from parent's children
        parent_path = path.rsplit('/', 1)[0] if '/' in path else 'root'
        if parent_path in self.nodes:
            children = self.nodes[parent_path].get('children', [])
            if path in children:
                children.remove(path)
        
        # Remove children recursively
        for child in list(self.nodes[path].get('children', [])):
            self._remove_node_internal(child)
        
        del self.nodes[path]
    
    def update_counts(self, path, warm_delta=0, cold_delta=0):
        """Update memory counts for a node."""
        if path in self.nodes:
            self.nodes[path]['warm_count'] = max(0, self.nodes[path].get('warm_count', 0) + warm_delta)
            self.nodes[path]['cold_count'] = max(0, self.nodes[path].get('cold_count', 0) + cold_delta)
            self.nodes[path]['last_access'] = time.time()
            self.save()
    
    def prune_dead_nodes(self, max_age_days=60):
        """Remove nodes with no activity in max_age_days."""
        cutoff = time.time() - (max_age_days * 86400)
        to_remove = []
        
        for path, node in self.nodes.items():
            # Skip root and metadata keys
            if path == 'root' or path.startswith('_'):
                continue
            # Skip non-dict entries (e.g., _schema_version)
            if not isinstance(node, dict):
                continue
            
            has_data = node.get('warm_count', 0) > 0 or node.get('cold_count', 0) > 0
            last_access = node.get('last_access', 0)
            is_old = last_access < cutoff
            
            if not has_data and (last_access == 0 or is_old):
                to_remove.append(path)
        
        for path in to_remove:
            self._remove_node_internal(path)
        
        if to_remove:
            self.save()
        
        return len(to_remove)
    
    def show(self):
        """Pretty-print the tree."""
        lines = ["Memory Tree Index", "=" * 50]
        
        def _show(path, indent=0):
            node = self.nodes.get(path, {})
            prefix = "  " * indent
            warm = node.get('warm_count', 0)
            cold = node.get('cold_count', 0)
            desc = node.get('desc', '')
            
            if path == 'root':
                lines.append(f"{prefix}📂 Root (warm:{warm}, cold:{cold})")
            else:
                lines.append(f"{prefix}📁 {path} — {desc}")
                lines.append(f"{prefix}   Memories: warm={warm}, cold={cold}")
            
            for child in sorted(node.get('children', [])):
                _show(child, indent + 1)
        
        _show('root')
        lines.append("")
        lines.append(f"Nodes: {len(self.nodes)}/{self.max_nodes}")
        lines.append(f"Size: {len(json.dumps(self.nodes))} / {self.max_size} bytes")
        return "\n".join(lines)

# ─── Hot Memory (Structured) ───

class HotMemory:
    """Structured core memory with auto-pruning."""
    
    def __init__(self, state_file):
        self.state_file = state_file
        self.max_bytes = CONFIG['hot']['max_bytes']
        self.max_lessons = CONFIG['hot']['max_lessons']
        self.max_events = CONFIG['hot']['max_events']
        self.max_tasks = CONFIG['hot']['max_tasks']
        self.state = {}
        self.load()
    
    def load(self):
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                'identity': {},
                'owner_profile': {},
                'active_context': {'projects': [], 'events': [], 'tasks': []},
                'critical_lessons': []
            }
    
    def save(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        self._enforce_limits()
        atomic_write_json(self.state_file, self.state, ensure_version=True)
    
    def _enforce_limits(self):
        """Auto-prune to stay within limits."""
        # Prune lessons (keep highest importance)
        lessons = self.state.get('critical_lessons', [])
        if isinstance(lessons, list) and len(lessons) > 0:
            # If lessons are dicts with importance
            if isinstance(lessons[0], dict):
                lessons.sort(key=lambda x: x.get('importance', 0.5), reverse=True)
                self.state['critical_lessons'] = lessons[:self.max_lessons]
            else:
                # Plain strings, just truncate
                self.state['critical_lessons'] = lessons[-self.max_lessons:]
        
        # Prune events (keep most recent)
        context = self.state.get('active_context', {})
        if 'events' in context:
            context['events'] = context['events'][-self.max_events:]
        
        # Prune tasks (keep most recent)
        if 'tasks' in context:
            context['tasks'] = context['tasks'][-self.max_tasks:]
        
        # Enforce total size
        serialized = json.dumps(self.state)
        while len(serialized) > self.max_bytes and self.state.get('critical_lessons'):
            # Remove oldest lesson
            self.state['critical_lessons'].pop(0)
            serialized = json.dumps(self.state)
    
    def update(self, key, data):
        """Update a section of hot memory."""
        if key == 'identity':
            self.state.setdefault('identity', {}).update(data)
        elif key == 'owner_profile':
            self.state.setdefault('owner_profile', {}).update(data)
        elif key == 'lesson':
            lessons = self.state.setdefault('critical_lessons', [])
            lesson = {
                'text': data.get('text', ''),
                'category': data.get('category', 'general'),
                'importance': data.get('importance', 0.7),
                'timestamp': time.time()
            }
            lessons.append(lesson)
        elif key == 'event':
            events = self.state.setdefault('active_context', {}).setdefault('events', [])
            events.append({
                'text': data.get('text', ''),
                'timestamp': time.time()
            })
        elif key == 'task':
            tasks = self.state.setdefault('active_context', {}).setdefault('tasks', [])
            tasks.append({
                'text': data.get('text', ''),
                'status': data.get('status', 'pending'),
                'timestamp': time.time()
            })
        elif key == 'project':
            projects = self.state.setdefault('active_context', {}).setdefault('projects', [])
            name = data.get('name', '')
            # Update existing or add new
            existing = [p for p in projects if p.get('name') == name]
            if existing:
                existing[0].update(data)
            else:
                projects.append(data)
        
        self.save()
    
    def generate_memory_md(self):
        """Generate MEMORY.md from hot state."""
        lines = [
            "# MEMORY.md - Long-Term Context",
            "",
            "*Core memory - auto-generated from tiered memory system*",
            "",
            "---",
            ""
        ]
        
        # Identity
        identity = self.state.get('identity', {})
        if identity:
            lines.append("## 🤖 Agent Identity")
            lines.append("")
            for k, v in identity.items():
                lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
            lines.append("")
        
        # Owner Profile
        owner = self.state.get('owner_profile', {})
        if owner:
            lines.append("## 👤 Owner Profile")
            lines.append("")
            for k, v in owner.items():
                if isinstance(v, list):
                    lines.append(f"- **{k.replace('_', ' ').title()}:** {', '.join(str(x) for x in v)}")
                else:
                    lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
            lines.append("")
        
        # Active Context
        context = self.state.get('active_context', {})
        
        if context.get('projects'):
            lines.append("## 💼 Active Projects")
            lines.append("")
            for p in context['projects']:
                lines.append(f"### {p.get('name', 'Unnamed')}")
                if p.get('description'):
                    lines.append(p['description'])
                if p.get('status'):
                    lines.append(f"**Status:** {p['status']}")
                lines.append("")
        
        if context.get('tasks'):
            lines.append("## ✅ Pending Tasks")
            lines.append("")
            for task in context['tasks'][-10:]:
                status = task.get('status', 'pending')
                text = task.get('text', '')
                lines.append(f"- [{status.upper()}] {text}")
            lines.append("")
        
        if context.get('events'):
            lines.append("## 📅 Recent Events")
            lines.append("")
            for event in context['events'][-10:]:
                ts = event.get('timestamp', 0)
                date = datetime.fromtimestamp(ts).strftime('%b %d') if ts else ''
                text = event.get('text', '')
                lines.append(f"- [{date}] {text}")
            lines.append("")
        
        # Critical Lessons
        lessons = self.state.get('critical_lessons', [])
        if lessons:
            lines.append("## 🎯 Critical Lessons")
            lines.append("")
            for lesson in lessons[-20:]:
                if isinstance(lesson, dict):
                    text = lesson.get('text', '')
                    cat = lesson.get('category', '')
                    if cat:
                        lines.append(f"- **[{cat}]** {text}")
                    else:
                        lines.append(f"- {text}")
                else:
                    lines.append(f"- {lesson}")
            lines.append("")
        
        lines.append("---")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        
        content = "\n".join(lines)
        
        # Final size check
        if len(content.encode()) > self.max_bytes:
            print(f"Warning: Generated MEMORY.md ({len(content.encode())} bytes) exceeds {self.max_bytes}", 
                  file=sys.stderr)
        
        return content

# ─── Warm Memory ───

class WarmMemory:
    """Scored recent facts with auto-eviction."""
    
    def __init__(self, warm_file):
        self.warm_file = warm_file
        self.facts = []
        self.max_kb = CONFIG['warm']['max_kb']
        self.max_bytes = self.max_kb * 1024
        self.retention_days = CONFIG['warm']['retention_days']
        self.threshold = CONFIG['warm']['eviction_threshold']
        self.load()
    
    def load(self):
        if os.path.exists(self.warm_file):
            with open(self.warm_file) as f:
                self.facts = json.load(f)
        else:
            self.facts = []
    
    def save(self):
        os.makedirs(os.path.dirname(self.warm_file), exist_ok=True)
        atomic_write_json(self.warm_file, self.facts, ensure_version=True)
    
    def add(self, text, category, importance=0.5, metadata=None):
        """
        Add a fact to warm memory with optional structured metadata.
        
        Args:
            text: Fact text
            category: Category path
            importance: 0.0-1.0
            metadata: Dict with optional keys: urls, commands, paths
        
        Returns:
            fact_id
        """
        fact_id = hashlib.md5(f"{text}{time.time()}".encode()).hexdigest()[:12]
        
        # Extract metadata if not provided
        if metadata is None:
            metadata = extract_structured_metadata(text)
        
        fact = {
            'id': fact_id,
            'text': text,
            'category': category,
            'importance': importance,
            'created_at': time.time(),
            'access_count': 0,
            'score': importance,
            'metadata': metadata  # NEW: structured metadata
        }
        self.facts.append(fact)
        self._recalculate_scores()
        self._enforce_limits()
        self.save()
        return fact_id
    
    def _recalculate_scores(self):
        """Recalculate all scores."""
        for fact in self.facts:
            # Ensure required fields exist
            if 'importance' not in fact:
                fact['importance'] = 0.5  # Default importance
            if 'created_at' not in fact and 'timestamp' in fact:
                fact['created_at'] = fact['timestamp']
            elif 'created_at' not in fact:
                fact['created_at'] = time.time()
            if 'access_count' not in fact:
                fact['access_count'] = 0
            
            fact['score'] = calculate_score(
                fact['importance'],
                fact['created_at'],
                fact.get('access_count', 0)
            )
            fact['tier'] = classify_tier(fact['score'])
    
    def _enforce_limits(self):
        """Evict lowest-scored facts if over size limit."""
        self._recalculate_scores()
        
        while self._size() > self.max_bytes and len(self.facts) > 1:
            self.facts.sort(key=lambda x: x['score'])
            self.facts.pop(0)
    
    def _size(self):
        return len(json.dumps(self.facts).encode())
    
    def evict_expired(self):
        """Remove expired facts. Returns evicted."""
        cutoff = time.time() - (self.retention_days * 86400)
        
        keep = []
        evicted = []
        
        self._recalculate_scores()
        
        for fact in self.facts:
            score = fact['score']
            age = time.time() - fact['created_at']
            
            # Evict if: old AND low score
            if fact['created_at'] < cutoff and score < self.threshold:
                evicted.append(fact)
            else:
                keep.append(fact)
        
        self.facts = keep
        self.save()
        return evicted
    
    def search(self, query, limit=5):
        """Search warm facts by keyword overlap."""
        query_words = set(query.lower().split())
        results = []
        
        self._recalculate_scores()
        
        for fact in self.facts:
            fact_words = set(fact['text'].lower().split())
            cat_words = set(re.split(r'[/_\-]', fact.get('category', '').lower()))
            all_words = fact_words | cat_words
            overlap = len(query_words & all_words)
            
            if overlap > 0:
                relevance = (overlap / max(len(query_words), 1)) * fact['score']
                fact['access_count'] += 1
                results.append({**fact, 'relevance': relevance, 'tier': 'warm'})
        
        results.sort(key=lambda x: x['relevance'], reverse=True)
        self.save()
        return results[:limit]
    
    def get_by_category(self, category, limit=10):
        """Get facts by category prefix."""
        self._recalculate_scores()
        matches = [f for f in self.facts if f.get('category', '').startswith(category)]
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:limit]
    
    def search_by_url(self, url_fragment, limit=5):
        """Search facts by URL fragment."""
        results = []
        for fact in self.facts:
            urls = fact.get('metadata', {}).get('urls', [])
            if any(url_fragment.lower() in url.lower() for url in urls):
                results.append(fact)
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:limit]
    
    def get_all_urls(self):
        """Extract all unique URLs from warm memory."""
        urls = set()
        for fact in self.facts:
            urls.update(fact.get('metadata', {}).get('urls', []))
        return sorted(urls)

# ─── Cold Memory (Turso) ───

def normalize_db_url(db_url):
    """Convert libsql:// to https:// for HTTP API."""
    if db_url.startswith('libsql://'):
        return db_url.replace('libsql://', 'https://', 1)
    return db_url

def cold_store(fact_id, text, category, importance, agent_id, db_url, auth_token):
    """Store a fact in cold storage."""
    import urllib.request
    
    db_url = normalize_db_url(db_url)
    
    payload = {
        'requests': [
            {
                'type': 'execute',
                'stmt': {
                    'sql': """INSERT INTO cold_memories 
                             (id, agent_id, text, category, importance, created_at, access_count)
                             VALUES (?, ?, ?, ?, ?, ?, 0)""",
                    'args': [
                        {'type': 'text', 'value': fact_id},
                        {'type': 'text', 'value': agent_id},
                        {'type': 'text', 'value': text},
                        {'type': 'text', 'value': category},
                        {'type': 'float', 'value': importance},
                        {'type': 'integer', 'value': str(int(time.time()))}
                    ]
                }
            },
            {'type': 'close'}
        ]
    }
    
    try:
        req = urllib.request.Request(
            f"{db_url}/v2/pipeline",
            data=json.dumps(payload).encode(),
            headers={
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Cold store error: {e}", file=sys.stderr)
        return False

def cold_query(query, agent_id, limit, db_url, auth_token):
    """Query cold storage by keyword."""
    import urllib.request
    
    db_url = normalize_db_url(db_url)
    
    words = query.split()[:3]
    conditions = ' OR '.join([f"text LIKE '%{w}%'" for w in words])
    
    payload = {
        'requests': [
            {
                'type': 'execute',
                'stmt': {
                    'sql': f"""SELECT id, text, category, importance, created_at 
                              FROM cold_memories 
                              WHERE agent_id = ? AND ({conditions})
                              ORDER BY importance DESC, created_at DESC 
                              LIMIT ?""",
                    'args': [
                        {'type': 'text', 'value': agent_id},
                        {'type': 'integer', 'value': str(limit)}
                    ]
                }
            },
            {'type': 'close'}
        ]
    }
    
    try:
        req = urllib.request.Request(
            f"{db_url}/v2/pipeline",
            data=json.dumps(payload).encode(),
            headers={
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
            rows = data.get('results', [{}])[0].get('response', {}).get('result', {}).get('rows', [])
            results = []
            for row in rows:
                results.append({
                    'id': row[0]['value'],
                    'text': row[1]['value'],
                    'category': row[2]['value'],
                    'importance': float(row[3]['value']),
                    'created_at': int(row[4]['value']),
                    'tier': 'cold'
                })
            return results
    except Exception as e:
        print(f"Cold query error: {e}", file=sys.stderr)
        return []

def cold_sync_critical(agent_id, hot_state, tree_nodes, db_url, auth_token):
    """Critical sync: hot state + tree to cloud."""
    import urllib.request
    
    db_url = normalize_db_url(db_url)
    
    data = {
        'hot_state': hot_state,
        'tree_nodes': tree_nodes,
        'timestamp': time.time()
    }
    
    payload = {
        'requests': [
            {
                'type': 'execute',
                'stmt': {
                    'sql': """INSERT OR REPLACE INTO critical_state 
                             (agent_id, data, updated_at)
                             VALUES (?, ?, ?)""",
                    'args': [
                        {'type': 'text', 'value': agent_id},
                        {'type': 'text', 'value': json.dumps(data)},
                        {'type': 'integer', 'value': str(int(time.time()))}
                    ]
                }
            },
            {'type': 'close'}
        ]
    }
    
    try:
        req = urllib.request.Request(
            f"{db_url}/v2/pipeline",
            data=json.dumps(payload).encode(),
            headers={
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Critical sync error: {e}", file=sys.stderr)
        return False

def cold_init_tables(db_url, auth_token):
    """Initialize Turso tables."""
    import urllib.request
    
    db_url = normalize_db_url(db_url)
    
    payload = {
        'requests': [
            {
                'type': 'execute',
                'stmt': {
                    'sql': """CREATE TABLE IF NOT EXISTS cold_memories (
                        id TEXT PRIMARY KEY,
                        agent_id TEXT NOT NULL,
                        text TEXT NOT NULL,
                        category TEXT NOT NULL,
                        importance REAL DEFAULT 0.5,
                        created_at INTEGER NOT NULL,
                        access_count INTEGER DEFAULT 0
                    )"""
                }
            },
            {
                'type': 'execute',
                'stmt': {'sql': "CREATE INDEX IF NOT EXISTS idx_cold_agent_category ON cold_memories(agent_id, category)"}
            },
            {
                'type': 'execute',
                'stmt': {'sql': "CREATE INDEX IF NOT EXISTS idx_cold_agent_created ON cold_memories(agent_id, created_at)"}
            },
            {
                'type': 'execute',
                'stmt': {
                    'sql': """CREATE TABLE IF NOT EXISTS critical_state (
                        agent_id TEXT PRIMARY KEY,
                        data TEXT NOT NULL,
                        updated_at INTEGER NOT NULL
                    )"""
                }
            },
            {'type': 'close'}
        ]
    }
    
    try:
        req = urllib.request.Request(
            f"{db_url}/v2/pipeline",
            data=json.dumps(payload).encode(),
            headers={
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Table init error: {e}", file=sys.stderr)
        return False

# ─── Retrieval (Multi-tier with LLM) ───

def retrieve(query, agent_id='default', limit=5, use_llm=False, 
             llm_endpoint=None, db_url=None, auth_token=None):
    """
    Multi-tier retrieval: tree search → warm → cold.
    
    Args:
        query: Search query
        agent_id: Agent identifier
        limit: Max results
        use_llm: Use LLM-powered tree search
        llm_endpoint: HTTP endpoint for LLM
        db_url: Turso URL for cold storage
        auth_token: Turso auth token
    
    Returns:
        list: Retrieved memories with tier labels
    """
    paths = get_agent_paths(agent_id)
    tree = MemoryTree(paths['tree_file'])
    warm = WarmMemory(paths['warm_file'])
    
    results = []
    seen_ids = set()
    
    # 1. Tree search to find relevant categories
    if use_llm and llm_endpoint:
        # Use LLM tree search
        import subprocess
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tree_search = os.path.join(script_dir, 'tree_search.py')
        
        try:
            cmd = [
                'python3', tree_search,
                '--query', query,
                '--tree-file', paths['tree_file'],
                '--mode', 'llm',
                '--llm-endpoint', llm_endpoint,
                '--top-k', str(3)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if result.returncode == 0:
                tree_results = json.loads(result.stdout)
                relevant_paths = [r['path'] for r in tree_results.get('results', [])]
            else:
                # Fallback to keyword
                print("LLM tree search failed, using keyword", file=sys.stderr)
                relevant_paths = [r['path'] for r in tree.nodes.keys() if r != 'root'][:3]
        except Exception as e:
            print(f"Tree search error: {e}", file=sys.stderr)
            relevant_paths = []
    else:
        # Keyword-based tree search
        from tree_search import search_keyword
        tree_results = search_keyword(tree.nodes, query, top_k=3)
        relevant_paths = [r['path'] for r in tree_results]
    
    # 2. Search warm memory (targeted by categories)
    for path in relevant_paths:
        cat_facts = warm.get_by_category(path, limit=limit)
        for fact in cat_facts:
            if fact['id'] not in seen_ids:
                fact['tier'] = 'warm'
                results.append(fact)
                seen_ids.add(fact['id'])
    
    # General warm search
    warm_hits = warm.search(query, limit=limit)
    for fact in warm_hits:
        if fact['id'] not in seen_ids:
            results.append(fact)
            seen_ids.add(fact['id'])
    
    # 3. Cold search if needed
    if len(results) < limit and db_url and auth_token:
        cold_hits = cold_query(query, agent_id, limit - len(results), db_url, auth_token)
        for fact in cold_hits:
            if fact['id'] not in seen_ids:
                results.append(fact)
                seen_ids.add(fact['id'])
    
    # Sort by relevance/score
    results.sort(key=lambda x: x.get('relevance', x.get('score', x.get('importance', 0))), reverse=True)
    return results[:limit]

# ─── Consolidation ───

def _llm_distill_chunk(text, llm_endpoint, tree_categories, api_key=None):
    """
    Use LLM to extract structured facts from a chunk of daily notes.
    Enhanced to preserve URLs and technical details with metadata extraction.
    
    Supports two endpoint formats:
    - Simple: POST {prompt, max_tokens} → {text}
    - OpenAI-compatible: POST {model, messages} → {choices: [{message: {content}}]}
    
    Returns list of dicts: [{text, category, importance, metadata}, ...]
    Returns None on failure (signals caller to use rule-based fallback).
    """
    import urllib.request
    
    cats_str = ", ".join(tree_categories[:20]) if tree_categories else "general, technical, projects, lessons"
    
    # Extract URLs before LLM processing to ensure they're not lost
    extracted_metadata = extract_structured_metadata(text)
    urls_context = ""
    if extracted_metadata['urls']:
        urls_context = f"\n\nIMPORTANT URLs found (MUST include in relevant facts):\n" + "\n".join(f"- {url}" for url in extracted_metadata['urls'][:5])
    
    user_prompt = f"""You are a memory distillation system. Extract important facts from these daily notes.

For each fact, output a JSON object with:
- "text": concise one-line fact (max 150 chars) - INCLUDE URLs if relevant!
- "category": best matching category from [{cats_str}]
- "importance": float 0.0-1.0 
  * 0.9+ for critical: credentials, API keys, URLs for new tools
  * 0.7-0.8 for important: project decisions, completed work, URLs for docs
  * 0.5-0.6 for general: routine updates, meeting notes
- "metadata": object with:
  * "urls": array of relevant URLs (empty if none)
  * "commands": array of shell commands (empty if none)
  * "paths": array of file paths (empty if none)

CRITICAL RULES:
- ALWAYS preserve URLs, especially documentation links, API endpoints, and tool links
- Include commands/paths when they're part of implementation details
- Each fact must be ACTIONABLE (can be used later to complete a task)
- Skip narrative/commentary
- Deduplicate similar facts
{urls_context}

Daily Notes:
{text[:3000]}

Output JSON array (no other text):"""

    # Detect endpoint format: if it ends in /v1/... or contains "openai" or "anthropic", use OpenAI format
    use_openai_format = any(x in llm_endpoint for x in ['/v1/', 'openai', 'integrate.api', 'api.z.ai'])
    
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    if use_openai_format:
        # OpenAI-compatible chat completions
        payload = {
            'messages': [{'role': 'user', 'content': user_prompt}],
            'max_tokens': 1000,
            'temperature': 0.2
        }
        # If endpoint doesn't specify model, some APIs need it
        if 'model' not in llm_endpoint:
            payload['model'] = 'default'
    else:
        # Simple format
        payload = {
            'prompt': user_prompt,
            'max_tokens': 1000,
            'temperature': 0.2
        }
    
    try:
        req = urllib.request.Request(
            llm_endpoint,
            data=json.dumps(payload).encode(),
            headers=headers
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.load(resp)
            
            # Extract response text from various formats
            response_text = ''
            if 'choices' in result and result['choices']:
                # OpenAI format
                choice = result['choices'][0]
                if isinstance(choice.get('message'), dict):
                    response_text = choice['message'].get('content', '')
                elif isinstance(choice.get('text'), str):
                    response_text = choice['text']
            elif 'text' in result:
                response_text = result['text']
            elif 'response' in result:
                response_text = result['response']
            
            if not response_text:
                print("LLM returned empty response", file=sys.stderr)
                return None
            
            # Parse JSON from response (handle markdown code blocks)
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                parts = response_text.split('```')
                if len(parts) >= 3:
                    response_text = parts[1]
            
            # Try to find JSON array in response
            response_text = response_text.strip()
            if not response_text.startswith('['):
                # Try to find the array
                idx = response_text.find('[')
                if idx >= 0:
                    response_text = response_text[idx:]
            
            facts = json.loads(response_text)
            if isinstance(facts, list):
                valid = []
                for f in facts:
                    if isinstance(f, dict) and 'text' in f and len(f['text']) >= 10:
                        # Ensure metadata is present, extract if LLM didn't provide it
                        if 'metadata' not in f or not f['metadata']:
                            f['metadata'] = extract_structured_metadata(f['text'])
                        
                        valid.append({
                            'text': f['text'][:150],
                            'category': f.get('category', 'general'),
                            'importance': max(0.0, min(1.0, float(f.get('importance', 0.6)))),
                            'metadata': f['metadata']
                        })
                return valid
            return []
    
    except Exception as e:
        print(f"LLM distillation failed: {e}", file=sys.stderr)
        return None  # Signal caller to use rule-based fallback


def _rule_based_extract(lines):
    """
    Rule-based fallback: extract facts from daily note lines using patterns.
    Used when LLM distillation is unavailable.
    Enhanced to include metadata extraction.
    
    Returns list of dicts: [{text, category, importance, metadata}, ...]
    """
    decision_re = re.compile(r'\b(decided|agreed|confirmed|fixed|blocked|resolved|deployed|installed|created|published|completed|migrated|downloaded)\b', re.IGNORECASE)
    
    results = []
    current_section = 'general'
    
    for line in lines:
        line = line.strip()
        
        # Track section headers for category context
        if line.startswith('## '):
            section_text = line.lstrip('#').strip().lower()
            if any(w in section_text for w in ['gpu', 'server', 'media', 'video', 'image', 'comfyui', 'ltx']):
                current_section = 'technical/gpu'
            elif any(w in section_text for w in ['evoclaw', 'coverage', 'ci', 'test']):
                current_section = 'projects/evoclaw'
            elif any(w in section_text for w in ['clawchain', 'substrate', 'blockchain']):
                current_section = 'projects/clawchain'
            elif any(w in section_text for w in ['memory', 'tiered', 'consolidat']):
                current_section = 'projects/evoclaw/memory'
            elif any(w in section_text for w in ['cron', 'monitor', 'alert']):
                current_section = 'technical/cron'
            elif any(w in section_text for w in ['twitter', 'social', 'moltbook']):
                current_section = 'social'
            else:
                current_section = 'general'
            continue
        
        fact_text = None
        importance = 0.5
        
        # Completed items
        if line.startswith('- [x]') or line.startswith('- [X]'):
            fact_text = line[5:].strip().lstrip('* ').rstrip()
            importance = 0.7
        # Bold markers (key facts)
        elif line.startswith('**') and '**' in line[2:] and len(line) > 10:
            fact_text = line.replace('**', '').strip().rstrip(':')
            if len(fact_text) < 15:
                continue
            importance = 0.7
        # Decision lines in bullet points
        elif line.startswith('- ') and decision_re.search(line) and len(line) > 30:
            fact_text = line[2:].strip()
            importance = 0.75
        
        if fact_text and len(fact_text) >= 15:
            # Extract metadata from the fact text
            metadata = extract_structured_metadata(fact_text)
            results.append({
                'text': fact_text, 
                'category': current_section, 
                'importance': importance,
                'metadata': metadata
            })
    
    return results


def ingest_daily_notes(days=2, agent_id='default', db_url=None, auth_token=None, dry_run=False, llm_endpoint=None):
    """
    Scan recent daily note files (memory/YYYY-MM-DD.md) and extract facts
    that aren't already in warm memory.
    
    Uses LLM-based distillation as primary method (--llm-endpoint).
    Falls back to rule-based extraction if LLM unavailable or fails.
    """
    paths = get_agent_paths(agent_id)
    warm = WarmMemory(paths['warm_file'])
    tree = MemoryTree(paths['tree_file'])
    
    # Get existing fact texts to avoid duplicates
    existing_texts = set()
    for fact in warm.facts:
        existing_texts.add(fact.get('text', '').lower().strip())
    
    # Get tree categories for LLM context
    tree_categories = [p for p in tree.nodes.keys() if p != 'root']
    
    # Find recent daily note files
    today = datetime.now()
    daily_files = []
    for i in range(days):
        day = today - timedelta(days=i)
        date_str = day.strftime('%Y-%m-%d')
        for f in sorted(os.listdir(MEMORY_DIR)):
            if f.startswith(date_str) and f.endswith('.md'):
                daily_files.append(os.path.join(MEMORY_DIR, f))
    
    daily_files = sorted(set(daily_files))
    
    results = {
        'files_scanned': len(daily_files),
        'mode': 'llm' if llm_endpoint else 'rule',
        'facts_found': 0,
        'facts_stored': 0,
        'facts_skipped': 0,
        'llm_fallbacks': 0,
        'facts': []
    }
    
    for fpath in daily_files:
        try:
            with open(fpath) as f:
                content = f.read()
                lines = content.splitlines()
        except Exception:
            continue
        
        # Try LLM distillation first, fall back to rule-based
        extracted = None
        if llm_endpoint:
            extracted = _llm_distill_chunk(content, llm_endpoint, tree_categories)
            if extracted is None:
                results['llm_fallbacks'] += 1
                extracted = _rule_based_extract(lines)
        else:
            extracted = _rule_based_extract(lines)
        
        for fact_data in extracted:
            fact_text = fact_data['text']
            category = fact_data['category']
            importance = fact_data['importance']
            metadata = fact_data.get('metadata', {})
            
            if len(fact_text) < 10:
                continue
            
            # Skip if duplicate
            if fact_text.lower().strip() in existing_texts:
                results['facts_skipped'] += 1
                continue
            
            results['facts_found'] += 1
            
            if dry_run:
                results['facts'].append({
                    'text': fact_text, 
                    'category': category, 
                    'importance': importance,
                    'metadata': metadata
                })
                continue
            
            # Store fact with metadata
            fact_id = warm.add(fact_text, category, importance, metadata=metadata)
            tree.add_node(category, category.split('/')[-1].replace('_', ' ').title())
            tree.update_counts(category, warm_delta=1)
            existing_texts.add(fact_text.lower().strip())
            results['facts_stored'] += 1
            results['facts'].append({
                'id': fact_id, 
                'text': fact_text, 
                'category': category, 
                'importance': importance,
                'metadata': metadata
            })
            
            # Also store to cold if configured
            if db_url and auth_token:
                cold_store(fact_id, fact_text, category, importance, agent_id, db_url, auth_token)
    
    return results


def consolidate(mode='quick', agent_id='default', db_url=None, auth_token=None, llm_endpoint=None):
    """
    Run consolidation based on mode.
    
    Modes:
        quick: Warm eviction + score recalc
        daily: quick + tree prune + ingest daily notes
        monthly: daily + tree rebuild + cold cleanup
        full: everything with full recalculation
    """
    paths = get_agent_paths(agent_id)
    tree = MemoryTree(paths['tree_file'])
    warm = WarmMemory(paths['warm_file'])
    hot = HotMemory(paths['hot_state_file'])
    
    stats = {
        'mode': mode,
        'agent_id': agent_id,
        'timestamp': datetime.now().isoformat()
    }
    
    # Daily/Monthly/Full: Ingest daily notes FIRST (before eviction)
    # This bridges daily markdown files → tiered memory
    if mode in ['daily', 'monthly', 'full']:
        try:
            ingest_stats = ingest_daily_notes(
                days=2,  # Last 2 days
                agent_id=agent_id,
                db_url=db_url,
                auth_token=auth_token,
                dry_run=False,
                llm_endpoint=llm_endpoint
            )
            stats['ingested_facts'] = ingest_stats.get('stored', 0)
            stats['ingest_skipped'] = ingest_stats.get('skipped', 0)
        except Exception as e:
            stats['ingest_error'] = str(e)
    
    # Quick: Warm eviction
    evicted = warm.evict_expired()
    stats['evicted_warm'] = len(evicted)
    
    # Archive to cold
    archived = 0
    if db_url and auth_token:
        for fact in evicted:
            if cold_store(
                fact['id'],
                fact['text'],
                fact.get('category', 'uncategorized'),
                fact.get('importance', 0.5),
                agent_id,
                db_url,
                auth_token
            ):
                archived += 1
                # Update tree cold count
                tree.update_counts(fact.get('category', 'uncategorized'), cold_delta=1)
    
    stats['archived_cold'] = archived
    
    # Daily: Tree prune
    if mode in ['daily', 'monthly', 'full']:
        pruned = tree.prune_dead_nodes(max_age_days=60)
        stats['pruned_nodes'] = pruned
    
    # Monthly: Tree rebuild (placeholder for LLM)
    if mode in ['monthly', 'full']:
        # TODO: LLM-powered tree rebuild
        # For now, just recalculate all counts
        for path in tree.nodes:
            if path == 'root':
                continue
            warm_facts = warm.get_by_category(path, limit=1000)
            tree.nodes[path]['warm_count'] = len(warm_facts)
        tree.save()
        stats['tree_rebuilt'] = True
    
    # Rebuild hot memory
    content = hot.generate_memory_md()
    with open(paths['memory_md'], 'w') as f:
        f.write(content)
    stats['hot_size_bytes'] = len(content.encode())
    
    # Update metrics
    update_metrics(agent_id, {
        'consolidation_count': 1,
        'last_consolidation': time.time(),
        'evictions_today': stats['evicted_warm']
    })
    
    return stats

# ─── Metrics ───

def load_metrics(agent_id='default'):
    """Load metrics for an agent."""
    paths = get_agent_paths(agent_id)
    if os.path.exists(paths['metrics_file']):
        with open(paths['metrics_file']) as f:
            return json.load(f)
    return {
        'retrieval_count': 0,
        'evictions_today': 0,
        'reinforcements_today': 0,
        'consolidation_count': 0,
        'last_consolidation': 0,
        'context_tokens_saved': 0
    }

def save_metrics(agent_id, metrics):
    """Save metrics for an agent."""
    paths = get_agent_paths(agent_id)
    os.makedirs(paths['agent_dir'], exist_ok=True)
    atomic_write_json(paths['metrics_file'], metrics, ensure_version=True)

def update_metrics(agent_id, updates):
    """Update specific metrics."""
    metrics = load_metrics(agent_id)
    for key, delta in updates.items():
        if key in metrics:
            if isinstance(metrics[key], (int, float)):
                metrics[key] += delta
            else:
                metrics[key] = delta
        else:
            metrics[key] = delta
    save_metrics(agent_id, metrics)

def get_metrics(agent_id='default'):
    """Get comprehensive metrics for an agent."""
    paths = get_agent_paths(agent_id)
    tree = MemoryTree(paths['tree_file'])
    warm = WarmMemory(paths['warm_file'])
    
    metrics = load_metrics(agent_id)
    
    # Calculate current stats
    tree_size = len(json.dumps(tree.nodes))
    warm_size = warm._size()
    
    if os.path.exists(paths['hot_state_file']):
        with open(paths['hot_state_file']) as f:
            hot_size = len(json.dumps(json.load(f)))
    else:
        hot_size = 0
    
    metrics.update({
        'tree_index_size_bytes': tree_size,
        'tree_node_count': len(tree.nodes),
        'hot_memory_size_bytes': hot_size,
        'warm_memory_count': len(warm.facts),
        'warm_memory_size_kb': round(warm_size / 1024, 1),
        'timestamp': datetime.now().isoformat()
    })
    
    return metrics

# ─── CLI ───

def main():
    parser = argparse.ArgumentParser(
        description='Tiered Memory CLI v2.0 - EvoClaw Architecture',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    sub = parser.add_subparsers(dest='command', required=True)
    
    # Common args
    def add_common_args(p):
        p.add_argument('--agent-id', default='default', help='Agent identifier')
        p.add_argument('--db-url', help='Turso database URL')
        p.add_argument('--auth-token', help='Turso auth token')
    
    # store
    p_store = sub.add_parser('store', help='Store a fact in memory')
    p_store.add_argument('--text', required=True)
    p_store.add_argument('--category', required=True)
    p_store.add_argument('--importance', type=float, default=0.5)
    p_store.add_argument('--url', action='append', help='Add URL to metadata (can be used multiple times)')
    p_store.add_argument('--cmd', action='append', dest='shell_command', help='Add shell command to metadata (can be used multiple times)')
    p_store.add_argument('--path', action='append', help='Add file path to metadata (can be used multiple times)')
    add_common_args(p_store)
    
    # retrieve
    p_ret = sub.add_parser('retrieve', help='Search across all tiers')
    p_ret.add_argument('--query', required=True)
    p_ret.add_argument('--limit', type=int, default=5)
    p_ret.add_argument('--llm', action='store_true', help='Use LLM-powered search')
    p_ret.add_argument('--llm-endpoint', help='LLM HTTP endpoint')
    add_common_args(p_ret)
    
    # distill
    p_dist = sub.add_parser('distill', help='Distill conversation to structured fact')
    p_dist.add_argument('--text', help='Raw conversation text')
    p_dist.add_argument('--file', help='Read from file')
    p_dist.add_argument('--llm', action='store_true', help='Use LLM distillation')
    p_dist.add_argument('--llm-endpoint', help='LLM HTTP endpoint')
    p_dist.add_argument('--core-summary', action='store_true', help='Generate core summary')
    
    # consolidate
    p_con = sub.add_parser('consolidate', help='Run consolidation')
    p_con.add_argument('--mode', choices=['quick', 'daily', 'monthly', 'full'], default='quick')
    p_con.add_argument('--llm-endpoint', help='LLM HTTP endpoint for distillation during ingest')
    add_common_args(p_con)
    
    # sync-critical
    p_sync = sub.add_parser('sync-critical', help='Sync hot+tree to cloud')
    add_common_args(p_sync)
    
    # metrics
    p_met = sub.add_parser('metrics', help='Show memory metrics')
    p_met.add_argument('--agent-id', default='default')
    
    # hot
    p_hot = sub.add_parser('hot', help='Manage hot memory')
    p_hot.add_argument('--update', nargs=2, metavar=('KEY', 'JSON'), help='Update hot state')
    p_hot.add_argument('--rebuild', action='store_true', help='Rebuild MEMORY.md')
    add_common_args(p_hot)
    
    # tree
    p_tree = sub.add_parser('tree', help='Manage tree index')
    p_tree.add_argument('--show', action='store_true')
    p_tree.add_argument('--add', nargs=2, metavar=('PATH', 'DESC'))
    p_tree.add_argument('--remove')
    p_tree.add_argument('--prune', action='store_true', help='Remove dead nodes')
    p_tree.add_argument('--agent-id', default='default')
    
    # cold
    p_cold = sub.add_parser('cold', help='Manage cold storage')
    p_cold.add_argument('--init', action='store_true', help='Initialize tables')
    p_cold.add_argument('--query')
    p_cold.add_argument('--limit', type=int, default=10)
    p_cold.add_argument('--agent-id', default='default')
    p_cold.add_argument('--db-url', required=True)
    p_cold.add_argument('--auth-token', required=True)
    
    # ingest-daily
    p_ingest = sub.add_parser('ingest-daily', help='Ingest facts from daily note files (LLM primary, rule-based fallback)')
    p_ingest.add_argument('--days', type=int, default=2, help='How many recent days to scan')
    p_ingest.add_argument('--dry-run', action='store_true', help='Show what would be ingested without storing')
    p_ingest.add_argument('--llm-endpoint', help='LLM HTTP endpoint for distillation (falls back to rule-based if not provided)')
    add_common_args(p_ingest)
    
    # validate
    p_validate = sub.add_parser('validate', help='Validate memory completeness')
    p_validate.add_argument('--file', help='Daily notes file to validate (optional, checks today if not specified)')
    p_validate.add_argument('--agent-id', default='default')
    
    # extract-metadata
    p_extract = sub.add_parser('extract-metadata', help='Extract structured metadata from file')
    p_extract.add_argument('--file', required=True, help='File to extract metadata from')
    
    # search-url
    p_search_url = sub.add_parser('search-url', help='Search facts by URL fragment')
    p_search_url.add_argument('--url', required=True, help='URL fragment to search for')
    p_search_url.add_argument('--limit', type=int, default=5, help='Max results')
    p_search_url.add_argument('--agent-id', default='default')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Commands
    if args.command == 'store':
        paths = get_agent_paths(args.agent_id)
        tree = MemoryTree(paths['tree_file'])
        warm = WarmMemory(paths['warm_file'])
        
        # Build metadata from args or extract from text
        metadata = None
        if (hasattr(args, 'url') and args.url) or \
           (hasattr(args, 'shell_command') and args.shell_command) or \
           (hasattr(args, 'path') and args.path):
            metadata = {
                'urls': getattr(args, 'url', None) or [],
                'commands': getattr(args, 'shell_command', None) or [],
                'paths': getattr(args, 'path', None) or []
            }
        
        # Add to warm with metadata
        fact_id = warm.add(args.text, args.category, args.importance, metadata=metadata)
        
        # Update tree
        tree.add_node(args.category, args.category.split('/')[-1].replace('_', ' ').title())
        tree.update_counts(args.category, warm_delta=1)
        
        # Archive to cold if configured
        cold_synced = False
        if args.db_url and args.auth_token:
            cold_synced = cold_store(
                fact_id, args.text, args.category, args.importance,
                args.agent_id, args.db_url, args.auth_token
            )
            if cold_synced:
                tree.update_counts(args.category, cold_delta=1)
        
        # Get the stored fact to show metadata
        stored_fact = next((f for f in warm.facts if f['id'] == fact_id), None)
        
        print(json.dumps({
            'id': fact_id,
            'category': args.category,
            'tier': classify_tier(args.importance),
            'metadata': stored_fact.get('metadata', {}) if stored_fact else {},
            'cold_synced': cold_synced
        }))
    
    elif args.command == 'retrieve':
        results = retrieve(
            args.query,
            agent_id=args.agent_id,
            limit=args.limit,
            use_llm=args.llm,
            llm_endpoint=args.llm_endpoint,
            db_url=args.db_url,
            auth_token=args.auth_token
        )
        
        update_metrics(args.agent_id, {'retrieval_count': 1})
        print(json.dumps(results, indent=2))
    
    elif args.command == 'distill':
        # Load distiller module
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, script_dir)
        import distiller
        
        if args.file:
            with open(args.file) as f:
                text = f.read()
        elif args.text:
            text = args.text
        else:
            parser.error('--text or --file required')
        
        if args.llm and args.llm_endpoint:
            result = distiller.distill_llm(text, args.llm_endpoint)
        else:
            result = distiller.distill_rule_based(text)
        
        output = {
            'distilled': result,
            'mode': 'llm' if args.llm else 'rule',
            'original_size': len(text),
            'distilled_size': len(json.dumps(result))
        }
        
        if args.core_summary:
            output['core_summary'] = distiller.generate_core_summary(result)
        
        print(json.dumps(output, indent=2))
    
    elif args.command == 'consolidate':
        stats = consolidate(
            mode=args.mode,
            agent_id=args.agent_id,
            db_url=args.db_url,
            auth_token=args.auth_token,
            llm_endpoint=getattr(args, 'llm_endpoint', None)
        )
        print(json.dumps(stats, indent=2))
    
    elif args.command == 'sync-critical':
        paths = get_agent_paths(args.agent_id)
        
        with open(paths['hot_state_file']) as f:
            hot_state = json.load(f)
        
        with open(paths['tree_file']) as f:
            tree_nodes = json.load(f)
        
        if args.db_url and args.auth_token:
            ok = cold_sync_critical(
                args.agent_id,
                hot_state,
                tree_nodes,
                args.db_url,
                args.auth_token
            )
            print(json.dumps({'synced': ok, 'timestamp': datetime.now().isoformat()}))
        else:
            print(json.dumps({'error': 'db-url and auth-token required'}))
    
    elif args.command == 'metrics':
        metrics = get_metrics(args.agent_id)
        print(json.dumps(metrics, indent=2))
    
    elif args.command == 'hot':
        paths = get_agent_paths(args.agent_id)
        hot = HotMemory(paths['hot_state_file'])
        
        if args.update:
            key, data_json = args.update
            data = json.loads(data_json)
            hot.update(key, data)
            
            # Sync to cloud if configured
            if args.db_url and args.auth_token:
                cold_sync_critical(
                    args.agent_id,
                    hot.state,
                    {},
                    args.db_url,
                    args.auth_token
                )
            
            print(json.dumps({'updated': key}))
        
        elif args.rebuild:
            content = hot.generate_memory_md()
            with open(paths['memory_md'], 'w') as f:
                f.write(content)
            print(json.dumps({
                'output': paths['memory_md'],
                'size_bytes': len(content.encode()),
                'max_bytes': hot.max_bytes
            }))
        
        else:
            print(json.dumps(hot.state, indent=2))
    
    elif args.command == 'tree':
        paths = get_agent_paths(args.agent_id)
        tree = MemoryTree(paths['tree_file'])
        
        if args.show:
            print(tree.show())
        elif args.add:
            ok = tree.add_node(args.add[0], args.add[1])
            print(json.dumps({'path': args.add[0], 'added': ok}))
        elif args.remove:
            ok = tree.remove_node(args.remove)
            print(json.dumps({'path': args.remove, 'removed': ok}))
        elif args.prune:
            pruned = tree.prune_dead_nodes()
            print(json.dumps({'pruned': pruned}))
        else:
            print(tree.show())
    
    elif args.command == 'cold':
        if args.init:
            ok = cold_init_tables(args.db_url, args.auth_token)
            print(json.dumps({'initialized': ok}))
        elif args.query:
            results = cold_query(args.query, args.agent_id, args.limit, args.db_url, args.auth_token)
            print(json.dumps(results, indent=2))
    
    elif args.command == 'ingest-daily':
        results = ingest_daily_notes(
            days=args.days,
            agent_id=args.agent_id,
            db_url=args.db_url if hasattr(args, 'db_url') else None,
            auth_token=args.auth_token if hasattr(args, 'auth_token') else None,
            dry_run=args.dry_run,
            llm_endpoint=args.llm_endpoint if hasattr(args, 'llm_endpoint') else None
        )
        print(json.dumps(results, indent=2))
    
    elif args.command == 'validate':
        # Determine file to validate
        if args.file:
            daily_path = args.file
        else:
            # Check today's daily notes
            today = datetime.now().strftime('%Y-%m-%d')
            daily_path = os.path.join(MEMORY_DIR, f'{today}.md')
        
        warnings = validate_memory_completeness(daily_path)
        
        if not warnings:
            print(json.dumps({
                'status': 'ok',
                'message': 'Memory validation passed - no issues found',
                'file': daily_path
            }))
            sys.exit(0)
        
        print(json.dumps({
            'status': 'warning',
            'warnings_count': len(warnings),
            'warnings': warnings,
            'file': daily_path,
            'suggestions': [
                'Add URLs for mentioned tools/services',
                'Include command examples for setup/installation steps',
                'Document next steps after decisions'
            ]
        }, indent=2))
        sys.exit(len(warnings))
    
    elif args.command == 'extract-metadata':
        if not os.path.exists(args.file):
            print(json.dumps({'error': f'File not found: {args.file}'}), file=sys.stderr)
            sys.exit(1)
        
        with open(args.file) as f:
            text = f.read()
        
        metadata = extract_structured_metadata(text)
        
        print(json.dumps({
            'file': args.file,
            'metadata': metadata,
            'summary': {
                'urls_count': len(metadata['urls']),
                'commands_count': len(metadata['commands']),
                'paths_count': len(metadata['paths'])
            }
        }, indent=2))
    
    elif args.command == 'search-url':
        paths = get_agent_paths(args.agent_id)
        warm = WarmMemory(paths['warm_file'])
        
        results = warm.search_by_url(args.url, limit=args.limit)
        
        print(json.dumps({
            'query': args.url,
            'results_count': len(results),
            'results': results
        }, indent=2))

if __name__ == '__main__':
    main()

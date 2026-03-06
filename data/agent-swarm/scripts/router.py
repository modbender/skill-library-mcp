#!/usr/bin/env python3
"""
Agent Swarm | OpenClaw Skill — Task-to-LLM routing for OpenClaw
Version 1.7.6

Orchestrator/router logic aligned with working friday-router backup:
  ~/Desktop/backup .openclaw/workspace/skills/friday-router
- Classification: same keyword sets, vision override, agentic bump, website→CREATIVE,
  COMPLEX→CODE/QUALITY, COMPLEX+FAST handling. CREATIVE tier canonicalized to
  openrouter/moonshotai/kimi-k2.5 (Kimi = Moonshot AI; never Minimax).

Security improvements (v1.7.3+):
- Input validation for task strings (length limits, null bytes; reject prompt-injection patterns)
- Config patch validation (whitelist approach - only tools.exec.host/node)
- Label validation
- Comprehensive security documentation
- Clarified "saves tokens" means cost savings (not token storage)
- Documented file access scope (only tools.exec.* from openclaw.json)
- Declared required environment variables and credentials in metadata (v1.7.5)

Fixed bugs from original intelligent-router:
- Simple indicators now properly invert (high match = SIMPLE, not complex)
- Agentic tasks properly bump to at least MEDIUM tier
- Code keywords actually detected
- Confidence scores vary appropriately

Features:
- Austin's preferred models (Flash, Haiku, GLM-5, Kimi, Grok, etc.)
- Keyword-based routing for obvious matches
- Weighted scoring for nuanced classification
- OpenClaw integration for spawning sub-agents
- Security-focused input validation and sanitization
"""

import argparse
import json
import math
import os
import re
import sys
import time
from pathlib import Path

# OpenClaw imports (if available)
try:
    import openclaw
    HAS_OPENCLAW = True
except ImportError:
    HAS_OPENCLAW = False

# CLI wizard ASCII header (shown for human-readable output only)
CLI_HEADER = r"""
                                            d8b
                                           88P
                                          d88
 .d888b,.d88b,.88P?88   d8P d888b8b   d888888
 ?8b,   88P  `88P'd88   88 d8P' ?88  d8P' ?88
   `?8b ?8b  d88  ?8(  d88 88b  ,88b 88b  ,88b
`?888P' `?888888  `?88P'?8b`?88P'`88b`?88P'`88b
            `?88
              88b
              ?8P
"""

# Security: Input validation and sanitization
def validate_task_string(task):
    """
    Validate and sanitize task string to prevent injection attacks.
    Returns sanitized task string or raises ValueError if invalid.
    """
    if not isinstance(task, str):
        raise ValueError("Task must be a string")
    
    # Check for reasonable length (prevent DoS)
    if len(task) > 10000:  # 10KB limit
        raise ValueError("Task string exceeds maximum length (10KB)")
    
    # Check for null bytes (common injection vector)
    if '\x00' in task:
        raise ValueError("Task string contains null bytes")
    
    # Reject prompt-injection patterns (script tags, protocols, event handlers)
    # so malicious task strings are not passed to sub-agent LLMs.
    suspicious_patterns = [
        (r'<script[^>]*>', "script tags"),
        (r'javascript:', "javascript: protocol"),
        (r'on\w+\s*=', "event-handler attributes (e.g. onclick=)"),
    ]
    for pattern, name in suspicious_patterns:
        if re.search(pattern, task, re.IGNORECASE):
            raise ValueError(
                f"Task string contains disallowed pattern ({name}). "
                "Rephrase the task without executable or markup-injection patterns."
            )

    return task.strip()


def validate_config_patch(patch_json_str):
    """
    Validate that a config patch only modifies safe fields.
    Returns validated patch dict or raises ValueError if unsafe.
    
    Allowed fields:
    - tools.exec.host (must be 'sandbox' or 'node')
    - tools.exec.node (only if host is 'node')
    """
    try:
        patch = json.loads(patch_json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config patch: {e}")
    
    # Only allow modifications to tools.exec
    allowed_paths = {
        ('tools', 'exec', 'host'),
        ('tools', 'exec', 'node'),
    }
    
    def check_path(obj, path=tuple()):
        """Recursively check that only allowed paths are modified."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = path + (key,)
                if current_path not in allowed_paths:
                    # Check if this is a parent of an allowed path
                    is_parent = any(
                        current_path == allowed[:len(current_path)]
                        for allowed in allowed_paths
                    )
                    if not is_parent:
                        raise ValueError(
                            f"Config patch modifies disallowed path: {'.'.join(current_path)}. "
                            f"Only tools.exec.host and tools.exec.node are allowed."
                        )
                check_path(value, current_path)
        elif isinstance(obj, list):
            raise ValueError("Config patch cannot contain arrays")
    
    check_path(patch)
    
    # Validate values
    exec_config = patch.get('tools', {}).get('exec', {})
    host = exec_config.get('host')
    if host and host not in ('sandbox', 'node'):
        raise ValueError(f"tools.exec.host must be 'sandbox' or 'node', got: {host}")
    
    if exec_config.get('host') != 'node' and exec_config.get('node'):
        raise ValueError("tools.exec.node can only be set when host is 'node'")
    
    return patch


def _log_delegation_audit(task: str, tier: str, model_id: str, recommendation: dict):
    """Append one JSONL line to OPENCLAW_HOME/logs/agent-swarm-delegations.jsonl for audit."""
    openclaw_home = os.environ.get("OPENCLAW_HOME") or os.path.expanduser("~/.openclaw")
    log_dir = Path(openclaw_home) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "agent-swarm-delegations.jsonl"
    try:
        entry = {
            "ts": time.time(),
            "task": task[:500] if task else "",
            "tier": tier,
            "model": model_id,
            "reasoning": (recommendation or {}).get("reasoning", ""),
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


# OpenRouter models API: https://openrouter.ai/docs/api-reference/list-available-models
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


def fetch_openrouter_models():
    """
    Fetch current model list from OpenRouter. Returns list of dicts with id, name, canonical_slug.
    Uses no auth (public list). On failure returns empty list and does not raise.
    """
    try:
        import urllib.request
        req = urllib.request.Request(OPENROUTER_MODELS_URL, headers={"User-Agent": "OpenClaw-Agent-Swarm/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return []
    items = data.get("data") if isinstance(data, dict) else []
    if not isinstance(items, list):
        return []
    return [
        {"id": m.get("id", ""), "name": m.get("name", ""), "canonical_slug": m.get("canonical_slug", "")}
        for m in items if isinstance(m, dict) and m.get("id")
    ]


def check_config_models_against_openrouter(config, openrouter_models=None):
    """
    Cross-check config model IDs and routing_rules primaries/fallbacks against OpenRouter.
    Config IDs are expected as openrouter/ provider/model (e.g. openrouter/z-ai/glm-4.7-flash).
    OpenRouter API returns id as provider/model (no openrouter/ prefix).
    Returns: {
      "ok": bool,
      "valid_ids": set of openrouter-prefixed ids that exist on OpenRouter,
      "invalid": [ {"id": "...", "where": "models[]|routing_rules...", "suggested": "openrouter/..." or null }, ... ],
      "openrouter_count": int,
    }
    """
    if openrouter_models is None:
        openrouter_models = fetch_openrouter_models()
    # Valid API ids (provider/model)
    api_ids = {m["id"] for m in openrouter_models}
    # Valid in our format (openrouter/provider/model)
    valid_prefixed = {"openrouter/" + mid for mid in api_ids}
    valid_prefixed.add("openrouter/openrouter/aurora-alpha")  # special case if needed
    invalid = []
    seen = set()

    def check_id(model_id, where):
        if not model_id or model_id in seen:
            return
        seen.add(model_id)
        if model_id in valid_prefixed:
            return
        # Strip prefix and check
        bare = model_id[11:] if model_id.startswith("openrouter/") else model_id
        if bare in api_ids:
            return  # Valid (openrouter/bare or bare both resolve)
        # Find best suggestion: same provider (first path segment)
        suggested = None
        provider = bare.split("/")[0] if "/" in bare else bare
        for m in openrouter_models:
            if m["id"].startswith(provider + "/"):
                suggested = "openrouter/" + m["id"]
                break
        invalid.append({"id": model_id, "where": where, "suggested": suggested})

    for m in config.get("models", []):
        check_id(m.get("id"), "models[]")
    rr = config.get("routing_rules", {})
    for tier, rules in rr.items():
        if not isinstance(rules, dict):
            continue
        for key in ("primary", "fallback"):
            val = rules.get(key)
            if key == "fallback" and isinstance(val, list):
                for v in val:
                    check_id(v, f"routing_rules.{tier}.fallback[]")
            else:
                check_id(val, f"routing_rules.{tier}.{key}")
    default_id = config.get("default_model")
    check_id(default_id, "default_model")

    return {
        "ok": len(invalid) == 0,
        "valid_ids": valid_prefixed,
        "invalid": invalid,
        "openrouter_count": len(openrouter_models),
    }


def get_current_openclaw_config():
    """Read tools.exec.host and tools.exec.node from openclaw.json (no gateway auth)."""
    openclaw_home = os.environ.get("OPENCLAW_HOME") or os.path.expanduser("~/.openclaw")
    config_path = Path(openclaw_home) / "openclaw.json"
    if not config_path.exists():
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    exec_config = config.get("tools", {}).get("exec", {})
    return {
        "tools_exec_host": exec_config.get("host", "sandbox"),
        "tools_exec_node": exec_config.get("node"),
    }


# Canonical model IDs per tier (fixes legacy friday-router wrong id: CREATIVE must be Moonshot Kimi, not Minimax)
# If config or any path returns e.g. openrouter/minimax/kimi-k2.5 for CREATIVE, we override to this.
TIER_CANONICAL_MODEL_ID = {
    "CREATIVE": "openrouter/moonshotai/kimi-k2.5",   # Kimi is Moonshot AI; never use minimax for Kimi
    "RESEARCH": "openrouter/x-ai/grok-4.1-fast",
    "VISION": "openrouter/openai/gpt-4o",
}


class FridayRouter:
    """Austin's intelligent model router with fixed scoring."""
    
    # Simple indicators that suggest SIMPLE/Fast tasks (NOT inverted anymore)
    SIMPLE_KEYWORDS = [
        'check', 'get', 'fetch', 'list', 'show', 'display', 'status',
        'what is', 'how much', 'tell me', 'find', 'search', 'summarize',
        'monitor', 'watch', 'read', 'look', 'simple', 'quick', 'fast'
    ]
    
    # Complex indicators that suggest QUALITY/Code tasks
    COMPLEX_KEYWORDS = [
        'build', 'create', 'implement', 'architect', 'design', 'system',
        'comprehensive', 'thorough', 'complex', 'multi', 'full-stack',
        'authentication', 'authorization', 'database', 'api', 'service'
    ]
    
    # Code-related keywords
    CODE_KEYWORDS = [
        'code', 'function', 'class', 'method', 'debug', 'fix', 'bug',
        'refactor', 'lint', 'test', 'unit', 'integration', 'component',
        'module', 'package', 'library', 'framework', 'import', 'export',
        'react', 'vue', 'angular', 'node', 'python', 'javascript',
        'typescript', 'rust', 'go', 'java', 'api', 'endpoint'
    ]
    
    # Reasoning keywords
    REASONING_KEYWORDS = [
        'prove', 'theorem', 'proof', 'derive', 'logic', 'reason',
        'analyze', 'reasoning', 'step by step', 'why', 'how does',
        'explain', 'mathematical', 'induction', 'deduction'
    ]
    
    # Creative keywords
    CREATIVE_KEYWORDS = [
        'creative', 'write', 'story', 'poem', 'article', 'blog',
        'design', 'UI', 'UX', 'frontend', 'website', 'landing',
        'copy', 'narrative', 'brainstorm', 'idea', 'concept'
    ]
    
    # Research keywords
    RESEARCH_KEYWORDS = [
        'research', 'find', 'search', 'lookup', 'web', 'information',
        'fact', 'review', 'compare', 'vs', 'versus', 'difference',
        'summary of', 'what are', 'best', 'top', 'alternatives'
    ]
    
    # Agentic/action keywords (multi-step tasks)
    AGENTIC_KEYWORDS = [
        'run', 'test', 'fix', 'deploy', 'edit', 'build', 'create',
        'implement', 'execute', 'refactor', 'migrate', 'integrate',
        'setup', 'configure', 'install', 'compile', 'debug'
    ]
    
    def __init__(self, config_path=None):
        """Initialize router with config file."""
        if config_path is None:
            # Default to config.json in parent directory of script
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / 'config.json'
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Removed troubleshooting loop detection and FACEPALM integration
        # Use FACEPALM skill separately if troubleshooting is needed
    
    def _load_config(self):
        """Load and parse configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _keyword_match(self, text, keywords):
        """Count keyword matches (case-insensitive)."""
        text_lower = text.lower()
        return sum(1 for kw in keywords if kw.lower() in text_lower)
    
    def classify_task(self, task_description, return_details=False):
        """
        Classify a task into a tier using keyword matching + scoring.
        
        Returns: FAST, REASONING, CREATIVE, RESEARCH, CODE, QUALITY, or VISION
        
        Security: Validates task_description input.
        """
        # Security: Validate input
        if not isinstance(task_description, str):
            raise ValueError("task_description must be a string")
        if len(task_description) > 10000:
            raise ValueError("task_description exceeds maximum length (10KB)")
        
        text = task_description.lower()
        
        # First, check for exact keyword tier matches (highest priority)
        tier_scores = {}
        
        # Count matches for each tier
        tier_scores['FAST'] = self._keyword_match(task_description, self.SIMPLE_KEYWORDS)
        tier_scores['REASONING'] = self._keyword_match(task_description, self.REASONING_KEYWORDS)
        tier_scores['CREATIVE'] = self._keyword_match(task_description, self.CREATIVE_KEYWORDS)
        tier_scores['RESEARCH'] = self._keyword_match(task_description, self.RESEARCH_KEYWORDS)
        tier_scores['CODE'] = self._keyword_match(task_description, self.CODE_KEYWORDS)
        tier_scores['COMPLEX'] = self._keyword_match(task_description, self.COMPLEX_KEYWORDS)
        
        # Check for vision keywords (highest priority - if image/picture/photo/screenshot present, force VISION)
        vision_keywords = ['image', 'picture', 'photo', 'screenshot', 'visual', 'see', 'describe what']
        vision_matches = self._keyword_match(task_description, vision_keywords)
        tier_scores['VISION'] = vision_matches
        
        # If vision keywords present, this IS a vision task - override other classifications
        if vision_matches > 0:
            return {
                'tier': 'VISION',
                'confidence': min(vision_matches / 3.0, 1.0),
                'tier_scores': {'VISION': vision_matches},
                'is_agentic': False
            }
        
        # Agentic task detection - if multi-step, bump to at least CODE
        agentic_count = self._keyword_match(task_description, self.AGENTIC_KEYWORDS)
        multi_step_patterns = [
            r'\bfirst\b.*\bthen\b', r'\bstep\s+\d+', r'\d+\.\s+\w+',
            r'\bnext\b', r'\bafter\b', r'\bfinally\b', r',\s*then\b'
        ]
        is_multi_step = any(re.search(p, text) for p in multi_step_patterns)
        
        if agentic_count >= 2 or is_multi_step:
            # Multi-step task - ensure at least CODE tier
            tier_scores['CODE'] += 2
            if tier_scores['FAST'] > 0:
                tier_scores['FAST'] = 0  # Override FAST if agentic
        
        # Find best matching tier
        if max(tier_scores.values()) == 0:
            # No keywords matched - default to FAST
            best_tier = 'FAST'
        else:
            best_tier = max(tier_scores, key=tier_scores.get)
        
        # Website/frontend projects → CREATIVE (Kimi k2.5), never CODE
        website_project_keywords = [
            'website', 'web site', 'landing page', 'landing', 'frontend',
            'community site', 'online community', 'build a site', 'new site'
        ]
        if self._keyword_match(task_description, website_project_keywords) > 0:
            best_tier = 'CREATIVE'
        
        # Map COMPLEX to CODE for our tier system
        if best_tier == 'COMPLEX':
            # If also has code keywords, use CODE tier
            if tier_scores['CODE'] > 0:
                best_tier = 'CODE'
            else:
                best_tier = 'QUALITY'
        
        # Special handling: if both COMPLEX and FAST matched, prefer CODE/QUALITY
        if tier_scores['COMPLEX'] > 0 and tier_scores['FAST'] > 0:
            if tier_scores['COMPLEX'] >= tier_scores['FAST']:
                best_tier = 'QUALITY' if tier_scores['COMPLEX'] >= 2 else 'CODE'
        
        # Calculate confidence based on match strength
        max_score = max(tier_scores.values())
        confidence = min(max_score / 5.0, 1.0)  # Cap at 1.0, normalize around 5 matches = 100%
        
        result = {
            'tier': best_tier,
            'confidence': round(confidence, 3),
            'tier_scores': {k: v for k, v in tier_scores.items() if v > 0},
            'is_agentic': agentic_count >= 2 or is_multi_step
        }
        
        if not return_details:
            return result['tier']
        
        return result
    
    def get_default_model(self):
        """Return the default model (Gemini 2.5 Flash). Used for session default and orchestrator."""
        default_id = self.config.get('default_model')
        if not default_id:
            # Fallback: QUALITY tier primary
            tier_rules = self.config.get('routing_rules', {}).get('QUALITY', {})
            default_id = tier_rules.get('primary')
        for m in self.config.get('models', []):
            if m['id'] == default_id:
                return m
        return None
    
    def recommend_model(self, task_description):
        """Classify task and recommend the best model."""
        classification = self.classify_task(task_description, return_details=True)
        tier = classification['tier']
        
        # Get routing rules for this tier
        routing_rules = self.config.get('routing_rules', {})
        tier_rules = routing_rules.get(tier, {})
        
        # Get primary model id; enforce canonical id for critical tiers (e.g. CREATIVE = Moonshot Kimi, not Minimax)
        primary_id = tier_rules.get('primary')
        if tier in TIER_CANONICAL_MODEL_ID:
            canonical_id = TIER_CANONICAL_MODEL_ID[tier]
            if primary_id != canonical_id:
                primary_id = canonical_id
        
        # Find model in config
        model = None
        for m in self.config.get('models', []):
            if m['id'] == primary_id:
                model = m
                break
        
        # Fallback
        fallback = None
        fallback_ids = tier_rules.get('fallback', [])
        if fallback_ids:
            for fb_id in fallback_ids:
                for m in self.config.get('models', []):
                    if m['id'] == fb_id:
                        fallback = m
                        break
        
        return {
            'tier': tier,
            'model': model,
            'fallback': fallback,
            'classification': classification,
            'reasoning': self._explain(tier, classification)
        }
    
    def _explain(self, tier, classification):
        """Provide reasoning for tier selection."""
        explanations = {
            'FAST': 'Simple, quick task - monitoring, checks, summaries',
            'REASONING': 'Logical analysis, math, step-by-step reasoning',
            'CREATIVE': 'Creative writing, design, frontend work',
            'RESEARCH': 'Information lookup, web search, fact-finding',
            'CODE': 'Code generation, debugging, implementation',
            'COMPLEX': 'Code generation, debugging, implementation',  # Maps to CODE
            'QUALITY': 'Complex, comprehensive, architectural work',
            'VISION': 'Image analysis, visual understanding'
        }
        
        explanation = explanations.get(tier, 'General task')
        
        if classification.get('is_agentic'):
            explanation += ' [Multi-step agentic task detected]'
        
        return explanation
    
    def estimate_cost(self, task_description):
        """Estimate cost for a task."""
        result = self.recommend_model(task_description)
        model = result['model']
        
        if not model:
            return {'error': 'No model found for tier'}
        
        # Rough token estimates
        token_estimate = {
            'FAST': {'in': 500, 'out': 200},
            'REASONING': {'in': 2000, 'out': 1500},
            'CREATIVE': {'in': 1500, 'out': 2000},
            'RESEARCH': {'in': 1000, 'out': 500},
            'CODE': {'in': 2000, 'out': 1500},
            'QUALITY': {'in': 5000, 'out': 3000},
            'VISION': {'in': 500, 'out': 500}
        }
        
        tokens = token_estimate.get(result['tier'], {'in': 500, 'out': 200})
        
        input_cost = (tokens['in'] / 1_000_000) * model['input_cost_per_m']
        output_cost = (tokens['out'] / 1_000_000) * model['output_cost_per_m']
        
        return {
            'tier': result['tier'],
            'model': model['alias'],
            'cost': round(input_cost + output_cost, 4),
            'currency': 'USD'
        }
    
    @staticmethod
    def split_into_tasks(message):
        """Split a message into multiple task strings for parallel spawn.
        Splits on ' and ', ' then ', '; ', and ' also '. Returns list of non-empty stripped strings.
        
        Security: Validates input and sanitizes each task.
        """
        if not isinstance(message, str):
            raise ValueError("message must be a string")
        if len(message) > 10000:
            raise ValueError("message exceeds maximum length (10KB)")
        
        if not (message or message.strip()):
            return []
        text = message.strip()
        for sep in [' and ', ' then ', '; ', ' also ']:
            text = text.replace(sep, '\n')
        parts = [p.strip() for p in text.split('\n') if p.strip()]
        # Security: Validate each split task
        validated_parts = []
        for part in (parts if len(parts) > 1 else ([message.strip()] if message.strip() else [])):
            try:
                validated_parts.append(validate_task_string(part))
            except ValueError:
                # Skip invalid parts rather than failing entirely
                continue
        return validated_parts

    def spawn_agent(self, task, session_target='isolated', label=None, required_exec_host='sandbox', required_exec_node=None):
        """Spawn an OpenClaw sub-agent with the appropriate model.
        Optionally checks tools.exec host/node; on mismatch returns needs_config_patch (no exit).
        Always returns one dict: either params+recommendation or needs_config_patch+message+recommended_config_patch.
        
        Security: Validates task input and config patches to prevent injection attacks.
        """
        # Security: Validate and sanitize task input
        try:
            task = validate_task_string(task)
        except ValueError as e:
            raise ValueError(f"Invalid task input: {e}")
        
        # Security: Validate label if provided
        if label:
            if not isinstance(label, str) or len(label) > 100:
                raise ValueError("Label must be a string under 100 characters")
            if '\x00' in label:
                raise ValueError("Label contains null bytes")
        
        # Security: Validate required_exec_host and required_exec_node
        if required_exec_host not in ('sandbox', 'node'):
            raise ValueError(f"required_exec_host must be 'sandbox' or 'node', got: {required_exec_host}")
        
        if required_exec_node and not isinstance(required_exec_node, str):
            raise ValueError("required_exec_node must be a string")
        if required_exec_node and len(required_exec_node) > 200:
            raise ValueError("required_exec_node exceeds maximum length")
        
        current_config = get_current_openclaw_config()
        current_exec_host = current_config["tools_exec_host"] if current_config else "sandbox"
        current_exec_node = current_config["tools_exec_node"] if current_config else None

        if required_exec_host and current_exec_host != required_exec_host:
            msg = (
                f"Task requires exec host '{required_exec_host}' but current config is '{current_exec_host}'. "
                "Apply the recommended config patch (triggers gateway restart if host=node)."
                if required_exec_host == "node"
                else f"Temporarily set default exec host to '{required_exec_host}'."
            )
            # Security: Only allow safe config patches
            patch_dict = {"tools": {"exec": {"host": required_exec_host}}}
            patch = json.dumps(patch_dict)
            # Validate the patch we're generating
            try:
                validate_config_patch(patch)
            except ValueError as e:
                raise ValueError(f"Generated invalid config patch: {e}")
            
            return {
                "needs_config_patch": True,
                "message": msg,
                "recommended_config_patch": patch,
                "params": None,
            }

        if required_exec_host == "node" and required_exec_node and current_exec_node != required_exec_node:
            msg = (
                f"Task requires exec node '{required_exec_node}' but current config is '{current_exec_node}'. "
                "Apply the recommended config patch (triggers gateway restart)."
            )
            # Security: Only allow safe config patches
            patch_dict = {"tools": {"exec": {"host": "node", "node": required_exec_node}}}
            patch = json.dumps(patch_dict)
            # Validate the patch we're generating
            try:
                validate_config_patch(patch)
            except ValueError as e:
                raise ValueError(f"Generated invalid config patch: {e}")
            
            return {
                "needs_config_patch": True,
                "message": msg,
                "recommended_config_patch": patch,
                "params": None,
            }

        recommendation = self.recommend_model(task)
        model = recommendation["model"]
        if not model:
            raise ValueError(f"No model found for tier: {recommendation['tier']}")

        params = {
            "task": task,
            "model": model["id"],
            "sessionTarget": session_target,
        }
        if label:
            params["label"] = label

        return {
            "params": params,
            "recommendation": recommendation,
            "executionContract": {
                "must_delegate": True,
                "required_action": "sessions_spawn",
                "self_execution_forbidden": True,
                "meta_only_exception": True,
            },
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Agent Swarm | OpenClaw Skill - Task-to-LLM routing for OpenClaw.")
    sub = parser.add_subparsers(dest="command", required=True)

    # Common args for classify, score, cost that require a task
    for cmd_name in ["classify", "score", "cost"]:
        p = sub.add_parser(cmd_name, help=f"{cmd_name.capitalize()} task")
        p.add_argument("task", type=str, nargs='+', help="The task description string")
        p.add_argument("--json", action="store_true", help="Output JSON report")

    # Default command
    p_default = sub.add_parser("default", help="Show session default model")
    p_default.add_argument("--json", action="store_true", help="Output JSON report")

    # Models command
    p_models = sub.add_parser("models", help="List all models")
    p_models.add_argument("--json", action="store_true", help="Output JSON report")

    # Check-models: cross-check config against OpenRouter (https://openrouter.ai/models)
    p_check = sub.add_parser("check-models", help="Cross-check/correct model names against OpenRouter")
    p_check.add_argument("--json", action="store_true", help="Output JSON report")
    p_check.add_argument("--fix", action="store_true", help="Update config.json with corrected IDs (backup created)")

    # Spawn command (always exit 0; with --json always one JSON object; needs_config_patch does not exit(1))
    p_spawn = sub.add_parser("spawn", help="Show spawn params for OpenClaw (sessions_spawn)")
    p_spawn.add_argument("task", type=str, nargs='+', help="The task string for the sub-agent")
    p_spawn.add_argument("--json", action="store_true", help="Machine-readable output for sessions_spawn")
    p_spawn.add_argument("--multi", action="store_true", help="Split message into parallel tasks (and / then / ;); output array of spawn params")
    p_spawn.add_argument("--required_exec_host", type=str, default="sandbox", help="Required exec host (sandbox or node)")
    p_spawn.add_argument("--required_exec_node", type=str, default=None, help="Required exec node ID or name if host=node")
    p_spawn.add_argument("--label", type=str, default=None, help="Optional label for the sub-agent session")
    
    args = parser.parse_args()

    # Show ASCII header only for human-readable (non-JSON) output
    if not getattr(args, "json", False):
        print(CLI_HEADER)

    router = FridayRouter()

    task_str = ' '.join(args.task) if 'task' in args and args.task else ""

    if args.command == 'default':
        m = router.get_default_model()
        if not m:
            print("❌ No default model configured (missing default_model or QUALITY primary in config)", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps({"model": m}))
        else:
            print("🎯 Session default model (capable by default):\n")
            print(f"   {m['alias']} ({m['id']})")
            print(f"   Cost: ${m['input_cost_per_m']}/${m['output_cost_per_m']} per M")
            print(f"   Use for: {', '.join(m.get('use_for', []))}")
            print("\n   Simple tasks down-route to FAST tier (e.g. Gemini 2.5 Flash).")

    elif args.command == 'classify':
        result = router.recommend_model(task_str)
        if args.json:
            print(json.dumps(result))
        else:
            print(f"📋 Task: {task_str}")
            print(f"\n🎯 Classification: {result['tier']}")
            print(f"   Confidence: {result['classification']['confidence']:.1%}")
            print(f"   Reasoning: {result['reasoning']}")
            if result['model']:
                m = result['model']
                print(f"\n🤖 Recommended Model:")
                print(f"   {m['alias']} ({m['id']})")
                print(f"   Cost: ${m['input_cost_per_m']}/${m['output_cost_per_m']} per M")
                print(f"   Use for: {', '.join(m.get('use_for', []))}")
            if result['fallback']:
                fb = result['fallback']
                print(f"\n🔄 Fallback: {fb['alias']} ({fb['id']})")

    elif args.command == 'score':
        result = router.classify_task(task_str, return_details=True)
        if args.json:
            print(json.dumps(result))
        else:
            print(f"📋 Task: {task_str}")
            print(f"\n🎯 Tier: {result['tier']}")
            print(f"   Confidence: {result['confidence']:.1%}")
            print(f"   Agentic: {'Yes' if result['is_agentic'] else 'No'}")
            
            print(f"\n📊 Tier Scores:")
            for tier, score in sorted(result['tier_scores'].items(), key=lambda x: x[1], reverse=True):
                bar = '█' * score
                print(f"   {tier:10} {bar} ({score})")

    elif args.command == 'cost':
        result = router.estimate_cost(task_str)
        if args.json:
            print(json.dumps(result))
        else:
            if 'error' in result:
                print(f"❌ Error: {result['error']}", file=sys.stderr)
            else:
                print(f"📋 Task: {task_str}")
                print(f"\n💰 Cost Estimate:")
                print(f"   Tier: {result['tier']}")
                print(f"   Model: {result['model']}")
                print(f"   Est. Cost: ${result['cost']} {result['currency']}")

    elif args.command == 'models':
        if args.json:
            print(json.dumps(router.config.get('models', [])))
        else:
            print("📦 Configured Models:\n")
            for model in router.config.get('models', []):
                print(f"  {model['alias']:20} [{model['tier']:8}] {model['id']}")
                print(f"                         ${model['input_cost_per_m']}/${model['output_cost_per_m']}/M")

    elif args.command == 'check-models':
        report = check_config_models_against_openrouter(router.config)
        if args.json:
            out = {
                "ok": report["ok"],
                "openrouter_models_count": report["openrouter_count"],
                "invalid": report["invalid"],
            }
            print(json.dumps(out, indent=2))
        else:
            print("🔗 OpenRouter model check (https://openrouter.ai/models)\n")
            print(f"   Fetched {report['openrouter_count']} models from OpenRouter.")
            if report["ok"]:
                print("   ✅ All config model IDs match OpenRouter.")
            else:
                print(f"   ⚠️  {len(report['invalid'])} ID(s) not found or need correction:\n")
                for inv in report["invalid"]:
                    sug = f" → use {inv['suggested']}" if inv.get("suggested") else " (no suggestion)"
                    print(f"      {inv['id']}  [{inv['where']}]{sug}")
                if getattr(args, "fix", False):
                    replacements = {e["id"]: e["suggested"] for e in report["invalid"] if e.get("suggested")}
                    if not replacements:
                        print("\n   No auto-fix available (no suggestions).")
                    else:
                        backup = router.config_path.with_suffix(router.config_path.suffix + ".bak.openrouter")
                        with open(router.config_path, "r", encoding="utf-8") as f:
                            config_data = json.load(f)
                        with open(backup, "w", encoding="utf-8") as f:
                            json.dump(config_data, f, indent=2)
                        def replace_ids(obj):
                            if isinstance(obj, dict):
                                for k, v in list(obj.items()):
                                    if isinstance(v, str) and v in replacements:
                                        obj[k] = replacements[v]
                                    else:
                                        replace_ids(v)
                            elif isinstance(obj, list):
                                for i, v in enumerate(obj):
                                    if isinstance(v, str) and v in replacements:
                                        obj[i] = replacements[v]
                                    else:
                                        replace_ids(v)
                        replace_ids(config_data)
                        with open(router.config_path, "w", encoding="utf-8") as f:
                            json.dump(config_data, f, indent=2)
                        print(f"\n   ✅ Applied {len(replacements)} correction(s). Backup: {backup}")
                else:
                    print("\n   Run with --fix to update config.json (backup created).")
        if not report["ok"] and not getattr(args, "fix", False):
            sys.exit(1)

    elif args.command == 'spawn':
        if not task_str:
            print("❌ Error: spawn requires a task string", file=sys.stderr)
            sys.exit(1)

        if getattr(args, 'multi', False):
            # Parallel tasks: split message, spawn each, output array
            try:
                tasks = FridayRouter.split_into_tasks(task_str)
            except ValueError as e:
                error_msg = f"❌ Error splitting tasks: {str(e)}"
                if args.json:
                    print(json.dumps({"error": error_msg, "type": "ValueError"}))
                else:
                    print(error_msg, file=sys.stderr)
                sys.exit(1)
            if not tasks:
                tasks = [task_str]
            results = []
            config_patch_result = None
            for i, one_task in enumerate(tasks):
                try:
                    spawn_result = router.spawn_agent(
                        task=one_task,
                        label=args.label or (f"parallel-{i+1}" if len(tasks) > 1 else None),
                        required_exec_host=args.required_exec_host,
                        required_exec_node=args.required_exec_node,
                    )
                except ValueError as e:
                    error_msg = f"❌ Validation error for task {i+1}: {str(e)}"
                    if args.json:
                        print(json.dumps({"error": error_msg, "task_index": i, "type": "ValueError"}))
                    else:
                        print(error_msg, file=sys.stderr)
                        print(f"   Task: {one_task[:100]}...", file=sys.stderr)
                    sys.exit(1)
                except Exception as e:
                    import traceback
                    error_msg = f"❌ Unexpected error spawning task {i+1}: {type(e).__name__}: {str(e)}"
                    if args.json:
                        print(json.dumps({
                            "error": error_msg,
                            "task_index": i,
                            "type": type(e).__name__,
                            "traceback": traceback.format_exc() if not getattr(sys, 'ps1', None) else None
                        }))
                    else:
                        print(error_msg, file=sys.stderr)
                        print(f"   Task: {one_task[:100]}...", file=sys.stderr)
                        if not getattr(sys, 'ps1', None):  # Not in interactive mode
                            print("\nFull traceback:", file=sys.stderr)
                            traceback.print_exc(file=sys.stderr)
                    sys.exit(1)
                if spawn_result.get("needs_config_patch"):
                    config_patch_result = spawn_result
                    break
                results.append({
                    "task": spawn_result["params"]["task"],
                    "model": spawn_result["params"]["model"],
                    "sessionTarget": spawn_result["params"]["sessionTarget"],
                })
                if spawn_result["params"].get("label"):
                    results[-1]["label"] = spawn_result["params"]["label"]
            if config_patch_result:
                if args.json:
                    print(json.dumps(config_patch_result))
                else:
                    print("🚧 Configuration required!\n")
                    print(f"   {config_patch_result['message']}\n")
                    print(f"   Recommended patch: {config_patch_result['recommended_config_patch']}")
            elif args.json:
                for r in results:
                    _log_delegation_audit(
                        task=r.get("task", ""),
                        tier="",
                        model_id=r.get("model", ""),
                        recommendation={"reasoning": "parallel"},
                    )
                print(json.dumps({
                    "parallel": True,
                    "spawns": results,
                    "count": len(results),
                    "executionContract": {
                        "must_delegate": True,
                        "required_action": "sessions_spawn",
                        "self_execution_forbidden": True,
                        "meta_only_exception": True,
                    },
                }))
            else:
                print(f"📋 Parallel tasks ({len(results)}):\n")
                for i, r in enumerate(results, 1):
                    print(f"   {i}. {r['task'][:50]}{'...' if len(r['task']) > 50 else ''} → {r['model'].split('/')[-1]}")
        else:
            try:
                spawn_result = router.spawn_agent(
                    task=task_str,
                    label=args.label,
                    required_exec_host=args.required_exec_host,
                    required_exec_node=args.required_exec_node,
                )
            except ValueError as e:
                error_msg = f"❌ Validation error: {str(e)}"
                if args.json:
                    print(json.dumps({"error": error_msg, "type": "ValueError"}))
                else:
                    print(error_msg, file=sys.stderr)
                    print(f"\n   Task: {task_str[:100]}...", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                import traceback
                error_msg = f"❌ Unexpected error in spawn_agent: {type(e).__name__}: {str(e)}"
                if args.json:
                    print(json.dumps({
                        "error": error_msg,
                        "type": type(e).__name__,
                        "traceback": traceback.format_exc() if not getattr(sys, 'ps1', None) else None
                    }))
                else:
                    print(error_msg, file=sys.stderr)
                    if not getattr(sys, 'ps1', None):  # Not in interactive mode
                        print("\nFull traceback:", file=sys.stderr)
                        traceback.print_exc(file=sys.stderr)
                sys.exit(1)

            if spawn_result.get("needs_config_patch"):
                if args.json:
                    print(json.dumps(spawn_result))
                else:
                    print("🚧 Configuration required!\n")
                    print(f"   {spawn_result['message']}\n")
                    print(f"   Recommended patch: {spawn_result['recommended_config_patch']}")
                    print("   Then retry spawn after gateway restarts if needed.")
            else:
                rec = spawn_result.get("recommendation", {})
                if args.json:
                    _log_delegation_audit(
                        task=task_str,
                        tier=rec.get("tier", ""),
                        model_id=spawn_result["params"].get("model", ""),
                        recommendation=rec,
                    )
                if args.json:
                    out = {k: v for k, v in spawn_result["params"].items()}
                    out["recommendation"] = spawn_result["recommendation"]
                    out["executionContract"] = spawn_result.get("executionContract", {
                        "must_delegate": True,
                        "required_action": "sessions_spawn",
                        "self_execution_forbidden": True,
                        "meta_only_exception": True,
                    })
                    print(json.dumps(out))
                else:
                    print(f"📋 Task: {task_str}")
                    print(f"\n🚀 OpenClaw Spawn Params:")
                    print(f"   model: {spawn_result['params']['model']}")
                    print(f"   sessionTarget: {spawn_result['params']['sessionTarget']}")
                    print(f"\n📦 Full recommendation:")
                    print(f"   Tier: {spawn_result['recommendation']['tier']}")
                    print(f"   Model: {spawn_result['recommendation']['model']['alias']}")

    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    import traceback
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        error_msg = f"❌ Error in router.py: {type(e).__name__}: {str(e)}"
        print(error_msg, file=sys.stderr)
        if not getattr(sys, 'ps1', None):  # Not in interactive mode
            print("\nFull traceback:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        sys.exit(1)

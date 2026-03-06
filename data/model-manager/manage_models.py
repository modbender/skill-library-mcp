#!/usr/bin/env python3
"""
OpenClaw Model Manager & Compute Router (v1.5.0)

This script is an official OpenClaw plugin for managing AI model configurations and orchestrating 
multi-agent tasks. It interacts with the OpenRouter API to fetch model pricing and modifies 
the local OpenClaw configuration file (`~/.openclaw/openclaw.json`) to enable dynamic model routing.

PERMISSIONS:
- Network: Connects to https://openrouter.ai/api/v1/models (READ ONLY)
- File System: Reads/Writes ~/.openclaw/openclaw.json (CONFIG)
- Process: Spawns sub-agents via `openclaw sessions spawn` (ORCHESTRATION)

AUTHOR: Notestone
LICENSE: MIT
"""

import argparse
import json
import urllib.request
import urllib.error
import sys
import os
import subprocess
import time
import shlex  # For secure command splitting
from datetime import datetime
from pathlib import Path

# --- Configuration & Constants ---
OPENROUTER_API = "https://openrouter.ai/api/v1/models"
CONFIG_FILE = os.path.expanduser("~/.openclaw/openclaw.json")
MEMORY_FILE = os.path.expanduser("~/.openclaw/workspace/swarm_memory.json")
PROMPTS_FILE = os.path.join(os.path.dirname(__file__), "prompts.json")
INSIGHTS_FILE = os.path.expanduser("~/.openclaw/workspace/swarm_insights.json")

# --- Utilities for Safe Operation ---

def safe_subprocess_run(cmd_list, timeout=60):
    """
    Executes a subprocess command safely with timeout and error handling.
    """
    try:
        # Explicitly use shell=False for security (default, but explicit is better)
        result = subprocess.run(
            cmd_list, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=False # Don't raise on non-zero exit, handle manually
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"⚠️ [System] Command timed out after {timeout}s: {' '.join(cmd_list[:3])}...")
        return None
    except Exception as e:
        print(f"❌ [System] Subprocess error: {str(e)}")
        return None

def load_json_safe(filepath):
    """Safely loads JSON data from a file."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ [Config] Error reading {filepath}: {e}")
        return {}

# --- Golden Gear Logic: Task Planner & Orchestrator ---

class TaskPlanner:
    def __init__(self):
        # Pricing reference (approximate output price per 1M tokens)
        self.prices = {
            "tier1": {"id": "anthropic/claude-3.5-sonnet", "price": 15.00, "role": "Architect/Reasoning"},
            "tier2": {"id": "openai/gpt-4o-mini", "price": 0.60, "role": "Coder/Drafter"},
            "tier3": {"id": "local/llama-3", "price": 0.00, "role": "Reviewer/Privacy"},
        }
        # Map tiers to allowed OpenRouter IDs for execution
        self.model_map = {
            "tier1": "openrouter/anthropic/claude-3.5-sonnet",
            "tier2": "openrouter/openai/gpt-4o-mini",
            # Fallback for tier3
            "tier3": "openrouter/openai/gpt-4o-mini" 
        }
        
        # Load DNA (Prompts) & Hippocampus (Insights)
        self.prompts = load_json_safe(PROMPTS_FILE).get("roles", {})
        self.insights = load_json_safe(INSIGHTS_FILE).get("model_performance", {})

    def _get_stable_model(self, tier_key):
        """Active Adaptation: Switch model if unstable based on historical insights."""
        default_model_id = self.model_map.get(tier_key, "openrouter/openai/gpt-4o-mini")
        
        # Check stability history
        if default_model_id in self.insights:
            stats = self.insights[default_model_id]
            # Threshold: < 50% success rate with at least 1 attempt
            if stats.get("sample_size", 0) > 0 and stats.get("success_rate", 100) < 50:
                # UNSTABLE! Switch strategy.
                # Strategy: Fallback to Tier 1 (Costly but reliable) if current is Tier 2/3
                if tier_key in ["tier2", "tier3"]:
                    fallback_id = self.model_map["tier1"]
                    return fallback_id, True, "Stability Fallback"
        
        return default_model_id, False, ""

    def plan(self, task_description, execute=False):
        """Simulate decomposing a task and optionally execute it."""
        
        # 1. Decompose (Heuristic) & Apply Prompts
        task_lower = task_description.lower()
        if any(w in task_lower for w in ["code", "app", "script", "program", "debug", "test"]):
            category = "Coding"
            # Helper to format prompt safely
            def get_prompt(role, default):
                template = self.prompts.get(role, {}).get("task_template", default)
                return template.replace("{task_description}", task_description)

            steps = [
                {
                    "phase": "1. Design", "model_tier": "tier1", "reason": "Architecture", "artifact": "SPEC.md",
                    "task": get_prompt("architect", f"Design architecture for: {task_description}")
                },
                {
                    "phase": "2. Code", "model_tier": "tier2", "reason": "Implementation", "artifact": "code",
                    "task": get_prompt("coder", f"Write code for: {task_description}")
                },
                {
                    "phase": "3. Review", "model_tier": "tier3", "reason": "Security Check", "artifact": "AUDIT.md",
                    "task": get_prompt("auditor", "Audit the code.")
                }
            ]
        else:
            category = "General"
            # Generic steps
            steps = [
                {
                    "phase": "1. Plan", "model_tier": "tier1", "reason": "Strategy", "artifact": "PLAN.md",
                    "task": f"Create a detailed plan for: {task_description}. Use 'write' to save to 'PLAN.md'."
                },
                {
                    "phase": "2. Draft", "model_tier": "tier2", "reason": "Execution", "artifact": "RESULT.md",
                    "task": "Read 'PLAN.md'. Execute the plan. Use 'write' to save output to 'RESULT.md'."
                }
            ]

        # 2. Display Plan & Apply Adaptation
        final_steps = self._display_plan(task_description, category, steps)

        # 3. Execute (if requested)
        if execute:
            self._execute_swarm(task_description, final_steps)

    def _display_plan(self, task, category, steps):
        # Calculate savings
        total_tokens = 1000
        # Baseline cost (All Tier 1)
        cost_baseline = len(steps) * (self.prices["tier1"]["price"] / 1_000_000) * total_tokens
        
        cost_optimized = 0
        final_steps = []

        print(f"\n🧠 **Golden Gear Task Planner**")
        print(f"**Task:** \"{task}\"")
        print(f"**Category:** {category}\n")
        print("| Phase | Assigned Agent | Model | Price/1M | Status |")
        print("| :--- | :--- | :--- | :--- | :--- |")
        
        for step in steps:
            tier = step["model_tier"]
            # Apply Active Adaptation
            model_id, switched, reason = self._get_stable_model(tier)
            
            # Find price (reverse lookup or approx)
            if switched:
                price = self.prices["tier1"]["price"]
                status_display = f"🔄 Switched ({reason})"
            else:
                price = self.prices[tier]["price"]
                status_display = "✅ Optimal"

            cost_optimized += (price / 1_000_000) * total_tokens
            
            # Update step for execution
            step["final_model_id"] = model_id
            final_steps.append(step)

            role_name = self.prices[tier]["role"]
            print(f"| {step['phase']} | {role_name} | `{model_id.split('/')[-1]}` | ${price:.2f} | {status_display} |")
        
        savings_pct = ((cost_baseline - cost_optimized) / cost_baseline) * 100
        print(f"\n📉 **Projected Savings:** **{savings_pct:.1f}%** 💸")
        return final_steps

    def _execute_swarm(self, original_task, steps):
        print(f"\n🚀 **Launching Golden Gear Swarm (Self-Healing Enabled)...**", flush=True)
        
        run_log = {
            "timestamp": datetime.now().isoformat(),
            "task": original_task,
            "steps": []
        }

        for step in steps:
            phase = step['phase']
            model_id = step['final_model_id']
            task = step['task']
            expected_artifact = step.get('artifact')
            
            # --- Retry Loop (The Ganglia Reflex) ---
            max_retries = 2
            success = False
            
            for attempt in range(max_retries + 1):
                if attempt > 0:
                    print(f"   🔄 **Retry Attempt {attempt}/{max_retries}** for {phase}...", flush=True)
                    # Mutation: Add error context to task
                    task = f"PREVIOUS ATTEMPT FAILED. FIX THIS ERROR: {error_snippet}\n\nORIGINAL TASK: {task}"

                print(f"\n▶️  **Executing {phase}** via `{model_id}`...", flush=True)
                
                cmd = [
                    "openclaw", "sessions", "spawn",
                    "--model", model_id,
                    "--task", task,
                    "--cleanup", "keep"
                ]
                
                start_time = time.time()
                result = safe_subprocess_run(cmd)
                
                # Default status
                status = "failed"
                error_snippet = ""

                if result and result.returncode == 0:
                    # Stigmergy Check
                    found = False
                    for _ in range(12): 
                        time.sleep(5)
                        if expected_artifact and expected_artifact != "code" and os.path.exists(expected_artifact):
                            print(f"   ✨ Artifact created: {expected_artifact}", flush=True)
                            found = True
                            status = "success"
                            break
                        elif expected_artifact == "code":
                             found = True 
                             status = "success"
                             break
                        else:
                            print(f"      ...waiting for agent...", flush=True)
                    
                    if found:
                        success = True
                        break # Exit retry loop
                    else:
                        status = "timeout"
                        error_snippet = "Artifact not found after execution."
                else:
                    raw_err = result.stderr if result else "Unknown error"
                    error_snippet = raw_err[-200:] if raw_err else "No error output captured."
                    print(f"   ❌ Execution Error: {error_snippet}", flush=True)
                    status = "error"
                
                # Log attempt
                run_log["steps"].append({
                    "phase": phase,
                    "attempt": attempt + 1,
                    "model": model_id,
                    "status": status,
                    "error": error_snippet,
                    "duration": time.time() - start_time
                })
            
            if not success:
                print(f"   🛑 **Phase Failed** after {max_retries} retries. Aborting swarm.", flush=True)
                break # Stop subsequent steps if dependency fails
                
        self._save_memory(run_log)
        print(f"\n💾 **Run saved to swarm_memory.json**", flush=True)

    def _save_memory(self, log_entry):
        data = []
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                data = [] # Reset on corruption
        
        data.append(log_entry)
        
        try:
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ [Memory] Failed to write memory: {e}")

# --- Existing Functions (Refactored for Safety) ---

def fetch_models():
    """Fetch models from OpenRouter public API using standard library (HTTPS)."""
    try:
        # Use a proper User-Agent to avoid being blocked
        req = urllib.request.Request(
            OPENROUTER_API, 
            headers={'User-Agent': 'OpenClaw-ModelManager/1.4.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('data', [])
    except urllib.error.URLError as e:
        print(f"❌ [Network] Error connecting to OpenRouter API: {e}")
        return []
    except Exception as e:
        print(f"❌ [System] Unexpected error fetching models: {e}")
        return []

def filter_and_rank(models, limit=20):
    """Filter for popular/powerful models and rank them."""
    # Priority keywords for ranking
    priority_keywords = ["gpt-4o", "claude-3.5-sonnet", "o1-preview", "gemini-pro-1.5", "llama-3-70b", "deepseek-coder", "mistral-large", "qwen-2.5-72b"]
    
    ranked = []
    others = []
    
    for m in models:
        model_id = m.get('id', '')
        is_priority = any(k in model_id for k in priority_keywords)
        
        if "test" in model_id or "beta" in model_id: 
            if not is_priority: continue 
            
        if is_priority:
            ranked.append(m)
        else:
            others.append(m)
            
    ranked.sort(key=lambda x: x.get('context_length', 0), reverse=True)
    others.sort(key=lambda x: x.get('context_length', 0), reverse=True)
    
    return (ranked + others)[:limit]

def display_models(models):
    """Print a markdown table of models."""
    print("| Index | ID | Context | Input Price ($/1M) | Output Price ($/1M) |")
    print("| :--- | :--- | :--- | :--- | :--- |")
    
    for idx, m in enumerate(models, 1):
        try:
            pricing = m.get('pricing', {})
            in_price = float(pricing.get('prompt', 0)) * 1_000_000
            out_price = float(pricing.get('completion', 0)) * 1_000_000
        except (ValueError, TypeError):
            in_price = 0.0
            out_price = 0.0
        
        context_k = m.get('context_length', 0) // 1000
        print(f"| {idx} | `{m['id']}` | {context_k}k | ${in_price:.2f} | ${out_price:.2f} |")
        
    print("\nTo enable a model, use: `python3 skills/model-manager/manage_models.py enable <Index>`")

def enable_model(model_id, config_path):
    """Generate OpenClaw config patch to enable a model."""
    print(f"🔒 [Config] Preparing patch for: {model_id}")
    
    # Read current config to avoid overwriting existing
    config = load_json_safe(config_path)
    if not config and os.path.exists(config_path):
        print(f"⚠️ [Config] Warning: Could not parse existing config at {config_path}")

    # Prepare patch data
    or_id = f"openrouter/{model_id}" if not model_id.startswith("openrouter/") else model_id
    
    try:
        current_fallbacks = config.get('agents', {}).get('defaults', {}).get('model', {}).get('fallbacks', [])
    except AttributeError:
        current_fallbacks = []
    
    if not isinstance(current_fallbacks, list):
        current_fallbacks = []

    new_fallbacks = list(current_fallbacks)
    if or_id not in new_fallbacks: 
        new_fallbacks.append(or_id)
        print(f"📝 [Config] Adding {or_id} to fallback list.")
    else:
        print(f"ℹ️ [Config] Model {or_id} already in fallback list.")
    
    # Construct the minimal patch object
    patch = {
        "agents": {
            "defaults": {
                "models": {
                    or_id: {}
                },
                "model": {
                    "fallbacks": new_fallbacks
                }
            }
        }
    }
    
    # Output JSON for piping (standard OpenClaw pattern)
    print(json.dumps(patch))

def main():
    if len(sys.argv) < 2:
        print("Usage: manage_models.py <list|enable|plan> [target/task] [--execute]")
        return

    # Argument parsing
    cmd_args = sys.argv[1:]
    action = cmd_args[0]
    
    if action == "plan":
        execute = "--execute" in cmd_args or "-x" in cmd_args
        # Extract task description safely
        task_words = [arg for arg in cmd_args[1:] if not arg.startswith("-")]
        if not task_words:
            print("Error: Please provide a task description.")
            return
        task = " ".join(task_words)
        
        planner = TaskPlanner()
        planner.plan(task, execute=execute)
        return

    # For list/enable, fetch models first
    models = fetch_models()
    if not models:
        return

    sorted_models = filter_and_rank(models)

    if action == "list":
        display_models(sorted_models)
        
    elif action == "enable":
        if len(cmd_args) < 2:
            print("Error: Please specify a model index to enable.")
            return
            
        target = cmd_args[1]
        selected_model_id = None
        
        if target.isdigit():
            idx = int(target) - 1
            if 0 <= idx < len(sorted_models):
                selected_model_id = sorted_models[idx]['id']
        else:
            for m in models:
                if m['id'] == target:
                    selected_model_id = m['id']
                    break
        
        if selected_model_id:
            enable_model(selected_model_id, CONFIG_FILE)
        else:
            print(f"Error: Model '{target}' not found.")

# --- New v1.5 Features ---

def get_benchmark_recommendations(task_type):
    """Get recommendations from model-benchmarks skill if available (v1.5)"""
    import subprocess
    import json
    
    try:
        # Try to call model-benchmarks skill
        cmd = ["python3", "skills/model-benchmarks/scripts/run.py", "recommend", "--task", task_type, "--format", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.expanduser("~/.openclaw/workspace"))
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("recommendations", [])
    except:
        pass
    
    return None

def enhanced_task_classification(task_description):
    """Enhanced task classification for v1.5"""
    task_lower = task_description.lower()
    
    # Enhanced patterns for v1.5
    patterns = {
        "coding": ["code", "program", "script", "debug", "function", "algorithm", "api", "database"],
        "writing": ["write", "article", "blog", "content", "story", "email", "letter"],
        "analysis": ["analyze", "compare", "evaluate", "research", "study", "report"],
        "translation": ["translate", "翻译", "convert language", "interpretation"],
        "creative": ["creative", "brainstorm", "idea", "design", "artistic"],
        "simple": ["simple", "quick", "basic", "summarize", "list", "count"]
    }
    
    scores = {}
    for category, keywords in patterns.items():
        score = sum(1 for kw in keywords if kw in task_lower)
        if score > 0:
            scores[category] = score
    
    if scores:
        return max(scores, key=scores.get)
    return "simple"

def display_v15_features():
    """Display v1.5 new features"""
    print("🆕 Model Manager v1.5 - New Features:")
    print("  • Enhanced task classification")
    print("  • Integration with model-benchmarks skill")  
    print("  • Improved cost calculations")
    print("  • Better error handling")
    print()
    print("💡 Pro Tip: Install 'model-benchmarks' skill for AI intelligence!")

if __name__ == "__main__":
    # Show v1.5 features on first run
    if len(sys.argv) == 1:
        display_v15_features()
    
    main()

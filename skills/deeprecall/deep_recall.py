"""
DeepRecall — Recursive Memory for Persistent AI Agents

Uses RLM (Recursive Language Models) to give AI agents infinite memory recall.
Instead of cramming all memory into the context window, the agent recursively 
queries its own memory files — enabling infinite identity persistence.

Part of the Anamnesis Architecture:
"The soul stays small, the mind scales forever."

Usage:
    from deep_recall import recall
    
    # Simple memory query
    result = recall("What did we decide about the budget?")
    
    # With options
    result = recall(
        "Summarize all project decisions from March",
        scope="memory",        # "memory", "identity", "project", "all"
        verbose=True,          # Show RLM execution
        config_overrides={     # Override RLM settings
            "max_depth": 3,
            "max_money_spent": 0.50,
        }
    )
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Ensure skill modules are importable
SKILL_DIR = Path(__file__).parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from provider_bridge import resolve_provider, ProviderConfig
from model_pairs import get_model_pair
from memory_scanner import MemoryScanner
from memory_indexer import build_memory_index, update_memory_index
from rlm_config_builder import build_rlm_config, set_env_for_rlm


def _find_fast_rlm() -> Optional[Path]:
    """Find the fast-rlm installation directory (contains deno.json)."""
    # Check environment variable
    rlm_dir = os.environ.get("FAST_RLM_DIR")
    if rlm_dir and Path(rlm_dir, "deno.json").exists():
        return Path(rlm_dir)
    
    # Check common locations
    candidates = [
        Path.home() / "fast-rlm",
        Path.home() / "Desktop" / "fast-rlm",
        Path.home() / ".local" / "share" / "fast-rlm",
        Path("/opt/fast-rlm"),
    ]
    
    # Also check if it's installed as a sibling to the workspace
    ws = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
    candidates.append(Path(ws) / "fast-rlm")
    candidates.append(Path(ws).parent / "fast-rlm")
    
    for candidate in candidates:
        if (candidate / "deno.json").exists():
            return candidate
    
    return None


def _find_deno() -> Optional[str]:
    """Find the Deno binary."""
    import shutil
    
    # Check PATH
    deno = shutil.which("deno")
    if deno:
        return deno
    
    # Check common locations
    candidates = [
        Path.home() / ".deno" / "bin" / "deno",
        Path("/usr/local/bin/deno"),
        Path("/usr/bin/deno"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    
    return None


def _find_workspace() -> Path:
    """Find the OpenClaw workspace directory."""
    # Check environment
    ws = os.environ.get("OPENCLAW_WORKSPACE")
    if ws:
        return Path(ws)
    
    # Check OpenClaw config
    config_file = Path(os.path.expanduser("~/.openclaw/openclaw.json"))
    if config_file.exists():
        import json
        try:
            with open(config_file) as f:
                config = json.load(f)
            ws = config.get("agents", {}).get("defaults", {}).get("workspace")
            if ws:
                return Path(ws)
        except Exception:
            pass
    
    # Default
    return Path(os.path.expanduser("~/.openclaw/workspace"))


def recall(
    query: str,
    scope: str = "memory",
    workspace: Optional[Path] = None,
    verbose: bool = False,
    config_overrides: Optional[dict] = None,
) -> str:
    """
    Recursively query the agent's memory using RLM.
    
    This is the main entry point for DeepRecall. It:
    1. Reads OpenClaw config to find the user's LLM provider
    2. Scans workspace for memory files
    3. Runs RLM to recursively search and reason over memory
    4. Returns the answer
    
    Args:
        query: What to recall / search for / analyze
        scope: What files to include:
            - "memory": MEMORY.md + daily logs + mind files (default, fast)
            - "identity": Soul + mind files only (minimal, fastest)  
            - "project": All readable workspace files (comprehensive)
            - "all": Everything (slowest, most thorough)
        workspace: Override workspace path (default: auto-detect from OpenClaw)
        verbose: Print RLM execution output to stdout
        config_overrides: Override RLM config values (max_depth, max_money_spent, etc.)
    
    Returns:
        The recalled information as a string
    
    Raises:
        RuntimeError: If fast-rlm is not installed or no provider configured
    """
    # Step 1: Find fast-rlm and Deno
    fast_rlm_dir = _find_fast_rlm()
    if not fast_rlm_dir:
        raise RuntimeError(
            "fast-rlm is not installed. To set up:\n"
            "  git clone https://github.com/avbiswas/fast-rlm.git\n"
            "  Set FAST_RLM_DIR=/path/to/fast-rlm\n"
            "Also requires Deno 2+: https://deno.land"
        )
    
    deno_bin = _find_deno()
    if not deno_bin:
        raise RuntimeError(
            "Deno is not installed. Install it with:\n"
            "  curl -fsSL https://deno.land/install.sh | sh"
        )
    
    # Step 2: Resolve provider
    try:
        provider_config = resolve_provider()
    except RuntimeError as e:
        raise RuntimeError(f"DeepRecall cannot resolve LLM provider: {e}")
    
    # Step 3: Build RLM config
    rlm_config = build_rlm_config(provider_config, overrides=config_overrides)
    
    # Step 4: Scan memory files
    ws = workspace or _find_workspace()
    scanner = MemoryScanner(workspace=ws)
    scanner.scan(scope=scope)
    
    if not scanner.files:
        return "[DeepRecall] No memory files found in workspace."
    
    context = scanner.get_context()
    
    # Step 5: Build memory index for efficient navigation
    memory_index = build_memory_index(workspace=ws)
    
    # Step 6: Build the full query
    full_query = (
        f"You are an AI agent's memory recall system. "
        f"The agent needs to find specific information from its memory store.\n\n"
        f"QUERY: {query}\n\n"
        f"INSTRUCTIONS:\n"
        f"- FIRST: Read the Memory Index below to locate which files likely contain the answer\n"
        f"- THEN: Search those files for the detailed information\n"
        f"- Base your answer on what you find in the files. Cite which file the information came from.\n"
        f"- You may synthesize across multiple files to build a complete answer.\n"
        f"- If the information is not found in any file, say so clearly.\n"
        f"- Return the answer in a clear, structured format.\n\n"
        f"=== MEMORY INDEX (read this first to navigate efficiently) ===\n"
        f"{memory_index}\n\n"
        f"{context}"
    )
    
    # Step 7: Write temporary config file
    import tempfile, json, subprocess, yaml
    
    tmp_config = tempfile.mktemp(suffix='.yaml', prefix='deeprecall_')
    with open(tmp_config, 'w') as f:
        yaml.dump(rlm_config, f)
    
    output_file = tempfile.mktemp(suffix='.json', prefix='deeprecall_out_')
    log_dir = tempfile.mkdtemp(prefix='deeprecall_logs_')
    
    # Step 8: Set environment for fast-rlm
    env = os.environ.copy()
    set_env_for_rlm(provider_config)
    env['RLM_MODEL_API_KEY'] = provider_config.api_key
    if provider_config.base_url:
        env['RLM_MODEL_BASE_URL'] = provider_config.base_url
    env['FRACTAL_PROJECT_PATH'] = str(ws)
    
    # Step 9: Run fast-rlm via Deno subprocess
    cmd = [
        deno_bin, 'task', '-q', 'subagent',
        '--output', output_file,
        '--config', tmp_config,
        '--log-dir', log_dir,
    ]
    
    if verbose:
        print(f"🧠 DeepRecall running...")
        print(f"   Provider: {provider_config.provider}")
        print(f"   Model: {provider_config.primary_model}")
        print(f"   Scope: {scope}")
        print(f"   Files: {len(scanner.files)}")
        print(f"   fast-rlm: {fast_rlm_dir}")
    
    try:
        proc = subprocess.run(
            cmd,
            input=full_query,
            text=True,
            cwd=str(fast_rlm_dir),
            env=env,
            capture_output=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return "[DeepRecall] Query timed out after 300 seconds."
    finally:
        # Clean up temp config
        try:
            os.unlink(tmp_config)
        except OSError:
            pass
    
    if verbose and proc.stderr:
        print(proc.stderr)
    
    # Step 10: Read results
    if os.path.exists(output_file):
        try:
            with open(output_file) as f:
                data = json.load(f)
            answer = data.get("results", "[DeepRecall] No result returned from RLM.")
            
            if verbose:
                usage = data.get("usage", {})
                print(f"\n   Tokens: {usage.get('total_tokens', '?')}")
            
            # Clean up output file
            try:
                os.unlink(output_file)
            except OSError:
                pass
        except (json.JSONDecodeError, IOError):
            answer = "[DeepRecall] Failed to parse RLM output."
    else:
        error_msg = proc.stderr[-500:] if proc.stderr else "Unknown error"
        answer = f"[DeepRecall] RLM execution failed (exit {proc.returncode}): {error_msg}"
    
    # Convert non-string results
    if isinstance(answer, dict):
        import json as json_mod
        answer = json_mod.dumps(answer, indent=2)
    elif isinstance(answer, list):
        answer = "\n".join(str(item) for item in answer)
    
    return str(answer)


def recall_quick(query: str, verbose: bool = False) -> str:
    """
    Quick memory recall with minimal scope (identity + mind files only).
    Fastest and cheapest option.
    """
    return recall(query, scope="identity", verbose=verbose, 
                  config_overrides={"max_depth": 1, "max_money_spent": 0.05})


def recall_deep(query: str, verbose: bool = False) -> str:
    """
    Deep memory recall with full scope (all workspace files).
    Most thorough but slower and more expensive.
    """
    return recall(query, scope="all", verbose=verbose,
                  config_overrides={"max_depth": 3, "max_money_spent": 0.50})


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deep_recall.py <query> [scope]")
        print("Scopes: memory (default), identity, project, all")
        sys.exit(1)
    
    query = sys.argv[1]
    scope = sys.argv[2] if len(sys.argv) > 2 else "memory"
    
    print(f"🧠 DeepRecall: querying memory (scope={scope})...")
    print(f"   Query: {query}\n")
    
    try:
        result = recall(query, scope=scope, verbose=True)
        print(f"\n📝 Result:\n{result}")
    except RuntimeError as e:
        print(f"❌ Error: {e}")

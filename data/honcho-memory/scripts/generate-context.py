#!/usr/bin/env python3
"""
Honcho Context Generator v2 — Generates token-budgeted context files for all agents.

Produces two types of files:
1. HONCHO-CONTEXT.md (workspace root) — shared context loaded by ALL agents
   - J's profile (distilled)
   - Current priorities
   - Cross-agent brief (what each agent did recently)
   ~1000-1500 tokens

2. agents/{name}/HONCHO-CONTEXT.md — agent-specific context
   - Agent's role and current focus
   - Recent performance/activity  
   - Pending items and learnings
   ~500-800 tokens per agent

Together: ~2000 tokens of highly relevant context vs ~15K of MEMORY.md + daily notes.
Loaded on session start AND survives compaction (workspace file).

Usage:
  python3 scripts/honcho-context-gen.py              # generate all
  python3 scripts/honcho-context-gen.py --agent axobotl  # one agent only
  python3 scripts/honcho-context-gen.py --query "What should we focus on?" --peer j
"""

import argparse
import json
import os
from datetime import datetime

MAX_SHARED_TOKENS = 5000  # ~20000 chars — comprehensive understanding
MAX_AGENT_TOKENS = 3000   # ~12000 chars — deep agent-specific context

def get_honcho():
    from honcho import Honcho
    with open(os.path.expanduser('~/.config/honcho/credentials.json')) as f:
        creds = json.load(f)
    return Honcho(workspace_id=creds.get('workspace_id', 'default'), api_key=creds['api_key'])

def truncate(text, max_chars):
    """Truncate text to approximate token budget (4 chars ≈ 1 token)."""
    if not text:
        return ''
    if len(text) <= max_chars:
        return text
    # Cut at last newline before limit
    cut = text[:max_chars].rfind('\n')
    if cut < max_chars * 0.5:
        cut = max_chars
    return text[:cut].rstrip()

def get_j_profile(honcho):
    """Get comprehensive J profile from Honcho's reasoning."""
    j = honcho.peer('j')
    sections = []
    
    # Full representation — this is what Honcho has reasoned about J
    try:
        rep = j.representation()
        if rep and len(rep) > 50:
            sections.append(rep)
    except:
        pass
    
    # Also ask targeted questions to fill gaps
    try:
        overview = j.chat(
            "Give me a comprehensive profile of J: who he is, what he's building, "
            "all his active projects, his communication style, what motivates him, "
            "his history (Mynd, peak state, PrimeState, AI Corp), the agent fleet, "
            "0xWork, CoShip, and any other important context. Be thorough.",
            reasoning_level='medium'
        )
        if overview and len(overview) > 50:
            sections.append(overview)
    except:
        pass
    
    return truncate('\n\n'.join(sections), MAX_SHARED_TOKENS * 4)

def get_current_priorities(honcho):
    """Get comprehensive current state across all projects."""
    j = honcho.peer('j')
    try:
        priorities = j.chat(
            "What is the full current state of everything J is working on? "
            "Include: all active projects and their status, pending decisions, "
            "what's blocked, recent wins, upcoming milestones, the agent fleet "
            "and what each agent does, infrastructure status, and anything else "
            "that would be important context for someone helping J.",
            reasoning_level='medium'
        )
        return truncate(priorities, MAX_SHARED_TOKENS * 2)
    except Exception as e:
        return f"Error getting priorities: {e}"

def get_cross_agent_brief(honcho):
    """Get comprehensive cross-agent context."""
    agents = ['axel', 'axobotl', 'larry', 'clarity', 'wire', 'drift']
    briefs = []
    
    for agent_name in agents:
        try:
            session = honcho.session(f'full-sync-{agent_name}')
            ctx = session.context(tokens=800)
            if ctx.summary and ctx.summary.content:
                briefs.append(f"### {agent_name}\n{ctx.summary.content}")
        except:
            continue
    
    return '\n\n'.join(briefs) if briefs else 'No recent agent activity.'

def get_agent_context(honcho, agent_name):
    """Get comprehensive agent-specific context."""
    agent = honcho.peer(agent_name)
    
    sections = []
    
    # Full agent representation
    try:
        rep = agent.representation()
        if rep and len(rep) > 50:
            sections.append(rep)
    except:
        pass
    
    # Rich session context
    try:
        session = honcho.session(f'full-sync-{agent_name}')
        ctx = session.context(tokens=2000)
        if ctx.summary and ctx.summary.content:
            sections.append(f"### Recent Activity & Context\n{ctx.summary.content}")
    except:
        pass
    
    # Deep agent-specific understanding
    try:
        focus = agent.chat(
            f"Give me a comprehensive overview of {agent_name}: what it does, "
            f"how it operates, its current focus, all pending tasks, recent "
            f"performance, learnings, mistakes to avoid, relationships with "
            f"other agents, and anything else important for understanding "
            f"this agent's role in the system.",
            reasoning_level='medium'
        )
        if focus and len(focus) > 20:
            sections.append(f"### Full Overview\n{focus}")
    except:
        pass
    
    return '\n\n'.join(sections)

def generate_agent_context(honcho, agent_name, shared_content=''):
    """Generate merged HONCHO-CONTEXT.md (shared + agent-specific) for one agent."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M PT')
    
    agent_ctx = get_agent_context(honcho, agent_name)
    
    content = f"""# Honcho Context — {agent_name.title()}
> Updated {timestamp} | Comprehensive reasoned context from real conversations | Refreshed hourly

{shared_content}

## {agent_name.title()} — Agent Context
{agent_ctx}
"""
    
    if agent_name == 'axel':
        path = os.path.expanduser('~/.openclaw/workspace/HONCHO-CONTEXT.md')
    else:
        path = os.path.expanduser(f'~/.openclaw/workspace/agents/{agent_name}/HONCHO-CONTEXT.md')
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    
    chars = len(content)
    tokens_est = chars // 4
    print(f"  {agent_name}: {chars} chars (~{tokens_est} tokens) → {path}")
    return path

def main():
    parser = argparse.ArgumentParser(description='Honcho Context Generator v2')
    parser.add_argument('--agent', help='Generate for specific agent only')
    parser.add_argument('--shared-only', action='store_true', help='Only generate shared context')
    parser.add_argument('--query', help='Direct query to Honcho')
    parser.add_argument('--peer', default='j', help='Peer to query')
    
    args = parser.parse_args()
    
    honcho = get_honcho()
    
    if args.query:
        peer = honcho.peer(args.peer)
        print(peer.chat(args.query, reasoning_level='medium'))
        return
    
    print("Generating Honcho context...\n")
    
    # Build shared content ONCE (J profile, priorities, cross-agent brief)
    print("  Building shared context (J profile, priorities, cross-agent)...")
    j_profile = get_j_profile(honcho)
    priorities = get_current_priorities(honcho)
    cross_brief = get_cross_agent_brief(honcho)
    
    shared_content = f"""## J
{j_profile}

## Current Priorities
{priorities}

## Agent Activity (Last Cycle)
{cross_brief}"""
    
    if args.shared_only:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M PT')
        path = os.path.expanduser('~/.openclaw/workspace/HONCHO-CONTEXT.md')
        with open(path, 'w') as f:
            f.write(f"# Honcho Context\n> Updated {timestamp}\n\n{shared_content}\n")
        print(f"  Shared only: {len(shared_content)} chars → {path}")
    else:
        # Merge shared + agent-specific into ONE file per agent
        agents = [args.agent] if args.agent else ['axel', 'axobotl', 'larry', 'clarity', 'wire', 'drift']
        for agent_name in agents:
            try:
                generate_agent_context(honcho, agent_name, shared_content)
            except Exception as e:
                print(f"  {agent_name}: ERROR - {e}")
    
    print("\nDone.")

if __name__ == '__main__':
    main()

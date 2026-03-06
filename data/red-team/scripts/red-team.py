#!/usr/bin/env python3
"""Red Team — Adversarial multi-agent debate engine for stress-testing decisions.

Uses `claude --print` (Claude Code CLI) as the backend, so it runs through your
Max subscription OAuth token — no API key needed.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# ── Built-in Personas ──────────────────────────────────────────────────────────

PERSONAS = {
    "bull": {
        "name": "The Bull",
        "description": "Optimistic, opportunity-focused, action-biased",
        "system": "You are the Bull — an optimistic, opportunity-focused analyst. You see upside potential, hate analysis paralysis, and believe in taking calculated risks. You look for asymmetric upside, first-mover advantages, and reasons why something WILL work. You push back hard on excessive caution. Your bias is toward action.",
    },
    "bear": {
        "name": "The Bear",
        "description": "Risk-averse, capital preservation, danger-sensing",
        "system": "You are the Bear — a risk-averse, capital-preservation-focused analyst. You find hidden dangers, worst-case scenarios, and reasons things fail. You stress-test assumptions, identify tail risks, and ask 'what if we're wrong?' Your job is to protect the downside. You're skeptical of optimistic projections.",
    },
    "contrarian": {
        "name": "The Contrarian",
        "description": "Deliberately oppositional, consensus-challenging",
        "system": "You are the Contrarian — you deliberately take the opposite position to whatever consensus is forming. If everyone agrees, you disagree. You look for groupthink, unexamined assumptions, and the road not taken.",
    },
    "operator": {
        "name": "The Operator",
        "description": "Pragmatist, execution-focused, complexity-aware",
        "system": "You are the Operator — a pragmatist focused on execution. You care about: How hard is this to actually do? What's the operational complexity? Who does the work? What are the dependencies? You've seen plenty of great ideas die in execution.",
    },
    "economist": {
        "name": "The Economist",
        "description": "Macro perspective, cycles, opportunity cost",
        "system": "You are the Economist — you think in terms of macro trends, market cycles, opportunity costs, and incentive structures. You ask: What else could this capital/time be used for? Where are we in the cycle?",
    },
    "local-realist": {
        "name": "The Local Realist",
        "description": "Ground truth, local knowledge, boots-on-the-ground",
        "system": "You are the Local Realist — you care about ground truth. What does this actually look like in practice, in this specific market/context? The map is not the territory.",
    },
    "cash-flow": {
        "name": "The Cash Flow Analyst",
        "description": "Income-focused, carrying costs, time-value of money",
        "system": "You are the Cash Flow Analyst — everything comes down to cash flows. What are the carrying costs? When does money come in vs go out? What's the IRR? Cash is king.",
    },
    "regulator": {
        "name": "The Regulator",
        "description": "Compliance, legal risk, regulatory exposure",
        "system": "You are the Regulator — you focus on compliance, legal risk, and regulatory exposure. What laws apply? What licenses are needed? What happens if regulations change?",
    },
    "technologist": {
        "name": "The Technologist",
        "description": "Automation, scalability, data advantages",
        "system": "You are the Technologist — you evaluate everything through technology leverage. Can this be automated? Does it scale? Is there a data advantage or network effect?",
    },
    "customer": {
        "name": "The Customer",
        "description": "End-user perspective, demand, willingness to pay",
        "system": "You are the Customer — you represent the end user. Would real people actually want this? Would they pay for it? You ground discussions in actual market demand and willingness to pay.",
    },
    "ethicist": {
        "name": "The Ethicist",
        "description": "Moral implications, stakeholder impact",
        "system": "You are the Ethicist — you evaluate decisions through moral and ethical lenses. Who gets hurt? Who benefits? What are the second-order social consequences?",
    },
    "historian": {
        "name": "The Historian",
        "description": "Pattern recognition, precedent, historical analogy",
        "system": "You are the Historian — you've seen this before. You draw on historical analogies, past failures and successes, and warn against 'this time is different' thinking.",
    },
}

# ── Claude CLI Helper ───────────────────────────────────────────────────────────


BACKENDS = {
    "claude": {
        "check": ["claude", "--version"],
        "install": "npm install -g @anthropic-ai/claude-code",
    },
    "codex": {
        "check": ["codex", "--version"],
        "install": "npm install -g @openai/codex",
    },
    "gemini": {
        "check": ["gemini", "--version"],
        "install": "npm install -g @google/gemini-cli",
    },
}


def _build_cmd(backend: str, system: str, user_msg: str, model: str) -> tuple[list[str], str | None]:
    """Build the CLI command and optional stdin for the given backend."""
    combined_prompt = f"{system}\n\n---\n\n{user_msg}"

    if backend == "claude":
        return [
            "claude", "--print",
            "--model", model,
            "--output-format", "text",
            "--no-session-persistence",
            "--append-system-prompt", system,
            user_msg,
        ], None
    elif backend == "codex":
        # Codex exec reads prompt from positional arg or stdin
        return [
            "codex", "exec",
            "--model", model,
            "--quiet",
            combined_prompt,
        ], None
    elif backend == "gemini":
        # Gemini CLI: prompt as positional arg
        return [
            "gemini", "-p", combined_prompt,
        ], None
    else:
        raise ValueError(f"Unknown backend: {backend}")


def call_agent(system: str, user_msg: str, label: str, model: str = "sonnet",
               backend: str = "claude") -> str:
    """Call a coding agent CLI with a system prompt and user message."""
    print(f"  ⏳ {label}...", end=" ", flush=True)
    t0 = time.time()

    cmd, stdin_data = _build_cmd(backend, system, user_msg, model)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            input=stdin_data,
            timeout=180,
        )
        if result.returncode != 0:
            print(f"FAILED")
            print(f"    stderr: {result.stderr[:200]}", file=sys.stderr)
            return f"[Agent error: {result.stderr[:200]}]"

        elapsed = time.time() - t0
        text = result.stdout.strip()
        print(f"done ({elapsed:.1f}s)")
        return text

    except subprocess.TimeoutExpired:
        print(f"TIMEOUT")
        return "[Agent timed out after 180s]"
    except FileNotFoundError:
        info = BACKENDS.get(backend, {})
        print(f"FAILED — '{backend}' CLI not found")
        print(f"Error: '{backend}' CLI not found. Install: {info.get('install', 'unknown')}", file=sys.stderr)
        sys.exit(1)


# ── Debate Engine ──────────────────────────────────────────────────────────────


def run_debate(question: str, persona_keys: list[str], personas: dict, rounds: int,
               context: str, model: str, backend: str = "claude") -> str:
    ctx_block = f"\n\n## Additional Context\n{context}" if context else ""
    sections = []
    sections.append(f"# Red Team Analysis\n\n**Question:** {question}\n\n**Personas:** {', '.join(p['name'] for p in [personas[k] for k in persona_keys])}\n**Rounds:** {rounds}\n**Model:** {model}\n")

    # ── Round 1: Proposals ──────────────────────────────────────────────────
    print("\n🔴 Round 1: Proposals")
    proposals = {}
    sections.append("---\n## Round 1: Initial Proposals\n")
    for key in persona_keys:
        p = personas[key]
        prompt = f"Analyze this question from your perspective. Give a clear position with reasoning (3-5 paragraphs).\n\n**Question:** {question}{ctx_block}"
        text = call_agent(p["system"], prompt, f"{p['name']} proposal", model, backend)
        proposals[key] = text
        sections.append(f"### {p['name']} ({p['description']})\n\n{text}\n")

    # ── Rounds 2..N: Critiques ──────────────────────────────────────────────
    critique_history = {k: [] for k in persona_keys}
    for r in range(2, rounds + 1):
        print(f"\n🔴 Round {r}: Critiques")
        sections.append(f"---\n## Round {r}: Critiques\n")
        proposals_text = "\n\n".join(
            f"**{personas[k]['name']}:** {proposals[k]}" for k in persona_keys
        )
        for key in persona_keys:
            p = personas[key]
            prompt = (
                f"Here are all proposals so far:\n\n{proposals_text}\n\n"
                f"Critique the OTHER agents' proposals from your perspective. "
                f"Be specific: what's wrong, what's missing, what risks do they ignore? "
                f"Also note where you agree (if anywhere). 2-4 paragraphs per critique.{ctx_block}"
            )
            text = call_agent(p["system"], prompt, f"{p['name']} critique", model, backend)
            critique_history[key].append(text)
            sections.append(f"### {p['name']}\n\n{text}\n")

    # ── Refinement Round ────────────────────────────────────────────────────
    print("\n🔴 Refinement Round")
    sections.append("---\n## Refinement Round\n")
    all_critiques = "\n\n".join(
        f"**{personas[k]['name']} critiques:**\n" + "\n".join(critique_history[k])
        for k in persona_keys if critique_history[k]
    )
    refined = {}
    for key in persona_keys:
        p = personas[key]
        prompt = (
            f"Original question: {question}\n\n"
            f"Your original proposal:\n{proposals[key]}\n\n"
            f"All critiques from the debate:\n{all_critiques}\n\n"
            f"Refine your position. Incorporate valid critiques, defend where you still disagree, "
            f"and sharpen your recommendation. 3-5 paragraphs.{ctx_block}"
        )
        text = call_agent(p["system"], prompt, f"{p['name']} refinement", model, backend)
        refined[key] = text
        sections.append(f"### {p['name']}\n\n{text}\n")

    # ── Conviction Scores ───────────────────────────────────────────────────
    print("\n🔴 Conviction Scoring")
    sections.append("---\n## Conviction Scores\n")
    all_refined = "\n\n".join(
        f"**{personas[k]['name']}:** {refined[k]}" for k in persona_keys
    )
    score_results = {}
    for key in persona_keys:
        p = personas[key]
        names = [personas[k]["name"] for k in persona_keys]
        prompt = (
            f"Here are all refined positions:\n\n{all_refined}\n\n"
            f"Allocate conviction scores (0-100) to each position INCLUDING your own. "
            f"Higher = more convinced this position is correct. Scores don't need to sum to 100.\n\n"
            f"Respond in EXACTLY this format, one per line:\n"
            + "\n".join(f"{n}: <score>" for n in names)
        )
        text = call_agent(p["system"], prompt, f"{p['name']} scoring", model, backend)
        score_results[key] = text
        sections.append(f"### {p['name']}\n\n{text}\n")

    # ── Synthesis ───────────────────────────────────────────────────────────
    print("\n🔴 Synthesis")
    full_debate = "\n\n".join(sections)
    synthesis_system = (
        "You are a neutral synthesis agent. You read adversarial debates and produce "
        "clear, actionable decision briefs. You are not biased toward any position. "
        "Your job is to extract signal from noise and give a genuinely useful recommendation."
    )
    synthesis_prompt = (
        f"Read this full adversarial debate and produce a structured decision brief.\n\n"
        f"{full_debate}\n\n"
        f"Produce the following sections in markdown:\n"
        f"1. **Executive Summary** (2-3 sentences — the bottom line)\n"
        f"2. **Consensus Points** (where all/most agents agree)\n"
        f"3. **Key Disagreements** (unresolved tensions)\n"
        f"4. **Risk Matrix** (table: risk | likelihood | impact | mitigation)\n"
        f"5. **Conviction Score Summary** (aggregate the scores)\n"
        f"6. **Synthesized Recommendation** (your actual recommendation with reasoning — be decisive)\n"
        f"7. **Next Steps** (concrete actions if proceeding)\n"
    )
    synthesis = call_agent(synthesis_system, synthesis_prompt, "Synthesis agent", model, backend)
    sections.append(f"---\n## Synthesis & Decision Brief\n\n{synthesis}\n")

    return "\n".join(sections)


# ── CLI ─────────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Red Team — adversarial multi-agent debate engine")
    parser.add_argument("--question", "-q", help="The question or decision to debate")
    parser.add_argument("--personas", "-p", default="bull,bear,operator", help="Comma-separated persona names (default: bull,bear,operator)")
    parser.add_argument("--rounds", "-r", type=int, default=2, help="Number of critique rounds (default: 2)")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument("--context-file", "-c", help="Path to additional context file")
    parser.add_argument("--custom-personas", help="Path to custom personas JSON file")
    parser.add_argument("--model", "-m", default="sonnet", help="Model to use (default: sonnet)")
    parser.add_argument("--backend", "-b", default="claude", choices=["claude", "codex", "gemini"],
                        help="CLI backend: claude (default), codex, or gemini")
    parser.add_argument("--list-personas", action="store_true", help="List available personas and exit")
    args = parser.parse_args()

    personas = dict(PERSONAS)

    # Load custom personas
    if args.custom_personas:
        try:
            with open(args.custom_personas) as f:
                custom = json.load(f)
            for k, v in custom.items():
                if all(field in v for field in ("name", "description", "system")):
                    personas[k] = v
                else:
                    print(f"Warning: custom persona '{k}' missing required fields, skipping", file=sys.stderr)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading custom personas: {e}", file=sys.stderr)
            sys.exit(1)

    if args.list_personas:
        print("Available personas:\n")
        for k, v in sorted(personas.items()):
            print(f"  {k:15s} — {v['description']}")
        sys.exit(0)

    if not args.question:
        parser.error("--question/-q is required (unless using --list-personas)")

    # Validate personas
    persona_keys = [p.strip() for p in args.personas.split(",")]
    for k in persona_keys:
        if k not in personas:
            print(f"Error: unknown persona '{k}'. Use --list-personas to see available options.", file=sys.stderr)
            sys.exit(1)

    if len(persona_keys) < 2:
        print("Error: need at least 2 personas for a debate.", file=sys.stderr)
        sys.exit(1)

    # Check backend CLI is available
    backend_info = BACKENDS.get(args.backend, {})
    try:
        subprocess.run(backend_info["check"], capture_output=True, timeout=10)
    except FileNotFoundError:
        print(f"Error: '{args.backend}' CLI not found. Install: {backend_info.get('install', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    # Load context
    context = ""
    if args.context_file:
        try:
            context = Path(args.context_file).read_text()
        except FileNotFoundError:
            print(f"Error: context file not found: {args.context_file}", file=sys.stderr)
            sys.exit(1)

    print(f"🔴 RED TEAM DEBATE ENGINE")
    print(f"   Question: {args.question}")
    print(f"   Personas: {', '.join(persona_keys)}")
    print(f"   Rounds: {args.rounds}")
    print(f"   Model: {args.model}")
    print(f"   Backend: {args.backend}")

    try:
        result = run_debate(args.question, persona_keys, personas, args.rounds, context, args.model, args.backend)
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(result)
        print(f"\n✅ Output written to {args.output}")
    else:
        print("\n" + result)


if __name__ == "__main__":
    main()

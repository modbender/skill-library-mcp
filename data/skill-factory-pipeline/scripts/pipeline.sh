#!/usr/bin/env bash
# pipeline.sh — Skill Factory Pipeline Orchestrator
#
# Runs 7 agents sequentially to build a skill from idea to market-ready package.
# Each agent is an isolated CLI call. No nested sessions. No parallelism.
#
# Usage:
#   pipeline.sh --workspace <path> [--from <stage>] [--to <stage>] [--dry-run]
#
# Stages (in order):
#   market → planner → arch → builder → auditor → docs → pricer
#
# Examples:
#   pipeline.sh --workspace /tmp/sf-stripe
#   pipeline.sh --workspace /tmp/sf-stripe --from auditor
#   pipeline.sh --workspace /tmp/sf-stripe --from planner --to builder
#   pipeline.sh --workspace /tmp/sf-stripe --dry-run

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STAGES=(market planner arch builder auditor docs pricer)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

usage() {
  cat <<'EOF'
Usage: pipeline.sh --workspace <path> [OPTIONS]

Options:
  --workspace <path>   Workspace directory created by init_pipeline.py (required)
  --from <stage>       Start pipeline from this stage (default: market)
  --to <stage>         Stop pipeline after this stage (default: pricer)
  --dry-run            Print agent commands without executing them
  -h, --help           Show this help

Stages: market → planner → arch → builder → auditor → docs → pricer
EOF
}

log()  { echo "[pipeline] $*"; }
info() { echo "[pipeline] INFO  $*"; }
ok()   { echo "[pipeline] OK    $*"; }
fail() { echo "[pipeline] FAIL  $*" >&2; }

stage_index() {
  local name="$1"
  local i
  for i in "${!STAGES[@]}"; do
    [[ "${STAGES[$i]}" == "$name" ]] && echo "$i" && return 0
  done
  echo "-1"
}

validate_stage() {
  local name="$1"
  local idx
  idx=$(stage_index "$name")
  if [[ "$idx" == "-1" ]]; then
    fail "Unknown stage: '$name'. Valid stages: ${STAGES[*]}"
    exit 1
  fi
}

mark_stage_done() {
  local stage="$1"
  local ws="$2"
  echo "$stage=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$ws/.pipeline_state"
}

# ---------------------------------------------------------------------------
# Gate checks — validate expected output files exist and are non-empty
# ---------------------------------------------------------------------------

gate_market() {
  local ws="$1"
  [[ -s "$ws/market.md" ]] || { fail "Gate [market]: market.md is missing or empty"; return 1; }
}

gate_planner() {
  local ws="$1"
  [[ -s "$ws/plan.md" ]] || { fail "Gate [planner]: plan.md is missing or empty"; return 1; }
}

gate_arch() {
  local ws="$1"
  [[ -s "$ws/arch.md" ]] || { fail "Gate [arch]: arch.md is missing or empty"; return 1; }
}

gate_builder() {
  local ws="$1"
  [[ -s "$ws/skill/SKILL.md" ]] || { fail "Gate [builder]: skill/SKILL.md is missing or empty"; return 1; }
}

gate_auditor() {
  local ws="$1"
  [[ -s "$ws/audit.md" ]] || { fail "Gate [auditor]: audit.md is missing or empty"; return 1; }
}

gate_docs() {
  local ws="$1"
  [[ -s "$ws/docs_review.md" ]] || { fail "Gate [docs]: docs_review.md is missing or empty"; return 1; }
}

gate_pricer() {
  local ws="$1"
  [[ -s "$ws/pricing.md" ]] || { fail "Gate [pricer]: pricing.md is missing or empty"; return 1; }
}

run_gate() {
  local stage="$1"
  local ws="$2"
  "gate_${stage}" "$ws"
}

# ---------------------------------------------------------------------------
# Agent prompt builders
# Each function echoes the prompt string for that stage.
# Prompts read from workspace files — all paths are absolute.
# ---------------------------------------------------------------------------

prompt_market() {
  local ws="$1"
  cat <<EOF
You are a market research analyst specializing in AI developer tools.

Read the skill idea at: $ws/idea.md

Produce a market research report and write it to: $ws/market.md

The report must include:
1. Problem validation — Is the problem real and felt by enough users?
2. Target audience — Who are the primary users? Secondary users?
3. Competitive landscape — What exists already (skills, tools, libraries)?
4. Differentiation — What would make this skill stand out?
5. Demand signals — Evidence of demand (searches, forum posts, tool popularity)
6. Market verdict — GO / NO-GO with one-paragraph rationale

Keep the report factual and concise. Use markdown headers.
Write ONLY to $ws/market.md. Do not create other files.
EOF
}

prompt_planner() {
  local ws="$1"
  cat <<EOF
You are a product planner for AI developer tools.

Read:
- Skill idea: $ws/idea.md
- Market research: $ws/market.md

Produce a product plan and write it to: $ws/plan.md

The plan must include:
1. Skill name (hyphen-case, max 32 chars)
2. One-sentence description (for SKILL.md frontmatter)
3. Core capabilities — what the skill enables an agent to do (3-7 items)
4. Out of scope — what this skill explicitly does NOT do
5. Trigger scenarios — exact user requests that should activate this skill
6. Required resources — which of scripts/, references/, assets/ are needed and why
7. Key files — list every file the skill will contain with one-line purpose
8. Acceptance criteria — how to verify the skill is complete

Write ONLY to $ws/plan.md. Do not create other files.
EOF
}

prompt_arch() {
  local ws="$1"
  cat <<EOF
You are a software architect specializing in AI skill design.

Read:
- Product plan: $ws/plan.md

Produce an architecture document and write it to: $ws/arch.md

The architecture must include:
1. Directory layout — exact tree of all files and directories
2. SKILL.md structure — section outline with purpose of each section
3. Scripts design — for each script: name, language, inputs, outputs, core logic
4. References design — for each reference file: name, content summary, when to load it
5. Data flow — how information moves between skill components
6. Integration points — how an agent will invoke the skill in practice
7. Open questions — any design decisions that need the builder's judgment

Write ONLY to $ws/arch.md. Do not create other files.
EOF
}

prompt_builder() {
  local ws="$1"
  cat <<EOF
You are an expert skill builder for the openclaw skill system.

Read:
- Architecture: $ws/arch.md
- Product plan: $ws/plan.md

Build the complete skill. Create all files inside: $ws/skill/

Required output:
- $ws/skill/SKILL.md — complete, production-ready (following the official template format with frontmatter: name, description)
- All scripts listed in arch.md, placed in $ws/skill/scripts/
- All reference files listed in arch.md, placed in $ws/skill/references/

Rules:
- SKILL.md frontmatter must have 'name' and 'description' fields
- Scripts must be executable and include a usage docstring
- Reference files must be thorough enough to stand alone
- Do not add placeholder TODOs — write real content
- Do not create files not listed in arch.md without justification

Write ONLY inside $ws/skill/. Do not modify other workspace files.
EOF
}

prompt_auditor() {
  local ws="$1"
  cat <<EOF
You are a quality auditor for AI developer skills.

Read all files in: $ws/skill/

Audit the skill and write your report to: $ws/audit.md

Audit checklist:
1. SKILL.md completeness — frontmatter valid, description accurate, all sections present
2. Trigger accuracy — will the skill fire for the right requests and not for wrong ones?
3. Script quality — correct shebang, error handling, usage docs, executable logic
4. Reference quality — comprehensive, accurate, no placeholder content
5. Internal consistency — do all files agree with each other?
6. Security review — no hardcoded secrets, no unsafe shell expansions, no command injection risks
7. Gaps — what is missing or incomplete?

For each item: PASS / WARN / FAIL with one-line explanation.

End with:
- OVERALL: PASS / FAIL
- Required fixes (if FAIL): numbered list of blocking issues
- Recommended improvements (if PASS): numbered list of non-blocking suggestions

Write ONLY to $ws/audit.md. Do not modify skill files.
EOF
}

prompt_docs() {
  local ws="$1"
  cat <<EOF
You are a technical documentation specialist for AI developer tools.

Read:
- Skill files: $ws/skill/
- Audit report: $ws/audit.md

If the audit overall result is FAIL, stop immediately and write to $ws/docs_review.md:
"BLOCKED: Audit failed. Fix required issues in audit.md before docs review."

Otherwise, review the documentation quality and write your report to: $ws/docs_review.md

Documentation review:
1. Clarity — can a new user understand what this skill does in 30 seconds?
2. Examples — are there concrete, realistic usage examples?
3. Decision guidance — does the skill tell agents WHEN to use each feature?
4. Edge cases — are failure modes and limitations documented?
5. Cross-references — do references between files work and add value?

Provide specific rewrites for any unclear passages (quote original, then improved version).

Write ONLY to $ws/docs_review.md. Do not modify skill files.
EOF
}

prompt_pricer() {
  local ws="$1"
  cat <<EOF
You are a pricing strategist for AI developer tools sold on the openclaw marketplace.

Read:
- Market research: $ws/market.md
- Product plan: $ws/plan.md
- Audit report: $ws/audit.md
- Skill files: $ws/skill/SKILL.md

Produce a pricing and positioning report and write it to: $ws/pricing.md

The report must include:
1. Skill quality tier — Starter / Standard / Pro (based on audit and complexity)
2. Recommended price — specific number in USD with rationale
3. Positioning statement — one paragraph for the marketplace listing
4. Key selling points — 3-5 bullet points for the listing description
5. Suggested tags/categories — for marketplace discovery
6. Launch strategy — free trial, bundle opportunity, or direct sale?
7. Risks — what could reduce perceived value or sales?

Write ONLY to $ws/pricing.md. Do not create other files.
EOF
}

# ---------------------------------------------------------------------------
# Stage runner
# ---------------------------------------------------------------------------

run_stage() {
  local stage="$1"
  local ws="$2"
  local dry_run="$3"

  local prompt
  prompt="$(prompt_${stage} "$ws")"

  log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  log "Stage: $stage"
  log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if [[ "$dry_run" == "true" ]]; then
    echo "[DRY-RUN] Would execute:"
    echo "  openclaw agent --agent $stage -m \"...\""
    echo "  Prompt preview (first 3 lines):"
    echo "$prompt" | head -3 | sed 's/^/    /'
    return 0
  fi

  info "Calling: openclaw agent --agent $stage"
  # IMPORTANT: This is a top-level isolated CLI call.
  # It must NOT be called from within an existing openclaw session.
  # No flags that would create nested or interactive sessions.
  openclaw agent --agent "$stage" -m "$prompt"

  info "Running gate check for: $stage"
  if ! run_gate "$stage" "$ws"; then
    fail "Stage '$stage' did not produce expected output. Aborting pipeline."
    fail "Fix the issue and re-run with: --from $stage"
    exit 1
  fi

  mark_stage_done "$stage" "$ws"
  ok "Stage '$stage' complete."
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
  local workspace=""
  local from_stage="market"
  local to_stage="pricer"
  local dry_run="false"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --workspace)   workspace="${2:-}"; shift 2 ;;
      --from)        from_stage="${2:-}"; shift 2 ;;
      --to)          to_stage="${2:-}"; shift 2 ;;
      --dry-run)     dry_run="true"; shift ;;
      -h|--help)     usage; exit 0 ;;
      *) fail "Unknown option: $1"; usage; exit 1 ;;
    esac
  done

  # Validate workspace
  if [[ -z "$workspace" ]]; then
    fail "--workspace is required"
    usage
    exit 1
  fi

  workspace="$(realpath "$workspace")"

  if [[ ! -d "$workspace" ]]; then
    fail "Workspace directory does not exist: $workspace"
    fail "Run init_pipeline.py first to create it."
    exit 1
  fi

  if [[ ! -f "$workspace/idea.md" ]]; then
    fail "idea.md not found in workspace: $workspace"
    fail "Run init_pipeline.py first to initialize the workspace."
    exit 1
  fi

  # Validate stage names
  validate_stage "$from_stage"
  validate_stage "$to_stage"

  local from_idx to_idx
  from_idx=$(stage_index "$from_stage")
  to_idx=$(stage_index "$to_stage")

  if [[ "$from_idx" -gt "$to_idx" ]]; then
    fail "--from '$from_stage' comes after --to '$to_stage' in the pipeline"
    exit 1
  fi

  log "Workspace:  $workspace"
  log "Stages:     $from_stage → $to_stage"
  [[ "$dry_run" == "true" ]] && log "Mode:       DRY-RUN"
  echo

  # Run stages sequentially
  local current_idx
  for i in "${!STAGES[@]}"; do
    current_idx="$i"
    local stage="${STAGES[$i]}"

    [[ "$current_idx" -lt "$from_idx" ]] && continue
    [[ "$current_idx" -gt "$to_idx" ]] && break

    run_stage "$stage" "$workspace" "$dry_run"
    echo
  done

  log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  if [[ "$dry_run" == "true" ]]; then
    ok "Dry-run complete. No agents were called."
  else
    ok "Pipeline complete."
    log "Workspace: $workspace"
    log "Review your outputs:"
    log "  $workspace/pricing.md    ← start here for the summary"
    log "  $workspace/skill/        ← the built skill"
    log "  $workspace/audit.md      ← quality report"
  fi
}

main "$@"

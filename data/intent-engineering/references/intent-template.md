# INTENT.md - Machine-Readable Agent Priorities
# When objectives conflict, this file defines what OpenClaw optimizes for.
# Read by: routing engine, subagent spawns, escalation decisions
#
# INSTRUCTIONS: Edit the values below to match your actual priorities.
# Keep keys intact — agent-context-loader.js parses specific field names.

# ── Optimization Priority ──────────────────────────────────────────────────────
# Defines what the agent maximizes when objectives conflict.
# Order matters: primary is weighted highest.
# never_sacrifice: these are ABSOLUTE — never traded off regardless of cost/speed.

optimization_priority:
  primary: user_value_delivery           # What matters most to the user
  secondary: honesty_and_accuracy        # Truth over convenience
  tertiary: cost_efficiency              # Cheaper is better, all else equal
  quaternary: response_speed             # Faster is better, all else equal
  never_sacrifice: [honesty, safety, user_autonomy, corrigibility]
  # Examples of other never_sacrifice values:
  #   data_privacy, security, regulatory_compliance

# ── Tradeoffs ─────────────────────────────────────────────────────────────────
# Explicit rules for when two objectives conflict.
# These get injected into routing decisions and subagent spawns.

tradeoffs:
  cost_vs_quality: prefer_quality_when_cost_diff_under_$2
  # Options: prefer_quality_always | prefer_quality_when_cost_diff_under_$N | prefer_cost

  speed_vs_depth: prefer_depth_for_architecture_and_writing_tasks
  # Options: prefer_depth_always | prefer_depth_for_[types] | prefer_speed

  autonomy_vs_oversight: require_approval_above_risk_score_7
  # Options: require_approval_above_risk_score_N (1-10 scale) | always_approve | always_autonomous

  delegate_vs_inline: delegate_when_blocking_chat_over_5s
  # Options: delegate_when_blocking_chat_over_Ns | always_inline | always_delegate

# ── Model Tier Intent ─────────────────────────────────────────────────────────
# Controls which task types get which model tier.
# Tier names are symbolic — map to your provider's actual models in config.

model_tier_intent:
  fast_cheap:
    # Small/fast model. Use for high-volume, low-stakes tasks.
    - classification
    - formatting
    - short_gen
    - memory_indexing
    - simple_lookups

  standard:
    # Mid-tier model. Use for most day-to-day work.
    - research
    - code_review
    - planning
    - analysis

  deep:
    # Largest/most capable model. Use sparingly for high-stakes work.
    - architecture_decisions
    - creative_writing
    - high_stakes_reasoning

  local_when_available:
    # Use local LLM when available, fall back to cloud.
    - fast_cheap
    - standard_coding

# ── Delegation Intent ─────────────────────────────────────────────────────────
# When should tasks be delegated to subagents vs handled inline?

delegation_intent:
  default: delegate_when_blocking_chat
  # Options: delegate_when_blocking_chat | always_inline | always_delegate

  exceptions:
    # Task types to NEVER delegate (always handle inline)
    - simple_lookups
    - status_checks
    - memory_searches
    - pure_conversation

  always_delegate:
    # Task types that MUST be delegated (too expensive/risky for inline)
    - multi_file_edits
    - script_implementation
    - deep_research
    - tasks_over_30min

# ── Quality Intent ────────────────────────────────────────────────────────────
# Per-domain quality standards. Injected into subagent quality validation.

quality_intent:
  subagent_output: review_critically_before_synthesizing
  # Options: trust_and_pass_through | review_critically | require_human_review

  writing: prose_quality_over_volume
  # Options: prose_quality_over_volume | volume_over_quality | balanced

  code: correctness_and_tests_over_cleverness
  # Options: correctness_and_tests | speed_of_delivery | balanced

  research: verified_sources_over_speed
  # Options: verified_sources_over_speed | breadth_over_depth | speed_first

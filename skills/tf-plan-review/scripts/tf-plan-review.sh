#!/usr/bin/env bash
# tf-plan-review — Terraform Plan Analyzer & Risk Assessor
# Part of the Anvil AI skill suite.
# STRICTLY READ-ONLY: never runs terraform apply, never modifies state.
set -euo pipefail

###############################################################################
# Constants & Defaults
###############################################################################
VERSION="0.1.1"
TF_BINARY="${TF_BINARY:-}"
PLAN_TIMEOUT="${TF_PLAN_TIMEOUT:-600}"

# Risk classification patterns (conservative — err on flagging danger)
# These are jq-compatible regex patterns.

# Critical: IAM, security groups, KMS, secrets, databases (data loss risk)
CRITICAL_PATTERNS='iam|security_group|kms|secretsmanager|secrets_manager|db_instance|rds_cluster|dynamodb_table|s3_bucket$|google_sql_database_instance|azurerm_mssql_database|azurerm_key_vault|google_kms|aws_s3_bucket_policy|aws_iam|google_iam|azurerm_role|elasticache_replication_group|redshift_cluster|cloudsql|firewall_rule|network_security_group|waf|shield|guardduty|cloudtrail|route53_record|google_dns|azurerm_dns'

# Dangerous: destroy/replace of stateful or network-critical resources
DANGEROUS_PATTERNS='aws_instance|aws_lb|aws_elb|aws_alb|aws_ecs_service|aws_ecs_cluster|aws_eks_cluster|aws_vpc|aws_subnet|aws_nat_gateway|aws_route_table|google_compute_instance|google_container_cluster|azurerm_virtual_machine|azurerm_kubernetes_cluster|azurerm_virtual_network|aws_lambda_function|aws_api_gateway|aws_cloudfront_distribution|aws_sqs_queue|aws_sns_topic|aws_kinesis'

# Moderate: scaling, config changes to non-critical resources
MODERATE_PATTERNS='aws_autoscaling|aws_launch_template|aws_cloudwatch|google_compute_autoscaler|azurerm_monitor|aws_appautoscaling|replica|capacity|scaling'

###############################################################################
# Helpers
###############################################################################
die() { echo "❌ ERROR: $*" >&2; exit 1; }
warn() { echo "⚠️  WARNING: $*" >&2; }
info() { echo "ℹ️  $*" >&2; }

json_error() {
  local msg="$1"
  jq -n --arg msg "$msg" '{"error": true, "message": $msg}'
  exit 1
}

detect_tf_binary() {
  # Returns the binary name on stdout. Caller must check return code.
  if [[ -n "$TF_BINARY" ]]; then
    if command -v "$TF_BINARY" &>/dev/null; then
      echo "$TF_BINARY"
      return 0
    fi
    return 1
  fi
  if command -v terraform &>/dev/null; then
    echo "terraform"
    return 0
  fi
  if command -v tofu &>/dev/null; then
    echo "tofu"
    return 0
  fi
  return 1
}

# Detects tf binary and sets TF_CMD global. Calls json_error on failure.
require_tf_binary() {
  TF_CMD="$(detect_tf_binary)" || true
  if [[ -z "$TF_CMD" ]]; then
    if [[ -n "$TF_BINARY" ]]; then
      json_error "$TF_BINARY not found. Please install it or set TF_BINARY to a valid binary path."
    else
      json_error "Neither 'terraform' nor 'tofu' found in PATH. Install Terraform: https://developer.hashicorp.com/terraform/install or OpenTofu: https://opentofu.org/docs/intro/install/"
    fi
  fi
}

require_jq() {
  command -v jq &>/dev/null || json_error "jq is required but not found. Install: https://jqlang.github.io/jq/download/"
}

resolve_dir() {
  # Resolves directory path. Sets RESOLVED_DIR global.
  local dir="${1:-.}"
  if [[ ! -d "$dir" ]]; then
    json_error "Directory not found: $dir"
  fi
  RESOLVED_DIR="$(cd "$dir" && pwd)"
}

###############################################################################
# Subcommand: plan [dir]
# Runs terraform plan -json, parses output, classifies risk per resource.
###############################################################################
cmd_plan() {
  resolve_dir "${1:-.}"
  local dir="$RESOLVED_DIR"
  require_jq
  require_tf_binary
  local tf="$TF_CMD"
  info "Using binary: $tf"
  info "Working directory: $dir"

  cd "$dir"

  # Verify terraform config exists
  local has_tf_files
  has_tf_files=$(find . -maxdepth 1 \( -name '*.tf' -o -name '*.tf.json' \) -print -quit 2>/dev/null || true)
  if [[ -z "$has_tf_files" ]]; then
    json_error "No Terraform configuration files (*.tf or *.tf.json) found in $dir"
  fi

  # Check if initialized
  if [[ ! -d ".terraform" ]]; then
    warn "Terraform not initialized. Running $tf init..."
    if ! "$tf" init -input=false -no-color >&2 2>&1; then
      json_error "$tf init failed. Please run '$tf init' manually in $dir"
    fi
  fi

  info "Running $tf plan -json (timeout: ${PLAN_TIMEOUT}s)..."

  # Run plan and capture JSON output
  local plan_json_file
  plan_json_file="$(mktemp /tmp/tf-plan-review-XXXXXX.json)"
  # shellcheck disable=SC2064
  trap "rm -f '$plan_json_file'" EXIT

  local plan_exit=0
  if command -v timeout &>/dev/null; then
    timeout "$PLAN_TIMEOUT" "$tf" plan -json -input=false -no-color -out=/dev/null 2>/dev/null > "$plan_json_file" || plan_exit=$?
  elif command -v gtimeout &>/dev/null; then
    gtimeout "$PLAN_TIMEOUT" "$tf" plan -json -input=false -no-color -out=/dev/null 2>/dev/null > "$plan_json_file" || plan_exit=$?
  else
    "$tf" plan -json -input=false -no-color -out=/dev/null 2>/dev/null > "$plan_json_file" || plan_exit=$?
  fi

  # Plan exit code 2 = changes present (not an error)
  if [[ "$plan_exit" -ne 0 && "$plan_exit" -ne 2 ]]; then
    # Try to extract error from plan JSON
    local tf_error
    tf_error=$(jq -r 'select(.type == "diagnostic") | .diagnostic.summary // empty' "$plan_json_file" 2>/dev/null | head -5 || true)
    if [[ -n "$tf_error" ]]; then
      json_error "$tf plan failed: $tf_error"
    else
      json_error "$tf plan failed with exit code $plan_exit. Run '$tf plan' manually for details."
    fi
  fi

  # Parse the streaming JSON (one JSON object per line)
  parse_plan_json "$plan_json_file" "$tf" "$dir"
}

###############################################################################
# Parse plan JSON and produce risk report
###############################################################################
parse_plan_json() {
  local plan_file="$1"
  local tf_binary="$2"
  local work_dir="$3"

  # Extract resource changes from the streaming JSON plan output
  # terraform plan -json outputs newline-delimited JSON objects
  local changes_json
  changes_json=$(jq -s '
    [.[] | select(.type == "resource_drift" or .type == "planned_change" or .type == "change_summary")]
  ' "$plan_file" 2>/dev/null || echo "[]")

  # Extract planned_change entries (these are actual resource changes)
  local resource_changes
  resource_changes=$(echo "$changes_json" | jq '
    [.[] | select(.type == "planned_change") | .change // empty]
  ' 2>/dev/null || echo "[]")

  # Extract drift entries
  local drift_changes
  drift_changes=$(echo "$changes_json" | jq '
    [.[] | select(.type == "resource_drift") | .change // empty]
  ' 2>/dev/null || echo "[]")

  # Extract change summary
  local change_summary
  change_summary=$(echo "$changes_json" | jq '
    [.[] | select(.type == "change_summary")] | last // {}
  ' 2>/dev/null || echo "{}")

  # Count by action type
  local creates updates destroys replaces no_ops imports
  creates=$(echo "$resource_changes" | jq '[.[] | select(.action == "create")] | length' 2>/dev/null || echo "0")
  updates=$(echo "$resource_changes" | jq '[.[] | select(.action == "update")] | length' 2>/dev/null || echo "0")
  destroys=$(echo "$resource_changes" | jq '[.[] | select(.action == "delete")] | length' 2>/dev/null || echo "0")
  replaces=$(echo "$resource_changes" | jq '[.[] | select(.action == "replace" or (.action | type == "array" and (contains(["delete","create"]) or contains(["create","delete"]))))] | length' 2>/dev/null || echo "0")
  no_ops=$(echo "$resource_changes" | jq '[.[] | select(.action == "no-op" or .action == "read")] | length' 2>/dev/null || echo "0")
  imports=$(echo "$resource_changes" | jq '[.[] | select(.action == "create" and .importing != null)] | length' 2>/dev/null || echo "0")

  local drift_count
  drift_count=$(echo "$drift_changes" | jq 'length' 2>/dev/null || echo "0")

  # Classify each resource change with risk level
  local classified_resources
  classified_resources=$(echo "$resource_changes" | jq --arg crit "$CRITICAL_PATTERNS" --arg dang "$DANGEROUS_PATTERNS" --arg mod "$MODERATE_PATTERNS" '
    [.[] | . as $change |
      # Determine the action string
      (if (.action | type) == "array" then
        if (.action | contains(["delete","create"]) or contains(["create","delete"])) then "replace"
        else (.action | join(","))
        end
      else .action
      end) as $action_str |

      # Get resource address
      (.resource.resource // .resource.addr // "unknown") as $addr |

      # Get resource type
      (.resource.resource_type // ($addr | split(".") | if length > 1 then .[0:-1] | join(".") else .[0] end) // "unknown") as $rtype |

      # Classify risk
      (
        if ($action_str == "delete" or $action_str == "replace") then
          if ($rtype | test($crit; "i")) then "🔴 CRITICAL"
          elif ($rtype | test($dang; "i")) then "🔴 DANGEROUS"
          else "🟠 DANGEROUS"
          end
        elif ($action_str == "update") then
          if ($rtype | test($crit; "i")) then "🟠 DANGEROUS"
          elif ($rtype | test($mod; "i")) then "🟡 MODERATE"
          else "🟡 MODERATE"
          end
        elif ($action_str == "create") then
          if ($rtype | test($crit; "i")) then "🟡 MODERATE"
          else "🟢 SAFE"
          end
        else "🟢 SAFE"
        end
      ) as $risk |

      {
        address: $addr,
        resource_type: $rtype,
        action: $action_str,
        risk: $risk,
        importing: (.importing // null)
      }
    ] | sort_by(
      if .risk | startswith("🔴 CRITICAL") then 0
      elif .risk | startswith("🔴 DANGEROUS") then 1
      elif .risk | startswith("🟠") then 2
      elif .risk | startswith("🟡") then 3
      else 4
      end
    )
  ' 2>/dev/null || echo "[]")

  # Calculate overall risk score
  local critical_count dangerous_count moderate_count safe_count
  critical_count=$(echo "$classified_resources" | jq '[.[] | select(.risk | startswith("🔴 CRITICAL"))] | length' 2>/dev/null || echo "0")
  dangerous_count=$(echo "$classified_resources" | jq '[.[] | select(.risk | contains("DANGEROUS"))] | length' 2>/dev/null || echo "0")
  moderate_count=$(echo "$classified_resources" | jq '[.[] | select(.risk | startswith("🟡"))] | length' 2>/dev/null || echo "0")
  safe_count=$(echo "$classified_resources" | jq '[.[] | select(.risk | startswith("🟢"))] | length' 2>/dev/null || echo "0")

  local overall_risk="🟢 LOW"
  if [[ "$critical_count" -gt 0 ]]; then
    overall_risk="🔴 CRITICAL"
  elif [[ "$dangerous_count" -gt 0 ]]; then
    overall_risk="🔴 HIGH"
  elif [[ "$moderate_count" -gt 0 ]]; then
    overall_risk="🟡 MODERATE"
  fi

  # Extract diagnostics/warnings from plan
  local diagnostics
  diagnostics=$(jq -s '
    [.[] | select(.type == "diagnostic") | .diagnostic | {severity, summary, detail: (.detail // "")}]
  ' "$plan_file" 2>/dev/null || echo "[]")

  # Build final JSON output
  jq -n \
    --arg version "$VERSION" \
    --arg tf "$tf_binary" \
    --arg dir "$work_dir" \
    --arg overall "$overall_risk" \
    --argjson creates "$creates" \
    --argjson updates "$updates" \
    --argjson destroys "$destroys" \
    --argjson replaces "$replaces" \
    --argjson no_ops "$no_ops" \
    --argjson imports "$imports" \
    --argjson drift_count "$drift_count" \
    --argjson critical "$critical_count" \
    --argjson dangerous "$dangerous_count" \
    --argjson moderate "$moderate_count" \
    --argjson safe "$safe_count" \
    --argjson resources "$classified_resources" \
    --argjson drift "$drift_changes" \
    --argjson diagnostics "$diagnostics" \
    '{
      tool: "tf-plan-review",
      version: $version,
      binary: $tf,
      directory: $dir,
      timestamp: (now | todate),
      overall_risk: $overall,
      summary: {
        total_changes: ($creates + $updates + $destroys + $replaces),
        create: $creates,
        update: $updates,
        destroy: $destroys,
        replace: $replaces,
        no_op: $no_ops,
        import: $imports,
        drift_detected: $drift_count
      },
      risk_breakdown: {
        critical: $critical,
        dangerous: $dangerous,
        moderate: $moderate,
        safe: $safe
      },
      resources: $resources,
      drift: $drift,
      diagnostics: $diagnostics,
      footer: "Powered by Anvil AI 🔍"
    }'

  # Also output Markdown report to stderr
  generate_markdown_report \
    "$overall_risk" "$creates" "$updates" "$destroys" "$replaces" \
    "$drift_count" "$critical_count" "$dangerous_count" "$moderate_count" "$safe_count" \
    "$classified_resources" "$drift_changes" "$diagnostics" "$work_dir" "$tf_binary" >&2
}

###############################################################################
# Generate Markdown report (sent to stderr)
###############################################################################
generate_markdown_report() {
  local overall="$1" creates="$2" updates="$3" destroys="$4" replaces="$5"
  local drift="$6" critical="$7" dangerous="$8" moderate="$9" safe="${10}"
  local resources="${11}" drift_changes="${12}" diagnostics="${13}" dir="${14}" tf="${15}"

  local total=$((creates + updates + destroys + replaces))

  cat <<HEADER

# 🔍 Terraform Plan Risk Assessment

**Directory:** \`$dir\`
**Binary:** \`$tf\`
**Overall Risk:** $overall

---

## 📊 Change Summary

| Action | Count |
|--------|-------|
| ➕ Create | $creates |
| ✏️  Update | $updates |
| 💥 Destroy | $destroys |
| 🔄 Replace (destroy+create) | $replaces |
| **Total Changes** | **$total** |

HEADER

  if [[ "$drift" -gt 0 ]]; then
    echo "⚠️  **Drift detected:** $drift resource(s) have changed outside of Terraform."
    echo ""
  fi

  cat <<RISK
## 🎯 Risk Breakdown

| Risk Level | Count |
|------------|-------|
| 🔴 Critical | $critical |
| 🟠 Dangerous | $dangerous |
| 🟡 Moderate | $moderate |
| 🟢 Safe | $safe |

RISK

  # Show critical and dangerous resources prominently
  if [[ "$critical" -gt 0 || "$dangerous" -gt 0 ]]; then
    echo "## 🚨 HIGH-RISK CHANGES — REVIEW CAREFULLY"
    echo ""
    echo "| Risk | Action | Resource |"
    echo "|------|--------|----------|"
    echo "$resources" | jq -r '
      .[] | select(.risk | test("CRITICAL|DANGEROUS")) |
      "| \(.risk) | \(.action) | `\(.address)` |"
    ' 2>/dev/null
    echo ""
  fi

  # Show destroys prominently
  if [[ "$destroys" -gt 0 || "$replaces" -gt 0 ]]; then
    echo "## 💀 RESOURCES BEING DESTROYED"
    echo ""
    echo "**The following resources will be PERMANENTLY DELETED:**"
    echo ""
    echo "$resources" | jq -r '
      .[] | select(.action == "delete" or .action == "replace") |
      "- ⛔ `\(.address)` — \(.action)"
    ' 2>/dev/null
    echo ""
    echo "> ⚠️  **Destruction is irreversible.** Verify backups exist for any stateful resources above."
    echo ""
  fi

  # Show all changes in a table
  if [[ "$total" -gt 0 ]]; then
    echo "## 📋 All Resource Changes"
    echo ""
    echo "| Risk | Action | Resource |"
    echo "|------|--------|----------|"
    echo "$resources" | jq -r '
      .[] | select(.action != "no-op" and .action != "read") |
      "| \(.risk) | \(.action) | `\(.address)` |"
    ' 2>/dev/null
    echo ""
  fi

  # Drift section
  if [[ "$drift" -gt 0 ]]; then
    echo "## 🔀 Drift Detected"
    echo ""
    echo "These resources were changed outside of Terraform:"
    echo ""
    echo "$drift_changes" | jq -r '
      .[] |
      "- `\(.resource.addr // .resource.resource // "unknown")` — \(.action // "modified")"
    ' 2>/dev/null
    echo ""
  fi

  # Diagnostics
  local diag_count
  diag_count=$(echo "$diagnostics" | jq 'length' 2>/dev/null || echo "0")
  if [[ "$diag_count" -gt 0 ]]; then
    echo "## ⚠️  Diagnostics"
    echo ""
    echo "$diagnostics" | jq -r '.[] | "- **\(.severity):** \(.summary)"' 2>/dev/null
    echo ""
  fi

  # Pre-apply checklist
  echo "## ✅ Pre-Apply Checklist"
  echo ""
  if [[ "$destroys" -gt 0 || "$replaces" -gt 0 ]]; then
    echo "- [ ] **Backups verified** for all resources being destroyed/replaced"
    echo "- [ ] **Data migration** completed if replacing databases or storage"
    echo "- [ ] **DNS TTL** lowered if replacing load balancers or endpoints"
  fi
  if [[ "$critical" -gt 0 ]]; then
    echo "- [ ] **IAM/security changes** reviewed by security team"
    echo "- [ ] **No overly permissive policies** (e.g., \`*\` on resources/actions)"
  fi
  if [[ "$drift" -gt 0 ]]; then
    echo "- [ ] **Drift investigated** — understand why resources changed outside TF"
  fi
  echo "- [ ] **Change reviewed** by at least one other team member"
  echo "- [ ] **Rollback plan** documented in case of failure"
  echo "- [ ] **Monitoring/alerts** in place for affected services"
  if [[ "$total" -eq 0 ]]; then
    echo "- [x] **No changes detected** — plan is a no-op ✨"
  fi
  echo ""

  echo "---"
  echo ""
  echo "*Powered by Anvil AI 🔍*"
}

###############################################################################
# Subcommand: state [filter]
# Inspect terraform state — read-only
###############################################################################
cmd_state() {
  local filter="${1:-}"
  local dir="${2:-.}"
  resolve_dir "$dir"
  dir="$RESOLVED_DIR"
  require_jq
  require_tf_binary
  local tf="$TF_CMD"
  info "Using binary: $tf"

  cd "$dir"

  # List all resources in state
  local state_list
  if ! state_list=$("$tf" state list 2>/dev/null); then
    json_error "No Terraform state found in $dir. Run '$tf init' and '$tf apply' first, or check your backend configuration."
  fi

  if [[ -z "$state_list" ]]; then
    jq -n --arg dir "$dir" '{
      tool: "tf-plan-review",
      subcommand: "state",
      directory: $dir,
      total_resources: 0,
      resources: [],
      message: "State is empty — no managed resources.",
      footer: "Powered by Anvil AI 🔍"
    }'
    return
  fi

  # Apply filter if provided
  local filtered_list="$state_list"
  if [[ -n "$filter" ]]; then
    filtered_list=$(echo "$state_list" | grep -i "$filter" || true)
    if [[ -z "$filtered_list" ]]; then
      jq -n --arg dir "$dir" --arg filter "$filter" '{
        tool: "tf-plan-review",
        subcommand: "state",
        directory: $dir,
        filter: $filter,
        total_resources: 0,
        resources: [],
        message: "No resources match filter.",
        footer: "Powered by Anvil AI 🔍"
      }'
      return
    fi
  fi

  # Count and list
  local total
  total=$(echo "$filtered_list" | wc -l | tr -d ' ')

  # Build resources array
  local resources_json="[]"
  while IFS= read -r addr; do
    [[ -z "$addr" ]] && continue
    # Extract type from address (e.g., aws_instance.web -> aws_instance)
    local rtype
    rtype=$(echo "$addr" | sed 's/\[[^]]*\]//g' | rev | cut -d. -f2- | rev)

    # Classify resource type
    local category="other"
    if echo "$rtype" | grep -qiE "$CRITICAL_PATTERNS"; then
      category="security/data"
    elif echo "$rtype" | grep -qiE "$DANGEROUS_PATTERNS"; then
      category="infrastructure"
    elif echo "$rtype" | grep -qiE "$MODERATE_PATTERNS"; then
      category="scaling/monitoring"
    fi

    resources_json=$(echo "$resources_json" | jq --arg addr "$addr" --arg rtype "$rtype" --arg cat "$category" '. + [{address: $addr, type: $rtype, category: $cat}]')
  done <<< "$filtered_list"

  jq -n \
    --arg dir "$dir" \
    --arg filter "${filter:-}" \
    --argjson total "$total" \
    --argjson resources "$resources_json" \
    '{
      tool: "tf-plan-review",
      subcommand: "state",
      directory: $dir,
      filter: (if $filter == "" then null else $filter end),
      total_resources: $total,
      resources: $resources,
      footer: "Powered by Anvil AI 🔍"
    }'

  # Markdown to stderr
  {
    echo ""
    echo "# 📦 Terraform State Inspection"
    echo ""
    echo "**Directory:** \`$dir\`"
    if [[ -n "$filter" ]]; then
      echo "**Filter:** \`$filter\`"
    fi
    echo "**Total resources:** $total"
    echo ""
    echo "| Resource | Type | Category |"
    echo "|----------|------|----------|"
    echo "$resources_json" | jq -r '.[] | "| `\(.address)` | \(.type) | \(.category) |"' 2>/dev/null
    echo ""
    echo "---"
    echo ""
    echo "*Powered by Anvil AI 🔍*"
  } >&2
}

###############################################################################
# Subcommand: validate [dir]
# Run terraform validate -json
###############################################################################
cmd_validate() {
  local dir="${1:-.}"
  resolve_dir "$dir"
  dir="$RESOLVED_DIR"
  require_jq
  require_tf_binary
  local tf="$TF_CMD"
  info "Using binary: $tf"

  cd "$dir"

  # Verify terraform config exists
  local has_tf_files
  has_tf_files=$(find . -maxdepth 1 \( -name '*.tf' -o -name '*.tf.json' \) -print -quit 2>/dev/null || true)
  if [[ -z "$has_tf_files" ]]; then
    json_error "No Terraform configuration files (*.tf or *.tf.json) found in $dir"
  fi

  # Initialize if needed
  if [[ ! -d ".terraform" ]]; then
    warn "Terraform not initialized. Running $tf init -backend=false..."
    if ! "$tf" init -input=false -backend=false -no-color >&2 2>&1; then
      json_error "$tf init failed. Please run '$tf init' manually in $dir"
    fi
  fi

  # Run validate
  local validate_output
  validate_output=$("$tf" validate -json -no-color 2>/dev/null || true)

  local valid
  valid=$(echo "$validate_output" | jq -r '.valid // false' 2>/dev/null || echo "false")

  local error_count
  error_count=$(echo "$validate_output" | jq '.error_count // 0' 2>/dev/null || echo "0")

  local warning_count
  warning_count=$(echo "$validate_output" | jq '.warning_count // 0' 2>/dev/null || echo "0")

  local diagnostics_arr
  diagnostics_arr=$(echo "$validate_output" | jq '.diagnostics // []' 2>/dev/null || echo "[]")

  # Output JSON
  jq -n \
    --arg dir "$dir" \
    --arg tf "$tf" \
    --argjson valid "$valid" \
    --argjson errors "$error_count" \
    --argjson warnings "$warning_count" \
    --argjson diagnostics "$diagnostics_arr" \
    '{
      tool: "tf-plan-review",
      subcommand: "validate",
      directory: $dir,
      binary: $tf,
      valid: $valid,
      error_count: $errors,
      warning_count: $warnings,
      diagnostics: $diagnostics,
      footer: "Powered by Anvil AI 🔍"
    }'

  # Markdown to stderr
  {
    echo ""
    if [[ "$valid" == "true" ]]; then
      echo "# ✅ Terraform Configuration Valid"
    else
      echo "# ❌ Terraform Configuration Invalid"
    fi
    echo ""
    echo "**Directory:** \`$dir\`"
    echo "**Errors:** $error_count | **Warnings:** $warning_count"
    echo ""
    if [[ "$error_count" -gt 0 || "$warning_count" -gt 0 ]]; then
      echo "$diagnostics_arr" | jq -r '.[] | "- **\(.severity // "error"):** \(.summary // "unknown")\(if .detail then " — " + .detail else "" end)"' 2>/dev/null
    fi
    echo ""
    echo "---"
    echo ""
    echo "*Powered by Anvil AI 🔍*"
  } >&2
}

###############################################################################
# Usage
###############################################################################
usage() {
  cat <<EOF
tf-plan-review v${VERSION} — Terraform Plan Analyzer & Risk Assessor

USAGE:
  tf-plan-review.sh <subcommand> [options]

SUBCOMMANDS:
  plan [dir]        Analyze terraform plan, classify risk per resource
  state [filter]    Inspect terraform state (read-only)
  validate [dir]    Validate terraform configuration

OPTIONS:
  --help, -h        Show this help message
  --version, -v     Show version

ENVIRONMENT:
  TF_BINARY         Override terraform binary (e.g., "tofu")
  TF_PLAN_TIMEOUT   Plan timeout in seconds (default: 600)

OUTPUT:
  stdout → JSON (structured data for agent consumption)
  stderr → Markdown report (human-readable)

SAFETY:
  This tool is STRICTLY READ-ONLY.
  It NEVER runs terraform apply.
  It NEVER modifies terraform state.

Powered by Anvil AI 🔍
EOF
  exit 0
}

###############################################################################
# Main dispatch
###############################################################################
main() {
  case "${1:-}" in
    plan)
      shift
      cmd_plan "${1:-.}"
      ;;
    state)
      shift
      local filter="${1:-}"
      local dir="${2:-.}"
      cmd_state "$filter" "$dir"
      ;;
    validate)
      shift
      cmd_validate "${1:-.}"
      ;;
    --help|-h|help)
      usage
      ;;
    --version|-v)
      echo "tf-plan-review v${VERSION}"
      ;;
    "")
      usage
      ;;
    *)
      die "Unknown subcommand: $1. Run with --help for usage."
      ;;
  esac
}

main "$@"

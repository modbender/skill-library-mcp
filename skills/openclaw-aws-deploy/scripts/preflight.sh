#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $0 [options]

Options:
  --region <aws-region>                 AWS region (default: AWS_REGION env)
  --auth-mode <role|keys>               AWS auth mode (default: role)
  --role-arn <arn>                      Optional in role mode; validated if provided
  --channel-profile <telegram|none>     Channel profile (default: telegram)
  --model-profile <cheap|balanced|quality>  Model profile (default: cheap)
  --cost-mode <dev-low-cost|prod-baseline>  Cost mode (default: prod-baseline)
  --output <path>                       Output JSON report (default: ./preflight-report.json)
  -h, --help                            Show help
USAGE
}

REGION="${AWS_REGION:-}"
AUTH_MODE="role"
ROLE_ARN=""
CHANNEL_PROFILE="telegram"
MODEL_PROFILE="cheap"
COST_MODE="prod-baseline"
OUTPUT_PATH="./preflight-report.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --region) REGION="${2:-}"; shift 2 ;;
    --auth-mode) AUTH_MODE="${2:-}"; shift 2 ;;
    --role-arn) ROLE_ARN="${2:-}"; shift 2 ;;
    --channel-profile) CHANNEL_PROFILE="${2:-}"; shift 2 ;;
    --model-profile) MODEL_PROFILE="${2:-}"; shift 2 ;;
    --cost-mode) COST_MODE="${2:-}"; shift 2 ;;
    --output) OUTPUT_PATH="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

errors=()
warnings=()

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    errors+=("Missing required command: $cmd")
  fi
}

for cmd in aws jq bash openssl; do
  require_cmd "$cmd"
done

case "$AUTH_MODE" in
  role|keys) ;;
  *) errors+=("Invalid --auth-mode: $AUTH_MODE (expected role|keys)") ;;
esac

case "$CHANNEL_PROFILE" in
  telegram|none) ;;
  *) errors+=("Invalid --channel-profile: $CHANNEL_PROFILE (expected telegram|none)") ;;
esac

case "$MODEL_PROFILE" in
  cheap|balanced|quality) ;;
  *) errors+=("Invalid --model-profile: $MODEL_PROFILE (expected cheap|balanced|quality)") ;;
esac

case "$COST_MODE" in
  dev-low-cost|prod-baseline) ;;
  *) errors+=("Invalid --cost-mode: $COST_MODE (expected dev-low-cost|prod-baseline)") ;;
esac

if [[ -z "$REGION" ]]; then
  errors+=("AWS region missing. Provide --region or AWS_REGION")
fi

if [[ -n "$ROLE_ARN" && ! "$ROLE_ARN" =~ ^arn:aws:iam::[0-9]{12}:role/.+ ]]; then
  errors+=("Invalid role ARN format: $ROLE_ARN")
fi

caller_account=""
caller_arn=""
identity_ok=false
region_ok=false
quota_checks=()

if command -v aws >/dev/null 2>&1; then
  if [[ -n "$REGION" ]]; then
    if aws sts get-caller-identity --region "$REGION" --output json >/dev/null 2>&1; then
      region_ok=true
    elif aws ec2 describe-regions --region us-east-1 --query "Regions[?RegionName=='$REGION'].RegionName" --output text 2>/dev/null | grep -q "$REGION"; then
      warnings+=("Region appears valid via describe-regions fallback, but sts check in-region failed (possible SCP/org restriction).")
      region_ok=true
    else
      errors+=("Region validation failed for: $REGION")
    fi
  fi

  if ident_json=$(aws sts get-caller-identity --output json 2>/dev/null); then
    identity_ok=true
    caller_account=$(jq -r '.Account // empty' <<<"$ident_json")
    caller_arn=$(jq -r '.Arn // empty' <<<"$ident_json")
  else
    errors+=("Unable to call sts:get-caller-identity with current AWS credentials")
  fi

  # Capacity/permission checks (warning-level for now)
  if [[ -n "$REGION" ]]; then
    if aws ec2 describe-instance-type-offerings --region "$REGION" --location-type region --filters Name=instance-type,Values=t3.small,t3.medium --output json >/dev/null 2>&1; then
      quota_checks+=("ec2.instanceTypeOfferings:ok")
    else
      warnings+=("Could not verify instance type offerings for t3.small/t3.medium in $REGION")
      quota_checks+=("ec2.instanceTypeOfferings:warn")
    fi

    if aws elasticloadbalancingv2 describe-account-limits --region "$REGION" --output json >/dev/null 2>&1; then
      quota_checks+=("elbv2.accountLimits:ok")
    else
      warnings+=("Could not verify ELBv2 account limits/permissions")
      quota_checks+=("elbv2.accountLimits:warn")
    fi

    if [[ "$COST_MODE" == "prod-baseline" ]]; then
      if aws ec2 describe-account-attributes --region "$REGION" --attribute-names max-elastic-ips --output json >/dev/null 2>&1; then
        quota_checks+=("ec2.eipAttribute:ok")
      else
        warnings+=("Could not verify EIP/NAT-related account attributes (prod-baseline uses NAT gateway)")
        quota_checks+=("ec2.eipAttribute:warn")
      fi
    fi
  fi
fi

if [[ "$COST_MODE" == "dev-low-cost" ]]; then
  warnings+=("dev-low-cost may reduce availability/security controls. Not recommended for production.")
fi

status="ok"
if (( ${#errors[@]} > 0 )); then
  status="failed"
fi

next_action="Proceed to plan and deploy."
if [[ "$status" == "failed" ]]; then
  next_action="Fix reported errors, then rerun preflight."
fi

mkdir -p "$(dirname "$OUTPUT_PATH")"

jq -n \
  --arg schemaVersion "1.1" \
  --arg status "$status" \
  --arg region "$REGION" \
  --arg authMode "$AUTH_MODE" \
  --arg roleArn "$ROLE_ARN" \
  --arg channelProfile "$CHANNEL_PROFILE" \
  --arg modelProfile "$MODEL_PROFILE" \
  --arg costMode "$COST_MODE" \
  --arg callerAccount "$caller_account" \
  --arg callerArn "$caller_arn" \
  --arg nextAction "$next_action" \
  --argjson identityOk "$identity_ok" \
  --argjson regionOk "$region_ok" \
  --arg generatedAt "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson errors "$(printf '%s\n' "${errors[@]:-}" | jq -R . | jq -s 'map(select(length>0))')" \
  --argjson warnings "$(printf '%s\n' "${warnings[@]:-}" | jq -R . | jq -s 'map(select(length>0))')" \
  --argjson quotaChecks "$(printf '%s\n' "${quota_checks[@]:-}" | jq -R . | jq -s 'map(select(length>0))')" \
  '{
    schemaVersion: $schemaVersion,
    status: $status,
    generatedAt: $generatedAt,
    nextAction: $nextAction,
    inputs: {
      region: $region,
      authMode: $authMode,
      roleArn: (if $roleArn == "" then null else $roleArn end),
      channelProfile: $channelProfile,
      modelProfile: $modelProfile,
      costMode: $costMode
    },
    aws: {
      identityOk: $identityOk,
      regionOk: $regionOk,
      accountId: (if $callerAccount == "" then null else $callerAccount end),
      callerArn: (if $callerArn == "" then null else $callerArn end),
      quotaChecks: $quotaChecks
    },
    warnings: $warnings,
    errors: $errors
  }' > "$OUTPUT_PATH"

if [[ "$status" == "failed" ]]; then
  echo "Preflight failed. See: $OUTPUT_PATH"
  exit 1
fi

echo "Preflight passed. Report: $OUTPUT_PATH"

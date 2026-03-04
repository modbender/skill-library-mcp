#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# deploy_minimal.sh — One-shot minimal OpenClaw deployment to AWS
#
# Creates: VPC, subnet, IGW, route table, security group (no inbound),
#          IAM role (SSM only), SSM parameters, EC2 t4g.medium (ARM64)
#
# AWS Authentication (in priority order):
#   1. --profile <name>   — uses named AWS CLI profile
#   2. .env.aws file      — loads AWS_ACCESS_KEY_ID/SECRET (if found)
#   3. Environment/SSO    — uses existing AWS credentials (env vars, SSO, role)
#
# Prerequisites:
#   - .env.<name> or .env.starfish (TELEGRAM_BOT_TOKEN, optionally GEMINI_API_KEY)
#     Looks for .env.<name> first, falls back to .env.starfish
#     In the workspace root (parent of skill repo, or specified via --env-dir)
#
# Usage:
#   ./scripts/deploy_minimal.sh --name starfish --region us-east-1
#   ./scripts/deploy_minimal.sh --name starfish --profile my-aws-profile
#   ./scripts/deploy_minimal.sh --name starfish --region us-east-1 --env-dir /path/to/envs
#   ./scripts/deploy_minimal.sh --name starfish --region us-east-1 --model amazon-bedrock/minimax.minimax-m2.1
#   ./scripts/deploy_minimal.sh --name starfish --no-rollback --no-monitoring
#
# Lessons incorporated (issues #1-24):
#   - t4g.medium (4GB) required — t4g.small OOMs during npm install + gateway startup
#   - Node 22+ required — OpenClaw 2026.x needs Node ≥22.12.0
#   - Official Node tarball — NodeSource setup_22.x unreliable on AL2023 ARM64
#   - git required — OpenClaw npm install has git-based dependencies
#   - openclaw@latest — bare "openclaw" may resolve to placeholder package
#   - gateway run (not start) — start tries systemctl --user which fails
#   - Simplified systemd — removed ProtectHome/ReadWritePaths that cause issues
#   - plugins.entries.telegram.enabled: true — must be explicit
#   - dmPolicy: pairing — not allowlist without users
#   - auth-profiles.json for Gemini API key
###############################################################################

# --- log() must be defined BEFORE personality resolution ---
log() { echo "[$(date '+%H:%M:%S')] $*"; }
warn() { echo "[$(date '+%H:%M:%S')] ⚠️  $*" >&2; }

usage() {
  cat <<USAGE
Usage: $0 [options]

AWS Authentication (pick one):
  --profile <name>        Use a named AWS CLI profile
  (no flag)               Uses .env.aws if found, else existing env/SSO/role creds

Options:
  --name <name>           Agent/project name (default: starfish)
  --region <region>       AWS region (default: us-east-1)
  --env-dir <path>        Directory containing .env.aws and .env.starfish
                          (default: workspace root)
  --instance-type <type>  EC2 instance type (default: t4g.medium)
  --vpc-cidr <cidr>       VPC CIDR (default: 10.50.0.0/16)
  --subnet-cidr <cidr>    Subnet CIDR (default: 10.50.0.0/24)
  --output <path>         Output JSON file (default: ./deploy-output.json)
  --model <model>         AI model (default: amazon-bedrock/minimax.minimax-m2.1)
                          Any model string — passed directly to openclaw.json.
                          Bedrock models use IAM role auth (no API key needed).
                          If GEMINI_API_KEY is in .env.starfish, Gemini auth is set up.
                          Examples:
                            amazon-bedrock/minimax.minimax-m2.1 (default, no API key needed)
                            google/gemini-2.0-flash             (needs GEMINI_API_KEY)
                            amazon-bedrock/minimax.minimax-m2   (MiniMax M2)
                            amazon-bedrock/deepseek.deepseek-r1 (DeepSeek R1)
                            amazon-bedrock/moonshotai.kimi-k2.5 (Kimi K2.5)
  --personality <name|path>  Agent personality: default, sentinel, researcher,
                          coder, companion — or path to custom SOUL.md
  --az <zone>             Availability zone (e.g. us-east-1a). Auto-selects if not set.
  --no-rollback           Don't auto-teardown on failure (for debugging)
  --pair-user <id>        Telegram user ID to auto-approve pairing after deploy
  --no-monitoring         Skip CloudWatch alarms and log shipping
  --dry-run               Show what would be created without creating
  --cleanup-first         Tear down existing resources with same name first
  -h, --help              Show this help

Examples:
  # Basic deploy with defaults (Gemini Flash, us-east-1)
  $0 --name starfish

  # Deploy with a Bedrock model (no API key needed)
  $0 --name starfish --model amazon-bedrock/deepseek.deepseek-r1

  # Deploy with a specific AWS profile
  $0 --name starfish --profile my-aws-profile --region eu-west-1

  # Deploy and auto-approve Telegram pairing
  $0 --name starfish --pair-user 123456789

Environment files:
  The script looks for .env.<name> first (e.g. .env.starfish when --name is
  starfish), falling back to .env.starfish for backward compatibility.
  Override the search directory with --env-dir.
USAGE
}

# Defaults — t4g.medium (4GB) required for OpenClaw 2026.x
NAME="starfish"
REGION="us-east-1"
ENV_DIR=""
INSTANCE_TYPE="t4g.medium"
VPC_CIDR="10.50.0.0/16"
SUBNET_CIDR="10.50.0.0/24"
OUTPUT_PATH="./deploy-output.json"
MODEL="amazon-bedrock/minimax.minimax-m2.1"
DRY_RUN=false
CLEANUP_FIRST=false
PERSONALITY="default"
AWS_PROFILE_FLAG=""
NO_ROLLBACK=false
MONITORING=true
AZ_OVERRIDE=""
PAIR_USER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="${2:-}"; shift 2 ;;
    --region) REGION="${2:-}"; shift 2 ;;
    --env-dir) ENV_DIR="${2:-}"; shift 2 ;;
    --instance-type) INSTANCE_TYPE="${2:-}"; shift 2 ;;
    --vpc-cidr) VPC_CIDR="${2:-}"; shift 2 ;;
    --subnet-cidr) SUBNET_CIDR="${2:-}"; shift 2 ;;
    --output) OUTPUT_PATH="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --personality) PERSONALITY="${2:-}"; shift 2 ;;
    --profile) AWS_PROFILE_FLAG="${2:-}"; shift 2 ;;
    --az) AZ_OVERRIDE="${2:-}"; shift 2 ;;
    --pair-user) PAIR_USER="${2:-}"; shift 2 ;;
    --no-rollback) NO_ROLLBACK=true; shift ;;
    --no-monitoring) MONITORING=false; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --cleanup-first) CLEANUP_FIRST=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

# --- Input validation ---
if ! [[ "$NAME" =~ ^[a-zA-Z][a-zA-Z0-9-]{0,30}$ ]]; then
  echo "ERROR: --name must be 1-31 alphanumeric/hyphen chars starting with a letter" >&2
  exit 1
fi

if [[ -n "$PAIR_USER" ]] && ! [[ "$PAIR_USER" =~ ^[0-9]+$ ]]; then
  echo "ERROR: --pair-user must be a numeric Telegram user ID" >&2
  exit 1
fi

if ! [[ "$REGION" =~ ^[a-z]{2}-[a-z]+-[0-9]+$ ]]; then
  echo "ERROR: --region must be a valid AWS region (e.g. us-east-1)" >&2
  exit 1
fi

if ! [[ "$INSTANCE_TYPE" =~ ^[a-z][0-9][a-z]?\.[a-z0-9]+$ ]]; then
  echo "ERROR: --instance-type must be a valid EC2 instance type (e.g. t4g.medium)" >&2
  exit 1
fi

if ! [[ "$VPC_CIDR" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$ ]]; then
  echo "ERROR: --vpc-cidr must be a valid CIDR block (e.g. 10.50.0.0/16)" >&2
  exit 1
fi

if ! [[ "$SUBNET_CIDR" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$ ]]; then
  echo "ERROR: --subnet-cidr must be a valid CIDR block (e.g. 10.50.0.0/24)" >&2
  exit 1
fi

if [[ -n "$AZ_OVERRIDE" ]] && ! [[ "$AZ_OVERRIDE" =~ ^[a-z]{2}-[a-z]+-[0-9]+[a-z]$ ]]; then
  echo "ERROR: --az must be a valid availability zone (e.g. us-east-1a)" >&2
  exit 1
fi

if ! [[ "$MODEL" =~ ^[A-Za-z0-9._:/-]+$ ]]; then
  echo "ERROR: --model contains invalid characters" >&2
  exit 1
fi

# Resolve paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

###############################################################################
# AWS Authentication Chain (P0 #1)
# Priority: --profile > .env.aws > existing env/SSO/role
###############################################################################

# Build AWS CLI wrapper that includes --profile if specified
if [[ -n "$AWS_PROFILE_FLAG" ]]; then
  log "AWS auth: using profile '$AWS_PROFILE_FLAG'"
  aws_cmd() { aws --region "$REGION" --profile "$AWS_PROFILE_FLAG" --output text "$@"; }
  aws_json() { aws --region "$REGION" --profile "$AWS_PROFILE_FLAG" --output json "$@"; }
  aws_raw() { aws --region "$REGION" --profile "$AWS_PROFILE_FLAG" "$@"; }
else
  # Try loading .env.aws if it exists (optional)
  if [[ -z "$ENV_DIR" ]]; then
    if [[ -f "$SKILL_DIR/../.env.aws" ]]; then
      ENV_DIR="$SKILL_DIR/.."
    elif [[ -f "$SKILL_DIR/.env.aws" ]]; then
      ENV_DIR="$SKILL_DIR"
    fi
  fi

  if [[ -n "$ENV_DIR" ]]; then
    ENV_DIR="$(cd "$ENV_DIR" && pwd)"
  fi

  if [[ -n "$ENV_DIR" && -f "$ENV_DIR/.env.aws" ]]; then
    log "AWS auth: loading credentials from $ENV_DIR/.env.aws"
    while IFS='=' read -r key value; do
      export "$key=$value"
    done < <(grep -E '^[A-Z0-9_]+=' "$ENV_DIR/.env.aws")
  else
    log "AWS auth: using existing environment/SSO/role credentials"
  fi

  export AWS_DEFAULT_REGION="$REGION"
  aws_cmd() { aws --region "$REGION" --output text "$@"; }
  aws_json() { aws --region "$REGION" --output json "$@"; }
  aws_raw() { aws --region "$REGION" "$@"; }
fi

# Verify AWS credentials work (regardless of auth method)
if ! aws_cmd sts get-caller-identity --query 'Account' >/dev/null 2>&1; then
  echo "ERROR: AWS credentials not valid. Provide --profile, set up .env.aws, or configure AWS SSO/env." >&2
  exit 1
fi

# Find .env.<name> (or fall back to .env.starfish for backward compatibility)
ENV_FILE=".env.${NAME}"
ENV_FALLBACK=".env.starfish"

resolve_env_file() {
  local dir="$1"
  if [[ -f "$dir/$ENV_FILE" ]]; then
    echo "$dir/$ENV_FILE"
  elif [[ -f "$dir/$ENV_FALLBACK" ]]; then
    echo "$dir/$ENV_FALLBACK"
  else
    echo ""
  fi
}

RESOLVED_ENV=""
if [[ -z "$ENV_DIR" ]]; then
  RESOLVED_ENV=$(resolve_env_file "$SKILL_DIR/..")
  if [[ -n "$RESOLVED_ENV" ]]; then
    ENV_DIR="$(cd "$SKILL_DIR/.." && pwd)"
  else
    RESOLVED_ENV=$(resolve_env_file "$SKILL_DIR")
    if [[ -n "$RESOLVED_ENV" ]]; then
      ENV_DIR="$(cd "$SKILL_DIR" && pwd)"
    else
      echo "ERROR: Cannot find $ENV_FILE (or $ENV_FALLBACK). Provide --env-dir" >&2
      exit 1
    fi
  fi
else
  RESOLVED_ENV=$(resolve_env_file "$ENV_DIR")
  if [[ -z "$RESOLVED_ENV" ]]; then
    echo "ERROR: Neither $ENV_DIR/$ENV_FILE nor $ENV_DIR/$ENV_FALLBACK found" >&2
    exit 1
  fi
fi

log "Env file: $RESOLVED_ENV"

# Load env file
while IFS='=' read -r key value; do
  export "$key=$value"
done < <(grep -E '^[A-Z0-9_]+=' "$RESOLVED_ENV")

# Validate required vars (only Telegram token — AWS keys are no longer hard-required)
if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  echo "ERROR: TELEGRAM_BOT_TOKEN is not set (check .env.starfish)" >&2
  exit 1
fi

# Check optional GEMINI_API_KEY
HAS_GEMINI_KEY=false
if [[ -n "${GEMINI_API_KEY:-}" ]]; then
  HAS_GEMINI_KEY=true
fi

# Determine if model is Bedrock and extract model ID
IS_BEDROCK=false
BEDROCK_MODEL_ID=""
if [[ "$MODEL" == amazon-bedrock/* ]]; then
  IS_BEDROCK=true
  BEDROCK_MODEL_ID="${MODEL#amazon-bedrock/}"
  log "Bedrock model detected: $BEDROCK_MODEL_ID"
fi

# Resolve personality file
PERSONALITIES_DIR="$SKILL_DIR/assets/personalities"
if [[ -f "$PERSONALITY" ]]; then
  SOUL_CONTENT=$(cat "$PERSONALITY")
  log "Personality: custom ($PERSONALITY)"
elif [[ -f "$PERSONALITIES_DIR/${PERSONALITY}.md" ]]; then
  SOUL_CONTENT=$(cat "$PERSONALITIES_DIR/${PERSONALITY}.md")
  log "Personality: $PERSONALITY (built-in)"
else
  echo "ERROR: Unknown personality '$PERSONALITY'" >&2
  echo "Available: default, sentinel, researcher, coder, companion" >&2
  echo "Or provide a path to a custom SOUL.md file" >&2
  exit 1
fi

# Base64-encode SOUL.md for safe transport in user-data
SOUL_B64=$(echo "$SOUL_CONTENT" | base64)

# Base64-encode agent default files
AGENT_DEFAULTS_DIR="$SKILL_DIR/assets/agent-defaults"
AGENTS_MD_B64=$(cat "$AGENT_DEFAULTS_DIR/AGENTS.md" | base64)
HEARTBEAT_MD_B64=$(cat "$AGENT_DEFAULTS_DIR/HEARTBEAT.md" | base64)
USER_MD_B64=$(cat "$AGENT_DEFAULTS_DIR/USER.md" | base64)

# Generate a gateway token
GATEWAY_TOKEN=$(openssl rand -hex 32)

TAG_KEY="Project"
TAG_VALUE="$NAME"

# Generate a unique deploy ID (timestamp-based, same across all resources)
DEPLOY_ID="${NAME}-$(date -u +%Y%m%dT%H%M%SZ)"
DEPLOY_TAG_KEY="DeployId"

log "Deploy ID: $DEPLOY_ID"

###############################################################################
# Failure trap — auto-rollback (P1 #6)
###############################################################################
cleanup_on_failure() {
  local exit_code=$?
  if [[ $exit_code -ne 0 ]]; then
    echo "" >&2
    echo "=========================================" >&2
    echo "  ❌ Deploy failed (exit code $exit_code)" >&2
    echo "=========================================" >&2

    # Save partial output for diagnostics
    if [[ -n "${VPC_ID:-}" || -n "${INSTANCE_ID:-}" ]]; then
      log "Saving partial deploy-output.json for diagnostics..."
      cat > "${OUTPUT_PATH}.partial" <<PARTEOF
{
  "name": "$NAME",
  "region": "$REGION",
  "deployId": "$DEPLOY_ID",
  "partial": true,
  "failedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "infrastructure": {
    "vpcId": "${VPC_ID:-}",
    "subnetId": "${SUBNET_ID:-}",
    "igwId": "${IGW_ID:-}",
    "routeTableId": "${RTB_ID:-}",
    "securityGroupId": "${SG_ID:-}",
    "iamRole": "${NAME}-role",
    "instanceProfile": "${NAME}-instance-profile"
  },
  "instance": {
    "instanceId": "${INSTANCE_ID:-}",
    "instanceType": "$INSTANCE_TYPE"
  }
}
PARTEOF
      log "Partial output saved to: ${OUTPUT_PATH}.partial"
    fi

    if [[ "$NO_ROLLBACK" == "true" ]]; then
      echo "  --no-rollback set. Resources left in place for debugging." >&2
      echo "  To clean up manually:" >&2
      echo "    $SCRIPT_DIR/teardown.sh --deploy-id $DEPLOY_ID --region $REGION --yes" >&2
    else
      echo "  Auto-rolling back (deploy-id: $DEPLOY_ID)..." >&2
      if [[ -x "$SCRIPT_DIR/teardown.sh" ]]; then
        # Scope teardown to this deploy only
        "$SCRIPT_DIR/teardown.sh" --deploy-id "$DEPLOY_ID" --region "$REGION" \
          ${ENV_DIR:+--env-dir "$ENV_DIR"} \
          ${AWS_PROFILE_FLAG:+--profile "$AWS_PROFILE_FLAG"} \
          --yes 2>&1 || warn "Auto-rollback encountered errors (see above)"
        log "Auto-rollback complete. Check AWS console to verify."
      else
        echo "  teardown.sh not found — manual cleanup required:" >&2
        echo "    $SCRIPT_DIR/teardown.sh --deploy-id $DEPLOY_ID --region $REGION --yes" >&2
      fi
    fi
    echo "=========================================" >&2
  fi
}
trap cleanup_on_failure EXIT

log "=========================================="
log "  OpenClaw Minimal Deploy: $NAME"
log "  Region: $REGION | Instance: $INSTANCE_TYPE"
log "  Model:  $MODEL"
log "  Monitoring: $MONITORING"
log "=========================================="

# Verify AWS identity
CALLER=$(aws_cmd sts get-caller-identity --query 'Account')
log "AWS Account: $CALLER"

###############################################################################
# Preflight Validation (P1 #5)
###############################################################################
log ""
log "--- Preflight Checks ---"

# Check IAM permissions
log "Checking IAM permissions..."
PREFLIGHT_FAIL=false

check_permission() {
  local action="$1" resource="$2"
  if ! aws_raw iam simulate-principal-policy \
    --policy-source-arn "$(aws_cmd sts get-caller-identity --query 'Arn')" \
    --action-names "$action" \
    --resource-arns "$resource" \
    --query 'EvaluationResults[0].EvalDecision' --output text 2>/dev/null | grep -q "allowed"; then
    # simulate-principal-policy may fail if caller lacks iam:SimulatePrincipalPolicy
    # In that case, we skip and let the actual API calls fail later
    return 1
  fi
  return 0
}

# Try permission check (best-effort — iam:SimulatePrincipalPolicy may not be available)
if aws_raw iam simulate-principal-policy \
  --policy-source-arn "$(aws_cmd sts get-caller-identity --query 'Arn')" \
  --action-names "ec2:CreateVpc" \
  --resource-arns "*" \
  --query 'EvaluationResults[0].EvalDecision' --output text 2>/dev/null | grep -q "allowed"; then
  log "  ✅ ec2:CreateVpc — allowed"

  for action in "ec2:RunInstances" "iam:CreateRole" "ssm:PutParameter"; do
    if aws_raw iam simulate-principal-policy \
      --policy-source-arn "$(aws_cmd sts get-caller-identity --query 'Arn')" \
      --action-names "$action" \
      --resource-arns "*" \
      --query 'EvaluationResults[0].EvalDecision' --output text 2>/dev/null | grep -q "allowed"; then
      log "  ✅ $action — allowed"
    else
      warn "  ❌ $action — denied or unknown"
      PREFLIGHT_FAIL=true
    fi
  done
else
  log "  ⏭️  Permission simulation unavailable (iam:SimulatePrincipalPolicy not granted) — skipping"
fi

# Check instance type availability in region
log "Checking instance type availability..."
OFFERING=$(aws_cmd ec2 describe-instance-type-offerings \
  --location-type availability-zone \
  --filters "Name=instance-type,Values=$INSTANCE_TYPE" \
  --query 'InstanceTypeOfferings[0].InstanceType' 2>/dev/null) || true
if [[ -z "$OFFERING" ]]; then
  warn "Instance type $INSTANCE_TYPE may not be available in $REGION"
  PREFLIGHT_FAIL=true
else
  log "  ✅ $INSTANCE_TYPE available in $REGION"
fi

# Check if resources with same name already exist
EXISTING_VPC=$(aws_cmd ec2 describe-vpcs \
  --filters "Name=tag:Project,Values=$NAME" \
  --query 'Vpcs[0].VpcId' 2>/dev/null) || true
if [[ -n "$EXISTING_VPC" && "$EXISTING_VPC" != "None" && "$CLEANUP_FIRST" != "true" ]]; then
  warn "Resources with Project=$NAME already exist (VPC: $EXISTING_VPC)"
  warn "Use --cleanup-first to tear down first, or use a different --name"
  PREFLIGHT_FAIL=true
fi

if [[ "$PREFLIGHT_FAIL" == "true" && "$DRY_RUN" != "true" ]]; then
  echo "ERROR: Preflight checks failed. Fix issues above before deploying." >&2
  exit 1
fi

log "Preflight checks passed ✅"

if [[ "$DRY_RUN" == "true" ]]; then
  log "[DRY RUN] Would create: VPC, subnet, IGW, SG, IAM role, SSM params, EC2 instance"
  log "[DRY RUN] Instance type: $INSTANCE_TYPE, AMI: AL2023 ARM64"
  exit 0
fi

###############################################################################
# Step 0: Cleanup if requested
###############################################################################
if [[ "$CLEANUP_FIRST" == "true" ]]; then
  log ""
  log "--- Step 0: Cleaning up existing $NAME resources ---"
  if [[ -x "$SCRIPT_DIR/teardown.sh" ]]; then
    "$SCRIPT_DIR/teardown.sh" --name "$NAME" --region "$REGION" \
      ${ENV_DIR:+--env-dir "$ENV_DIR"} \
      ${AWS_PROFILE_FLAG:+--profile "$AWS_PROFILE_FLAG"} \
      --yes || true
  else
    log "WARN: teardown.sh not executable, skipping cleanup"
  fi
fi

# Initialize resource tracking variables for rollback
VPC_ID=""
IGW_ID=""
SUBNET_ID=""
RTB_ID=""
SG_ID=""
INSTANCE_ID=""

###############################################################################
# Step 1: VPC
###############################################################################
log ""
log "--- Step 1: Creating VPC ---"
VPC_ID=$(aws_cmd ec2 create-vpc \
  --cidr-block "$VPC_CIDR" \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${NAME}-vpc},{Key=$TAG_KEY,Value=$TAG_VALUE},{Key=$DEPLOY_TAG_KEY,Value=$DEPLOY_ID}]" \
  --query 'Vpc.VpcId')
log "VPC: $VPC_ID"

# Enable DNS
aws_raw ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-support '{"Value":true}'
aws_raw ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames '{"Value":true}'

###############################################################################
# Step 2: Internet Gateway
###############################################################################
log ""
log "--- Step 2: Creating Internet Gateway ---"
IGW_ID=$(aws_cmd ec2 create-internet-gateway \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${NAME}-igw},{Key=$TAG_KEY,Value=$TAG_VALUE},{Key=$DEPLOY_TAG_KEY,Value=$DEPLOY_ID}]" \
  --query 'InternetGateway.InternetGatewayId')
log "IGW: $IGW_ID"

aws_raw ec2 attach-internet-gateway --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID"

###############################################################################
# Step 3: Subnet (P1 #9: AZ Selection)
###############################################################################
log ""
log "--- Step 3: Creating Subnet ---"

if [[ -n "$AZ_OVERRIDE" ]]; then
  AZ="$AZ_OVERRIDE"
  log "AZ: $AZ (user-specified)"
else
  # Get all AZs and try them in order if capacity errors occur
  ALL_AZS=$(aws_cmd ec2 describe-availability-zones --query 'AvailabilityZones[*].ZoneName')
  AZ=$(echo "$ALL_AZS" | awk '{print $1}')
  log "AZ: $AZ (auto-selected, first available)"
fi

SUBNET_ID=$(aws_cmd ec2 create-subnet \
  --vpc-id "$VPC_ID" \
  --cidr-block "$SUBNET_CIDR" \
  --availability-zone "$AZ" \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${NAME}-subnet},{Key=$TAG_KEY,Value=$TAG_VALUE},{Key=$DEPLOY_TAG_KEY,Value=$DEPLOY_ID}]" \
  --query 'Subnet.SubnetId')
log "Subnet: $SUBNET_ID ($AZ)"

# Auto-assign public IPs
aws_raw ec2 modify-subnet-attribute --subnet-id "$SUBNET_ID" --map-public-ip-on-launch

###############################################################################
# Step 4: Route Table
###############################################################################
log ""
log "--- Step 4: Creating Route Table ---"
RTB_ID=$(aws_cmd ec2 create-route-table \
  --vpc-id "$VPC_ID" \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${NAME}-rtb},{Key=$TAG_KEY,Value=$TAG_VALUE},{Key=$DEPLOY_TAG_KEY,Value=$DEPLOY_ID}]" \
  --query 'RouteTable.RouteTableId')
log "Route Table: $RTB_ID"

aws_raw ec2 create-route --route-table-id "$RTB_ID" --destination-cidr-block 0.0.0.0/0 --gateway-id "$IGW_ID" > /dev/null
aws_raw ec2 associate-route-table --route-table-id "$RTB_ID" --subnet-id "$SUBNET_ID" > /dev/null

###############################################################################
# Step 5: Security Group (NO inbound — SSM only)
###############################################################################
log ""
log "--- Step 5: Creating Security Group (no inbound) ---"
SG_ID=$(aws_cmd ec2 create-security-group \
  --group-name "${NAME}-sg" \
  --description "OpenClaw ${NAME} - outbound only, SSM access" \
  --vpc-id "$VPC_ID" \
  --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=${NAME}-sg},{Key=$TAG_KEY,Value=$TAG_VALUE},{Key=$DEPLOY_TAG_KEY,Value=$DEPLOY_ID}]" \
  --query 'GroupId')
log "Security Group: $SG_ID"

###############################################################################
# Step 6: IAM Role (SSM + SSM Parameter Store + Bedrock + optional CloudWatch)
###############################################################################
log ""
log "--- Step 6: Creating IAM Role ---"

TRUST_POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "ec2.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}'

# Create role (ignore error if exists)
if aws_raw iam create-role \
  --role-name "${NAME}-role" \
  --assume-role-policy-document "$TRUST_POLICY" \
  --tags "Key=$TAG_KEY,Value=$TAG_VALUE" "Key=$DEPLOY_TAG_KEY,Value=$DEPLOY_ID" > /dev/null 2>&1; then
  log "IAM Role: ${NAME}-role (created)"
else
  log "IAM Role: ${NAME}-role (already exists)"
fi

# Attach SSM managed policy
aws_raw iam attach-role-policy --role-name "${NAME}-role" \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore 2>/dev/null || true

# Add inline policy for SSM Parameter Store access
SSM_PARAM_POLICY=$(cat <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParametersByPath"
      ],
      "Resource": "arn:aws:ssm:${REGION}:${CALLER}:parameter/${NAME}/*"
    }
  ]
}
POLICY
)

aws_raw iam put-role-policy --role-name "${NAME}-role" \
  --policy-name SSMParameterAccess \
  --policy-document "$SSM_PARAM_POLICY"

# Add Bedrock permissions (always — costs nothing, enables any Bedrock model)
BEDROCK_POLICY=$(cat <<BPOLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels"
      ],
      "Resource": [
        "*",
        "arn:aws:bedrock:${REGION}::foundation-model/*",
        "arn:aws:bedrock:${REGION}:*:inference-profile/*",
        "arn:aws:bedrock:${REGION}:*:application-inference-profile/*"
      ]
    }
  ]
}
BPOLICY
)
aws_raw iam put-role-policy --role-name "${NAME}-role" \
  --policy-name BedrockAccess \
  --policy-document "$BEDROCK_POLICY"
log "Added BedrockAccess inline policy"

# Add CloudWatch permissions if monitoring enabled (P1 #7, #8)
if [[ "$MONITORING" == "true" ]]; then
  CW_POLICY=$(cat <<CWPOLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams",
        "logs:DescribeLogGroups",
        "logs:PutRetentionPolicy"
      ],
      "Resource": "*"
    }
  ]
}
CWPOLICY
)
  aws_raw iam put-role-policy --role-name "${NAME}-role" \
    --policy-name CloudWatchAccess \
    --policy-document "$CW_POLICY"
  log "Added CloudWatchAccess inline policy"
fi

# Create instance profile
if aws_raw iam create-instance-profile --instance-profile-name "${NAME}-instance-profile" > /dev/null 2>&1; then
  log "Instance Profile: ${NAME}-instance-profile (created)"
else
  log "Instance Profile: ${NAME}-instance-profile (already exists)"
fi

# Ensure role is attached (idempotent — ignore EntityAlreadyExists)
aws_raw iam add-role-to-instance-profile \
  --instance-profile-name "${NAME}-instance-profile" \
  --role-name "${NAME}-role" 2>/dev/null || true

# Wait for profile to propagate
log "Waiting 10s for IAM propagation..."
sleep 10

###############################################################################
# Step 7: Store secrets in SSM Parameter Store
###############################################################################
log ""
log "--- Step 7: Storing secrets in SSM Parameter Store ---"

aws_raw ssm put-parameter \
  --name "/${NAME}/telegram/bot_token" \
  --value "$TELEGRAM_BOT_TOKEN" \
  --type SecureString \
  --overwrite > /dev/null
log "Stored: /${NAME}/telegram/bot_token"

if [[ "$HAS_GEMINI_KEY" == "true" ]]; then
  aws_raw ssm put-parameter \
    --name "/${NAME}/gemini/api_key" \
    --value "$GEMINI_API_KEY" \
    --type SecureString \
    --overwrite > /dev/null
  log "Stored: /${NAME}/gemini/api_key"
else
  log "Skipped: /${NAME}/gemini/api_key (not provided)"
fi

aws_raw ssm put-parameter \
  --name "/${NAME}/gateway/token" \
  --value "$GATEWAY_TOKEN" \
  --type SecureString \
  --overwrite > /dev/null
log "Stored: /${NAME}/gateway/token"

###############################################################################
# Step 8: Get AMI (AL2023 ARM64)
###############################################################################
log ""
log "--- Step 8: Getting latest AL2023 ARM64 AMI ---"
AMI_ID=$(aws_cmd ssm get-parameter \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64 \
  --query 'Parameter.Value')
log "AMI: $AMI_ID"

###############################################################################
# Step 9: Generate user-data script
###############################################################################
log ""
log "--- Step 9: Generating user-data ---"

# Node version — OpenClaw 2026.x requires ≥22.12.0
NODE_VERSION="22.14.0"

# Build CloudWatch agent config snippet for user-data (P1 #8)
if [[ "$MONITORING" == "true" ]]; then
  CW_AGENT_SETUP='
# Install and configure CloudWatch agent for log shipping
echo "[$(date)] Installing CloudWatch agent..."
retry_cmd dnf install -y amazon-cloudwatch-agent || true

if command -v amazon-cloudwatch-agent-ctl &>/dev/null; then
  echo "[$(date)] Configuring CloudWatch agent..."
  mkdir -p /opt/aws/amazon-cloudwatch-agent/etc
  cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json <<CWEOF
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/openclaw-bootstrap.log",
            "log_group_name": "/openclaw/__NAME__",
            "log_stream_name": "{instance_id}/bootstrap",
            "retention_in_days": 7
          }
        ]
      }
    }
  }
}
CWEOF
  sed -i "s/__NAME__/${AGENT_NAME}/g" /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
  amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json || true
  echo "[$(date)] CloudWatch agent started"
else
  echo "[$(date)] WARN: CloudWatch agent not available — skipping log shipping"
fi
'
else
  CW_AGENT_SETUP='# CloudWatch agent disabled (--no-monitoring)'
fi

USER_DATA=$(cat <<'USERDATA'
#!/bin/bash
set -euo pipefail

exec > /var/log/openclaw-bootstrap.log 2>&1
echo "[$(date)] Starting OpenClaw bootstrap..."

# Variables (replaced by deploy script)
AGENT_NAME="__NAME__"
REGION="__REGION__"
NODE_VERSION="__NODE_VERSION__"
MODEL="__MODEL__"
HAS_GEMINI_KEY="__HAS_GEMINI_KEY__"

# Retry helper — 3 retries with exponential backoff
retry_cmd() {
  local max_retries=3
  local delay=5
  local attempt=1
  while true; do
    if "$@"; then
      return 0
    fi
    if [[ $attempt -ge $max_retries ]]; then
      echo "[$(date)] FATAL: Command failed after $max_retries attempts: $*" >&2
      return 1
    fi
    echo "[$(date)] Attempt $attempt failed, retrying in ${delay}s..."
    sleep $delay
    delay=$((delay * 2))
    attempt=$((attempt + 1))
  done
}

# Install dependencies (git required for npm, jq for JSON)
echo "[$(date)] Installing dependencies..."
retry_cmd dnf install -y git jq tar gzip

__CW_AGENT_SETUP__

# Install Node.js from official tarball (NodeSource unreliable on AL2023 ARM64)
echo "[$(date)] Installing Node.js ${NODE_VERSION}..."
cd /tmp
NODE_TARBALL="node-v${NODE_VERSION}-linux-arm64.tar.xz"
retry_cmd curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/${NODE_TARBALL}" -o node.tar.xz
retry_cmd curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt" -o SHASUMS256.txt

# Verify tarball integrity
echo "[$(date)] Verifying Node.js tarball SHA256..."
EXPECTED_SHA=$(grep "${NODE_TARBALL}" SHASUMS256.txt | awk '{print $1}')
ACTUAL_SHA=$(sha256sum node.tar.xz | awk '{print $1}')
if [[ "$EXPECTED_SHA" != "$ACTUAL_SHA" ]]; then
  echo "[$(date)] FATAL: SHA256 mismatch! Expected=$EXPECTED_SHA Actual=$ACTUAL_SHA" >&2
  exit 1
fi
echo "[$(date)] SHA256 verified OK"

tar -xf node.tar.xz -C /usr/local --strip-components=1
rm -f node.tar.xz SHASUMS256.txt
hash -r

# Verify Node
echo "[$(date)] Node version: $(node --version)"
echo "[$(date)] npm version: $(npm --version)"

# Install OpenClaw (must use @latest to avoid placeholder package)
echo "[$(date)] Installing OpenClaw..."
retry_cmd npm install -g openclaw@latest 2>&1 | tail -20
echo "[$(date)] OpenClaw path: $(which openclaw)"

# Create openclaw user
echo "[$(date)] Creating openclaw user..."
useradd -r -m -s /bin/bash openclaw || true

# Create directories
mkdir -p /home/openclaw/.openclaw/agents/main/agent
mkdir -p /home/openclaw/.openclaw/workspace

# Create startup script (P0 #2: Secrets at Rest — fetches from SSM at each start)
echo "[$(date)] Writing startup script..."
cat > /usr/local/bin/openclaw-startup.sh <<'STARTEOF'
#!/bin/bash
set -e

export HOME="/home/openclaw"
export PATH="/usr/local/bin:/usr/bin:$PATH"
export NODE_OPTIONS="--max-old-space-size=1024"
export AWS_DEFAULT_REGION="__REGION__"
export AWS_REGION="__REGION__"

AGENT_NAME="__NAME__"
MODEL="__MODEL__"
HAS_GEMINI_KEY="__HAS_GEMINI_KEY__"

cd /home/openclaw/.openclaw

echo "[$(date)] Fetching secrets from SSM Parameter Store..."

# Fetch secrets from SSM at runtime (secrets rewritten on each start, not baked into images)
TELEGRAM_TOKEN=$(aws ssm get-parameter --region "$AWS_REGION" --name "/${AGENT_NAME}/telegram/bot_token" --with-decryption --query 'Parameter.Value' --output text)
GW_TOKEN=$(aws ssm get-parameter --region "$AWS_REGION" --name "/${AGENT_NAME}/gateway/token" --with-decryption --query 'Parameter.Value' --output text)

GEMINI_KEY=""
if [[ "$HAS_GEMINI_KEY" == "true" ]]; then
  GEMINI_KEY=$(aws ssm get-parameter --region "$AWS_REGION" --name "/${AGENT_NAME}/gemini/api_key" --with-decryption --query 'Parameter.Value' --output text)
fi

echo "[$(date)] Writing ephemeral config files..."

# Write openclaw.json (overwritten each start — ephemeral)
cat > /home/openclaw/.openclaw/openclaw.json <<OCEOF
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "${GW_TOKEN}"
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "${MODEL}"
      },
      "workspace": "/home/openclaw/.openclaw/workspace",
      "heartbeat": {
        "every": "30m",
        "prompt": "Check HEARTBEAT.md if it exists. If nothing needs attention, reply HEARTBEAT_OK."
      }
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "dmPolicy": "pairing",
      "groupPolicy": "allowlist",
      "streamMode": "partial",
      "accounts": {
        "default": {
          "name": "${AGENT_NAME}",
          "dmPolicy": "pairing",
          "botToken": "${TELEGRAM_TOKEN}",
          "groupPolicy": "allowlist",
          "streamMode": "partial"
        }
      }
    }
  },
  "plugins": {
    "entries": {
      "telegram": {
        "enabled": true
      }
    }
  },
  __MODELS_BLOCK__
  "tools": {
    "agentToAgent": {
      "enabled": true
    }
  }
}
OCEOF

# Write auth-profiles.json (always include Bedrock for IAM-based access)
if [[ "$HAS_GEMINI_KEY" == "true" && -n "$GEMINI_KEY" ]]; then
  cat > /home/openclaw/.openclaw/agents/main/agent/auth-profiles.json <<APEOF
{
  "version": 1,
  "profiles": {
    "amazon-bedrock:default": {
      "type": "aws",
      "provider": "amazon-bedrock",
      "awsRegion": "${AWS_REGION}"
    },
    "google:default": {
      "type": "token",
      "provider": "google",
      "token": "${GEMINI_KEY}"
    }
  }
}
APEOF
else
  cat > /home/openclaw/.openclaw/agents/main/agent/auth-profiles.json <<APEOF
{
  "version": 1,
  "profiles": {
    "amazon-bedrock:default": {
      "type": "aws",
      "provider": "amazon-bedrock",
      "awsRegion": "${AWS_REGION}"
    }
  }
}
APEOF
fi

# Ensure ownership
chown -R openclaw:openclaw /home/openclaw/.openclaw

echo "[$(date)] Starting gateway..."

# Start gateway in FOREGROUND mode
# CRITICAL: Use 'run' not 'start' — start tries systemctl --user which fails
# AWS_PROFILE=default tells OpenClaw to use the AWS SDK default credential chain (IMDS/instance role)
# Must be set AFTER SSM calls above (which use IMDS directly without a profile)
export AWS_PROFILE=default
exec /usr/local/bin/openclaw gateway run --allow-unconfigured
STARTEOF
chmod +x /usr/local/bin/openclaw-startup.sh
sed -i "s/__REGION__/${REGION}/g" /usr/local/bin/openclaw-startup.sh
sed -i "s/__NAME__/${AGENT_NAME}/g" /usr/local/bin/openclaw-startup.sh
sed -i "s/__HAS_GEMINI_KEY__/${HAS_GEMINI_KEY}/g" /usr/local/bin/openclaw-startup.sh

# Use | delimiter for sed to handle slashes in model paths (e.g. amazon-bedrock/minimax.minimax-m2.1)
sed -i "s|__MODEL__|${MODEL}|g" /usr/local/bin/openclaw-startup.sh

# Create systemd service (simplified — security hardening removed due to namespace issues)
echo "[$(date)] Writing systemd service..."
cat > /etc/systemd/system/openclaw.service <<'SVCEOF'
[Unit]
Description=OpenClaw Gateway
Documentation=https://docs.openclaw.ai
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=openclaw
Group=openclaw
WorkingDirectory=/home/openclaw/.openclaw
ExecStart=/usr/local/bin/openclaw-startup.sh
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=openclaw

[Install]
WantedBy=multi-user.target
SVCEOF

# Write SOUL.md (personality) to workspace
echo "[$(date)] Writing SOUL.md (personality)..."
echo "__SOUL_B64__" | base64 -d > /home/openclaw/.openclaw/workspace/SOUL.md
cp /home/openclaw/.openclaw/workspace/SOUL.md /home/openclaw/.openclaw/agents/main/agent/SOUL.md

echo "[$(date)] Writing agent default files (AGENTS.md, HEARTBEAT.md, USER.md)..."
echo "__AGENTS_MD_B64__" | base64 -d > /home/openclaw/.openclaw/workspace/AGENTS.md
echo "__HEARTBEAT_MD_B64__" | base64 -d > /home/openclaw/.openclaw/workspace/HEARTBEAT.md
echo "__USER_MD_B64__" | base64 -d > /home/openclaw/.openclaw/workspace/USER.md
mkdir -p /home/openclaw/.openclaw/workspace/memory

# Fix ownership
chown -R openclaw:openclaw /home/openclaw/.openclaw

# Enable and start
echo "[$(date)] Starting OpenClaw service..."
systemctl daemon-reload
systemctl enable openclaw
systemctl start openclaw

# Wait and check
sleep 15
if systemctl is-active openclaw; then
  echo "[$(date)] ✅ OpenClaw is running!"
  journalctl -u openclaw -n 10 --no-pager
else
  echo "[$(date)] ❌ OpenClaw failed to start"
  journalctl -u openclaw -n 30 --no-pager
  exit 1
fi

echo "[$(date)] Bootstrap complete!"
USERDATA
)

# MODEL already validated in input validation section above
MODEL_ESCAPED="$MODEL"

# Generate models config block based on provider
if [[ "$IS_BEDROCK" == "true" ]]; then
  MODELS_BLOCK=$(cat <<MEOF
"models": {
    "providers": {
      "amazon-bedrock": {
        "baseUrl": "https://bedrock-runtime.${REGION}.amazonaws.com",
        "api": "bedrock-converse-stream",
        "auth": "aws-sdk",
        "models": [
          {
            "id": "${BEDROCK_MODEL_ID}",
            "name": "${BEDROCK_MODEL_ID}",
            "input": ["text"],
            "contextWindow": 128000,
            "maxTokens": 4096
          }
        ]
      }
    },
    "bedrockDiscovery": {
      "enabled": true,
      "region": "${REGION}"
    }
  },
MEOF
)
else
  MODELS_BLOCK=$(cat <<'MEOF'
"models": {
    "bedrockDiscovery": {
      "enabled": false
    }
  },
MEOF
)
fi

# Replace placeholders
USER_DATA="${USER_DATA//__NAME__/$NAME}"
USER_DATA="${USER_DATA//__REGION__/$REGION}"
USER_DATA="${USER_DATA//__NODE_VERSION__/$NODE_VERSION}"
USER_DATA="${USER_DATA//__MODEL__/$MODEL_ESCAPED}"
USER_DATA="${USER_DATA//__HAS_GEMINI_KEY__/$HAS_GEMINI_KEY}"
USER_DATA="${USER_DATA//__MODELS_BLOCK__/$MODELS_BLOCK}"
USER_DATA="${USER_DATA//__SOUL_B64__/$SOUL_B64}"
USER_DATA="${USER_DATA//__AGENTS_MD_B64__/$AGENTS_MD_B64}"
USER_DATA="${USER_DATA//__HEARTBEAT_MD_B64__/$HEARTBEAT_MD_B64}"
USER_DATA="${USER_DATA//__USER_MD_B64__/$USER_MD_B64}"
USER_DATA="${USER_DATA//__CW_AGENT_SETUP__/$CW_AGENT_SETUP}"

# Gzip + Base64 encode (cloud-init auto-detects gzip; avoids 16KB user-data limit)
USER_DATA_B64=$(echo "$USER_DATA" | gzip -9 | base64)

###############################################################################
# Step 9b: Verify Bedrock model access (if using Bedrock)
if [[ "$IS_BEDROCK" == "true" ]]; then
  log ""
  log "--- Step 9b: Checking Bedrock model access ---"
  MODEL_AVAIL=$(aws_cmd bedrock get-foundation-model-availability \
    --model-id "$BEDROCK_MODEL_ID" \
    --query 'authorizationStatus' 2>/dev/null || echo "UNKNOWN")
  if [[ "$MODEL_AVAIL" == "AUTHORIZED" ]]; then
    log "✅ Bedrock model $BEDROCK_MODEL_ID is authorized"
  else
    log "⚠️  Bedrock model $BEDROCK_MODEL_ID status: $MODEL_AVAIL"
    log "    You may need to enable it in the AWS Bedrock Console:"
    log "    https://console.aws.amazon.com/bedrock/home?region=${REGION}#/modelaccess"
    log "    Continuing deployment — model may fail until enabled."
  fi
fi

###############################################################################
# Step 10: Launch EC2 Instance (P1 #9: AZ retry)
###############################################################################
log ""
log "--- Step 10: Launching EC2 Instance ---"

launch_instance() {
  local az="$1"
  aws_cmd ec2 run-instances \
    --image-id "$AMI_ID" \
    --instance-type "$INSTANCE_TYPE" \
    --subnet-id "$SUBNET_ID" \
    --security-group-ids "$SG_ID" \
    --iam-instance-profile "Name=${NAME}-instance-profile" \
    --user-data "$USER_DATA_B64" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${NAME}},{Key=$TAG_KEY,Value=$TAG_VALUE},{Key=$DEPLOY_TAG_KEY,Value=$DEPLOY_ID}]" \
    --metadata-options "HttpTokens=required,HttpEndpoint=enabled" \
    --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":20,"VolumeType":"gp3","Encrypted":true}}]' \
    --query 'Instances[0].InstanceId' 2>&1
}

# Try launching — if InsufficientInstanceCapacity and no AZ was forced, try other AZs
INSTANCE_ID=""
LAUNCH_OUTPUT=$(launch_instance "$AZ" 2>&1) || true

if [[ "$LAUNCH_OUTPUT" == i-* ]]; then
  INSTANCE_ID="$LAUNCH_OUTPUT"
elif [[ -z "$AZ_OVERRIDE" ]] && echo "$LAUNCH_OUTPUT" | grep -qi "InsufficientInstanceCapacity\|Unsupported"; then
  log "Capacity issue in $AZ, trying other AZs..."
  for fallback_az in $ALL_AZS; do
    [[ "$fallback_az" == "$AZ" ]] && continue
    log "Trying AZ: $fallback_az..."
    # Need new subnet in this AZ — recreate
    aws_raw ec2 delete-subnet --subnet-id "$SUBNET_ID" 2>/dev/null || true
    SUBNET_ID=$(aws_cmd ec2 create-subnet \
      --vpc-id "$VPC_ID" \
      --cidr-block "$SUBNET_CIDR" \
      --availability-zone "$fallback_az" \
      --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${NAME}-subnet},{Key=$TAG_KEY,Value=$TAG_VALUE},{Key=$DEPLOY_TAG_KEY,Value=$DEPLOY_ID}]" \
      --query 'Subnet.SubnetId')
    aws_raw ec2 modify-subnet-attribute --subnet-id "$SUBNET_ID" --map-public-ip-on-launch
    # Re-associate route table
    aws_raw ec2 associate-route-table --route-table-id "$RTB_ID" --subnet-id "$SUBNET_ID" > /dev/null

    LAUNCH_OUTPUT=$(launch_instance "$fallback_az" 2>&1) || true
    if [[ "$LAUNCH_OUTPUT" == i-* ]]; then
      INSTANCE_ID="$LAUNCH_OUTPUT"
      AZ="$fallback_az"
      log "Launched in AZ: $AZ"
      break
    fi
  done
fi

if [[ -z "$INSTANCE_ID" ]]; then
  echo "ERROR: Failed to launch instance: $LAUNCH_OUTPUT" >&2
  exit 1
fi

log "Instance: $INSTANCE_ID (AZ: $AZ)"

log "Waiting for instance to be running..."
aws_raw ec2 wait instance-running --instance-ids "$INSTANCE_ID"

PUBLIC_IP=$(aws_cmd ec2 describe-instances \
  --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].PublicIpAddress')
log "Public IP: $PUBLIC_IP"

###############################################################################
# Step 10b: CloudWatch Alarms (P1 #7)
###############################################################################
ALARM_ARNS=()

if [[ "$MONITORING" == "true" ]]; then
  log ""
  log "--- Step 10b: Creating CloudWatch Alarms ---"

  # StatusCheckFailed alarm
  STATUS_ALARM_NAME="${NAME}-status-check-failed"
  if aws_raw cloudwatch put-metric-alarm \
    --alarm-name "$STATUS_ALARM_NAME" \
    --alarm-description "OpenClaw ${NAME}: instance status check failed" \
    --namespace AWS/EC2 \
    --metric-name StatusCheckFailed \
    --dimensions "Name=InstanceId,Value=$INSTANCE_ID" \
    --statistic Maximum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --treat-missing-data breaching \
    --tags "Key=$TAG_KEY,Value=$TAG_VALUE" "Key=$DEPLOY_TAG_KEY,Value=$DEPLOY_ID" 2>/dev/null; then
    STATUS_ALARM_ARN=$(aws_cmd cloudwatch describe-alarms \
      --alarm-names "$STATUS_ALARM_NAME" \
      --query 'MetricAlarms[0].AlarmArn' 2>/dev/null) || true
    [[ -n "$STATUS_ALARM_ARN" && "$STATUS_ALARM_ARN" != "None" ]] && ALARM_ARNS+=("$STATUS_ALARM_ARN")
    log "  ✅ StatusCheckFailed alarm: $STATUS_ALARM_NAME"
  else
    warn "  Failed to create StatusCheckFailed alarm — check CloudWatch permissions"
  fi

  # CPUUtilization > 90% for 5 min
  CPU_ALARM_NAME="${NAME}-cpu-high"
  if aws_raw cloudwatch put-metric-alarm \
    --alarm-name "$CPU_ALARM_NAME" \
    --alarm-description "OpenClaw ${NAME}: CPU > 90% for 5 min" \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions "Name=InstanceId,Value=$INSTANCE_ID" \
    --statistic Average \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 90 \
    --comparison-operator GreaterThanThreshold \
    --treat-missing-data missing \
    --tags "Key=$TAG_KEY,Value=$TAG_VALUE" "Key=$DEPLOY_TAG_KEY,Value=$DEPLOY_ID" 2>/dev/null; then
    CPU_ALARM_ARN=$(aws_cmd cloudwatch describe-alarms \
      --alarm-names "$CPU_ALARM_NAME" \
      --query 'MetricAlarms[0].AlarmArn' 2>/dev/null) || true
    [[ -n "$CPU_ALARM_ARN" && "$CPU_ALARM_ARN" != "None" ]] && ALARM_ARNS+=("$CPU_ALARM_ARN")
    log "  ✅ CPUUtilization alarm: $CPU_ALARM_NAME"
  else
    warn "  Failed to create CPUUtilization alarm — check CloudWatch permissions"
  fi

  # Set up CloudWatch log group with retention (P1 #8)
  log "Creating CloudWatch log group..."
  if aws_raw logs create-log-group --log-group-name "/openclaw/${NAME}" \
    --tags "$TAG_KEY=$TAG_VALUE,$DEPLOY_TAG_KEY=$DEPLOY_ID" 2>/dev/null; then
    aws_raw logs put-retention-policy --log-group-name "/openclaw/${NAME}" \
      --retention-in-days 7 2>/dev/null || true
    log "  ✅ Log group: /openclaw/${NAME} (7 day retention)"
  else
    warn "  Failed to create log group — check CloudWatch Logs permissions (logs may already exist)"
  fi
fi

###############################################################################
# Step 11: Wait for SSM + bootstrap to complete
###############################################################################
log ""
log "--- Step 11: Waiting for SSM agent and bootstrap ---"
log "This takes 4-6 minutes for Node.js + OpenClaw install..."

# Wait for SSM to be available
for i in $(seq 1 30); do
  if aws_raw ssm describe-instance-information \
    --filters "Key=InstanceIds,Values=$INSTANCE_ID" \
    --query 'InstanceInformationList[0].PingStatus' --output text 2>/dev/null | grep -q "Online"; then
    log "SSM agent is online (attempt $i)"
    break
  fi
  if [[ $i -eq 30 ]]; then
    log "WARN: SSM agent not online after 5 min — instance may still be bootstrapping"
  fi
  sleep 10
done

# Wait for bootstrap to finish (check for the log file marker)
log "Waiting for bootstrap to complete..."
for i in $(seq 1 48); do
  RESULT=$(aws_raw ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["grep -c \"Bootstrap complete\" /var/log/openclaw-bootstrap.log 2>/dev/null || echo 0"]' \
    --query 'Command.CommandId' --output text 2>/dev/null) || true

  if [[ -n "$RESULT" ]]; then
    sleep 5
    STATUS=$(aws_raw ssm get-command-invocation \
      --command-id "$RESULT" --instance-id "$INSTANCE_ID" \
      --query 'StandardOutputContent' --output text 2>/dev/null) || true
    if [[ "$STATUS" == *"1"* ]]; then
      log "Bootstrap completed!"
      break
    fi
  fi

  if [[ $i -eq 48 ]]; then
    log "WARN: Bootstrap may still be running after 8 min"
    log "Check logs: aws ssm start-session --target $INSTANCE_ID"
  fi
  sleep 10
done

###############################################################################
# Step 12: Smoke Test
###############################################################################
log ""
log "--- Step 12: Smoke Test ---"

SMOKE_CMD='systemctl is-active openclaw && echo "SERVICE_OK"; journalctl -u openclaw -n 5 --no-pager'
SMOKE_ID=$(aws_raw ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"$SMOKE_CMD\"]" \
  --query 'Command.CommandId' --output text 2>/dev/null) || true

if [[ -n "$SMOKE_ID" ]]; then
  sleep 10
  SMOKE_OUT=$(aws_raw ssm get-command-invocation \
    --command-id "$SMOKE_ID" --instance-id "$INSTANCE_ID" \
    --query 'StandardOutputContent' --output text 2>/dev/null) || true
  log "Smoke test output:"
  echo "$SMOKE_OUT"
fi

###############################################################################
# Step 12b: Auto-approve pairing (if --pair-user provided)
###############################################################################
if [[ -n "$PAIR_USER" ]]; then
  log ""
  log "--- Step 12b: Auto-approving Telegram pairing for user $PAIR_USER ---"
  log "Waiting 30s for gateway to register pairing request..."
  sleep 30

  PAIR_CMD="sudo -u openclaw bash -c 'cd /home/openclaw/.openclaw && /usr/local/bin/openclaw pairing approve telegram $PAIR_USER'"
  PAIR_ID=$(aws_raw ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters "commands=[\"$PAIR_CMD\"]" \
    --query 'Command.CommandId' --output text 2>/dev/null) || true

  if [[ -n "$PAIR_ID" ]]; then
    sleep 10
    PAIR_OUT=$(aws_raw ssm get-command-invocation \
      --command-id "$PAIR_ID" --instance-id "$INSTANCE_ID" \
      --query 'StandardOutputContent' --output text 2>/dev/null) || true
    PAIR_ERR=$(aws_raw ssm get-command-invocation \
      --command-id "$PAIR_ID" --instance-id "$INSTANCE_ID" \
      --query 'StandardErrorContent' --output text 2>/dev/null) || true

    if [[ -n "$PAIR_OUT" ]]; then
      log "Pairing output: $PAIR_OUT"
    fi
    if [[ -n "$PAIR_ERR" && "$PAIR_ERR" != "None" ]]; then
      warn "Pairing stderr: $PAIR_ERR"
    fi
    log "Auto-pairing command sent. If the user hasn't messaged the bot yet,"
    log "they can message it and you can re-run pairing via SSM."
  else
    warn "Failed to send pairing command via SSM"
  fi
fi

###############################################################################
# Step 13: Save outputs
###############################################################################
log ""
log "--- Step 13: Saving deployment outputs ---"

# Build conditional SSM entry for deploy output
if [[ "$HAS_GEMINI_KEY" == "true" ]]; then
  GEMINI_SSM_JSON_ENTRY=",
    \"/${NAME}/gemini/api_key\""
else
  GEMINI_SSM_JSON_ENTRY=""
fi

# Build alarm ARNs JSON array
ALARM_JSON="[]"
if [[ ${#ALARM_ARNS[@]} -gt 0 ]]; then
  ALARM_JSON="["
  for i in "${!ALARM_ARNS[@]}"; do
    [[ $i -gt 0 ]] && ALARM_JSON+=","
    ALARM_JSON+="\"${ALARM_ARNS[$i]}\""
  done
  ALARM_JSON+="]"
fi

cat > "$OUTPUT_PATH" <<OUTEOF
{
  "name": "$NAME",
  "region": "$REGION",
  "accountId": "$CALLER",
  "deployId": "$DEPLOY_ID",
  "deployedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "infrastructure": {
    "vpcId": "$VPC_ID",
    "subnetId": "$SUBNET_ID",
    "igwId": "$IGW_ID",
    "routeTableId": "$RTB_ID",
    "securityGroupId": "$SG_ID",
    "iamRole": "${NAME}-role",
    "instanceProfile": "${NAME}-instance-profile"
  },
  "instance": {
    "instanceId": "$INSTANCE_ID",
    "instanceType": "$INSTANCE_TYPE",
    "amiId": "$AMI_ID",
    "publicIp": "$PUBLIC_IP",
    "availabilityZone": "$AZ"
  },
  "ssmParameters": [
    "/${NAME}/telegram/bot_token",
    "/${NAME}/gateway/token"${GEMINI_SSM_JSON_ENTRY}
  ],
  "monitoring": {
    "enabled": $MONITORING,
    "alarmArns": $ALARM_JSON,
    "logGroup": "/openclaw/${NAME}"
  },
  "config": {
    "model": "$MODEL",
    "channel": "telegram",
    "dmPolicy": "pairing",
    "gatewayPort": 18789,
    "personality": "$PERSONALITY"
  },
  "access": {
    "ssm": "aws ssm start-session --target $INSTANCE_ID --region $REGION",
    "logs": "aws ssm send-command --instance-ids $INSTANCE_ID --document-name AWS-RunShellScript --parameters 'commands=[\"journalctl -u openclaw -n 50 --no-pager\"]' --region $REGION"
  }
}
OUTEOF

log ""
log "=========================================="
log "  ✅ Deployment Complete!"
log "=========================================="
log ""
log "  Instance:  $INSTANCE_ID"
log "  Public IP: $PUBLIC_IP"
log "  AZ:        $AZ"
log "  Model:     $MODEL"
log "  Channel:   Telegram (@${NAME} bot)"
log ""
log "  SSM Access:"
log "    aws ssm start-session --target $INSTANCE_ID --region $REGION"
log ""
if [[ -n "$PAIR_USER" ]]; then
  log "  Pairing: auto-approved for Telegram user $PAIR_USER"
else
  log "  Next steps:"
  log "    1. Message the Telegram bot to get a pairing code"
  log "    2. Approve pairing via SSM:"
  log "       openclaw pairing approve telegram <CODE>"
fi
log ""
log "  Output saved to: $OUTPUT_PATH"
log "=========================================="

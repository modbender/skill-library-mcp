#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# setup_deployer_role.sh — Create an IAM role/user with minimum permissions
#                          to run the OpenClaw deploy + teardown scripts.
#
# This creates a deployer role (or user) with precisely the permissions needed.
# No AdministratorAccess required.
#
# Usage:
#   # Create IAM role (for SSO/assume-role workflows):
#   ./scripts/setup_deployer_role.sh --type role --name openclaw-deployer
#
#   # Create IAM user (for key-based auth):
#   ./scripts/setup_deployer_role.sh --type user --name openclaw-deployer
#
#   # Use existing AWS profile for auth:
#   ./scripts/setup_deployer_role.sh --type role --name openclaw-deployer --profile admin
#
#   # Dry run (print policy, don't create):
#   ./scripts/setup_deployer_role.sh --dry-run
###############################################################################

usage() {
  cat <<USAGE
Usage: $0 [options]

Options:
  --type <role|user>      Create IAM role or user (default: role)
  --name <name>           IAM role/user name (default: openclaw-deployer)
  --profile <profile>     AWS profile to use for creating the role
  --region <region>       AWS region (default: us-east-1)
  --account-id <id>       AWS account ID (auto-detected if not provided)
  --trust-principal <arn> Trust principal for role (default: current user/role)
  --dry-run               Print the policy JSON without creating anything
  -h, --help              Show help

Examples:
  # Create deployer role (assumes current identity can create IAM resources)
  ./scripts/setup_deployer_role.sh --type role --name openclaw-deployer

  # Create deployer user with access keys
  ./scripts/setup_deployer_role.sh --type user --name openclaw-deployer

  # Just print the policy
  ./scripts/setup_deployer_role.sh --dry-run
USAGE
}

TYPE="role"
NAME="openclaw-deployer"
PROFILE=""
REGION="us-east-1"
ACCOUNT_ID=""
TRUST_PRINCIPAL=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type) TYPE="${2:-}"; shift 2 ;;
    --name) NAME="${2:-}"; shift 2 ;;
    --profile) PROFILE="${2:-}"; shift 2 ;;
    --region) REGION="${2:-}"; shift 2 ;;
    --account-id) ACCOUNT_ID="${2:-}"; shift 2 ;;
    --trust-principal) TRUST_PRINCIPAL="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

# Build AWS CLI prefix
AWS_OPTS="--region $REGION --output json"
[[ -n "$PROFILE" ]] && AWS_OPTS="$AWS_OPTS --profile $PROFILE"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# Detect account ID
if [[ -z "$ACCOUNT_ID" ]]; then
  ACCOUNT_ID=$(aws $AWS_OPTS sts get-caller-identity --query 'Account' --output text 2>/dev/null) || {
    echo "ERROR: Cannot detect AWS account ID. Provide --account-id or configure AWS credentials." >&2
    exit 1
  }
fi

log "AWS Account: $ACCOUNT_ID"
log "Region: $REGION"

# Detect current principal for trust policy
if [[ -z "$TRUST_PRINCIPAL" && "$TYPE" == "role" ]]; then
  TRUST_PRINCIPAL=$(aws $AWS_OPTS sts get-caller-identity --query 'Arn' --output text 2>/dev/null) || true
  # If it's a role session, extract the role ARN
  if [[ "$TRUST_PRINCIPAL" == *":assumed-role/"* ]]; then
    ROLE_NAME=$(echo "$TRUST_PRINCIPAL" | sed 's|.*:assumed-role/||; s|/.*||')
    TRUST_PRINCIPAL="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
  fi
fi

###############################################################################
# The deployer policy — minimum permissions for deploy + teardown
###############################################################################

DEPLOYER_POLICY=$(cat <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EC2NetworkManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateVpc",
        "ec2:DeleteVpc",
        "ec2:ModifyVpcAttribute",
        "ec2:DescribeVpcs",
        "ec2:CreateSubnet",
        "ec2:DeleteSubnet",
        "ec2:ModifySubnetAttribute",
        "ec2:DescribeSubnets",
        "ec2:CreateInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:AttachInternetGateway",
        "ec2:DetachInternetGateway",
        "ec2:DescribeInternetGateways",
        "ec2:CreateRouteTable",
        "ec2:DeleteRouteTable",
        "ec2:CreateRoute",
        "ec2:AssociateRouteTable",
        "ec2:DisassociateRouteTable",
        "ec2:DescribeRouteTables",
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup",
        "ec2:DescribeSecurityGroups",
        "ec2:CreateTags",
        "ec2:DescribeTags",
        "ec2:DescribeAvailabilityZones"
      ],
      "Resource": "*"
    },
    {
      "Sid": "EC2InstanceManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:TerminateInstances",
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceTypeOfferings",
        "ec2:DescribeImages"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMRoleManagement",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:TagRole",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:CreateInstanceProfile",
        "iam:DeleteInstanceProfile",
        "iam:AddRoleToInstanceProfile",
        "iam:RemoveRoleFromInstanceProfile",
        "iam:PassRole",
        "iam:SimulatePrincipalPolicy",
        "iam:ListRoleTags",
        "iam:ListRolePolicies",
        "iam:ListAttachedRolePolicies"
      ],
      "Resource": [
        "arn:aws:iam::${ACCOUNT_ID}:role/*-role",
        "arn:aws:iam::${ACCOUNT_ID}:instance-profile/*-instance-profile",
        "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
      ]
    },
    {
      "Sid": "SSMParameterStore",
      "Effect": "Allow",
      "Action": [
        "ssm:PutParameter",
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:DeleteParameter",
        "ssm:DescribeInstanceInformation",
        "ssm:SendCommand",
        "ssm:GetCommandInvocation",
        "ssm:StartSession"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchMonitoring",
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricAlarm",
        "cloudwatch:DeleteAlarms",
        "cloudwatch:DescribeAlarms",
        "logs:CreateLogGroup",
        "logs:DeleteLogGroup",
        "logs:PutRetentionPolicy",
        "logs:TagLogGroup"
      ],
      "Resource": "*"
    },
    {
      "Sid": "STSIdentity",
      "Effect": "Allow",
      "Action": [
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
POLICY
)

###############################################################################
# Output or create
###############################################################################

if [[ "$DRY_RUN" == "true" ]]; then
  log ""
  log "=== Deployer Policy (dry run) ==="
  echo "$DEPLOYER_POLICY" | python3 -m json.tool 2>/dev/null || echo "$DEPLOYER_POLICY"
  log ""
  log "To create manually:"
  log "  1. Create IAM role/user named '$NAME'"
  log "  2. Attach the above policy as an inline policy"
  log "  3. Use --profile $NAME with the deploy script"
  exit 0
fi

if [[ "$TYPE" == "role" ]]; then
  log ""
  log "Creating IAM role: $NAME"

  TRUST_POLICY=$(cat <<TRUST
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "${TRUST_PRINCIPAL}" },
      "Action": "sts:AssumeRole"
    }
  ]
}
TRUST
)

  aws $AWS_OPTS iam create-role \
    --role-name "$NAME" \
    --assume-role-policy-document "$TRUST_POLICY" \
    --description "OpenClaw AWS deployer — minimum permissions for deploy + teardown" \
    > /dev/null 2>&1 && log "  ✅ Role created" || log "  Role already exists"

  aws $AWS_OPTS iam put-role-policy \
    --role-name "$NAME" \
    --policy-name "OpenClawDeployerAccess" \
    --policy-document "$DEPLOYER_POLICY" \
    > /dev/null && log "  ✅ Policy attached"

  ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${NAME}"
  log ""
  log "=========================================="
  log "  ✅ Deployer role ready: $NAME"
  log "=========================================="
  log ""
  log "  To use with deploy script:"
  log "    # Add to ~/.aws/config:"
  log "    [profile openclaw-deployer]"
  log "    role_arn = $ROLE_ARN"
  log "    source_profile = default"
  log ""
  log "    # Then deploy:"
  log "    ./scripts/deploy_minimal.sh --name starfish --profile openclaw-deployer"
  log ""

elif [[ "$TYPE" == "user" ]]; then
  log ""
  log "Creating IAM user: $NAME"

  aws $AWS_OPTS iam create-user --user-name "$NAME" \
    > /dev/null 2>&1 && log "  ✅ User created" || log "  User already exists"

  aws $AWS_OPTS iam put-user-policy \
    --user-name "$NAME" \
    --policy-name "OpenClawDeployerAccess" \
    --policy-document "$DEPLOYER_POLICY" \
    > /dev/null && log "  ✅ Policy attached"

  log ""
  log "Creating access keys..."
  KEYS=$(aws $AWS_OPTS iam create-access-key --user-name "$NAME" 2>/dev/null) || {
    log "  ⚠️  Could not create access keys (may already have 2). Delete old keys first."
    log ""
    log "  Role is ready. Create keys manually:"
    log "    aws iam create-access-key --user-name $NAME"
    exit 0
  }

  ACCESS_KEY=$(echo "$KEYS" | python3 -c "import sys,json; print(json.load(sys.stdin)['AccessKey']['AccessKeyId'])")
  SECRET_KEY=$(echo "$KEYS" | python3 -c "import sys,json; print(json.load(sys.stdin)['AccessKey']['SecretAccessKey'])")

  log ""
  log "=========================================="
  log "  ✅ Deployer user ready: $NAME"
  log "=========================================="
  log ""
  log "  Access Key ID:     $ACCESS_KEY"
  log "  Secret Access Key: $SECRET_KEY"
  log ""
  log "  ⚠️  Save these now — the secret key won't be shown again!"
  log ""
  log "  Option 1: Add to .env.aws:"
  log "    AWS_ACCESS_KEY_ID=$ACCESS_KEY"
  log "    AWS_SECRET_ACCESS_KEY=$SECRET_KEY"
  log "    AWS_DEFAULT_REGION=$REGION"
  log ""
  log "  Option 2: Add to ~/.aws/credentials:"
  log "    [openclaw-deployer]"
  log "    aws_access_key_id = $ACCESS_KEY"
  log "    aws_secret_access_key = $SECRET_KEY"
  log ""
  log "  Then deploy:"
  log "    ./scripts/deploy_minimal.sh --name starfish --profile openclaw-deployer"
  log ""
fi

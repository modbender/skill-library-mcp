#!/bin/bash
# Safe configuration change workflow with automatic baseline capture and rollback
# Usage: ./scripts/safe-apply.sh <cluster-name> <vc-ip> <changes.json> [password] [dry-run]

set -e

CLUSTER_NAME=${1:-"office-iap"}
VC_IP=${2:-"192.168.20.56"}
CHANGES_FILE=${3:-"./changes.json"}
SSH_PASSWORD=${4:-""}
DRY_RUN=${5:-""}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BASE_DIR="./changes/${TIMESTAMP}"

echo "🔧 Safe Configuration Change Workflow"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Cluster: ${CLUSTER_NAME}"
echo "VC: ${VC_IP}"
echo "Changes: ${CHANGES_FILE}"
echo "Dry Run: ${DRY_RUN:-no}"
echo "Base Dir: ${BASE_DIR}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify changes file exists
if [ ! -f "${CHANGES_FILE}" ]; then
    echo "❌ Error: Changes file not found: ${CHANGES_FILE}"
    echo "💡 Example: ./safe-apply.sh office-iap 192.168.20.56 ./changes.json"
    exit 1
fi

# Create output directories
mkdir -p "${BASE_DIR}/diff" "${BASE_DIR}/apply" "${BASE_DIR}/verify"

# Step 1: Generate diff and risk assessment
echo "📋 Step 1: Generating diff and risk assessment..."

# Build diff command
DIFF_CMD="iapctl diff-cmd --cluster ${CLUSTER_NAME} --vc ${VC_IP} --in ${CHANGES_FILE} --out ${BASE_DIR}/diff --change-id chg_${TIMESTAMP}"

# Add password if provided
if [ -n "${SSH_PASSWORD}" ]; then
    DIFF_CMD="${DIFF_CMD} --ssh-password ${SSH_PASSWORD}"
fi

${DIFF_CMD}

if [ ! -f "${BASE_DIR}/diff/result.json" ]; then
    echo "❌ Diff generation failed!"
    exit 1
fi

# Display risk assessment
echo ""
echo "📊 Risk Assessment:"
cat "${BASE_DIR}/diff/risk.json" | python3 -m json.tool

RISK_LEVEL=$(cat "${BASE_DIR}/diff/risk.json" | python3 -c "import json, sys; print(json.load(sys.stdin)['level'])")
echo ""
echo "⚠️  Risk Level: ${RISK_LEVEL}"

# Ask for confirmation if risk level is medium or high
if [ "${RISK_LEVEL}" != "low" ] && [ -z "${DRY_RUN}" ]; then
    echo ""
    read -p "❓ Do you want to proceed? (yes/no): " CONFIRM
    if [ "${CONFIRM}" != "yes" ]; then
        echo "❌ Cancelled by user."
        exit 0
    fi
fi

# Display commands to be applied
echo ""
echo "📝 Commands to be applied:"
cat "${BASE_DIR}/diff/commands.txt"

# Ask for final confirmation if not dry run
if [ -z "${DRY_RUN}" ]; then
    echo ""
    read -p "❓ Confirm apply these changes? (yes/no): " FINAL_CONFIRM
    if [ "${FINAL_CONFIRM}" != "yes" ]; then
        echo "❌ Cancelled by user."
        exit 0
    fi
fi

# Step 2: Apply changes (with dry run if specified)
echo ""
echo "⚙️  Step 2: Applying changes..."

# Build apply command
APPLY_CMD="iapctl apply-cmd --cluster ${CLUSTER_NAME} --vc ${VC_IP} --change-id chg_${TIMESTAMP} --in ${BASE_DIR}/diff/commands.json --out ${BASE_DIR}/apply"

# Add password if provided
if [ -n "${SSH_PASSWORD}" ]; then
    APPLY_CMD="${APPLY_CMD} --ssh-password ${SSH_PASSWORD}"
fi

# Add dry run flag if specified
if [ -n "${DRY_RUN}" ]; then
    APPLY_CMD="${APPLY_CMD} --dry-run"
fi

if [ -n "${DRY_RUN}" ]; then
    echo "🧪 DRY RUN MODE - No changes will be applied"
    ${APPLY_CMD}
else
    ${APPLY_CMD}
fi

if [ ! -f "${BASE_DIR}/apply/result.json" ]; then
    echo "❌ Apply failed!"
    echo ""
    echo "💡 Rollback command:"
    echo "   iapctl rollback-cmd --cluster ${CLUSTER_NAME} --vc ${VC_IP} --from-change-id chg_${TIMESTAMP} --out ${BASE_DIR}/rollback"
    exit 1
fi

# Check if apply was successful
APPLY_OK=$(cat "${BASE_DIR}/apply/result.json" | python3 -c "import json, sys; print(json.load(sys.stdin)['ok'])")
if [ "${APPLY_OK}" != "True" ]; then
    echo "❌ Apply failed with errors!"
    echo ""
    echo "💡 Rollback command:"
    echo "   iapctl rollback-cmd --cluster ${CLUSTER_NAME} --vc ${VC_IP} --from-change-id chg_${TIMESTAMP} --out ${BASE_DIR}/rollback"
    exit 1
fi

# Step 3: Verify changes
echo ""
echo "✓ Step 3: Verifying changes..."

# Build verify command
VERIFY_CMD="iapctl verify-cmd --cluster ${CLUSTER_NAME} --vc ${VC_IP} --level full --out ${BASE_DIR}/verify"

# Add password if provided
if [ -n "${SSH_PASSWORD}" ]; then
    VERIFY_CMD="${VERIFY_CMD} --ssh-password ${SSH_PASSWORD}"
fi

${VERIFY_CMD}

if [ ! -f "${BASE_DIR}/verify/result.json" ]; then
    echo "⚠️  Verification failed, but changes were applied"
    echo ""
    echo "💡 Rollback command:"
    echo "   iapctl rollback-cmd --cluster ${CLUSTER_NAME} --vc ${VC_IP} --from-change-id chg_${TIMESTAMP} --out ${BASE_DIR}/rollback"
else
    echo "✅ Verification completed"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Configuration change completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Change artifacts: ${BASE_DIR}"
echo "  - diff/      : Change analysis and risk assessment"
echo "  - apply/     : Baseline snapshots and apply output"
echo "  - verify/    : Post-change verification"
echo ""
echo "💡 Baseline snapshot: ${BASE_DIR}/apply/pre_running-config.txt"
echo "💡 Post-config snapshot: ${BASE_DIR}/apply/post_running-config.txt"
echo ""
echo "🔄 Rollback command (if needed):"
echo "   iapctl rollback-cmd --cluster ${CLUSTER_NAME} --vc ${VC_IP} --from-change-id chg_${TIMESTAMP} --out ${BASE_DIR}/rollback"
echo ""

# Display comparison if both snapshots exist
if [ -f "${BASE_DIR}/apply/pre_running-config.txt" ] && [ -f "${BASE_DIR}/apply/post_running-config.txt" ]; then
    echo "📊 Configuration diff:"
    echo ""
    diff -u "${BASE_DIR}/apply/pre_running-config.txt" "${BASE_DIR}/apply/post_running-config.txt" | head -50 || true
fi

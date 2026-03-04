#!/bin/bash
#
# generate-report.sh - Generate deployment report for vLLM deployment
#
# This script is part of the rocm_vllm_deployment skill.
# It creates a human-readable deployment report in markdown format.
#
# Usage:
#   ./generate-report.sh <model-id> <container-name> <port> <status> [model-load-time] [memory-used]
#
# Example:
#   ./generate-report.sh "Qwen-Qwen3-0.6B" "vllm-qwen3-0-6b" "8001" "✅ Success" "3.6" "1.2"
#
# Exit Codes:
#   0 - Report generated successfully
#   1 - Missing required parameters
#   2 - Output directory not found
#

set -e

# Parameters
MODEL_ID="$1"
CONTAINER_NAME="$2"
PORT="$3"
STATUS="$4"
MODEL_LOAD_TIME="${5:-N/A}"
MEMORY_USED="${6:-N/A}"

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$HOME/vllm-compose/$MODEL_ID"
REPORT_FILE="$OUTPUT_DIR/DEPLOYMENT_REPORT.md"

#------------------------------------------------------------------------------
# Validate parameters
#------------------------------------------------------------------------------
if [ -z "$MODEL_ID" ] || [ -z "$CONTAINER_NAME" ] || [ -z "$PORT" ] || [ -z "$STATUS" ]; then
    echo "ERROR: Missing required parameters"
    echo ""
    echo "Usage: $0 <model-id> <container-name> <port> <status> [model-load-time] [memory-used]"
    echo ""
    echo "Example:"
    echo "  $0 \"Qwen-Qwen3-0.6B\" \"vllm-qwen3-0-6b\" \"8001\" \"✅ Success\" \"3.6\" \"1.2\""
    exit 1
fi

# Check if output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "ERROR: Output directory not found: $OUTPUT_DIR"
    exit 2
fi

#------------------------------------------------------------------------------
# Helper functions
#------------------------------------------------------------------------------
check_file() {
    if [ -f "$1" ]; then
        echo "✅"
    else
        echo "❌"
    fi
}

get_compose_value() {
    local key="$1"
    local file="$OUTPUT_DIR/docker-compose.yml"
    if [ -f "$file" ]; then
        # Try JSON array format first: "--key", "value"
        local val=$(grep -o "\"--$key\", \"[^\"]*\"" "$file" 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/' | head -1)
        if [ -n "$val" ]; then
            echo "$val"
            return
        fi
        # Try YAML format: key: value
        val=$(grep -o "$key: [^ ]*" "$file" 2>/dev/null | cut -d' ' -f2 | head -1)
        if [ -n "$val" ]; then
            echo "$val"
            return
        fi
        echo "N/A"
    else
        echo "N/A"
    fi
}

#------------------------------------------------------------------------------
# Read test results if available
#------------------------------------------------------------------------------
TEST_RESULTS_FILE="$OUTPUT_DIR/test-results.json"
if [ -f "$TEST_RESULTS_FILE" ]; then
    TEST_RESPONSE=$(cat "$TEST_RESULTS_FILE" | head -c 2000)
    PROMPT_TOKENS=$(cat "$TEST_RESULTS_FILE" | grep -o '"prompt_tokens":[0-9]*' | grep -o '[0-9]*' || echo "N/A")
    COMPLETION_TOKENS=$(cat "$TEST_RESULTS_FILE" | grep -o '"completion_tokens":[0-9]*' | grep -o '[0-9]*' || echo "N/A")
    TOTAL_TOKENS=$(cat "$TEST_RESULTS_FILE" | grep -o '"total_tokens":[0-9]*' | grep -o '[0-9]*' || echo "N/A")
    TEST_STATUS="✅ PASSED"
else
    TEST_RESPONSE="Test results not available"
    PROMPT_TOKENS="N/A"
    COMPLETION_TOKENS="N/A"
    TOTAL_TOKENS="N/A"
    TEST_STATUS="❌ FAILED"
fi

#------------------------------------------------------------------------------
# Get deployment info
#------------------------------------------------------------------------------
# Check health status from deployment.log
HEALTH_STATUS="⚠️ Not recorded"
if [ -f "$OUTPUT_DIR/deployment.log" ]; then
    if grep -q "Health OK" "$OUTPUT_DIR/deployment.log" 2>/dev/null; then
        HEALTH_STATUS="✅ PASSED"
    elif grep -q "health" "$OUTPUT_DIR/deployment.log" 2>/dev/null; then
        HEALTH_STATUS="⚠️ In progress"
    fi
fi

# Get max model len
MAX_MODEL_LEN=$(get_compose_value "max-model-len")

# Get tensor parallel size
TP_SIZE=$(get_compose_value "tensor-parallel-size")

# Get GPU memory utilization
GPU_MEM_UTIL=$(get_compose_value "gpu-memory-utilization")

# Get Docker image
DOCKER_IMAGE="N/A"
if [ -f "$OUTPUT_DIR/docker-compose.yml" ]; then
    DOCKER_IMAGE=$(grep -o 'image: [^ ]*' "$OUTPUT_DIR/docker-compose.yml" 2>/dev/null | cut -d' ' -f2 || echo "N/A")
fi

# Get environment info
HF_TOKEN_STATUS="Not set"
if [ -n "$HF_TOKEN" ]; then
    HF_TOKEN_STATUS="Set (${HF_TOKEN:0:10}...)"
fi

HF_HOME_STATUS="${HF_HOME:-default: ~/.cache/huggingface/hub}"

#------------------------------------------------------------------------------
# Generate report
#------------------------------------------------------------------------------
cat > "$REPORT_FILE" << EOF
# Deployment Report

| | |
|---|---|
| **Model** | $MODEL_ID |
| **Status** | $STATUS |
| **Timestamp** | $(date '+%Y-%m-%d %H:%M:%S %Z') |
| **Container** | $CONTAINER_NAME |

---

## 📁 Output Structure

\`\`\`
$OUTPUT_DIR/
├── deployment.log       $(check_file "$OUTPUT_DIR/deployment.log")
├── test-results.json    $(check_file "$OUTPUT_DIR/test-results.json")
├── docker-compose.yml   $(check_file "$OUTPUT_DIR/docker-compose.yml")
└── DEPLOYMENT_REPORT.md ✅
\`\`\`

---

## 📊 Deployment Summary

| Metric | Value |
|--------|-------|
| **Health Check** | $HEALTH_STATUS |
| **Functional Test** | $TEST_STATUS |
| **Model Load Time** | $MODEL_LOAD_TIME seconds |
| **Memory Used** | $MEMORY_USED GiB |
| **Max Context Length** | $MAX_MODEL_LEN tokens |
| **Tensor Parallel Size** | $TP_SIZE |
| **GPU Memory Utilization** | ${GPU_MEM_UTIL}% |

---

## 🧪 Test Results

**Endpoint:** \`http://localhost:$PORT/v1/chat/completions\`

**Request:**
\`\`\`json
{
  "model": "$MODEL_ID",
  "messages": [{"role": "user", "content": "<test_prompt>"}],
  "max_tokens": <X>
}
\`\`\`

**Response:**
\`\`\`json
$TEST_RESPONSE
\`\`\`

**Token Usage:**
- Prompt Tokens: $PROMPT_TOKENS
- Completion Tokens: $COMPLETION_TOKENS
- Total Tokens: $TOTAL_TOKENS

---

## 🔧 Environment

| Variable | Value |
|----------|-------|
| **HF_TOKEN** | $HF_TOKEN_STATUS |
| **HF_HOME** | $HF_HOME_STATUS |
| **Docker Image** | $DOCKER_IMAGE |
| **Port Mapping** | $PORT:8000 |

---

## 🚀 Quick Commands

\`\`\`bash
# View live logs
tail -f $OUTPUT_DIR/deployment.log

# Test endpoint
curl http://localhost:$PORT/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{"model":"$MODEL_ID","messages":[{"role":"user","content":"Hello"}],"max_tokens":50}'

# Check container status
docker ps | grep $CONTAINER_NAME

# Stop container
cd $OUTPUT_DIR && docker compose down
\`\`\`

---

## 📝 Notes

- Report generated by: generate-report.sh
- Skill: rocm_vllm_deployment
- Skill directory: $SKILL_DIR
- Generated at: $(date '+%Y-%m-%d %H:%M:%S %Z')
EOF

echo "✅ Report generated: $REPORT_FILE"
exit 0

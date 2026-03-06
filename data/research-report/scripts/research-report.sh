#!/usr/bin/env bash
# research-report.sh — Research project/paper and generate technical report with PDF
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Defaults
MODE="lite"
ITERATIONS=3
OUTPUT="both"
TOPIC=""
PROJECT_PATH=""
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace-research}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*"; }

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --topic) TOPIC="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --iterations) ITERATIONS="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --project-path) PROJECT_PATH="$2"; shift 2 ;;
    --workspace) WORKSPACE="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 --topic <name> [options]"
      echo "Options:"
      echo "  --topic          Required. Paper/project name or arXiv ID"
      echo "  --mode           lite (default) or full"
      echo "  --iterations     Report revision count (default: 3)"
      echo "  --output         md, pdf, or both (default: both)"
      echo "  --project-path   Local code directory (optional)"
      echo "  --workspace      Workspace directory (default: ~/.openclaw/workspace-research)"
      exit 0 ;;
    *) log_error "Unknown option: $1"; exit 1 ;;
  esac
done

# Validate
if [ -z "$TOPIC" ]; then
  log_error "--topic is required"
  exit 1
fi

if [[ "$MODE" != "lite" && "$MODE" != "full" ]]; then
  log_error "--mode must be 'lite' or 'full'"
  exit 1
fi

if [[ "$OUTPUT" != "md" && "$OUTPUT" != "pdf" && "$OUTPUT" != "both" ]]; then
  log_error "--output must be 'md', 'pdf', or 'both'"
  exit 1
fi

if ! command -v pandoc &>/dev/null && [[ "$OUTPUT" == *"pdf"* ]]; then
  log_error "pandoc not found. Install: sudo apt install pandoc texlive-xetex"
  exit 1
fi

# Setup directories
REPORTS_DIR="$WORKSPACE/reports"
LOGS_DIR="$WORKSPACE/logs"
MEMORY_DIR="$WORKSPACE/memory"
mkdir -p "$REPORTS_DIR" "$LOGS_DIR" "$MEMORY_DIR"

TOPIC_SAFE=$(echo "$TOPIC" | tr ' ' '-' | tr -cd '[:alnum:]-')
REPORT_BASE="$REPORTS_DIR/${TOPIC_SAFE}_report"
LOG_FILE="$LOGS_DIR/${TOPIC_SAFE}_research_${TIMESTAMP}.log"

log_info "Topic: $TOPIC"
log_info "Mode: $MODE"
log_info "Iterations: $ITERATIONS"
log_info "Output: $OUTPUT"
log_info "Workspace: $WORKSPACE"
log_info "Log file: $LOG_FILE"

# Start logging
exec > >(tee -a "$LOG_FILE") 2>&1

log_info "=== Research Report Generation Started ==="
log_info "Timestamp: $(date)"

# Phase 1: Discovery
log_info ""
log_info "=== Phase 1: Discovery ==="

# Create initial research notes
NOTES_FILE="$REPORTS_DIR/${TOPIC_SAFE}_research_notes.md"
cat > "$NOTES_FILE" << EOF
# Research Notes: $TOPIC

## Search Queries
- arXiv: "$TOPIC"
- GitHub: "$TOPIC"
- Project page: "$TOPIC"

## Related Papers
(TBD)

## Key Technologies
(TBD)

## Code Repositories
(TBD)

---
Generated: $(date)
Mode: $MODE | Iterations: $ITERATIONS
EOF

log_success "Created research notes: $NOTES_FILE"

# Phase 2: Analysis
log_info ""
log_info "=== Phase 2: Analysis ==="

if [ -n "$PROJECT_PATH" ] && [ -d "$PROJECT_PATH" ]; then
  log_info "Analyzing local code: $PROJECT_PATH"
  CODE_FILES=$(find "$PROJECT_PATH" -type f \( -name "*.py" -o -name "*.md" -o -name "*.yaml" \) | head -20)
  log_info "Found files:"
  echo "$CODE_FILES" | while read -r f; do log_info "  - $f"; done
else
  log_info "No local code provided. Will analyze from remote sources."
fi

# Phase 3: Report Writing (iterations)
log_info ""
log_info "=== Phase 3: Report Writing (${ITERATIONS} iterations) ==="

PREV_VERSION=""
for i in $(seq 1 $ITERATIONS); do
  log_info ""
  log_info "--- Iteration $i/$ITERATIONS ---"
  
  if [ $i -eq 1 ]; then
    CURRENT_VERSION="${REPORT_BASE}_v${i}.md"
    # Draft initial outline
    cat > "$CURRENT_VERSION" << EOF
# ${TOPIC} Technical Report

## Executive Summary
(TBD - will be filled in final iteration)

## 1. Motivation
### 1.1 Problem Statement
(TBD)

### 1.2 Why This Matters
(TBD)

## 2. Background
### 2.1 Prerequisites
(TBD)

### 2.2 Related Work
(TBD)

## 3. Core Method
### 3.1 Architecture Overview
(TBD)

### 3.2 Key Innovations
(TBD)

## 4. Code Analysis
### 4.1 Project Structure
(TBD)

### 4.2 Key Components
(TBD)

## 5. Experiments
### 5.1 Setup
(TBD)

### 5.2 Results
(TBD)

## 6. Troubleshooting
(TBD)

## 7. References
(TBD)

---
Version: v$i | Generated: $(date)
EOF
    log_success "Created draft v$i"
  else
    CURRENT_VERSION="${REPORT_BASE}_v${i}.md"
    PREV_VERSION="${REPORT_BASE}_v$((i-1)).md"
    # Copy previous and mark for revision
    cp "$PREV_VERSION" "$CURRENT_VERSION"
    log_success "Copied v$((i-1)) → v$i (ready for revision)"
  fi
  
  PREV_VERSION="$CURRENT_VERSION"
done

FINAL_MD="${REPORT_BASE}_final.md"
cp "$PREV_VERSION" "$FINAL_MD"
log_success "Final report: $FINAL_MD"

# Phase 4: Full mode - Environment + Experiments
if [ "$MODE" == "full" ]; then
  log_info ""
  log_info "=== Phase 4: Environment Setup + Experiments ==="
  log_warn "Full mode requires manual intervention for conda setup and experiment runs"
  log_info "Append experiment results to: $FINAL_MD"
fi

# Phase 5: PDF Generation
if [[ "$OUTPUT" == *"pdf"* ]]; then
  log_info ""
  log_info "=== Phase 5: PDF Generation ==="
  
  # Check if md2pdf skill exists
  MD2PDF_SCRIPT="$HOME/.openclaw/skills/md2pdf/scripts/md2pdf.sh"
  if [ -f "$MD2PDF_SCRIPT" ]; then
    log_info "Using md2pdf skill for conversion"
    bash "$MD2PDF_SCRIPT" "$FINAL_MD" "${FINAL_MD%.md}.pdf" 2>&1 | while read -r line; do
      log_info "  $line"
    done
    if [ -f "${FINAL_MD%.md}.pdf" ]; then
      log_success "PDF generated: ${FINAL_MD%.md}.pdf"
    else
      log_warn "PDF generation may have failed"
    fi
  else
    log_warn "md2pdf skill not found. Using direct pandoc:"
    pandoc "$FINAL_MD" -o "${FINAL_MD%.md}.pdf" \
      --pdf-engine=xelatex \
      -V geometry:margin=20mm \
      -V fontsize=10pt \
      --toc 2>&1 | while read -r line; do
      log_info "  $line"
    done
  fi
fi

# Append to memory
TODAY=$(date +%Y-%m-%d)
MEMORY_FILE="$MEMORY_DIR/${TODAY}.md"
cat >> "$MEMORY_FILE" << EOF

## ${TOPIC} Research Report

- **Mode:** $MODE
- **Iterations:** $ITERATIONS
- **Output:** $OUTPUT
- **Report:** $FINAL_MD
- **PDF:** ${FINAL_MD%.md}.pdf
- **Log:** $LOG_FILE

EOF
log_success "Appended to memory: $MEMORY_FILE"

log_info ""
log_info "=== Research Report Generation Complete ==="
log_success "Final report: $FINAL_MD"
if [[ "$OUTPUT" == *"pdf"* ]]; then
  log_success "PDF: ${FINAL_MD%.md}.pdf"
fi
log_info "Log file: $LOG_FILE"

# Print summary
echo ""
echo "=========================================="
echo "           GENERATION COMPLETE          "
echo "=========================================="
echo "Report (Markdown): $FINAL_MD"
if [[ "$OUTPUT" == *"pdf"* ]]; then
  echo "Report (PDF):       ${FINAL_MD%.md}.pdf"
fi
echo "Log file:          $LOG_FILE"
echo "=========================================="

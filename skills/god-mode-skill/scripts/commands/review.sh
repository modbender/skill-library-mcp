#!/usr/bin/env bash
# god review - Monthly activity reviews
# Usage: god review --month 2026-01

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/../lib"

# Source libraries
source "$LIB_DIR/output.sh"
source "$LIB_DIR/config.sh"
source "$LIB_DIR/db.sh"
source "$LIB_DIR/logging.sh"
source "$LIB_DIR/llm.sh"

# Show help
show_help() {
    cat << 'EOF'
Usage: god review [options]

Generate monthly activity reviews across all projects.

Options:
  --month YYYY-MM     Review specific month (default: last month)
  --json              Output as JSON
  -h, --help          Show this help

Examples:
  god review                    # Last month's activity
  god review --month 2026-01    # January 2026
  god review --json             # JSON output for scripting
EOF
}

# Parse month argument (YYYY-MM format)
parse_month() {
    local month_arg="$1"
    
    # Validate format
    if [[ ! "$month_arg" =~ ^[0-9]{4}-[0-9]{2}$ ]]; then
        error "Invalid month format. Use YYYY-MM (e.g., 2026-01)"
        exit 1
    fi
    
    local year="${month_arg%-*}"
    local month="${month_arg#*-}"
    
    # Calculate timestamps
    local start_ts=$(date -d "${year}-${month}-01" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "${year}-${month}-01" +%s)
    
    # Calculate end of month (start of next month)
    local next_month=$((10#$month + 1))
    local next_year=$year
    if [[ $next_month -gt 12 ]]; then
        next_month=1
        next_year=$((year + 1))
    fi
    next_month=$(printf "%02d" $next_month)
    
    local end_ts=$(date -d "${next_year}-${next_month}-01" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "${next_year}-${next_month}-01" +%s)
    
    echo "$start_ts|$end_ts|$month_arg"
}

# Get default month (last complete month)
get_last_month() {
    local last_month_date=$(date -d "$(date +%Y-%m-01) -1 month" +%Y-%m 2>/dev/null || date -v-1m +%Y-%m)
    echo "$last_month_date"
}

# Query monthly commit activity
get_monthly_commits() {
    local start_ts="$1"
    local end_ts="$2"
    
    db_query "SELECT 
                project_id,
                COUNT(*) as commits,
                COUNT(DISTINCT author) as authors,
                datetime(MIN(timestamp), 'unixepoch') as first_commit,
                datetime(MAX(timestamp), 'unixepoch') as last_commit,
                GROUP_CONCAT(DISTINCT author) as author_list
              FROM commits
              WHERE timestamp >= $start_ts AND timestamp < $end_ts
              GROUP BY project_id
              ORDER BY commits DESC"
}

# Query monthly PR activity
# Note: PR timestamps often NULL in database, so showing current state for context
get_monthly_prs() {
    # Show all current PRs (timestamps not reliable for filtering)
    db_query "SELECT 
                project_id,
                state,
                COUNT(*) as count
              FROM pull_requests
              GROUP BY project_id, state"
}

# Get commit type breakdown for a project in the time range
get_commit_types() {
    local project_id="$1"
    local start_ts="$2"
    local end_ts="$3"
    
    local messages=$(db_query "SELECT message FROM commits 
                               WHERE project_id = '$project_id' 
                               AND timestamp >= $start_ts 
                               AND timestamp < $end_ts")
    
    local feat=$(echo "$messages" | jq -r '.[].message' | grep -c "^feat" || echo 0)
    local fix=$(echo "$messages" | jq -r '.[].message' | grep -c "^fix" || echo 0)
    local docs=$(echo "$messages" | jq -r '.[].message' | grep -c "^docs" || echo 0)
    local test=$(echo "$messages" | jq -r '.[].message' | grep -c "^test" || echo 0)
    local other=$(echo "$messages" | jq length)
    other=$((other - feat - fix - docs - test))
    
    jq -n \
        --argjson feat "$feat" \
        --argjson fix "$fix" \
        --argjson docs "$docs" \
        --argjson test "$test" \
        --argjson other "$other" \
        '{feat: $feat, fix: $fix, docs: $docs, test: $test, other: $other}'
}

# Display monthly review
display_review() {
    local month_name="$1"
    local commits_data="$2"
    local prs_data="$3"
    local json_output="${4:-false}"
    
    if [[ "$json_output" == "true" ]]; then
        # Build JSON output
        local total_commits=$(echo "$commits_data" | jq '[.[] | .commits] | add // 0')
        local active_projects=$(echo "$commits_data" | jq 'length')
        
        jq -n \
            --arg month "$month_name" \
            --argjson commits "$commits_data" \
            --argjson prs "$prs_data" \
            --argjson total_commits "$total_commits" \
            --argjson active_projects "$active_projects" \
            '{
                month: $month,
                summary: {
                    total_commits: $total_commits,
                    active_projects: $active_projects
                },
                commits: $commits,
                prs: $prs
            }'
        return
    fi
    
    # Text display
    header "Monthly Review: $month_name"
    
    local total_commits=$(echo "$commits_data" | jq '[.[] | .commits] | add // 0')
    local active_projects=$(echo "$commits_data" | jq 'length')
    local total_authors=$(echo "$commits_data" | jq '[.[] | .authors] | add // 0')
    
    echo ""
    info "Total Activity"
    echo "  📊 $total_commits commits across $active_projects projects"
    echo "  👥 $total_authors unique contributors"
    echo ""
    
    # Top projects
    echo -e "${BOLD}Most Active Projects${RESET}"
    echo ""
    
    local top_projects=$(echo "$commits_data" | jq -r '.[0:5] | .[] | "\(.project_id)|\(.commits)|\(.authors)"')
    
    while IFS='|' read -r project_id commits authors; do
        local project_name=$(config_get_project "$project_id" | jq -r '.name // .id')
        echo -e "  ${BOLD}${project_name}${RESET}"
        echo -e "    ${GREEN}${commits}${RESET} commits • ${authors} author(s)"
    done <<< "$top_projects"
    
    echo ""
    
    # PR summary (if any)
    local total_prs=$(echo "$prs_data" | jq '[.[] | .count] | add // 0')
    if [[ "$total_prs" -gt 0 ]]; then
        echo -e "${BOLD}Pull Requests${RESET}"
        echo ""
        
        # Group by project
        local pr_projects=$(echo "$prs_data" | jq -r '[.[] | .project_id] | unique | .[]')
        
        while read -r project_id; do
            local project_name=$(config_get_project "$project_id" | jq -r '.name // .id')
            local project_prs=$(echo "$prs_data" | jq --arg pid "$project_id" '[.[] | select(.project_id == $pid)]')
            
            local merged=$(echo "$project_prs" | jq '[.[] | select(.state == "merged" or .state == "completed") | .count] | add // 0')
            local active=$(echo "$project_prs" | jq '[.[] | select(.state == "open" or .state == "active") | .count] | add // 0')
            local closed=$(echo "$project_prs" | jq '[.[] | select(.state == "closed" or .state == "abandoned") | .count] | add // 0')
            
            echo -e "  ${BOLD}${project_name}${RESET}"
            [[ $merged -gt 0 ]] && echo -e "    ${GREEN}✓${RESET} ${merged} merged"
            [[ $active -gt 0 ]] && echo -e "    ${YELLOW}◐${RESET} ${active} active"
            [[ $closed -gt 0 ]] && echo -e "    ${DIM}✗${RESET} ${closed} closed"
        done <<< "$pr_projects"
        
        echo ""
    fi
    
    # Detailed project breakdown
    echo -e "${BOLD}Project Details${RESET}"
    echo ""
    
    echo "$commits_data" | jq -c '.[]' | while read -r project; do
        local project_id=$(echo "$project" | jq -r '.project_id')
        local project_name=$(config_get_project "$project_id" | jq -r '.name // .id')
        local commits=$(echo "$project" | jq -r '.commits')
        local first=$(echo "$project" | jq -r '.first_commit')
        local last=$(echo "$project" | jq -r '.last_commit')
        
        echo -e "${BOLD}${project_name}${RESET} (${commits} commits)"
        echo -e "  Period: ${DIM}${first}${RESET} → ${DIM}${last}${RESET}"
        echo ""
    done
    
    divider
    echo ""
    info "Run 'god review --month $month_name --json' for structured data"
    echo ""
}

# Main review function
run_review() {
    local month_arg="$1"
    local json_output="$2"
    
    # Parse month
    local month_data
    if [[ -z "$month_arg" ]]; then
        month_arg=$(get_last_month)
    fi
    
    month_data=$(parse_month "$month_arg")
    IFS='|' read -r start_ts end_ts month_name <<< "$month_data"
    
    # Log review start
    log_command "god review --month $month_name"
    
    # Query data
    local commits_data=$(get_monthly_commits "$start_ts" "$end_ts")
    local prs_data=$(get_monthly_prs "$start_ts" "$end_ts")
    
    # Check if any data
    local commit_count=$(echo "$commits_data" | jq 'length')
    if [[ "$commit_count" -eq 0 ]]; then
        if [[ "$json_output" == "true" ]]; then
            jq -n --arg month "$month_name" \
                '{month: $month, summary: {total_commits: 0, active_projects: 0}, commits: [], prs: []}'
        else
            warn "No activity found for $month_name"
            info "Run 'god sync' to fetch repository data"
        fi
        return
    fi
    
    # Display review
    display_review "$month_name" "$commits_data" "$prs_data" "$json_output"
}

# Parse arguments
MONTH_ARG=""
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --month)
            MONTH_ARG="$2"
            shift 2
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            error "Unknown argument: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run review
run_review "$MONTH_ARG" "$JSON_OUTPUT"

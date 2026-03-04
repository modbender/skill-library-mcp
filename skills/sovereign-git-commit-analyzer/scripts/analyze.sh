#!/usr/bin/env bash
#
# Git Commit Analyzer - analyze.sh
# Analyzes git commit history and generates comprehensive reports.
#
# Usage: ./analyze.sh [OPTIONS]
#
# Options:
#   --days <number>         Number of days to analyze (default: 30)
#   --branch <name>         Branch to analyze (default: current branch)
#   --author <email>        Filter commits by author
#   --output <format>       Output format: markdown, json, text (default: markdown)
#   --top <number>          Number of top contributors (default: 10)
#   --quality-threshold <n> Minimum quality score to pass (default: 60)
#   --since <date>          Start date (YYYY-MM-DD)
#   --until <date>          End date (YYYY-MM-DD)
#   --no-heatmap            Disable file change heatmap
#   --output-file <path>    Write report to a file
#   --help                  Show this help message
#
# Author: Sovereign AI (Taylor)
# License: MIT
# Version: 1.0.0

set -euo pipefail

# ─── Defaults ───────────────────────────────────────────────────────────────

DAYS="${GCA_DAYS:-30}"
BRANCH="${GCA_BRANCH:-}"
AUTHOR_FILTER=""
OUTPUT_FORMAT="${GCA_OUTPUT:-markdown}"
TOP_N=10
QUALITY_THRESHOLD="${GCA_THRESHOLD:-60}"
SINCE_DATE=""
UNTIL_DATE=""
SHOW_HEATMAP=true
OUTPUT_FILE=""

# ─── Argument Parsing ──────────────────────────────────────────────────────

show_help() {
    sed -n '3,/^$/s/^# \?//p' "$0"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --days)        DAYS="$2"; shift 2 ;;
        --branch)      BRANCH="$2"; shift 2 ;;
        --author)      AUTHOR_FILTER="$2"; shift 2 ;;
        --output)      OUTPUT_FORMAT="$2"; shift 2 ;;
        --top)         TOP_N="$2"; shift 2 ;;
        --quality-threshold) QUALITY_THRESHOLD="$2"; shift 2 ;;
        --since)       SINCE_DATE="$2"; shift 2 ;;
        --until)       UNTIL_DATE="$2"; shift 2 ;;
        --no-heatmap)  SHOW_HEATMAP=false; shift ;;
        --heatmap)     SHOW_HEATMAP=true; shift ;;
        --output-file) OUTPUT_FILE="$2"; shift 2 ;;
        --help|-h)     show_help ;;
        *)             echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ─── Validation ─────────────────────────────────────────────────────────────

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
    echo "Error: Not inside a git repository." >&2
    exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"

if [[ -z "$BRANCH" ]]; then
    BRANCH="$(git rev-parse --abbrev-ref HEAD)"
fi

# Build date range arguments for git log
DATE_ARGS=()
if [[ -n "$SINCE_DATE" ]]; then
    DATE_ARGS+=(--since="$SINCE_DATE")
elif [[ -n "$DAYS" ]]; then
    DATE_ARGS+=(--since="${DAYS} days ago")
fi

if [[ -n "$UNTIL_DATE" ]]; then
    DATE_ARGS+=(--until="$UNTIL_DATE")
fi

AUTHOR_ARGS=()
if [[ -n "$AUTHOR_FILTER" ]]; then
    AUTHOR_ARGS+=(--author="$AUTHOR_FILTER")
fi

# ─── Data Collection ────────────────────────────────────────────────────────

# Collect all commits in the date range
COMMITS_RAW=$(git log "$BRANCH" "${DATE_ARGS[@]}" "${AUTHOR_ARGS[@]}" \
    --pretty=format:"%H|%an|%ae|%aI|%s" 2>/dev/null || true)

if [[ -z "$COMMITS_RAW" ]]; then
    echo "No commits found for the specified parameters." >&2
    exit 0
fi

TOTAL_COMMITS=$(echo "$COMMITS_RAW" | wc -l | tr -d ' ')

# ─── Commit Frequency ──────────────────────────────────────────────────────

compute_frequency() {
    local freq
    freq=$(echo "$COMMITS_RAW" | awk -F'|' '{print substr($4,1,10)}' | sort | uniq -c | sort -rn)

    local most_active_day most_active_count least_active_day least_active_count
    most_active_day=$(echo "$freq" | head -1 | awk '{print $2}')
    most_active_count=$(echo "$freq" | head -1 | awk '{print $1}')
    least_active_day=$(echo "$freq" | tail -1 | awk '{print $2}')
    least_active_count=$(echo "$freq" | tail -1 | awk '{print $1}')

    local avg_per_day
    local num_days
    num_days=$(echo "$freq" | wc -l | tr -d ' ')
    if [[ "$num_days" -gt 0 ]]; then
        avg_per_day=$(echo "scale=1; $TOTAL_COMMITS / $num_days" | bc 2>/dev/null || echo "N/A")
    else
        avg_per_day="0"
    fi

    # Weekly aggregation
    local weekly
    weekly=$(echo "$COMMITS_RAW" | awk -F'|' '{print substr($4,1,10)}' | \
        while read -r date; do
            if command -v date &>/dev/null; then
                # Get ISO week number
                week_num=$(date -d "$date" +%V 2>/dev/null || date -j -f "%Y-%m-%d" "$date" +%V 2>/dev/null || echo "01")
                echo "$week_num"
            else
                echo "01"
            fi
        done | sort | uniq -c | sort -k2 -n)

    echo "TOTAL:$TOTAL_COMMITS"
    echo "AVG_PER_DAY:$avg_per_day"
    echo "MOST_ACTIVE:$most_active_day ($most_active_count commits)"
    echo "LEAST_ACTIVE:$least_active_day ($least_active_count commits)"
    echo "---WEEKLY---"
    echo "$weekly" | while read -r count week; do
        local bar=""
        for ((i=0; i<count; i++)); do bar+="#"; done
        echo "  Week $week | $bar ($count)"
    done
}

# ─── Top Contributors ──────────────────────────────────────────────────────

compute_contributors() {
    # Count commits per author
    echo "$COMMITS_RAW" | awk -F'|' '{print $3}' | sort | uniq -c | sort -rn | head -n "$TOP_N" | \
    while read -r count email; do
        # Get lines added/deleted for this author
        local stats
        stats=$(git log "$BRANCH" "${DATE_ARGS[@]}" --author="$email" \
            --pretty=tformat: --numstat 2>/dev/null | \
            awk '{ added += $1; deleted += $2; files++ } END { printf "%d|%d|%d", added, deleted, files }')

        local added deleted files
        added=$(echo "$stats" | cut -d'|' -f1)
        deleted=$(echo "$stats" | cut -d'|' -f2)
        files=$(echo "$stats" | cut -d'|' -f3)

        # Get author name
        local name
        name=$(echo "$COMMITS_RAW" | awk -F'|' -v e="$email" '$3==e {print $2; exit}')

        echo "$count|$name|$email|${added:-0}|${deleted:-0}|${files:-0}"
    done
}

# ─── File Change Heatmap ───────────────────────────────────────────────────

compute_heatmap() {
    git log "$BRANCH" "${DATE_ARGS[@]}" "${AUTHOR_ARGS[@]}" \
        --pretty=format: --name-only 2>/dev/null | \
        grep -v '^$' | sort | uniq -c | sort -rn | head -20 | \
    while read -r count filepath; do
        local last_modified
        last_modified=$(git log -1 --format="%aI" -- "$filepath" 2>/dev/null | cut -c1-10)
        echo "$count|$filepath|${last_modified:-unknown}"
    done
}

# ─── Commit Message Quality ────────────────────────────────────────────────

compute_quality() {
    local total=0
    local good_length=0
    local imperative=0
    local no_trailing_period=0
    local has_type_prefix=0
    local not_vague=0

    local imperative_verbs="Add|Fix|Update|Remove|Refactor|Implement|Create|Delete|Move|Rename|Improve|Optimize|Handle|Support|Enable|Disable|Merge|Revert|Release|Bump|Change|Set|Use|Allow|Prevent|Ensure|Make|Convert|Extract|Introduce|Replace|Simplify|Clean|Reduce|Increase|Adjust|Configure|Deploy|Test|Document|Upgrade|Downgrade"
    local type_prefixes="feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert"
    local vague_patterns="^(fix|update|change|stuff|things|misc|wip|temp|tmp|test|asdf|xxx)$"

    while IFS='|' read -r _hash _name _email _date subject; do
        total=$((total + 1))

        # Length check (10-72 characters)
        local len=${#subject}
        if [[ $len -ge 10 && $len -le 72 ]]; then
            good_length=$((good_length + 1))
        fi

        # Imperative mood check
        local first_word
        first_word=$(echo "$subject" | awk '{print $1}' | sed 's/^[a-z]*://;s/([^)]*)//g' | tr -d '[:space:]')
        if echo "$first_word" | grep -qiE "^($imperative_verbs)" 2>/dev/null; then
            imperative=$((imperative + 1))
        fi

        # No trailing period
        if [[ "${subject: -1}" != "." ]]; then
            no_trailing_period=$((no_trailing_period + 1))
        fi

        # Conventional commit prefix
        if echo "$subject" | grep -qE "^($type_prefixes)(\(.+\))?:" 2>/dev/null; then
            has_type_prefix=$((has_type_prefix + 1))
        fi

        # Not vague
        local cleaned
        cleaned=$(echo "$subject" | sed 's/^[a-z]*://;s/([^)]*)//g' | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')
        if ! echo "$cleaned" | grep -qiE "$vague_patterns" 2>/dev/null; then
            not_vague=$((not_vague + 1))
        fi
    done <<< "$COMMITS_RAW"

    if [[ $total -eq 0 ]]; then
        echo "SCORE:0"
        return
    fi

    # Each criterion is worth 20 points
    local length_score=$((good_length * 20 / total))
    local imperative_score=$((imperative * 20 / total))
    local period_score=$((no_trailing_period * 20 / total))
    local prefix_score=$((has_type_prefix * 20 / total))
    local vague_score=$((not_vague * 20 / total))
    local total_score=$((length_score + imperative_score + period_score + prefix_score + vague_score))

    local length_pct=$((good_length * 100 / total))
    local imperative_pct=$((imperative * 100 / total))
    local period_pct=$((no_trailing_period * 100 / total))
    local prefix_pct=$((has_type_prefix * 100 / total))
    local vague_pct=$((not_vague * 100 / total))

    local grade="Poor"
    if [[ $total_score -ge 90 ]]; then grade="Excellent"
    elif [[ $total_score -ge 75 ]]; then grade="Good"
    elif [[ $total_score -ge 60 ]]; then grade="Acceptable"
    elif [[ $total_score -ge 40 ]]; then grade="Needs Improvement"
    fi

    echo "SCORE:$total_score"
    echo "GRADE:$grade"
    echo "LENGTH:$length_pct%|$length_score/20"
    echo "IMPERATIVE:$imperative_pct%|$imperative_score/20"
    echo "NO_PERIOD:$period_pct%|$period_score/20"
    echo "CONVENTIONAL:$prefix_pct%|$prefix_score/20"
    echo "NOT_VAGUE:$vague_pct%|$vague_score/20"

    # Find worst offenders (most common short/vague messages)
    echo "---OFFENDERS---"
    echo "$COMMITS_RAW" | awk -F'|' '{print $5}' | \
        awk '{print tolower($0)}' | sort | uniq -c | sort -rn | head -5 | \
        while read -r cnt msg; do
            if [[ ${#msg} -lt 15 ]]; then
                echo "  \"$msg\" (used $cnt times)"
            fi
        done
}

# ─── Report Generation ─────────────────────────────────────────────────────

generate_markdown_report() {
    echo "# Git Commit Analysis Report"
    echo ""
    echo "**Repository:** $REPO_NAME"
    echo "**Branch:** $BRANCH"
    echo "**Analysis Period:** ${SINCE_DATE:-last $DAYS days} to ${UNTIL_DATE:-now}"
    echo "**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%d)"
    echo ""

    # ── Frequency Section ──
    echo "## Commit Frequency"
    echo ""
    local freq_data
    freq_data=$(compute_frequency)

    echo "$freq_data" | while IFS=: read -r key value; do
        case "$key" in
            TOTAL)         echo "- **Total commits:** $value" ;;
            AVG_PER_DAY)   echo "- **Average per day:** $value" ;;
            MOST_ACTIVE)   echo "- **Most active day:** $value" ;;
            LEAST_ACTIVE)  echo "- **Least active day:** $value" ;;
            ---WEEKLY---)  echo ""; echo "### Weekly Breakdown"; echo '```' ;;
            *)             echo "$key:$value" ;;
        esac
    done
    echo '```'
    echo ""

    # ── Contributors Section ──
    echo "## Top Contributors"
    echo ""
    echo "| Rank | Author | Email | Commits | Lines Added | Lines Deleted | Files Changed |"
    echo "|------|--------|-------|---------|-------------|---------------|---------------|"

    local rank=1
    compute_contributors | while IFS='|' read -r commits name email added deleted files; do
        echo "| $rank | $name | $email | $commits | $added | $deleted | $files |"
        rank=$((rank + 1))
    done
    echo ""

    # ── Heatmap Section ──
    if [[ "$SHOW_HEATMAP" == "true" ]]; then
        echo "## File Change Heatmap"
        echo ""
        echo "| File | Changes | Last Modified |"
        echo "|------|---------|---------------|"

        compute_heatmap | while IFS='|' read -r count filepath last_mod; do
            echo "| $filepath | $count | $last_mod |"
        done
        echo ""
    fi

    # ── Quality Section ──
    echo "## Commit Message Quality"
    echo ""
    local quality_data
    quality_data=$(compute_quality)

    local score grade
    score=$(echo "$quality_data" | grep "^SCORE:" | cut -d: -f2)
    grade=$(echo "$quality_data" | grep "^GRADE:" | cut -d: -f2)

    echo "**Overall Score:** $score/100 ($grade)"
    echo ""
    echo "| Criterion | Pass Rate | Score |"
    echo "|-----------|-----------|-------|"

    echo "$quality_data" | while IFS=: read -r key value; do
        case "$key" in
            LENGTH)       echo "| Length (10-72 chars) | $(echo "$value" | cut -d'|' -f1) | $(echo "$value" | cut -d'|' -f2) |" ;;
            IMPERATIVE)   echo "| Imperative mood | $(echo "$value" | cut -d'|' -f1) | $(echo "$value" | cut -d'|' -f2) |" ;;
            NO_PERIOD)    echo "| No trailing period | $(echo "$value" | cut -d'|' -f1) | $(echo "$value" | cut -d'|' -f2) |" ;;
            CONVENTIONAL) echo "| Conventional prefix | $(echo "$value" | cut -d'|' -f1) | $(echo "$value" | cut -d'|' -f2) |" ;;
            NOT_VAGUE)    echo "| Not vague | $(echo "$value" | cut -d'|' -f1) | $(echo "$value" | cut -d'|' -f2) |" ;;
        esac
    done
    echo ""

    # Worst offenders
    local offenders
    offenders=$(echo "$quality_data" | sed -n '/---OFFENDERS---/,$ p' | tail -n +2)
    if [[ -n "$offenders" ]]; then
        echo "### Worst Offenders"
        echo ""
        echo "$offenders"
        echo ""
    fi

    # ── Summary ──
    echo "---"
    echo ""
    if [[ "$score" -ge "$QUALITY_THRESHOLD" ]]; then
        echo "Result: **PASS** (score $score >= threshold $QUALITY_THRESHOLD)"
    else
        echo "Result: **FAIL** (score $score < threshold $QUALITY_THRESHOLD)"
    fi
}

generate_json_report() {
    local freq_data quality_data
    freq_data=$(compute_frequency)
    quality_data=$(compute_quality)

    local score
    score=$(echo "$quality_data" | grep "^SCORE:" | cut -d: -f2)
    local grade
    grade=$(echo "$quality_data" | grep "^GRADE:" | cut -d: -f2)

    echo "{"
    echo "  \"repository\": \"$REPO_NAME\","
    echo "  \"branch\": \"$BRANCH\","
    echo "  \"total_commits\": $TOTAL_COMMITS,"
    echo "  \"analysis_days\": $DAYS,"
    echo "  \"quality_score\": $score,"
    echo "  \"quality_grade\": \"$grade\","
    echo "  \"threshold\": $QUALITY_THRESHOLD,"
    echo "  \"pass\": $([ "$score" -ge "$QUALITY_THRESHOLD" ] && echo "true" || echo "false"),"
    echo "  \"contributors\": ["

    local first=true
    compute_contributors | while IFS='|' read -r commits name email added deleted files; do
        if [[ "$first" == "true" ]]; then first=false; else echo ","; fi
        printf '    {"name": "%s", "email": "%s", "commits": %s, "lines_added": %s, "lines_deleted": %s, "files_changed": %s}' \
            "$name" "$email" "$commits" "$added" "$deleted" "$files"
    done

    echo ""
    echo "  ],"

    if [[ "$SHOW_HEATMAP" == "true" ]]; then
        echo "  \"heatmap\": ["
        local first=true
        compute_heatmap | while IFS='|' read -r count filepath last_mod; do
            if [[ "$first" == "true" ]]; then first=false; else echo ","; fi
            printf '    {"file": "%s", "changes": %s, "last_modified": "%s"}' \
                "$filepath" "$count" "$last_mod"
        done
        echo ""
        echo "  ],"
    fi

    echo "  \"generated\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%d)\""
    echo "}"
}

generate_text_report() {
    echo "============================================"
    echo "  GIT COMMIT ANALYSIS REPORT"
    echo "============================================"
    echo ""
    echo "Repository:  $REPO_NAME"
    echo "Branch:      $BRANCH"
    echo "Period:      ${SINCE_DATE:-last $DAYS days} to ${UNTIL_DATE:-now}"
    echo "Total:       $TOTAL_COMMITS commits"
    echo ""

    echo "── COMMIT FREQUENCY ──"
    echo ""
    compute_frequency
    echo ""

    echo "── TOP CONTRIBUTORS ──"
    echo ""
    printf "%-4s %-25s %-8s %-10s %-10s %-8s\n" "Rank" "Author" "Commits" "Added" "Deleted" "Files"
    printf "%-4s %-25s %-8s %-10s %-10s %-8s\n" "----" "-------------------------" "-------" "---------" "---------" "-------"

    local rank=1
    compute_contributors | while IFS='|' read -r commits name email added deleted files; do
        printf "%-4s %-25s %-8s %-10s %-10s %-8s\n" "$rank" "$name" "$commits" "$added" "$deleted" "$files"
        rank=$((rank + 1))
    done
    echo ""

    if [[ "$SHOW_HEATMAP" == "true" ]]; then
        echo "── FILE CHANGE HEATMAP ──"
        echo ""
        printf "%-50s %-8s %-12s\n" "File" "Changes" "Last Modified"
        printf "%-50s %-8s %-12s\n" "--------------------------------------------------" "-------" "------------"
        compute_heatmap | while IFS='|' read -r count filepath last_mod; do
            printf "%-50s %-8s %-12s\n" "$filepath" "$count" "$last_mod"
        done
        echo ""
    fi

    echo "── COMMIT MESSAGE QUALITY ──"
    echo ""
    compute_quality
    echo ""

    local score
    score=$(compute_quality | grep "^SCORE:" | cut -d: -f2)
    echo "============================================"
    if [[ "$score" -ge "$QUALITY_THRESHOLD" ]]; then
        echo "  RESULT: PASS (score $score >= $QUALITY_THRESHOLD)"
    else
        echo "  RESULT: FAIL (score $score < $QUALITY_THRESHOLD)"
    fi
    echo "============================================"
}

# ─── Main ───────────────────────────────────────────────────────────────────

main() {
    local output

    case "$OUTPUT_FORMAT" in
        markdown|md)  output=$(generate_markdown_report) ;;
        json)         output=$(generate_json_report) ;;
        text|txt)     output=$(generate_text_report) ;;
        *)
            echo "Error: Unknown output format '$OUTPUT_FORMAT'. Use: markdown, json, text" >&2
            exit 1
            ;;
    esac

    if [[ -n "$OUTPUT_FILE" ]]; then
        echo "$output" > "$OUTPUT_FILE"
        echo "Report written to $OUTPUT_FILE"
    else
        echo "$output"
    fi

    # Exit with failure if quality score is below threshold
    local score
    score=$(compute_quality | grep "^SCORE:" | cut -d: -f2)
    if [[ "$score" -lt "$QUALITY_THRESHOLD" ]]; then
        exit 1
    fi
}

main

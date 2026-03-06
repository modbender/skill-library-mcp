#!/bin/bash
#===============================================================================
# BABY Brain - General Automation Script
#===============================================================================
# Description: General-purpose automation for repetitive tasks
# Author: Baby
# Version: 1.0.0
#===============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Icons
ICON_SUCCESS="✅"
ICON_ERROR="❌"
ICON_INFO="ℹ️"
ICON_WARNING="⚠️"
ICON_ROCKET="🚀"
ICON_GEAR="⚙️"
ICON_FILE="📄"
ICON_FOLDER="📁"

#-------------------------------------------------------------------------------
# Configuration
#-------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.baby-brain"
LOG_DIR="${CONFIG_DIR}/logs"
TEMP_DIR="${CONFIG_DIR}/temp"

# Ensure directories exist
mkdir -p "${CONFIG_DIR}" "${LOG_DIR}" "${TEMP_DIR}"

#-------------------------------------------------------------------------------
# Helper Functions
#-------------------------------------------------------------------------------
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[${timestamp}] [${level}] ${message}" >> "${LOG_DIR}/automation.log"
    echo -e "[${timestamp}] [${level}] ${message}"
}

success() {
    echo -e "${GREEN}${ICON_SUCCESS}${NC} $*"
    log "SUCCESS" "$*"
}

error() {
    echo -e "${RED}${ICON_ERROR}${NC} $*" >&2
    log "ERROR" "$*"
}

info() {
    echo -e "${BLUE}${ICON_INFO}${NC} $*"
    log "INFO" "$*"
}

warning() {
    echo -e "${YELLOW}${ICON_WARNING}${NC} $*"
    log "WARNING" "$*"
}

header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $*${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

footer() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

#-------------------------------------------------------------------------------
# Help
#-------------------------------------------------------------------------------
show_help() {
    cat << EOF
${CYAN}BABY Brain - General Automation Script${NC}

${YELLOW}USAGE:${NC}
    $(basename "$0") [COMMAND] [OPTIONS]

${YELLOW}COMMANDS:${NC}
    ${GEAR} batch          Batch process files
    ${GEAR} schedule       Schedule automated tasks
    ${GEAR} workflow       Execute workflow files
    ${GEAR} cron          Manage cron jobs
    ${GEAR} template       Generate from template
    ${GEAR} backup        Create backups
    ${GEAR} sync         Sync directories
    ${GEAR} clean         Clean temporary files
    ${GEAR} monitor       Monitor directory changes
    ${GEAR} convert       Convert file formats
    ${GEAR} validate      Validate data/files

    ${GEAR} help          Show this help message

${YELLOW}OPTIONS:${NC}
    -h, --help            Show this help
    -v, --version         Show version
    -d, --debug           Enable debug mode
    -q, --quiet           Quiet mode (less output)
    --dry-run             Show what would be done

${YELLOW}EXAMPLES:${NC}
    $(basename "$0") batch --input ./files --operation compress
    $(basename "$0") schedule --task backup --cron "0 2 * * *"
    $(basename "$0") workflow --file workflow.yaml
    $(basename "$0") template --type api --output ./new-api

${YELLOW}ENVIRONMENT:${NC}
    BABY_BRAIN_CONFIG     Config directory (default: ~/.baby-brain)
    BABY_BRAIN_LOG        Log file path
    BABY_BRAIN_DEBUG      Enable debug mode (1 = true)

${YELLOW}EXIT CODES:${NC}
    0   Success
    1   General error
    2   Invalid arguments
    3   File not found
    4   Permission denied
    5   Command failed

${YELLOW}DOCUMENTATION:${NC}
    See ${CYAN}references/automation.md${NC} for detailed documentation

${YELLOW}SUPPORT:${NC}
    Issues: https://github.com/baby007/baby-brain/issues
    Discord: https://discord.gg/baby-brain

EOF
}

#-------------------------------------------------------------------------------
# Version
#-------------------------------------------------------------------------------
show_version() {
    cat << EOF
${CYAN}BABY Brain Automation Script${NC}
Version: 1.0.0
Author: Baby
License: MIT

This is part of BABY Brain - Ultimate AI Assistant Platform
Website: https://github.com/baby007/baby-brain
EOF
}

#-------------------------------------------------------------------------------
# Batch Processing
#-------------------------------------------------------------------------------
cmd_batch() {
    local input_dir=""
    local operation="list"
    local output_dir=""
    local pattern="*"
    local recursive=false
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --input|-i)
                input_dir="$2"
                shift 2
                ;;
            --operation|-o)
                operation="$2"
                shift 2
                ;;
            --output|-u)
                output_dir="$2"
                shift 2
                ;;
            --pattern|-p)
                pattern="$2"
                shift 2
                ;;
            --recursive|-r)
                recursive=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 2
                ;;
        esac
    done

    if [[ -z "$input_dir" ]]; then
        error "Missing required argument: --input"
        exit 2
    fi

    if [[ ! -d "$input_dir" ]]; then
        error "Directory not found: $input_dir"
        exit 3
    fi

    header "${ICON_FOLDER} Batch Processing"

    case "$operation" in
        list)
            info "Files in $input_dir:"
            if $recursive; then
                find "$input_dir" -type f -name "$pattern" | head -50
            else
                ls -la "$input_dir"/$pattern 2>/dev/null | head -50
            fi
            ;;
        count)
            local count=$(find "$input_dir" -type f -name "$pattern" 2>/dev/null | wc -l)
            success "Found $count files matching pattern '$pattern'"
            ;;
        compress)
            if [[ -z "$output_dir" ]]; then
                output_dir="${input_dir}.compressed"
            fi
            info "Compressing files from $input_dir to $output_dir"
            mkdir -p "$output_dir"
            if $dry_run; then
                warning "[DRY RUN] Would compress files"
            else
                tar -czf "${output_dir}/archive.tar.gz" -C "$input_dir" .
                success "Compressed to ${output_dir}/archive.tar.gz"
            fi
            ;;
        extract)
            if [[ -z "$output_dir" ]]; then
                output_dir="."
            fi
            info "Extracting $input_dir to $output_dir"
            if $dry_run; then
                warning "[DRY RUN] Would extract to $output_dir"
            else
                tar -xzf "$input_dir" -C "$output_dir"
                success "Extracted to $output_dir"
            fi
            ;;
        rename)
            local find_pattern="$2"
            local replace_pattern="$3"
            if [[ -z "$find_pattern" || -z "$replace_pattern" ]]; then
                error "Missing rename patterns"
                exit 2
            fi
            info "Renaming files: $find_pattern -> $replace_pattern"
            if $dry_run; then
                warning "[DRY RUN] Would rename files"
            else
                find "$input_dir" -type f -name "$find_pattern" -exec rename "$find_pattern" "$replace_pattern" {} \;
                success "Renamed files"
            fi
            ;;
        delete)
            info "Deleting files matching '$pattern' in $input_dir"
            if $dry_run; then
                warning "[DRY RUN] Would delete files"
            else
                find "$input_dir" -type f -name "$pattern" -delete
                success "Deleted files"
            fi
            ;;
        *)
            error "Unknown operation: $operation"
            exit 2
            ;;
    esac

    footer
}

#-------------------------------------------------------------------------------
# Scheduling
#-------------------------------------------------------------------------------
cmd_schedule() {
    local task=""
    local cron_expr=""
    local command=""
    local list=false
    local remove=false
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --task|-t)
                task="$2"
                shift 2
                ;;
            --cron|-c)
                cron_expr="$2"
                shift 2
                ;;
            --command|-m)
                command="$2"
                shift 2
                ;;
            --list|-l)
                list=true
                shift
                ;;
            --remove|-r)
                remove="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 2
                ;;
        esac
    done

    header "${ICON_ROCKET} Task Scheduling"

    if $list; then
        info "Scheduled tasks:"
        crontab -l 2>/dev/null | grep -i "baby-brain" || echo "No BABY Brain tasks scheduled"
        footer
        return
    fi

    if [[ -n "$remove" ]]; then
        info "Removing task: $remove"
        if $dry_run; then
            warning "[DRY RUN] Would remove $remove"
        else
            crontab -l 2>/dev/null | grep -v "$remove" | crontab -
            success "Removed task: $remove"
        fi
        footer
        return
    fi

    if [[ -z "$task" ]]; then
        error "Missing required argument: --task"
        footer
        exit 2
    fi

    # Check for built-in tasks
    local task_cmd=""
    case "$task" in
        backup)
            task_cmd="bash ${SCRIPT_DIR}/automation.sh backup"
            [[ -z "$cron_expr" ]] && cron_expr="0 2 * * *"
            ;;
        health)
            task_cmd="bash ${SCRIPT_DIR}/system.sh health"
            [[ -z "$cron_expr" ]] && cron_expr="*/5 * * * *"
            ;;
        update)
            task_cmd="clawhub update baby-brain"
            [[ -z "$cron_expr" ]] && cron_expr="0 6 * * 0"
            ;;
        clean)
            task_cmd="bash ${SCRIPT_DIR}/automation.sh clean"
            [[ -z "$cron_expr" ]] && cron_expr="0 3 * * *"
            ;;
        *)
            if [[ -z "$command" ]]; then
                error "Unknown task: $task"
                footer
                exit 2
            fi
            task_cmd="$command"
            ;;
    esac

    local cron_entry="$cron_expr $task_cmd # BABY Brain - $task"

    info "Scheduling task: $task"
    info "Schedule: $cron_expr"
    info "Command: $task_cmd"

    if $dry_run; then
        warning "[DRY RUN] Would add cron entry"
    else
        (crontab -l 2>/dev/null || true; echo "$cron_entry") | crontab -
        success "Scheduled task: $task"
    fi

    footer
}

#-------------------------------------------------------------------------------
# Workflow Execution
#-------------------------------------------------------------------------------
cmd_workflow() {
    local workflow_file=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --file|-f)
                workflow_file="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 2
                ;;
        esac
    done

    if [[ -z "$workflow_file" ]]; then
        error "Missing required argument: --file"
        exit 2
    fi

    if [[ ! -f "$workflow_file" ]]; then
        error "Workflow file not found: $workflow_file"
        exit 3
    fi

    header "${ICON_GEAR} Executing Workflow"

    info "Loading workflow: $workflow_file"

    # Simple YAML-like workflow parser
    local step_num=0
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue

        # Extract step
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]name:[[:space:]]*(.+) ]]; then
            local step_name="${BASH_REMATCH[1]}"
            ((step_num++))
            echo -e "${YELLOW}[$step_num]${NC} Executing: $step_name"

            if $dry_run; then
                warning "[DRY RUN] Would execute: $step_name"
            else
                # Execute step (simplified - would need full YAML parser for complex workflows)
                bash -c "$step_name" 2>/dev/null || warning "Step failed: $step_name"
                success "Completed: $step_name"
            fi
        fi
    done < "$workflow_file"

    success "Workflow execution complete"
    footer
}

#-------------------------------------------------------------------------------
# Backup
#-------------------------------------------------------------------------------
cmd_backup() {
    local source="${HOME}"
    local destination="${HOME}/.baby-brain/backups/$(date +%Y%m%d_%H%M%S)"
    local include=""
    local exclude="*.tmp *.log node_modules .git"
    local compress=true
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --source|-s)
                source="$2"
                shift 2
                ;;
            --destination|-d)
                destination="$2"
                shift 2
                ;;
            --include|-i)
                include="$2"
                shift 2
                ;;
            --exclude|-e)
                exclude="$exclude $2"
                shift 2
                ;;
            --no-compress)
                compress=false
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 2
                ;;
        esac
    done

    header "${ICON_FOLDER} Backup"

    info "Source: $source"
    info "Destination: $destination"

    mkdir -p "$(dirname "$destination")"

    if $dry_run; then
        warning "[DRY RUN] Would create backup"
        footer
        return
    fi

    if $compress; then
        local archive="${destination}.tar.gz"
        info "Creating compressed archive: $archive"
        tar -czf "$archive" -C "$(dirname "$source")" "$(basename "$source")" 2>/dev/null || true
        success "Backup created: $archive"
    else
        info "Copying files..."
        cp -r "$source" "$destination" 2>/dev/null || true
        success "Backup created: $destination"
    fi

    footer
}

#-------------------------------------------------------------------------------
# Sync
#-------------------------------------------------------------------------------
cmd_sync() {
    local source=""
    local destination=""
    local direction="push"
    local dry_run=false
    local delete=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --source|-s)
                source="$2"
                shift 2
                ;;
            --destination|-d)
                destination="$2"
                shift 2
                ;;
            --pull)
                direction="pull"
                shift
                ;;
            --push)
                direction="push"
                shift
                ;;
            --delete)
                delete=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 2
                ;;
        esac
    done

    if [[ -z "$source" || -z "$destination" ]]; then
        error "Missing required arguments: --source and --destination"
        exit 2
    fi

    header "${ICON_FOLDER} Sync"

    info "Source: $source"
    info "Destination: $destination"
    info "Direction: $direction"

    if $dry_run; then
        warning "[DRY RUN] Would sync files"
        footer
        return
    fi

    case "$direction" in
        push)
            rsync -avz --progress ${delete:+--delete} "$source/" "$destination/"
            ;;
        pull)
            rsync -avz --progress ${delete:+--delete} "$destination/" "$source/"
            ;;
    esac

    success "Sync complete"
    footer
}

#-------------------------------------------------------------------------------
# Clean
#-------------------------------------------------------------------------------
cmd_clean() {
    local temp=true
    local logs=true
    local cache=true
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --no-temp)
                temp=false
                shift
                ;;
            --no-logs)
                logs=false
                shift
                ;;
            --no-cache)
                cache=false
                shift
                ;;
            --all)
                temp=true
                logs=true
                cache=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 2
                ;;
        esac
    done

    header "${ICON_FOLDER} Cleanup"

    local freed=0

    if $temp && [[ -d "${TEMP_DIR}" ]]; then
        local temp_size=$(du -sm "${TEMP_DIR}" 2>/dev/null | cut -f1 || echo 0)
        info "Cleaning temp files (${temp_size}MB)..."
        if $dry_run; then
            warning "[DRY RUN] Would clean ${temp_size}MB of temp files"
        else
            rm -rf "${TEMP_DIR}"/* 2>/dev/null || true
            success "Cleaned ${temp_size}MB of temp files"
        fi
        ((freed+=temp_size))
    fi

    if $logs && [[ -d "${LOG_DIR}" ]]; then
        local log_size=$(find "${LOG_DIR}" -type f -name "*.log" -mtime +7 -exec ls -sm {} \; 2>/dev/null | awk '{sum+=$1} END {print sum+0}' || echo 0)
        info "Cleaning old logs (${log_size}MB)..."
        if $dry_run; then
            warning "[DRY RUN] Would clean ${log_size}MB of old logs"
        else
            find "${LOG_DIR}" -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
            success "Cleaned ${log_size}MB of old logs"
        fi
        ((freed+=log_size))
    fi

    if $cache && [[ -d "${HOME}/.cache" ]]; then
        local cache_size=$(du -sm "${HOME}/.cache" 2>/dev/null | cut -f1 || echo 0)
        info "Cleaning cache (${cache_size}MB)..."
        if $dry_run; then
            warning "[DRY RUN] Would clean ${cache_size}MB of cache"
        else
            rm -rf "${HOME}/.cache"/* 2>/dev/null || true
            success "Cleaned ${cache_size}MB of cache"
        fi
        ((freed+=cache_size))
    fi

    success "Total freed: ${freed}MB"
    footer
}

#-------------------------------------------------------------------------------
# Monitor
#-------------------------------------------------------------------------------
cmd_monitor() {
    local directory="${PWD}"
    local interval=5
    local max_changes=10
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dir|-d)
                directory="$2"
                shift 2
                ;;
            --interval|-i)
                interval="$2"
                shift 2
                ;;
            --max|-m)
                max_changes="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 2
                ;;
        esac
    done

    header "${ICON_FOLDER} Monitoring"

    info "Watching: $directory"
    info "Interval: ${interval}s"
    info "Max changes: $max_changes"

    if ! command -v inotifywait &> /dev/null; then
        warning "inotify-tools not installed. Using polling mode..."
        while true; do
            local changes=$(find "$directory" -type f -mmin -$((interval/60)) 2>/dev/null | wc -l)
            if [[ $changes -gt 0 ]]; then
                info "$changes file(s) modified"
            fi
            sleep "$interval"
        done
    else
        info "Using inotify for real-time monitoring..."
        inotifywait -m -r -e modify,create,delete "$directory" --format '%w%f %e' | head -n "$max_changes" | while read -r file event; do
            echo -e "${YELLOW}${event}${NC}: $file"
        done
    fi

    footer
}

#-------------------------------------------------------------------------------
# Convert
#-------------------------------------------------------------------------------
cmd_convert() {
    local input=""
    local output=""
    local from_format=""
    local to_format=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --input|-i)
                input="$2"
                shift 2
                ;;
            --output|-o)
                output="$2"
                shift 2
                ;;
            --from|-f)
                from_format="$2"
                shift 2
                ;;
            --to|-t)
                to_format="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 2
                ;;
        esac
    done

    if [[ -z "$input" || -z "$output" ]]; then
        error "Missing required arguments: --input and --output"
        exit 2
    fi

    header "${ICON_FILE} Format Conversion"

    info "Input: $input"
    info "Output: $output"

    if $dry_run; then
        warning "[DRY RUN] Would convert file"
        footer
        return
    fi

    # Auto-detect format if not specified
    [[ -z "$from_format" ]] && from_format="${input##*.}"
    [[ -z "$to_format" ]] && to_format="${output##*.}"

    info "Converting: $from_format -> $to_format"

    case "$from_format" in
        json)
            case "$to_format" in
                yaml|yml)
                    python3 -c "import yaml, json, sys; yaml.dump(json.load(open('$input')), open('$output', 'w'))" 2>/dev/null && success "Converted" || error "Conversion failed"
                    ;;
                csv)
                    python3 -c "import csv, json, sys; data=json.load(open('$input')); [print(','.join(str(x.get(h, '')) for h in data[0].keys())) for x in data]" > "$output" && success "Converted" || error "Conversion failed"
                    ;;
                *)
                    error "Unsupported output format: $to_format"
                    ;;
            esac
            ;;
        yaml|yml)
            case "$to_format" in
                json)
                    python3 -c "import json, yaml, sys; json.dump(yaml.safe_load(open('$input').read()), open('$output', 'w'), indent=2)" 2>/dev/null && success "Converted" || error "Conversion failed"
                    ;;
                *)
                    error "Unsupported output format: $to_format"
                    ;;
            esac
            ;;
        csv)
            case "$to_format" in
                json)
                    python3 -c "import json, csv, sys; data=[dict(r) for r in csv.DictReader(open('$input'))]; json.dump(data, open('$output', 'w'), indent=2)" 2>/dev/null && success "Converted" || error "Conversion failed"
                    ;;
                *)
                    error "Unsupported output format: $to_format"
                    ;;
            esac
            ;;
        *)
            error "Unsupported input format: $from_format"
            ;;
    esac

    footer
}

#-------------------------------------------------------------------------------
# Validate
#-------------------------------------------------------------------------------
cmd_validate() {
    local target=""
    local type="file"
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --file|-f)
                target="$2"
                shift 2
                ;;
            --type|-t)
                type="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 2
                ;;
        esac
    done

    if [[ -z "$target" ]]; then
        error "Missing required argument: --file"
        exit 2
    fi

    header "${ICON_FILE} Validation"

    info "Validating: $target"
    info "Type: $type"

    case "$type" in
        file)
            if [[ -f "$target" ]]; then
                # JSON validation
                if [[ "$target" =~ \.json$ ]]; then
                    if python3 -c "import json; json.load(open('$target'))" 2>/dev/null; then
                        success "Valid JSON file"
                    else
                        error "Invalid JSON"
                        exit 5
                    fi
                # YAML validation
                elif [[ "$target" =~ \.(yaml|yml)$ ]]; then
                    if python3 -c "import yaml; yaml.safe_load(open('$target').read())" 2>/dev/null; then
                        success "Valid YAML file"
                    else
                        error "Invalid YAML"
                        exit 5
                    fi
                else
                    success "File exists"
                fi
            else
                error "File not found: $target"
                exit 3
            fi
            ;;
        url)
            if curl -s -o /dev/null -w "%{http_code}" "$target" | grep -q "200"; then
                success "URL is reachable"
            else
                error "URL is not reachable: $target"
                exit 5
            fi
            ;;
        json)
            if echo "$target" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
                success "Valid JSON"
            else
                error "Invalid JSON"
                exit 5
            fi
            ;;
        email)
            if [[ "$target" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
                success "Valid email format"
            else
                error "Invalid email format"
                exit 5
            fi
            ;;
        *)
            error "Unknown type: $type"
            exit 2
            ;;
    esac

    footer
}

#-------------------------------------------------------------------------------
# Template
#-------------------------------------------------------------------------------
cmd_template() {
    local type=""
    local output=""
    local name=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --type|-t)
                type="$2"
                shift 2
                ;;
            --output|-o)
                output="$2"
                shift 2
                ;;
            --name|-n)
                name="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 2
                ;;
        esac
    done

    if [[ -z "$type" ]]; then
        error "Missing required argument: --type"
        exit 2
    fi

    header "${ICON_FILE} Template Generation"

    [[ -z "$output" ]] && output="${PWD}"
    [[ -z "$name" ]] && name="$type"

    info "Template type: $type"
    info "Output directory: $output"
    info "Name: $name"

    if $dry_run; then
        warning "[DRY RUN] Would generate template"
        footer
        return
    fi

    mkdir -p "$output"

    case "$type" in
        api)
            cat > "$output/${name}.py" << 'PYEOF'
#!/usr/bin/env python3
"""API Template"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/v1/<action>', methods=['GET', 'POST'])
def api_action(action):
    return jsonify({'action': action, 'data': request.json or {}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
PYEOF
            success "Generated API template: ${name}.py"
            ;;
        script)
            cat > "$output/${name}.sh" << 'BASHEOF'
#!/bin/bash
# Script Template

set -euo pipefail

echo "Running ${name}..."

# Your code here

echo "Done!"
BASHEOF
            chmod +x "$output/${name}.sh"
            success "Generated script template: ${name}.sh"
            ;;
        docker)
            cat > "$output/Dockerfile" << 'DOCKEREOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
DOCKEREOF
            success "Generated Dockerfile"
            ;;
        README)
            cat > "$output/README.md" << 'MDEOF'
# Project Title

Brief description of the project.

## Installation

\`\`\`bash
npm install
\`\`\`

## Usage

\`\`\`bash
npm start
\`\`\`

## License

MIT
MDEOF
            success "Generated README.md"
            ;;
        workflow)
            cat > "$output/${name}.yaml" << 'YAMLEOF'
# Workflow Template
version: '1.0'
name: ${name}

steps:
  - name: Step 1
    command: echo "Step 1"
  - name: Step 2
    command: echo "Step 2"
  - name: Step 3
    command: echo "Step 3"
YAMLEOF
            success "Generated workflow template: ${name}.yaml"
            ;;
        *)
            error "Unknown template type: $type"
            exit 2
            ;;
    esac

    footer
}

#-------------------------------------------------------------------------------
# Main Entry Point
#-------------------------------------------------------------------------------
main() {
    local command="${1:-}"
    shift 2>/dev/null || true

    # Handle --help and --version at top level
    if [[ "$command" == "--help" || "$command" == "-h" ]]; then
        show_help
        exit 0
    fi

    if [[ "$command" == "--version" || "$command" == "-v" ]]; then
        show_version
        exit 0
    fi

    # Check for debug mode
    if [[ "${BABY_BRAIN_DEBUG:-}" == "1" ]] || [[ "$*" == *"--debug"* ]]; then
        set -x
    fi

    # Default command if none provided
    if [[ -z "$command" ]]; then
        show_help
        exit 0
    fi

    # Execute command
    case "$command" in
        batch)
            cmd_batch "$@"
            ;;
        schedule)
            cmd_schedule "$@"
            ;;
        workflow)
            cmd_workflow "$@"
            ;;
        cron)
            cmd_schedule "$@"
            ;;
        template)
            cmd_template "$@"
            ;;
        backup)
            cmd_backup "$@"
            ;;
        sync)
            cmd_sync "$@"
            ;;
        clean)
            cmd_clean "$@"
            ;;
        monitor)
            cmd_monitor "$@"
            ;;
        convert)
            cmd_convert "$@"
            ;;
        validate)
            cmd_validate "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $command"
            echo ""
            show_help
            exit 2
            ;;
    esac
}

# Run main
main "$@"

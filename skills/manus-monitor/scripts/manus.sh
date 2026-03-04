#!/bin/bash
# Manus API helper script
# Usage: manus.sh <action> [args]

API_BASE="https://api.manus.ai/v1"
DATA_DIR="$(dirname "$0")/../data"
TASK_LIST="$DATA_DIR/task_list.txt"

# Ensure data directory exists
mkdir -p "$DATA_DIR"

if [ -z "$MANUS_API_KEY" ]; then
  echo "Error: MANUS_API_KEY not set" >&2
  exit 1
fi

action="$1"
shift

case "$action" in
  create)
    # Create a task: manus.sh create "your prompt here" [profile]
    prompt="$1"
    profile="${2:-manus-1.6}"
    curl -s -X POST "$API_BASE/tasks" \
      -H "API_KEY: $MANUS_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"prompt\": $(echo "$prompt" | jq -Rs .), \"agentProfile\": \"$profile\", \"taskMode\": \"agent\", \"createShareableLink\": true}"
    ;;
  
  get)
    # Get task: manus.sh get <task_id>
    task_id="$1"
    curl -s "$API_BASE/tasks/$task_id" \
      -H "API_KEY: $MANUS_API_KEY"
    ;;
  
  status)
    # Get task status only: manus.sh status <task_id>
    task_id="$1"
    curl -s "$API_BASE/tasks/$task_id" \
      -H "API_KEY: $MANUS_API_KEY" | jq -r '.status // "unknown"'
    ;;
  
  wait)
    # Wait for task completion: manus.sh wait <task_id> [timeout_seconds]
    task_id="$1"
    timeout="${2:-600}"
    elapsed=0
    interval=10
    
    while [ $elapsed -lt $timeout ]; do
      status=$(curl -s "$API_BASE/tasks/$task_id" -H "API_KEY: $MANUS_API_KEY" | jq -r '.status // "unknown"')
      
      if [ "$status" = "completed" ]; then
        echo "completed"
        exit 0
      elif [ "$status" = "failed" ]; then
        echo "failed"
        exit 1
      fi
      
      sleep $interval
      elapsed=$((elapsed + interval))
      echo "waiting... ($elapsed/$timeout sec, status: $status)" >&2
    done
    
    echo "timeout"
    exit 1
    ;;
  
  files)
    # List output files: manus.sh files <task_id>
    task_id="$1"
    curl -s "$API_BASE/tasks/$task_id" \
      -H "API_KEY: $MANUS_API_KEY" | jq -r '.output[]?.content[]? | select(.type == "output_file") | "\(.fileName)\t\(.fileUrl)"'
    ;;
  
  download)
    # Download output files: manus.sh download <task_id> [output_dir]
    task_id="$1"
    output_dir="${2:-.}"
    mkdir -p "$output_dir"
    
    curl -s "$API_BASE/tasks/$task_id" \
      -H "API_KEY: $MANUS_API_KEY" | jq -r '.output[]?.content[]? | select(.type == "output_file") | "\(.fileName)\t\(.fileUrl)"' | \
    while IFS=$'\t' read -r filename url; do
      if [ -n "$filename" ] && [ -n "$url" ]; then
        # Sanitize filename
        safe_name=$(echo "$filename" | tr -cd '[:alnum:]._-' | head -c 100)
        [ -z "$safe_name" ] && safe_name="output_file"
        echo "Downloading: $safe_name" >&2
        curl -sL "$url" -o "$output_dir/$safe_name"
        echo "$output_dir/$safe_name"
      fi
    done
    ;;
  
  list)
    # List tasks: manus.sh list
    curl -s "$API_BASE/tasks" \
      -H "API_KEY: $MANUS_API_KEY"
    ;;
  
  save)
    # Save a task_id to local list: manus.sh save <task_id> [description]
    task_id="$1"
    description="${2:-}"
    timestamp=$(date +%s)
    
    if [ -z "$task_id" ]; then
      echo "Error: task_id required" >&2
      exit 1
    fi
    
    # Check if already exists
    if grep -q "^$task_id|" "$TASK_LIST" 2>/dev/null; then
      echo "Task already saved: $task_id" >&2
      exit 0
    fi
    
    echo "$task_id|$timestamp|$description" >> "$TASK_LIST"
    echo "" >> "$TASK_LIST"  # Ensure newline at end
    echo "Saved: $task_id${description:+ - $description}"

    # 自动启动监控
    SCRIPT_DIR="$(dirname "$0")"
    if [ -f "$SCRIPT_DIR/manus-monitor-start.sh" ]; then
      "$SCRIPT_DIR/manus-monitor-start.sh" > /dev/null 2>&1
    fi
    ;;
  
  saved)
    # List saved tasks: manus.sh saved
    if [ ! -f "$TASK_LIST" ] || [ ! -s "$TASK_LIST" ]; then
      echo "No saved tasks found."
      exit 0
    fi
    
    echo "=== Saved Tasks ==="
    while IFS='|' read -r task_id timestamp description status title; do
      if [ -n "$task_id" ]; then
        date_str=$(date -d "@$timestamp" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "$timestamp")
        echo "$task_id | $date_str | ${description:-$title} | $status"
      fi
    done < "$TASK_LIST"
    ;;
  
  status-all)
    # Get status for all saved tasks: manus.sh status-all
    if [ ! -f "$TASK_LIST" ] || [ ! -s "$TASK_LIST" ]; then
      echo "No saved tasks found."
      exit 0
    fi
    
    echo "=== Task Status ==="
    while IFS='|' read -r task_id timestamp description status title; do
      if [ -n "$task_id" ]; then
        echo "$task_id | $status | ${description:-$title}"
      fi
    done < "$TASK_LIST"
    ;;
  
  refresh)
    # Refresh and update status for all saved tasks: manus.sh refresh
    if [ ! -f "$TASK_LIST" ] || [ ! -s "$TASK_LIST" ]; then
      echo "No saved tasks found."
      exit 0
    fi
    
    echo "=== Task Status (Updated) ==="
    temp_file=$(mktemp)
    
    while IFS='|' read -r task_id timestamp description; do
      if [ -n "$task_id" ]; then
        response=$(curl -s "$API_BASE/tasks/$task_id" \
          -H "API_KEY: $MANUS_API_KEY")
        
        status=$(echo "$response" | jq -r '.status // "unknown"')
        title=$(echo "$response" | jq -r '.metadata.task_title // ""')
        # Truncate title to 50 chars
        title=$(echo "$title" | cut -c1-50)
        
        # Update status in temp file
        echo "$task_id|$timestamp|$description|$status|$title" >> "$temp_file"
        echo "" >> "$temp_file"  # Ensure newline at end
        
        echo "$task_id | $status | ${description:-$title}"
      fi
    done < "$TASK_LIST"
    
    # Replace original file with updated info
    mv "$temp_file" "$TASK_LIST"

    # 检查是否所有任务都完成了，如果完成则停止监控
    SCRIPT_DIR="$(dirname "$0")"
    running_count=$("$SCRIPT_DIR/manus.sh" running 2>/dev/null | grep -c "running/pending" || echo "0")
    if [ "$running_count" -eq 0 ] && [ -f "$SCRIPT_DIR/manus-monitor-stop.sh" ]; then
      "$SCRIPT_DIR/manus-monitor-stop.sh" > /dev/null 2>&1
      echo "(所有任务已完成，监控已停止)"
    fi
    ;;
  
  running)
    # List only running/pending tasks: manus.sh running
    if [ ! -f "$TASK_LIST" ] || [ ! -s "$TASK_LIST" ]; then
      echo "No saved tasks found."
      exit 0
    fi
    
    echo "=== Running/Pending Tasks ==="
    count=0
    
    while IFS='|' read -r task_id timestamp description status title; do
      if [ -n "$task_id" ] && [ "$status" != "completed" ] && [ "$status" != "failed" ]; then
        echo "$task_id | $status | ${description:-$title}"
        count=$((count + 1))
      fi
    done < "$TASK_LIST"
    
    if [ $count -eq 0 ]; then
      echo "No running or pending tasks."
    else
      echo ""
      echo "Total: $count running/pending task(s)."
    fi
    ;;
  
  delete)
    # Delete a saved task: manus.sh delete <task_id>
    task_id="$1"
    
    if [ -z "$task_id" ]; then
      echo "Error: task_id required" >&2
      exit 1
    fi
    
    if [ ! -f "$TASK_LIST" ]; then
      echo "No saved tasks found." >&2
      exit 1
    fi
    
    if grep -q "^$task_id|" "$TASK_LIST"; then
      grep -v "^$task_id|" "$TASK_LIST" > "$TASK_LIST.tmp" && mv "$TASK_LIST.tmp" "$TASK_LIST"
      echo "Deleted: $task_id"
    else
      echo "Task not found: $task_id" >&2
      exit 1
    fi
    ;;
  
  clear)
    # Clear all saved tasks: manus.sh clear
    if [ -f "$TASK_LIST" ]; then
      rm -f "$TASK_LIST"
      echo "All saved tasks cleared."
    else
      echo "No saved tasks to clear."
    fi
    ;;
  
  *)
    echo "Usage: manus.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  create \"prompt\" [profile]  - Create a new task (default: manus-1.6)"
    echo "  get <task_id>              - Get full task details"
    echo "  status <task_id>          - Get task status (pending/running/completed/failed)"
    echo "  wait <task_id> [timeout]   - Wait for task completion (default: 600s)"
    echo "  files <task_id>            - List output files"
    echo "  download <task_id> [dir]   - Download all output files"
    echo "  list                       - List all tasks from API"
    echo "  save <task_id> [desc]      - Save a task_id to local list"
    echo "  saved                      - List saved tasks"
    echo "  status-all                 - Get status for all saved tasks"
    echo "  running                    - List only running/pending tasks"
    echo "  refresh                    - Refresh and update all task statuses"
    echo "  delete <task_id>          - Delete a saved task"
    echo "  clear                      - Clear all saved tasks"
    echo ""
    echo "Profiles: manus-1.6 (default), manus-1.6-lite, manus-1.6-max"
    exit 1
    ;;
esac

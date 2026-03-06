#!/bin/bash
# autopilot-lib.sh — shared utility functions for autopilot scripts
# Source this file: source "${SCRIPT_DIR}/autopilot-lib.sh"
#
# Provides:
#   normalize_int()        — sanitize to integer
#   sanitize()             — safe filename from window name
#   now_ts()               — current unix timestamp
#   file_mtime()           — 跨平台文件修改时间
#   run_with_timeout()     — macOS-compatible timeout wrapper
#   load_telegram_config() — sets LIB_TG_TOKEN and LIB_TG_CHAT
#   send_telegram()        — send Telegram message (background)
#   get_discord_channel_for_window()  — 按窗口名查 Discord 频道名
#   get_tmux_window_for_channel()     — 按 Discord 频道名查窗口名
#   get_discord_channel_id_for_channel() — 按频道名查 Discord channel_id
#   get_tmux_window_for_project_dir() — 按项目目录查 tmux 窗口名
#   acquire_lock()         — mkdir-based lock with stale timeout
#   release_lock()         — release mkdir lock
#
# Requires caller to set:
#   LOCK_DIR — for acquire_lock/release_lock

# Guard against double-sourcing
[ -n "${_AUTOPILOT_LIB_LOADED:-}" ] && return 0
_AUTOPILOT_LIB_LOADED=1

# Source shared constants (状态常量等)
_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${_LIB_DIR}/autopilot-constants.sh" ]; then
    # shellcheck source=autopilot-constants.sh
    source "${_LIB_DIR}/autopilot-constants.sh"
fi

normalize_int() {
    local val
    val=$(echo "${1:-}" | tr -dc '0-9')
    echo "${val:-0}"
}

sanitize() {
    echo "${1:-}" | tr -cd 'a-zA-Z0-9_-'
}

now_ts() {
    date +%s
}

file_mtime() {
    local f="$1"
    if stat -f %m "$f" 2>/dev/null; then return; fi
    stat -c %Y "$f" 2>/dev/null || echo 0
}

# ---- 项目加载（config.yaml -> watchdog-projects.conf -> defaults）----
AUTOPILOT_PROJECT_SOURCE="${AUTOPILOT_PROJECT_SOURCE:-}"
AUTOPILOT_PROJECT_COUNT="${AUTOPILOT_PROJECT_COUNT:-0}"

autopilot_parse_projects_from_config_yaml() {
    local config_file="$1"
    [ -f "$config_file" ] || return 1

    awk '
    function ltrim(s) { sub(/^[[:space:]]+/, "", s); return s }
    function rtrim(s) { sub(/[[:space:]]+$/, "", s); return s }
    function trim(s) { return rtrim(ltrim(s)) }
    function strip_quotes(s) {
        s = trim(s)
        if (s ~ /^".*"$/) return substr(s, 2, length(s) - 2)
        return s
    }
    function strip_inline_comment(s, out, i, ch, in_double) {
        out = ""
        in_double = 0
        for (i = 1; i <= length(s); i++) {
            ch = substr(s, i, 1)
            if (ch == "\"") {
                in_double = !in_double
            } else if (ch == "#" && in_double == 0) {
                break
            }
            out = out ch
        }
        return out
    }
    function reset_item() {
        current_window = ""
        current_dir = ""
    }
    function flush_item() {
        if (current_window == "" && current_dir == "") return
        if (current_window == "" || current_dir == "") {
            parse_error = 1
            reset_item()
            return
        }
        print current_window ":" current_dir
        parsed_count++
        reset_item()
    }
    BEGIN {
        in_projects = 0
        projects_indent = -1
        list_mode = 0
        saw_projects = 0
        parse_error = 0
        parsed_count = 0
        reset_item()
    }
    {
        line = $0
        sub(/\r$/, "", line)

        if (in_projects == 0) {
            if (line ~ /^[[:space:]]*projects:[[:space:]]*($|#)/) {
                saw_projects = 1
                in_projects = 1
                match(line, /^[[:space:]]*/)
                projects_indent = RLENGTH
                list_mode = 0
            }
            next
        }

        if (line ~ /^[[:space:]]*$/ || line ~ /^[[:space:]]*#/) next

        match(line, /^[[:space:]]*/)
        indent = RLENGTH
        if (indent <= projects_indent) {
            flush_item()
            in_projects = 0
            next
        }

        content = substr(line, indent + 1)
        content = trim(strip_inline_comment(content))
        if (content == "") next

        if (content ~ /^-[[:space:]]*/) {
            flush_item()
            list_mode = 1
            content = trim(substr(content, 2))
            if (content == "") next
        }

        split_pos = index(content, ":")
        if (split_pos == 0) {
            if (list_mode == 1) parse_error = 1
            next
        }

        key = strip_quotes(trim(substr(content, 1, split_pos - 1)))
        value = trim(strip_quotes(strip_inline_comment(substr(content, split_pos + 1))))

        if (value == "") {
            if (key == "window" || key == "name" || key == "dir" || key == "project_dir" || key == "path") {
                parse_error = 1
            }
            next
        }

        if (key == "window" || key == "name") {
            current_window = value
            if (current_window != "" && current_dir != "") flush_item()
            next
        }

        if (key == "dir" || key == "project_dir" || key == "path") {
            current_dir = value
            if (current_window != "" && current_dir != "") flush_item()
            next
        }

        if (list_mode == 0) {
            current_window = key
            current_dir = value
            flush_item()
        }
    }
    END {
        if (in_projects == 1) flush_item()
        if (saw_projects == 0) exit 10
        if (parse_error != 0 || parsed_count == 0) exit 11
    }
    ' "$config_file"
}

autopilot_parse_project_dirs_from_config_yaml() {
    local config_file="$1"
    [ -f "$config_file" ] || return 1

    awk '
    function ltrim(s) { sub(/^[[:space:]]+/, "", s); return s }
    function rtrim(s) { sub(/[[:space:]]+$/, "", s); return s }
    function trim(s) { return rtrim(ltrim(s)) }
    function strip_quotes(s) {
        s = trim(s)
        if (s ~ /^".*"$/) return substr(s, 2, length(s) - 2)
        if (s ~ /^'\''.*'\''$/) return substr(s, 2, length(s) - 2)
        return s
    }
    function strip_inline_comment(s, out, i, ch, in_double, in_single) {
        out = ""
        in_double = 0
        in_single = 0
        for (i = 1; i <= length(s); i++) {
            ch = substr(s, i, 1)
            if (ch == "\"" && in_single == 0) {
                in_double = !in_double
            } else if (ch == "'\''" && in_double == 0) {
                in_single = !in_single
            } else if (ch == "#" && in_double == 0 && in_single == 0) {
                break
            }
            out = out ch
        }
        return out
    }
    BEGIN {
        in_dirs = 0
        dirs_indent = -1
        parsed_count = 0
    }
    {
        line = $0
        sub(/\r$/, "", line)

        if (in_dirs == 0) {
            if (line ~ /^[[:space:]]*project_dirs:[[:space:]]*($|#)/) {
                in_dirs = 1
                match(line, /^[[:space:]]*/)
                dirs_indent = RLENGTH
            }
            next
        }

        if (line ~ /^[[:space:]]*$/ || line ~ /^[[:space:]]*#/) next

        match(line, /^[[:space:]]*/)
        indent = RLENGTH
        if (indent <= dirs_indent) {
            in_dirs = 0
            next
        }

        content = trim(strip_inline_comment(substr(line, indent + 1)))
        if (content == "") next
        if (content !~ /^-[[:space:]]*/) next

        value = trim(substr(content, 2))
        value = strip_quotes(strip_inline_comment(value))
        if (value == "") next

        print value
        parsed_count++
    }
    END {
        if (parsed_count == 0) exit 10
    }
    ' "$config_file"
}

autopilot_default_config_yaml() {
    echo "${AUTOPILOT_CONFIG_FILE:-$HOME/.autopilot/config.yaml}"
}

autopilot_parse_discord_channels_from_config_yaml() {
    local config_file="$1"
    [ -f "$config_file" ] || return 1

    awk '
    function ltrim(s) { sub(/^[[:space:]]+/, "", s); return s }
    function rtrim(s) { sub(/[[:space:]]+$/, "", s); return s }
    function trim(s) { return rtrim(ltrim(s)) }
    function strip_quotes(s) {
        s = trim(s)
        if (s ~ /^".*"$/) return substr(s, 2, length(s) - 2)
        if (s ~ /^'\''.*'\''$/) return substr(s, 2, length(s) - 2)
        return s
    }
    function strip_inline_comment(s, out, i, ch, in_double, in_single) {
        out = ""
        in_double = 0
        in_single = 0
        for (i = 1; i <= length(s); i++) {
            ch = substr(s, i, 1)
            if (ch == "\"" && in_single == 0) {
                in_double = !in_double
            } else if (ch == "'\''" && in_double == 0) {
                in_single = !in_single
            } else if (ch == "#" && in_double == 0 && in_single == 0) {
                break
            }
            out = out ch
        }
        return out
    }
    function reset_item() {
        current_name = ""
        current_channel_id = ""
        current_tmux_window = ""
        current_project_dir = ""
        current_indent = -1
    }
    function flush_item() {
        if (current_name == "") return
        print current_name "\t" current_channel_id "\t" current_tmux_window "\t" current_project_dir
        parsed_count++
        reset_item()
    }
    BEGIN {
        in_discord = 0
        discord_indent = -1
        saw_discord = 0
        parse_error = 0
        parsed_count = 0
        reset_item()
    }
    {
        line = $0
        sub(/\r$/, "", line)

        if (in_discord == 0) {
            if (line ~ /^[[:space:]]*discord_channels:[[:space:]]*($|#)/) {
                saw_discord = 1
                in_discord = 1
                match(line, /^[[:space:]]*/)
                discord_indent = RLENGTH
            }
            next
        }

        if (line ~ /^[[:space:]]*$/ || line ~ /^[[:space:]]*#/) next

        match(line, /^[[:space:]]*/)
        indent = RLENGTH
        if (indent <= discord_indent) {
            flush_item()
            in_discord = 0
            next
        }

        content = trim(strip_inline_comment(substr(line, indent + 1)))
        if (content == "") next

        split_pos = index(content, ":")
        if (split_pos == 0) next

        key = strip_quotes(trim(substr(content, 1, split_pos - 1)))
        raw_value = trim(substr(content, split_pos + 1))
        value = strip_quotes(trim(strip_inline_comment(raw_value)))

        is_known_field = (key == "channel_id" || key == "tmux_window" || key == "project_dir" || key == "dir" || key == "path")
        if (raw_value == "" || value == "") {
            # 仅“频道名:”允许空值，表示开始新条目；字段空值视为解析错误。
            if (current_name == "" || indent <= current_indent) {
                flush_item()
                current_name = key
                current_channel_id = ""
                current_tmux_window = ""
                current_project_dir = ""
                current_indent = indent
            } else if (is_known_field) {
                parse_error = 1
            }
            next
        }

        if (current_name == "" || indent <= current_indent) next

        if (key == "channel_id") {
            current_channel_id = value
            next
        }
        if (key == "tmux_window") {
            current_tmux_window = value
            next
        }
        if (key == "project_dir" || key == "dir" || key == "path") {
            current_project_dir = value
            next
        }
    }
    END {
        if (in_discord == 1) flush_item()
        if (saw_discord == 0) exit 10
        if (parse_error != 0 || parsed_count == 0) exit 11
    }
    ' "$config_file"
}

get_discord_channel_for_window() {
    local window="${1:-}"
    local config_file="${2:-$(autopilot_default_config_yaml)}"
    [ -n "$window" ] || return 1

    local safe_window
    safe_window=$(sanitize "$window")
    local parsed_channels
    parsed_channels=$(autopilot_parse_discord_channels_from_config_yaml "$config_file" 2>/dev/null) || return 1

    local channel_name channel_id tmux_window project_dir safe_tmux_window
    while IFS=$'\t' read -r channel_name channel_id tmux_window project_dir || [ -n "$channel_name" ]; do
        [ -n "$channel_name" ] || continue
        if [ "$tmux_window" = "$window" ]; then
            echo "$channel_name"
            return 0
        fi
        safe_tmux_window=$(sanitize "$tmux_window")
        if [ -n "$safe_tmux_window" ] && [ "$safe_tmux_window" = "$safe_window" ]; then
            echo "$channel_name"
            return 0
        fi
    done <<< "$parsed_channels"

    return 1
}

get_tmux_window_for_channel() {
    local channel_name="${1:-}"
    local config_file="${2:-$(autopilot_default_config_yaml)}"
    [ -n "$channel_name" ] || return 1

    local target_channel_lower
    target_channel_lower=$(printf '%s' "$channel_name" | tr '[:upper:]' '[:lower:]')
    local parsed_channels
    parsed_channels=$(autopilot_parse_discord_channels_from_config_yaml "$config_file" 2>/dev/null) || return 1

    local cfg_channel cfg_channel_id cfg_tmux_window cfg_project_dir cfg_channel_lower
    while IFS=$'\t' read -r cfg_channel cfg_channel_id cfg_tmux_window cfg_project_dir || [ -n "$cfg_channel" ]; do
        [ -n "$cfg_channel" ] || continue
        if [ "$cfg_channel" = "$channel_name" ]; then
            echo "$cfg_tmux_window"
            return 0
        fi
        cfg_channel_lower=$(printf '%s' "$cfg_channel" | tr '[:upper:]' '[:lower:]')
        if [ "$cfg_channel_lower" = "$target_channel_lower" ]; then
            echo "$cfg_tmux_window"
            return 0
        fi
    done <<< "$parsed_channels"

    return 1
}

get_discord_channel_id_for_channel() {
    local channel_name="${1:-}"
    local config_file="${2:-$(autopilot_default_config_yaml)}"
    [ -n "$channel_name" ] || return 1

    local target_channel_lower
    target_channel_lower=$(printf '%s' "$channel_name" | tr '[:upper:]' '[:lower:]')
    local parsed_channels
    parsed_channels=$(autopilot_parse_discord_channels_from_config_yaml "$config_file" 2>/dev/null) || return 1

    local cfg_channel cfg_channel_id cfg_tmux_window cfg_project_dir cfg_channel_lower
    while IFS=$'\t' read -r cfg_channel cfg_channel_id cfg_tmux_window cfg_project_dir || [ -n "$cfg_channel" ]; do
        [ -n "$cfg_channel" ] || continue
        if [ "$cfg_channel" = "$channel_name" ]; then
            [ -n "$cfg_channel_id" ] || return 1
            echo "$cfg_channel_id"
            return 0
        fi
        cfg_channel_lower=$(printf '%s' "$cfg_channel" | tr '[:upper:]' '[:lower:]')
        if [ "$cfg_channel_lower" = "$target_channel_lower" ]; then
            [ -n "$cfg_channel_id" ] || return 1
            echo "$cfg_channel_id"
            return 0
        fi
    done <<< "$parsed_channels"

    return 1
}

get_tmux_window_for_project_dir() {
    local project_dir="${1:-}"
    local config_file="${2:-$(autopilot_default_config_yaml)}"
    [ -n "$project_dir" ] || return 1

    local target_dir="${project_dir%/}"
    [ -n "$target_dir" ] || return 1
    local parsed_channels
    parsed_channels=$(autopilot_parse_discord_channels_from_config_yaml "$config_file" 2>/dev/null) || return 1

    local cfg_channel cfg_channel_id cfg_tmux_window cfg_project_dir cfg_dir
    while IFS=$'\t' read -r cfg_channel cfg_channel_id cfg_tmux_window cfg_project_dir || [ -n "$cfg_channel" ]; do
        [ -n "$cfg_tmux_window" ] || continue
        [ -n "$cfg_project_dir" ] || continue
        cfg_dir="${cfg_project_dir%/}"
        if [ "$cfg_dir" = "$target_dir" ]; then
            echo "$cfg_tmux_window"
            return 0
        fi
    done <<< "$parsed_channels"

    return 1
}

autopilot_derive_window_name_from_path() {
    local dir="${1:-}"
    dir="${dir%/}"
    local window
    window=$(basename "$dir" 2>/dev/null || echo "")
    [ -n "$window" ] || window="project"
    window=$(printf '%s' "$window" | sed 's/[[:space:]]\+/-/g; s/:/-/g')
    [ -n "$window" ] || window="project"
    echo "$window"
}

_autopilot_project_window_exists() {
    local needle="${1:-}"
    shift || true
    local entry
    for entry in "$@"; do
        if [ "${entry%%:*}" = "$needle" ]; then
            return 0
        fi
    done
    return 1
}

# Usage:
#   autopilot_load_projects_entries <config_yaml> <fallback_conf> [default "window:/dir"...]
# Output:
#   每行一个 "window:dir"
# Side effects:
#   AUTOPILOT_PROJECT_SOURCE = config.yaml | watchdog-projects.conf | defaults
#   AUTOPILOT_PROJECT_COUNT  = number
autopilot_load_projects_entries() {
    local config_yaml_file="${1:-}"
    local fallback_conf_file="${2:-}"
    shift 2 || true
    local -a default_projects=("$@")
    local -a projects=()
    local parse_mode="" parsed_lines="" line window dir

    AUTOPILOT_PROJECT_SOURCE=""
    AUTOPILOT_PROJECT_COUNT=0

    if [ -n "$config_yaml_file" ] && [ -f "$config_yaml_file" ]; then
        if parsed_lines=$(autopilot_parse_projects_from_config_yaml "$config_yaml_file" 2>/dev/null); then
            parse_mode="projects"
        elif parsed_lines=$(autopilot_parse_project_dirs_from_config_yaml "$config_yaml_file" 2>/dev/null); then
            parse_mode="project_dirs"
        fi
    fi

    if [ -n "$parse_mode" ] && [ -n "$parsed_lines" ]; then
        while IFS= read -r line || [ -n "$line" ]; do
            line="${line%$'\r'}"
            [ -n "$line" ] || continue

            if [ "$parse_mode" = "projects" ]; then
                window="${line%%:*}"
                dir="${line#*:}"
                [ "$dir" = "$line" ] && continue
            else
                dir="$line"
                # project_dirs 模式下优先复用 discord_channels 里的 tmux_window 映射，
                # 避免目录名（如 .autopilot）自动推导与真实窗口名（autopilot-dev）不一致。
                window=$(get_tmux_window_for_project_dir "$dir" "$config_yaml_file" 2>/dev/null || true)
                [ -n "$window" ] || window=$(autopilot_derive_window_name_from_path "$dir")
                if [ "${#projects[@]}" -gt 0 ] && _autopilot_project_window_exists "$window" "${projects[@]}"; then
                    local suffix=2
                    local base_window="$window"
                    while [ "${#projects[@]}" -gt 0 ] && _autopilot_project_window_exists "${base_window}-${suffix}" "${projects[@]}"; do
                        suffix=$((suffix + 1))
                    done
                    window="${base_window}-${suffix}"
                fi
            fi

            [ -n "$window" ] || continue
            [ -n "$dir" ] || continue
            projects+=("${window}:${dir}")
        done <<< "$parsed_lines"
    fi

    if [ "${#projects[@]}" -gt 0 ]; then
        AUTOPILOT_PROJECT_SOURCE="config.yaml"
        AUTOPILOT_PROJECT_COUNT="${#projects[@]}"
        printf '%s\n' "${projects[@]}"
        return 0
    fi

    if [ -n "$fallback_conf_file" ] && [ -f "$fallback_conf_file" ]; then
        while IFS= read -r line || [ -n "$line" ]; do
            line="${line%$'\r'}"
            case "$line" in
                ""|\#*)
                    continue
                    ;;
            esac

            window="${line%%:*}"
            dir="${line#*:}"
            [ "$dir" = "$line" ] && continue
            dir="${dir%%:*}"

            [ -n "$window" ] || continue
            [ -n "$dir" ] || continue
            projects+=("${window}:${dir}")
        done < "$fallback_conf_file"
    fi

    if [ "${#projects[@]}" -gt 0 ]; then
        AUTOPILOT_PROJECT_SOURCE="watchdog-projects.conf"
        AUTOPILOT_PROJECT_COUNT="${#projects[@]}"
        printf '%s\n' "${projects[@]}"
        return 0
    fi

    if [ "${#default_projects[@]}" -eq 0 ]; then
        return 1
    fi

    AUTOPILOT_PROJECT_SOURCE="defaults"
    AUTOPILOT_PROJECT_COUNT="${#default_projects[@]}"
    printf '%s\n' "${default_projects[@]}"
    return 0
}

# macOS-compatible timeout (prefers timeout/gtimeout, fallback to background+kill)
_LIB_TIMEOUT_CMD=""
if command -v timeout >/dev/null 2>&1; then
    _LIB_TIMEOUT_CMD="timeout"
elif command -v gtimeout >/dev/null 2>&1; then
    _LIB_TIMEOUT_CMD="gtimeout"
fi

run_with_timeout() {
    local secs="$1"; shift
    if [ -n "$_LIB_TIMEOUT_CMD" ]; then
        "$_LIB_TIMEOUT_CMD" "$secs" "$@"
    else
        "$@" &
        local pid=$!
        (
            sleep "$secs"
            kill "$pid" 2>/dev/null
        ) &
        local watcher=$!
        wait "$pid" 2>/dev/null
        local rc=$?
        kill "$watcher" 2>/dev/null || true
        wait "$watcher" 2>/dev/null || true
        return "$rc"
    fi
}

# Load Telegram config from ~/.autopilot/config.yaml
# Sets: LIB_TG_TOKEN, LIB_TG_CHAT
load_telegram_config() {
    local config_file="${HOME}/.autopilot/config.yaml"
    LIB_TG_TOKEN=$(grep -E '^[[:space:]]*bot_token[[:space:]]*:' "$config_file" 2>/dev/null | awk '{print $2}' | tr -d '"' || true)
    LIB_TG_CHAT=$(grep -E '^[[:space:]]*chat_id[[:space:]]*:' "$config_file" 2>/dev/null | awk '{print $2}' | tr -d '"' || true)
}

# Send a Telegram message (background, non-blocking)
# Usage: send_telegram "message text"
send_telegram() {
    local msg="${1:-}"
    [ -n "$msg" ] || return 0
    if [ -z "${LIB_TG_TOKEN:-}" ] || [ -z "${LIB_TG_CHAT:-}" ]; then
        load_telegram_config
    fi
    if [ -n "${LIB_TG_TOKEN:-}" ] && [ -n "${LIB_TG_CHAT:-}" ]; then
        curl -s -X POST "https://api.telegram.org/bot${LIB_TG_TOKEN}/sendMessage" \
            -d chat_id="${LIB_TG_CHAT}" --data-urlencode "text=${msg}" >/dev/null 2>&1 &
    fi
}

# mkdir-based lock with stale timeout (macOS compatible, no flock)
# Usage: acquire_lock <lock_name> [stale_seconds]
#   lock_name: creates ${LOCK_DIR}/<lock_name>.lock.d
#   stale_seconds: auto-expire after this many seconds (default: 60)
# Requires: LOCK_DIR to be set by the caller
acquire_lock() {
    local lock_name="${1:?acquire_lock: lock_name required}"
    local stale_seconds="${2:-60}"
    local lock_path="${LOCK_DIR:?LOCK_DIR not set}/${lock_name}.lock.d"

    if mkdir "$lock_path" 2>/dev/null; then
        echo "$$" > "${lock_path}/pid"
        return 0
    fi

    # Check for stale lock
    if [ -d "$lock_path" ]; then
        local lock_age
        lock_age=$(( $(now_ts) - $(file_mtime "$lock_path") ))
        if [ "$lock_age" -gt "$stale_seconds" ]; then
            rm -rf "$lock_path" 2>/dev/null || true
            if mkdir "$lock_path" 2>/dev/null; then
                echo "$$" > "${lock_path}/pid"
                return 0
            fi
        fi
    fi
    return 1
}

# Release a mkdir-based lock
# Usage: release_lock <lock_name>
release_lock() {
    local lock_name="${1:?release_lock: lock_name required}"
    rm -rf "${LOCK_DIR:?LOCK_DIR not set}/${lock_name}.lock.d" 2>/dev/null || true
}

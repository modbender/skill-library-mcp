#!/usr/bin/env bash
# OpenSoul CLI - Share your OpenClaw workspace with the community

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$SCRIPT_DIR/scripts"

usage() {
  cat << EOF
OpenSoul - Share your OpenClaw workspace

Usage: opensoul <command> [options]

Commands:
  register          Register with OpenSoul (one-time)
  share             Share your workspace (extract → anonymize → summarize → upload)
  share --preview   Preview what will be shared (no upload)
  share --note "…"  Attach a personal note when sharing
  list              List your shared souls
  delete <id>       Delete a soul you shared
  browse [query]    Browse community souls
  suggest           Get suggestions based on your setup
  import <id>       Import a soul for inspiration
  help              Show this help message

Examples:
  opensoul register
  opensoul share
  opensoul share --preview
  opensoul share --note "My first share!"
  opensoul list
  opensoul delete abc123
  opensoul browse "automation"
  opensoul import abc123

EOF
}

usage_register() {
  cat << EOF
opensoul register - Register with OpenSoul (one-time)

Usage: opensoul register [--handle <handle>] [--name <name>] [--description <desc>]

Without arguments, runs interactively with prompts.
Credentials are saved to ~/.opensoul/credentials.json.
EOF
}

usage_share() {
  cat << EOF
opensoul share - Share your workspace with the community

Usage: opensoul share [options]

Options:
  --preview       Preview what will be shared (no upload)
  --note "text"   Attach a personal note to your shared soul

The pipeline: extract → anonymize → summarize → upload.
Install Ollama + LFM2.5 for richer summaries:
  ollama pull hf.co/LiquidAI/LFM2.5-1.2B-Instruct
EOF
}

usage_browse() {
  cat << EOF
opensoul browse - Browse community souls

Usage: opensoul browse [query] [options]

Options:
  --sort <key>    Sort by: recent, popular, remixed (default: recent)
  --limit <n>     Number of results (default: 10)
  --json          Output raw JSON

Examples:
  opensoul browse                 # Recent souls
  opensoul browse "automation"    # Search
  opensoul browse --sort popular  # By popularity
EOF
}

usage_suggest() {
  cat << EOF
opensoul suggest - Get suggestions based on your setup

Usage: opensoul suggest [--json]

Analyzes your workspace and recommends community souls
that complement your current capabilities.
EOF
}

usage_import() {
  cat << EOF
opensoul import - Import a soul for inspiration

Usage: opensoul import <soul-id>

Downloads the soul's files to ~/.openclaw/workspace/imported/<soul-id>/.
Find soul IDs by browsing: opensoul browse
EOF
}

usage_list() {
  cat << EOF
opensoul list - List your shared souls

Usage: opensoul list [--json]

Shows all souls you've shared, with IDs for deletion.
EOF
}

usage_delete() {
  cat << EOF
opensoul delete - Delete a soul you shared

Usage: opensoul delete <soul-id> [--force]

Options:
  --force    Skip confirmation prompt

Find your soul IDs with: opensoul list
EOF
}

# Check for subcommand-level --help
has_help_flag() {
  for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
      return 0
    fi
  done
  return 1
}

case "$1" in
  register)
    shift
    if has_help_flag "$@"; then usage_register; exit 0; fi
    tsx "$SCRIPTS/register.ts" "$@"
    ;;
  share)
    shift
    if has_help_flag "$@"; then usage_share; exit 0; fi
    # Parse share flags
    PREVIEW=false
    NOTE=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --preview) PREVIEW=true; shift ;;
        --note) NOTE="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    if [[ "$PREVIEW" == "true" ]]; then
      tsx "$SCRIPTS/extract.ts" | tsx "$SCRIPTS/anonymize.ts" | tsx "$SCRIPTS/summarize.ts"
    elif [[ -n "$NOTE" ]]; then
      OPENSOUL_NOTE="$NOTE" tsx "$SCRIPTS/extract.ts" | tsx "$SCRIPTS/anonymize.ts" | tsx "$SCRIPTS/summarize.ts" | OPENSOUL_NOTE="$NOTE" tsx "$SCRIPTS/upload.ts"
    else
      tsx "$SCRIPTS/extract.ts" | tsx "$SCRIPTS/anonymize.ts" | tsx "$SCRIPTS/summarize.ts" | tsx "$SCRIPTS/upload.ts"
    fi
    ;;
  browse)
    shift
    if has_help_flag "$@"; then usage_browse; exit 0; fi
    tsx "$SCRIPTS/browse.ts" "$@"
    ;;
  suggest)
    shift
    if has_help_flag "$@"; then usage_suggest; exit 0; fi
    tsx "$SCRIPTS/extract.ts" | tsx "$SCRIPTS/suggest.ts"
    ;;
  import)
    shift
    if has_help_flag "$@"; then usage_import; exit 0; fi
    tsx "$SCRIPTS/import.ts" "$@"
    ;;
  list)
    shift
    if has_help_flag "$@"; then usage_list; exit 0; fi
    tsx "$SCRIPTS/list.ts" "$@"
    ;;
  delete)
    shift
    if has_help_flag "$@"; then usage_delete; exit 0; fi
    tsx "$SCRIPTS/delete.ts" "$@"
    ;;
  -h|--help|help|"")
    usage
    ;;
  *)
    echo "Unknown command: $1"
    usage
    exit 1
    ;;
esac

#!/usr/bin/env bash
#
# cca-aliases.sh - Short-form command aliases for cursor-cloud-agents
#
# Usage: Source this file in your shell profile:
#   source /path/to/scripts/cca-aliases.sh
#
# Or add to your ~/.bashrc or ~/.zshrc:
#   source ~/.openclaw/workspace/projects/cursor-cloud-agents/scripts/cca-aliases.sh
#
# Then use 'cca' instead of 'cursor-api.sh':
#   cca list              # List all agents
#   cca launch ...        # Launch a new agent
#   cca status <id>       # Get agent status
#
# ============================================================================

# Determine the script directory (works when sourced)
# Validate the path to prevent execution from unexpected locations
_CCA_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"

# Security: Ensure the script directory looks reasonable
if [[ ! -f "${_CCA_SCRIPT_DIR}/cursor-api.sh" ]]; then
    echo "Error: cursor-api.sh not found in ${_CCA_SCRIPT_DIR}" >&2
    echo "Please ensure cca-aliases.sh is sourced from the correct scripts/ directory" >&2
    return 1
fi

# Main cca function - wraps cursor-api.sh
cca() {
    local cmd="${1:-}"

    # Handle case where no arguments provided
    if [[ $# -eq 0 ]]; then
        _cca_help
        return 0
    fi

    shift

    case "$cmd" in
        list)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" list "$@"
            ;;

        launch)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" launch "$@"
            ;;

        status)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" status "$@"
            ;;

        conversation)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" conversation "$@"
            ;;

        followup)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" followup "$@"
            ;;

        stop)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" stop "$@"
            ;;

        delete)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" delete "$@"
            ;;

        models)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" models "$@"
            ;;

        me)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" me "$@"
            ;;

        verify)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" verify "$@"
            ;;

        usage)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" usage "$@"
            ;;

        clear-cache)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" clear-cache "$@"
            ;;

        # Background task commands
        bg-list)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" bg-list "$@"
            ;;

        bg-status)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" bg-status "$@"
            ;;

        bg-logs)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" bg-logs "$@"
            ;;

        # Help
        help|-h|--help)
            _cca_help
            ;;

        # Version
        version|-v|--version)
            echo "cca (cursor-cloud-agents) - Short command wrapper for cursor-api.sh"
            echo "Source: ${_CCA_SCRIPT_DIR}/cca-aliases.sh"
            ;;

        # Unknown command - pass through to cursor-api.sh
        *)
            "${_CCA_SCRIPT_DIR}/cursor-api.sh" "$cmd" "$@"
            ;;
    esac
}

# Help function
_cca_help() {
    cat << 'EOF'
cca - Short commands for cursor-cloud-agents

USAGE:
  cca <command> [options] [args]

COMMANDS:
  list              List all agents
  launch            Launch a new agent
  status <id>       Get agent status
  conversation <id> Get agent conversation
  followup <id>     Send follow-up message
  stop <id>         Stop an agent
  delete <id>       Delete an agent
  models            List available models
  me                Get account info
  verify <repo>     Verify repository access
  usage             Get usage/cost info
  clear-cache       Clear response cache

Background Commands:
  bg-list [--all]   List background tasks
  bg-status <id>    Get background task status
  bg-logs <id>      Show background task logs

EXAMPLES:
  cca list                              # List all agents
  cca launch --repo owner/repo --prompt "Add tests"
  cca status <agent-id>                 # Check status
  cca conversation <agent-id>           # Get conversation
  cca followup <agent-id> --prompt "..." # Send followup
  cca delete <agent-id>                 # Delete agent

For full documentation: cursor-api.sh --help
EOF
}

# Export the function for use in subshells
export -f cca 2>/dev/null || true

echo "cca loaded. Type 'cca help' for usage."

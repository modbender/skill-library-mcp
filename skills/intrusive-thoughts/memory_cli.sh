#!/bin/bash
#
# Memory System CLI Wrapper
#
# Simple command-line interface for the Advanced Multi-Store Memory System.
# Provides easy access to all memory operations with proper argument handling.
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_SCRIPT="$SCRIPT_DIR/memory_system.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage information
usage() {
    echo -e "${BLUE}Advanced Multi-Store Memory System CLI${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}encode${NC} <event> [--emotion <emotion>] [--importance <0-1>]"
    echo "    Store a new episodic memory"
    echo "    Examples:"
    echo "      ./memory_cli.sh encode \"Learned Python decorators\" --emotion happy --importance 0.8"
    echo "      ./memory_cli.sh encode \"Meeting went poorly\" --emotion frustrated --importance 0.6"
    echo ""
    echo -e "  ${GREEN}recall${NC} <query> [--type <type>] [--limit <n>]"
    echo "    Search memories with semantic matching"
    echo "    Types: episodic, semantic, procedural, working, all (default)"
    echo "    Examples:"
    echo "      ./memory_cli.sh recall \"Python learning\" --type episodic --limit 5"
    echo "      ./memory_cli.sh recall \"meeting\" --limit 10"
    echo ""
    echo -e "  ${GREEN}consolidate${NC}"
    echo "    Run memory consolidation (decay old memories, extract patterns)"
    echo "    Example:"
    echo "      ./memory_cli.sh consolidate"
    echo ""
    echo -e "  ${GREEN}stats${NC}"
    echo "    Show comprehensive memory system statistics"
    echo "    Example:"
    echo "      ./memory_cli.sh stats"
    echo ""
    echo -e "  ${GREEN}reflect${NC}"
    echo "    Run meta-cognitive analysis on memory patterns"
    echo "    Example:"
    echo "      ./memory_cli.sh reflect"
    echo ""
    echo -e "  ${GREEN}forget${NC} [--threshold <0-1>]"
    echo "    Remove memories below importance threshold"
    echo "    Example:"
    echo "      ./memory_cli.sh forget --threshold 0.2"
    echo ""
    echo "Emotions: happy, sad, excited, frustrated, curious, proud, anxious, calm, angry, surprised"
    echo "Importance: 0.0 (trivial) to 1.0 (critical), default 0.5"
}

# Error handling
error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Check if Python script exists
if [ ! -f "$MEMORY_SCRIPT" ]; then
    error_exit "Memory system script not found at $MEMORY_SCRIPT"
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    error_exit "python3 is required but not installed"
fi

# Main command processing
case "${1:-help}" in
    "encode")
        if [ -z "$2" ]; then
            error_exit "Event description required for encode command"
        fi
        
        EVENT="$2"
        shift 2
        
        ARGS=("encode" "$EVENT")
        
        # Parse optional arguments
        while [[ $# -gt 0 ]]; do
            case $1 in
                --emotion)
                    if [ -z "$2" ]; then
                        error_exit "--emotion requires a value"
                    fi
                    ARGS+=("--emotion" "$2")
                    shift 2
                    ;;
                --importance)
                    if [ -z "$2" ]; then
                        error_exit "--importance requires a value"
                    fi
                    # Validate importance is a number between 0 and 1
                    if ! [[ "$2" =~ ^[0-1]?(\.[0-9]+)?$ ]]; then
                        error_exit "Importance must be a number between 0 and 1"
                    fi
                    ARGS+=("--importance" "$2")
                    shift 2
                    ;;
                *)
                    error_exit "Unknown option: $1"
                    ;;
            esac
        done
        
        echo -e "${BLUE}Encoding memory...${NC}"
        python3 "$MEMORY_SCRIPT" "${ARGS[@]}"
        ;;
    
    "recall")
        if [ -z "$2" ]; then
            error_exit "Search query required for recall command"
        fi
        
        QUERY="$2"
        shift 2
        
        ARGS=("recall" "$QUERY")
        
        # Parse optional arguments
        while [[ $# -gt 0 ]]; do
            case $1 in
                --type)
                    if [ -z "$2" ]; then
                        error_exit "--type requires a value"
                    fi
                    # Validate type
                    case "$2" in
                        episodic|semantic|procedural|working|all)
                            ARGS+=("--type" "$2")
                            ;;
                        *)
                            error_exit "Invalid type: $2. Must be one of: episodic, semantic, procedural, working, all"
                            ;;
                    esac
                    shift 2
                    ;;
                --limit)
                    if [ -z "$2" ]; then
                        error_exit "--limit requires a value"
                    fi
                    # Validate limit is a positive integer
                    if ! [[ "$2" =~ ^[1-9][0-9]*$ ]]; then
                        error_exit "Limit must be a positive integer"
                    fi
                    ARGS+=("--limit" "$2")
                    shift 2
                    ;;
                *)
                    error_exit "Unknown option: $1"
                    ;;
            esac
        done
        
        echo -e "${BLUE}Searching memories for: \"$QUERY\"${NC}"
        python3 "$MEMORY_SCRIPT" "${ARGS[@]}"
        ;;
    
    "consolidate")
        echo -e "${YELLOW}Running memory consolidation...${NC}"
        echo "This process will:"
        echo "• Apply forgetting curve decay to episodic memories"
        echo "• Remove memories below threshold"
        echo "• Extract semantic patterns from episodes"
        echo "• Update procedural knowledge"
        echo ""
        python3 "$MEMORY_SCRIPT" consolidate
        echo -e "${GREEN}Consolidation complete!${NC}"
        ;;
    
    "stats")
        echo -e "${BLUE}Memory System Statistics${NC}"
        echo "=========================="
        python3 "$MEMORY_SCRIPT" stats
        ;;
    
    "reflect")
        echo -e "${BLUE}Running memory reflection analysis...${NC}"
        echo "Analyzing patterns, emotions, and temporal distributions..."
        echo ""
        python3 "$MEMORY_SCRIPT" reflect
        ;;
    
    "forget")
        shift 1
        
        ARGS=("forget")
        
        # Parse optional arguments
        while [[ $# -gt 0 ]]; do
            case $1 in
                --threshold)
                    if [ -z "$2" ]; then
                        error_exit "--threshold requires a value"
                    fi
                    # Validate threshold is a number between 0 and 1
                    if ! [[ "$2" =~ ^[0-1]?(\.[0-9]+)?$ ]]; then
                        error_exit "Threshold must be a number between 0 and 1"
                    fi
                    ARGS+=("--threshold" "$2")
                    shift 2
                    ;;
                *)
                    error_exit "Unknown option: $1"
                    ;;
            esac
        done
        
        echo -e "${YELLOW}Removing low-importance memories...${NC}"
        python3 "$MEMORY_SCRIPT" "${ARGS[@]}"
        echo -e "${GREEN}Memory cleanup complete!${NC}"
        ;;
    
    "help"|"--help"|"-h"|"")
        usage
        ;;
    
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        usage
        exit 1
        ;;
esac
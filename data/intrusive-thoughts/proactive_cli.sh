#!/bin/bash
#
# Proactive Agent CLI - Command-line interface for the Proactive Agent Protocol
#
# This script provides a convenient interface to the WAL and Working Buffer system.
# All operations are backed by proactive.py.
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROACTIVE_PY="$SCRIPT_DIR/proactive.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
DEFAULT_MOOD="curious"
DEFAULT_PRIORITY="medium"
DEFAULT_CATEGORY="reminder"
DEFAULT_EXPIRES="24"

usage() {
    cat << EOF
${BLUE}Proactive Agent CLI${NC} - WAL and Working Buffer Interface

${YELLOW}WAL (Write-Ahead Log) Commands:${NC}
  log <content> [options]           Log an action/plan/observation
    --type <action|plan|observation|reflection>  (default: action)
    --category <build|explore|social|organize|learn>  (default: explore)
    --mood <mood>                   (default: curious)
    --outcome <success|failure|pending|skipped>  (default: pending)
    --energy <0.0-1.0>              Energy cost (default: 0.0)
    --value <0.0-1.0>               Value generated (default: 0.0)
    --tags <tag1,tag2>              Comma-separated tags
    --related <id1,id2>             Related WAL entry IDs

  search [options]                  Search WAL entries
    --query <text>                  Text search
    --category <category>           Filter by category
    --mood <mood>                   Filter by mood
    --since <7d|1h|2023-01-01>      Time filter
    --limit <number>                Max results (default: 20)

  stats                             Show WAL statistics
  update <entry-id> <outcome>       Update entry outcome

${YELLOW}Buffer Commands:${NC}
  buffer-add <content> [options]    Add item to working buffer
    --priority <high|medium|low>    (default: medium)
    --category <project|reminder|observation|goal>  (default: reminder)
    --expires <hours>               Hours until expiry (default: 24)
    --mood <mood1,mood2>            Relevant moods

  buffer-list [options]             List active buffer items
    --mood <mood>                   Filter by mood relevance
    --priority <priority>           Filter by priority

  buffer-complete <item-id>         Mark buffer item as completed
  buffer-prune                      Remove expired items

${YELLOW}Proactive Commands:${NC}
  suggest [options]                 Get next action suggestions
    --mood <mood>                   Current mood (default: curious)
    --time <morning|day|evening|night>  Time context (auto-detected)

${YELLOW}Examples:${NC}
  ./proactive_cli.sh log "installed ripgrep" --type action --category explore --mood curious
  ./proactive_cli.sh buffer-add "Review PR on intrusive-thoughts" --priority high --expires 48
  ./proactive_cli.sh buffer-list --priority high
  ./proactive_cli.sh suggest --mood hyperfocus
  ./proactive_cli.sh search --category build --since 7d
  ./proactive_cli.sh stats

EOF
}

# Parse command and arguments
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

COMMAND="$1"
shift

# Initialize variables
CONTENT=""
TYPE="action"
CATEGORY="explore"
MOOD="$DEFAULT_MOOD"
OUTCOME="pending"
ENERGY="0.0"
VALUE="0.0"
TAGS=""
RELATED=""
QUERY=""
SINCE=""
LIMIT="20"
PRIORITY="$DEFAULT_PRIORITY"
EXPIRES="$DEFAULT_EXPIRES"
MOOD_LIST=""
TIME=""
ENTRY_ID=""

# Function to call Python module
call_python() {
    python3 "$PROACTIVE_PY" "$@"
}

# Parse command-specific arguments
case "$COMMAND" in
    log)
        if [ $# -eq 0 ]; then
            echo -e "${RED}Error: Content required for log command${NC}"
            echo "Usage: ./proactive_cli.sh log <content> [options]"
            exit 1
        fi
        CONTENT="$1"
        shift
        
        # Parse options
        while [[ $# -gt 0 ]]; do
            case $1 in
                --type) TYPE="$2"; shift 2 ;;
                --category) CATEGORY="$2"; shift 2 ;;
                --mood) MOOD="$2"; shift 2 ;;
                --outcome) OUTCOME="$2"; shift 2 ;;
                --energy) ENERGY="$2"; shift 2 ;;
                --value) VALUE="$2"; shift 2 ;;
                --tags) TAGS="$2"; shift 2 ;;
                --related) RELATED="$2"; shift 2 ;;
                *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
            esac
        done
        
        echo -e "${BLUE}Logging WAL entry...${NC}"
        echo -e "Type: ${YELLOW}$TYPE${NC}, Category: ${YELLOW}$CATEGORY${NC}, Mood: ${YELLOW}$MOOD${NC}"
        echo -e "Content: ${CYAN}$CONTENT${NC}"
        
        # Build Python command
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from proactive import ProactiveAgent

agent = ProactiveAgent()
tags = [tag.strip() for tag in '$TAGS'.split(',') if tag.strip()] if '$TAGS' else None
related = [id.strip() for id in '$RELATED'.split(',') if id.strip()] if '$RELATED' else None

entry_id = agent.wal_log(
    type_='$TYPE',
    category='$CATEGORY', 
    content='$CONTENT',
    mood='$MOOD',
    outcome='$OUTCOME',
    energy_cost=float('$ENERGY'),
    value_generated=float('$VALUE'),
    tags=tags,
    related_to=related
)
print(f'${GREEN}✓ Logged entry: ${CYAN}{entry_id}${NC}')
"
        ;;
        
    search)
        # Parse options
        while [[ $# -gt 0 ]]; do
            case $1 in
                --query) QUERY="$2"; shift 2 ;;
                --category) CATEGORY="$2"; shift 2 ;;
                --mood) MOOD="$2"; shift 2 ;;
                --since) SINCE="$2"; shift 2 ;;
                --limit) LIMIT="$2"; shift 2 ;;
                *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
            esac
        done
        
        echo -e "${BLUE}Searching WAL entries...${NC}"
        
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from proactive import ProactiveAgent

agent = ProactiveAgent()
results = agent.wal_search(
    query='$QUERY' if '$QUERY' else None,
    category='$CATEGORY' if '$CATEGORY' != 'explore' else None,
    mood='$MOOD' if '$MOOD' != '$DEFAULT_MOOD' else None,
    since='$SINCE' if '$SINCE' else None,
    limit=int('$LIMIT')
)

if not results:
    print('${YELLOW}No entries found${NC}')
else:
    print(f'${GREEN}Found {len(results)} entries:${NC}')
    for entry in results:
        timestamp = entry['timestamp'][:19].replace('T', ' ')
        mood_color = '${PURPLE}' if entry.get('mood') else ''
        outcome_color = '${GREEN}' if entry.get('outcome') == 'success' else '${RED}' if entry.get('outcome') == 'failure' else '${YELLOW}'
        print(f\"{timestamp} [{mood_color}{entry.get('mood', 'unknown')}${NC}] [{outcome_color}{entry.get('outcome', 'pending')}${NC}] {entry.get('content', '')}\")
        if entry.get('tags'):
            print(f\"  Tags: ${CYAN}{', '.join(entry['tags'])}${NC}\")
"
        ;;
        
    stats)
        echo -e "${BLUE}Generating WAL statistics...${NC}"
        
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from proactive import ProactiveAgent
import json

agent = ProactiveAgent()
stats = agent.wal_stats()

print('${GREEN}=== WAL Statistics ===${NC}')
print(f'Total entries: ${YELLOW}{stats.get(\"total_entries\", 0)}${NC}')

if 'by_type' in stats:
    print('\n${CYAN}By Type:${NC}')
    for type_, count in stats['by_type'].items():
        print(f'  {type_}: {count}')

if 'by_category' in stats:
    print('\n${CYAN}By Category:${NC}')
    for cat, count in stats['by_category'].items():
        print(f'  {cat}: {count}')

if 'by_outcome' in stats:
    print('\n${CYAN}By Outcome:${NC}')
    for outcome, count in stats['by_outcome'].items():
        print(f'  {outcome}: {count}')

if 'mood_success_rates' in stats and stats['mood_success_rates']:
    print('\n${CYAN}Mood Success Rates:${NC}')
    for mood, rate in sorted(stats['mood_success_rates'].items(), key=lambda x: x[1], reverse=True):
        rate_color = '${GREEN}' if rate >= 0.7 else '${YELLOW}' if rate >= 0.4 else '${RED}'
        print(f'  {mood}: {rate_color}{rate:.0%}${NC}')

if stats.get('most_productive_mood'):
    print(f'\n${GREEN}Most productive mood: ${PURPLE}{stats[\"most_productive_mood\"]}${NC}')

print(f'\nAverage energy cost: ${YELLOW}{stats.get(\"avg_energy_cost\", 0):.2f}${NC}')
print(f'Average value generated: ${YELLOW}{stats.get(\"avg_value_generated\", 0):.2f}${NC}')
"
        ;;
        
    buffer-add)
        if [ $# -eq 0 ]; then
            echo -e "${RED}Error: Content required for buffer-add command${NC}"
            echo "Usage: ./proactive_cli.sh buffer-add <content> [options]"
            exit 1
        fi
        CONTENT="$1"
        shift
        
        # Parse options
        while [[ $# -gt 0 ]]; do
            case $1 in
                --priority) PRIORITY="$2"; shift 2 ;;
                --category) CATEGORY="$2"; shift 2 ;;
                --expires) EXPIRES="$2"; shift 2 ;;
                --mood) MOOD_LIST="$2"; shift 2 ;;
                *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
            esac
        done
        
        echo -e "${BLUE}Adding to buffer...${NC}"
        echo -e "Priority: ${YELLOW}$PRIORITY${NC}, Category: ${YELLOW}$CATEGORY${NC}, Expires: ${YELLOW}${EXPIRES}h${NC}"
        echo -e "Content: ${CYAN}$CONTENT${NC}"
        
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from proactive import ProactiveAgent

agent = ProactiveAgent()
mood_list = [mood.strip() for mood in '$MOOD_LIST'.split(',') if mood.strip()] if '$MOOD_LIST' else None

item_id = agent.buffer_add(
    content='$CONTENT',
    priority='$PRIORITY',
    category='$CATEGORY',
    expires_hours=int('$EXPIRES'),
    mood_relevant=mood_list
)
print(f'${GREEN}✓ Added to buffer: ${CYAN}{item_id}${NC}')
"
        ;;
        
    buffer-list)
        # Parse options
        while [[ $# -gt 0 ]]; do
            case $1 in
                --mood) MOOD="$2"; shift 2 ;;
                --priority) PRIORITY="$2"; shift 2 ;;
                *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
            esac
        done
        
        echo -e "${BLUE}Active buffer items:${NC}"
        
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from proactive import ProactiveAgent
from datetime import datetime

agent = ProactiveAgent()
items = agent.buffer_get(
    mood='$MOOD' if '$MOOD' != '$DEFAULT_MOOD' else None,
    priority='$PRIORITY' if '$PRIORITY' != '$DEFAULT_PRIORITY' else None
)

if not items:
    print('${YELLOW}No active buffer items${NC}')
else:
    for item in items:
        priority_color = '${RED}' if item['priority'] == 'high' else '${YELLOW}' if item['priority'] == 'medium' else '${GREEN}'
        created = datetime.fromisoformat(item['created']).strftime('%m-%d %H:%M')
        expires = datetime.fromisoformat(item['expires']).strftime('%m-%d %H:%M')
        
        print(f\"[{priority_color}{item['priority'].upper()}${NC}] {item['content']}\")
        print(f\"  ID: ${CYAN}{item['id']}${NC} | Created: {created} | Expires: {expires}\")
        if item.get('mood_relevant'):
            print(f\"  Relevant moods: ${PURPLE}{', '.join(item['mood_relevant'])}${NC}\")
        print()
"
        ;;
        
    buffer-complete)
        if [ $# -eq 0 ]; then
            echo -e "${RED}Error: Item ID required for buffer-complete command${NC}"
            echo "Usage: ./proactive_cli.sh buffer-complete <item-id>"
            exit 1
        fi
        ENTRY_ID="$1"
        
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from proactive import ProactiveAgent

agent = ProactiveAgent()
success = agent.buffer_complete('$ENTRY_ID')

if success:
    print('${GREEN}✓ Buffer item completed${NC}')
else:
    print('${RED}✗ Item not found${NC}')
"
        ;;
        
    buffer-prune)
        echo -e "${BLUE}Pruning expired buffer items...${NC}"
        
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from proactive import ProactiveAgent

agent = ProactiveAgent()
pruned = agent.buffer_prune()

if pruned > 0:
    print(f'${GREEN}✓ Pruned {pruned} expired items${NC}')
else:
    print('${YELLOW}No expired items to prune${NC}')
"
        ;;
        
    suggest)
        # Parse options
        while [[ $# -gt 0 ]]; do
            case $1 in
                --mood) MOOD="$2"; shift 2 ;;
                --time) TIME="$2"; shift 2 ;;
                *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
            esac
        done
        
        echo -e "${BLUE}Generating suggestions for mood: ${PURPLE}$MOOD${NC}"
        
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from proactive import ProactiveAgent

agent = ProactiveAgent()
suggestions = agent.suggest_next_action(
    current_mood='$MOOD',
    time_of_day='$TIME' if '$TIME' else None
)

if not suggestions:
    print('${YELLOW}No suggestions available${NC}')
else:
    print('${GREEN}=== Suggested Actions ===${NC}')
    for i, suggestion in enumerate(suggestions, 1):
        priority_color = '${RED}' if suggestion['priority'] >= 80 else '${YELLOW}' if suggestion['priority'] >= 60 else '${GREEN}'
        print(f\"{i}. [{priority_color}P{suggestion['priority']}${NC}] {suggestion['action']}\")
        print(f\"   ${CYAN}→ {suggestion['reasoning']}${NC}\")
        print(f\"   Source: {suggestion['source']}\")
        print()
"
        ;;
        
    update)
        if [ $# -lt 2 ]; then
            echo -e "${RED}Error: Entry ID and outcome required${NC}"
            echo "Usage: ./proactive_cli.sh update <entry-id> <outcome>"
            exit 1
        fi
        ENTRY_ID="$1"
        OUTCOME="$2"
        
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from proactive import ProactiveAgent

agent = ProactiveAgent()
success = agent.wal_update_outcome('$ENTRY_ID', '$OUTCOME')

if success:
    print('${GREEN}✓ Entry outcome updated${NC}')
else:
    print('${RED}✗ Failed to update entry${NC}')
"
        ;;
        
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo -e "Run './proactive_cli.sh' for usage information"
        exit 1
        ;;
esac
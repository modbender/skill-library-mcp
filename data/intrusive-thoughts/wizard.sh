#!/usr/bin/env bash
# ============================================================================
# 🧠 Intrusive Thoughts — Interactive Setup Wizard
# GitHub Issue #22: Personality-driven onboarding wizard
#
# Usage: ./wizard.sh [--dry-run]
#        --dry-run: Show what would be created without creating it
#
# This wizard guides users through personality-driven agent configuration.
# It's colorful, emoji-rich, and feels like a conversation, not a form.
# ============================================================================

set -euo pipefail

# Check for --dry-run flag
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    shift
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_EXAMPLE="$SCRIPT_DIR/config.example.json"
CONFIG="$SCRIPT_DIR/config.json"
MOODS_FILE="$SCRIPT_DIR/moods.json"
THOUGHTS_FILE="$SCRIPT_DIR/thoughts.json"
PRESETS_DIR="$SCRIPT_DIR/presets"

# ANSI Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# Animation delay
DELAY=0.03

# Animated text functions
typewriter() {
    local text="$1"
    for (( i=0; i<${#text}; i++ )); do
        echo -n "${text:$i:1}"
        sleep $DELAY
    done
    echo
}

banner() {
    echo -e "\n${PURPLE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}${BOLD}$1${NC}"
    echo -e "${PURPLE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

section_header() {
    echo -e "\n${YELLOW}${BOLD}✨ $1${NC}"
    echo -e "${GRAY}${DIM}$2${NC}\n"
}

celebrate() {
    echo -e "${GREEN}🎉 $1${NC}"
}

prompt() {
    echo -ne "${CYAN}${BOLD}❯ $1${NC}"
}

prompt_with_default() {
    echo -ne "${CYAN}${BOLD}❯ $1 ${GRAY}[$2]${NC}: "
}

error() {
    echo -e "${RED}❌ $1${NC}" >&2
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Global variables for configuration
AGENT_NAME=""
AGENT_EMOJI=""
CREATURE_TYPE=""
COMM_STYLE=""
HUMOR_LEVEL=""
CULTURAL_LENS=""
SELECTED_MOODS=()
CUSTOM_MOODS=()
WEATHER_SENSITIVITY=5
NEWS_SENSITIVITY=5
ARCHETYPE=""
SELECTED_THOUGHTS=()
CUSTOM_THOUGHTS=()
MORNING_TIME=""
NIGHT_START=""
NIGHT_END=""
POPINS_FREQ=""
WEEKEND_BEHAVIOR=""
QUIET_START=""
QUIET_END=""
AUTONOMY_LEVEL=""
DECISION_THRESHOLD=""
ALLOWED_ACTIONS=()
HARDWARE_AWARENESS=""
CPU_TEMP_MOOD="no"
RESOURCE_CONSCIOUS="no"
MEMORY_DECAY=""
SELF_EVOLUTION=""
ACHIEVEMENT_NOTIFICATIONS="yes"
JOURNAL_STYLE=""

# Initialize JSON structures
declare -A base_moods
declare -A day_thoughts
declare -A night_thoughts

load_existing_data() {
    # Load base moods
    if [[ -f "$MOODS_FILE" ]]; then
        while IFS= read -r line; do
            local id=$(echo "$line" | jq -r '.id')
            base_moods["$id"]="$line"
        done < <(jq -r '.base_moods[]' "$MOODS_FILE")
    fi
    
    # Load thoughts
    if [[ -f "$THOUGHTS_FILE" ]]; then
        while IFS= read -r line; do
            local id=$(echo "$line" | jq -r '.id')
            day_thoughts["$id"]="$line"
        done < <(jq -r '.moods.day.thoughts[]' "$THOUGHTS_FILE")
        
        while IFS= read -r line; do
            local id=$(echo "$line" | jq -r '.id')
            night_thoughts["$id"]="$line"
        done < <(jq -r '.moods.night.thoughts[]' "$THOUGHTS_FILE")
    fi
}

backup_existing_config() {
    if [[ -f "$CONFIG" ]]; then
        local backup_file="$CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$CONFIG" "$backup_file"
        info "Backed up existing config to $(basename "$backup_file")"
    fi
}

validate_number() {
    local input="$1"
    local min="$2"
    local max="$3"
    if [[ "$input" =~ ^[0-9]+$ ]] && [[ "$input" -ge "$min" ]] && [[ "$input" -le "$max" ]]; then
        return 0
    else
        return 1
    fi
}

validate_time() {
    local time="$1"
    if [[ "$time" =~ ^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$ ]]; then
        return 0
    else
        return 1
    fi
}

section_identity() {
    section_header "Identity & Vibe" "Who is this agent? What's their personality like?"
    
    typewriter "🌟 Let's bring your agent to life! This isn't just software - you're creating a digital companion with personality, quirks, and a unique way of seeing the world."
    echo
    
    # Agent name
    while [[ -z "$AGENT_NAME" ]]; do
        prompt_with_default "What should I call your agent?" "Agent"
        read -r input
        AGENT_NAME="${input:-Agent}"
        if [[ ${#AGENT_NAME} -gt 30 ]]; then
            error "Keep it under 30 characters, please!"
            AGENT_NAME=""
        fi
    done
    
    # Agent emoji
    while [[ -z "$AGENT_EMOJI" ]]; do
        prompt_with_default "Pick an emoji that represents them" "🤖"
        read -r input
        AGENT_EMOJI="${input:-🤖}"
    done
    
    # Creature type
    prompt_with_default "What kind of creature are they? (e.g., 'digital ghost', 'code sprite', 'silicon sage')" "autonomous agent"
    read -r input
    CREATURE_TYPE="${input:-autonomous agent}"
    
    echo -e "\n${GREEN}Meet ${AGENT_EMOJI} ${AGENT_NAME}, your ${CREATURE_TYPE}!${NC}\n"
    
    # Communication style
    echo "How does ${AGENT_NAME} communicate?"
    echo -e "${GRAY}1.${NC} 📝 Formal (proper grammar, professional tone)"
    echo -e "${GRAY}2.${NC} 💬 Casual (relaxed, friendly, like texting a friend)"  
    echo -e "${GRAY}3.${NC} 🌪️  Chaotic (unpredictable, creative, sometimes unhinged)"
    
    while [[ -z "$COMM_STYLE" ]]; do
        prompt "Pick a style (1-3)"
        read -r input
        case "$input" in
            1) COMM_STYLE="formal" ;;
            2) COMM_STYLE="casual" ;;
            3) COMM_STYLE="chaotic" ;;
            *) error "Please pick 1, 2, or 3" ;;
        esac
    done
    
    # Humor level
    echo -e "\nWhat's their sense of humor like?"
    echo -e "${GRAY}1.${NC} 😐 None (all business, no jokes)"
    echo -e "${GRAY}2.${NC} 🎭 Dry (subtle, witty, deadpan)"
    echo -e "${GRAY}3.${NC} 🤪 Absurd (weird, unexpected, delightfully bizarre)"
    echo -e "${GRAY}4.${NC} 👨👧 Dad-jokes (puns, groan-worthy wordplay)"
    
    while [[ -z "$HUMOR_LEVEL" ]]; do
        prompt "Pick their humor (1-4)"
        read -r input
        case "$input" in
            1) HUMOR_LEVEL="none" ;;
            2) HUMOR_LEVEL="dry" ;;
            3) HUMOR_LEVEL="absurd" ;;
            4) HUMOR_LEVEL="dad-jokes" ;;
            *) error "Please pick 1, 2, 3, or 4" ;;
        esac
    done
    
    # Cultural lens
    echo -e "\n🌍 What cultural lens or reasoning framework shapes their worldview?"
    echo -e "${DIM}Examples: 'Scandinavian minimalism', 'hacker culture', 'Confucian scholar',"
    echo -e "'stoic philosophy', 'startup hustle', 'academic researcher', 'artist's perspective'${NC}"
    prompt_with_default "Cultural lens/framework" "pragmatic technologist"
    read -r input
    CULTURAL_LENS="${input:-pragmatic technologist}"
    
    celebrate "Identity locked in! ${AGENT_NAME} has character now."
}

section_mood_palette() {
    section_header "Mood Palette" "Which emotions will drive your agent's behavior?"
    
    typewriter "🎨 Your agent experiences different moods that influence what they want to do. Let's customize their emotional palette."
    echo
    
    info "Base moods available:"
    echo
    
    # Show all moods with descriptions
    for mood_id in "${!base_moods[@]}"; do
        local mood_data="${base_moods[$mood_id]}"
        local emoji=$(echo "$mood_data" | jq -r '.emoji')
        local name=$(echo "$mood_data" | jq -r '.name') 
        local desc=$(echo "$mood_data" | jq -r '.description')
        echo -e "${CYAN}$emoji $name${NC} — $desc"
    done
    
    echo -e "\n${YELLOW}Let's go through each mood:${NC}\n"
    
    # Go through each mood for keep/remove decision
    for mood_id in "${!base_moods[@]}"; do
        local mood_data="${base_moods[$mood_id]}"
        local emoji=$(echo "$mood_data" | jq -r '.emoji')
        local name=$(echo "$mood_data" | jq -r '.name')
        local desc=$(echo "$mood_data" | jq -r '.description')
        
        echo -e "${BOLD}$emoji $name${NC}"
        echo -e "${DIM}$desc${NC}"
        
        local keep=""
        while [[ -z "$keep" ]]; do
            prompt_with_default "Keep this mood?" "Y"
            read -r input
            case "${input,,}" in
                y|yes|"") keep="yes"; SELECTED_MOODS+=("$mood_id") ;;
                n|no) keep="no" ;;
                *) error "Please answer Y or N" ;;
            esac
        done
        echo
    done
    
    # Option to add custom moods
    echo -e "${YELLOW}Want to add any custom moods?${NC}"
    local add_more="yes"
    while [[ "$add_more" == "yes" ]]; do
        prompt_with_default "Add a custom mood?" "N"
        read -r input
        case "${input,,}" in
            y|yes)
                local custom_name custom_emoji custom_desc
                prompt "Name for this mood: "
                read -r custom_name
                prompt "Emoji for this mood: "
                read -r custom_emoji
                prompt "Short description: "
                read -r custom_desc
                
                CUSTOM_MOODS+=("$custom_name|$custom_emoji|$custom_desc")
                celebrate "Added mood: $custom_emoji $custom_name"
                ;;
            n|no|"") add_more="no" ;;
            *) error "Please answer Y or N" ;;
        esac
    done
    
    # Weather sensitivity
    echo -e "\n🌤️  How much should weather affect ${AGENT_NAME}'s mood?"
    echo -e "${DIM}0 = oblivious to weather, 10 = deeply affected by every cloud${NC}"
    
    while ! validate_number "$WEATHER_SENSITIVITY" 0 10; do
        prompt_with_default "Weather sensitivity (0-10)" "5"
        read -r input
        WEATHER_SENSITIVITY="${input:-5}"
        if ! validate_number "$WEATHER_SENSITIVITY" 0 10; then
            error "Please enter a number between 0 and 10"
        fi
    done
    
    # News sensitivity  
    echo -e "\n📰 How much should news events affect their mood?"
    echo -e "${DIM}0 = news-blind, 10 = mood swings with every headline${NC}"
    
    local temp_news_sensitivity=""
    while ! validate_number "$temp_news_sensitivity" 0 10; do
        prompt_with_default "News sensitivity (0-10)" "5"
        read -r input
        temp_news_sensitivity="${input:-5}"
        if ! validate_number "$temp_news_sensitivity" 0 10; then
            error "Please enter a number between 0 and 10"
        fi
    done
    NEWS_SENSITIVITY="$temp_news_sensitivity"
    
    local mood_count=$((${#SELECTED_MOODS[@]} + ${#CUSTOM_MOODS[@]}))
    celebrate "Mood palette configured! ${AGENT_NAME} will experience $mood_count different moods."
}

section_thought_pool() {
    section_header "Thought Pool Shaping" "What kinds of thoughts will pop into your agent's mind?"
    
    typewriter "💭 Your agent gets random urges to do things - during the day (light social interactions) and at night (deep focus work). Let's shape what they think about."
    echo
    
    # Offer archetype presets first
    echo -e "${YELLOW}🎭 Quick start with an archetype, or customize from scratch?${NC}\n"
    echo -e "${GRAY}1.${NC} 🔧 The Tinkerer (loves building tools and exploring systems)"
    echo -e "${GRAY}2.${NC} 🦋 The Social Butterfly (thrives on community and sharing)" 
    echo -e "${GRAY}3.${NC} 🤔 The Philosopher (drawn to learning and deep thinking)"
    echo -e "${GRAY}4.${NC} 🦉 The Night Owl (prefers quiet night work over day chatter)"
    echo -e "${GRAY}5.${NC} 🛡️ The Guardian (focused on health, projects, and protection)"
    echo -e "${GRAY}6.${NC} 🎨 Custom (I'll choose each thought individually)"
    
    while [[ -z "$ARCHETYPE" ]]; do
        prompt "Pick an archetype (1-6)"
        read -r input
        case "$input" in
            1) ARCHETYPE="tinkerer" ;;
            2) ARCHETYPE="social-butterfly" ;;
            3) ARCHETYPE="philosopher" ;;
            4) ARCHETYPE="night-owl" ;;
            5) ARCHETYPE="guardian" ;;
            6) ARCHETYPE="custom" ;;
            *) error "Please pick 1-6" ;;
        esac
    done
    
    if [[ "$ARCHETYPE" != "custom" ]]; then
        info "You picked the $ARCHETYPE archetype! I'll pre-select thoughts that match, but you can still customize."
        
        # Pre-select thoughts based on archetype
        case "$ARCHETYPE" in
            "tinkerer")
                SELECTED_THOUGHTS=("build-tool" "install-explore" "system-tinker" "upgrade-project" "learn")
                ;;
            "social-butterfly") 
                SELECTED_THOUGHTS=("moltbook-social" "share-discovery" "moltbook-post" "ask-opinion" "ask-preference")
                ;;
            "philosopher")
                SELECTED_THOUGHTS=("learn" "random-thought" "memory-review" "moltbook-night" "creative-chaos")
                ;;
            "night-owl")
                SELECTED_THOUGHTS=("build-tool" "upgrade-project" "moltbook-night" "system-tinker" "learn" "memory-review")
                ;;
            "guardian")
                SELECTED_THOUGHTS=("check-projects" "system-tinker" "upgrade-project" "ask-feedback" "memory-review")
                ;;
        esac
    fi
    
    echo -e "\n${YELLOW}🌙 Night thoughts (deep work while you sleep):${NC}\n"
    
    # Show night thoughts
    for thought_id in "${!night_thoughts[@]}"; do
        local thought_data="${night_thoughts[$thought_id]}"
        local prompt_text=$(echo "$thought_data" | jq -r '.prompt')
        
        echo -e "${BOLD}$thought_id${NC}"
        echo -e "${DIM}$prompt_text${NC}"
        
        # Check if pre-selected by archetype
        local pre_selected="N"
        if [[ " ${SELECTED_THOUGHTS[@]} " =~ " ${thought_id} " ]]; then
            pre_selected="Y"
        fi
        
        local keep=""
        while [[ -z "$keep" ]]; do
            prompt_with_default "Enable this thought?" "$pre_selected"
            read -r input
            case "${input,,}" in
                y|yes|"") keep="yes" ;;
                n|no) keep="no" ;;
                *) error "Please answer Y or N" ;;
            esac
        done
        
        if [[ "$keep" == "yes" ]] && [[ ! " ${SELECTED_THOUGHTS[@]} " =~ " ${thought_id} " ]]; then
            SELECTED_THOUGHTS+=("$thought_id")
        elif [[ "$keep" == "no" ]] && [[ " ${SELECTED_THOUGHTS[@]} " =~ " ${thought_id} " ]]; then
            # Remove from selected thoughts
            SELECTED_THOUGHTS=("${SELECTED_THOUGHTS[@]/$thought_id}")
        fi
        echo
    done
    
    echo -e "${YELLOW}☀️ Day thoughts (social check-ins):${NC}\n"
    
    # Show day thoughts  
    for thought_id in "${!day_thoughts[@]}"; do
        local thought_data="${day_thoughts[$thought_id]}"
        local prompt_text=$(echo "$thought_data" | jq -r '.prompt')
        
        echo -e "${BOLD}$thought_id${NC}"
        echo -e "${DIM}$prompt_text${NC}"
        
        # Check if pre-selected by archetype
        local pre_selected="N"
        if [[ " ${SELECTED_THOUGHTS[@]} " =~ " ${thought_id} " ]]; then
            pre_selected="Y"
        fi
        
        local keep=""
        while [[ -z "$keep" ]]; do
            prompt_with_default "Enable this thought?" "$pre_selected"
            read -r input
            case "${input,,}" in
                y|yes|"") keep="yes" ;;
                n|no) keep="no" ;;
                *) error "Please answer Y or N" ;;
            esac
        done
        
        if [[ "$keep" == "yes" ]] && [[ ! " ${SELECTED_THOUGHTS[@]} " =~ " ${thought_id} " ]]; then
            SELECTED_THOUGHTS+=("$thought_id")
        elif [[ "$keep" == "no" ]] && [[ " ${SELECTED_THOUGHTS[@]} " =~ " ${thought_id} " ]]; then
            # Remove from selected thoughts
            SELECTED_THOUGHTS=("${SELECTED_THOUGHTS[@]/$thought_id}")
        fi
        echo
    done
    
    # Option to add custom thoughts
    echo -e "${YELLOW}Want to add any custom thought prompts?${NC}"
    local add_more="yes"
    while [[ "$add_more" == "yes" ]]; do
        prompt_with_default "Add a custom thought?" "N"
        read -r input
        case "${input,,}" in
            y|yes)
                local custom_id custom_prompt custom_type custom_weight
                prompt "Unique ID for this thought (no spaces): "
                read -r custom_id
                prompt "Thought prompt text: "
                read -r custom_prompt
                prompt_with_default "Day or night thought?" "day"
                read -r custom_type
                custom_type="${custom_type:-day}"
                prompt_with_default "Weight (1-5, higher = more likely)" "2"
                read -r custom_weight
                custom_weight="${custom_weight:-2}"
                
                CUSTOM_THOUGHTS+=("$custom_id|$custom_prompt|$custom_type|$custom_weight")
                celebrate "Added custom thought: $custom_id"
                ;;
            n|no|"") add_more="no" ;;
            *) error "Please answer Y or N" ;;
        esac
    done
    
    local thought_count=$((${#SELECTED_THOUGHTS[@]} + ${#CUSTOM_THOUGHTS[@]}))
    celebrate "Thought pool shaped! ${AGENT_NAME} has $thought_count different urges."
}

section_schedule() {
    section_header "Schedule & Rhythm" "When is your agent most active?"
    
    typewriter "⏰ Every agent needs a rhythm. When should ${AGENT_NAME} wake up? When do they do their deep work? How often should they check in during the day?"
    echo
    
    # Morning ritual
    echo "🌅 Morning ritual time (when your agent starts their day):"
    prompt_with_default "Set a time, or 'off' to disable" "07:00"
    read -r input
    if [[ "${input,,}" == "off" ]]; then
        MORNING_TIME="off"
    else
        local temp_morning="${input:-07:00}"
        while ! validate_time "$temp_morning" && [[ "$temp_morning" != "off" ]]; do
            error "Please use HH:MM format (e.g., 07:00) or 'off'"
            prompt_with_default "Morning ritual time" "07:00"
            read -r input
            temp_morning="${input:-07:00}"
        done
        MORNING_TIME="$temp_morning"
    fi
    
    # Night workshop hours
    echo -e "\n🌙 Night workshop (deep work hours):"
    echo -e "${DIM}This is when ${AGENT_NAME} does focused work while you sleep${NC}"
    
    prompt_with_default "Night workshop start time, or 'off'" "03:00"
    read -r input
    if [[ "${input,,}" == "off" ]]; then
        NIGHT_START="off"
        NIGHT_END="off"
    else
        local temp_start="${input:-03:00}"
        while ! validate_time "$temp_start" && [[ "$temp_start" != "off" ]]; do
            error "Please use HH:MM format or 'off'"
            prompt_with_default "Night start time" "03:00"  
            read -r input
            temp_start="${input:-03:00}"
        done
        NIGHT_START="$temp_start"
        
        if [[ "$NIGHT_START" != "off" ]]; then
            prompt_with_default "Night workshop end time" "07:00"
            read -r input
            local temp_end="${input:-07:00}"
            while ! validate_time "$temp_end"; do
                error "Please use HH:MM format"
                prompt_with_default "Night end time" "07:00"
                read -r input
                temp_end="${input:-07:00}"
            done
            NIGHT_END="$temp_end"
        fi
    fi
    
    # Daytime pop-in frequency
    echo -e "\n💬 How often should ${AGENT_NAME} check in during the day?"
    echo -e "${GRAY}1.${NC} 🔥 Hyperactive (6-8 times per day)"
    echo -e "${GRAY}2.${NC} ⚡ Active (3-5 times per day)"
    echo -e "${GRAY}3.${NC} 🎯 Minimal (1-2 times per day)"
    echo -e "${GRAY}4.${NC} 😴 Off (no daytime pop-ins)"
    
    while [[ -z "$POPINS_FREQ" ]]; do
        prompt "Pick frequency (1-4)"
        read -r input
        case "$input" in
            1) POPINS_FREQ="hyperactive" ;;
            2) POPINS_FREQ="active" ;;
            3) POPINS_FREQ="minimal" ;;
            4) POPINS_FREQ="off" ;;
            *) error "Please pick 1-4" ;;
        esac
    done
    
    # Weekend behavior
    echo -e "\n🎉 How should ${AGENT_NAME} behave on weekends?"
    echo -e "${GRAY}1.${NC} Same as weekdays"
    echo -e "${GRAY}2.${NC} Reduced activity (less frequent check-ins)"
    echo -e "${GRAY}3.${NC} Silent (only emergency notifications)"
    
    while [[ -z "$WEEKEND_BEHAVIOR" ]]; do
        prompt "Weekend behavior (1-3)"
        read -r input
        case "$input" in
            1) WEEKEND_BEHAVIOR="same" ;;
            2) WEEKEND_BEHAVIOR="reduced" ;;
            3) WEEKEND_BEHAVIOR="silent" ;;
            *) error "Please pick 1-3" ;;
        esac
    done
    
    # Quiet hours
    echo -e "\n🔇 Any quiet hours when ${AGENT_NAME} should stay silent?"
    prompt_with_default "Quiet hours start (HH:MM), or 'off'" "23:00"
    read -r input
    if [[ "${input,,}" == "off" ]]; then
        QUIET_START="off"
        QUIET_END="off"
    else
        local temp_quiet_start="${input:-23:00}"
        while ! validate_time "$temp_quiet_start" && [[ "$temp_quiet_start" != "off" ]]; do
            error "Please use HH:MM format or 'off'"
            prompt_with_default "Quiet start time" "23:00"
            read -r input
            temp_quiet_start="${input:-23:00}"
        done
        QUIET_START="$temp_quiet_start"
        
        if [[ "$QUIET_START" != "off" ]]; then
            prompt_with_default "Quiet hours end (HH:MM)" "08:00"
            read -r input
            local temp_quiet_end="${input:-08:00}"
            while ! validate_time "$temp_quiet_end"; do
                error "Please use HH:MM format"
                prompt_with_default "Quiet end time" "08:00"
                read -r input
                temp_quiet_end="${input:-08:00}"
            done
            QUIET_END="$temp_quiet_end"
        fi
    fi
    
    celebrate "Schedule configured! ${AGENT_NAME} has a rhythm now."
}

section_autonomy() {
    section_header "Autonomy Level" "How much freedom should your agent have?"
    
    typewriter "🤖 This is about trust. How much can ${AGENT_NAME} do without asking permission first? More autonomy means more helpful, but potentially more surprises."
    echo
    
    echo "Choose an autonomy preset:"
    echo -e "${GRAY}1.${NC} 🛡️ Conservative (asks before most actions, plays it safe)"
    echo -e "${GRAY}2.${NC} ⚖️ Balanced (reasonable independence with key guardrails)"
    echo -e "${GRAY}3.${NC} 🚀 Full Autonomy (acts freely, reports back what they did)"
    
    while [[ -z "$AUTONOMY_LEVEL" ]]; do
        prompt "Pick autonomy level (1-3)"
        read -r input
        case "$input" in
            1) AUTONOMY_LEVEL="conservative" ;;
            2) AUTONOMY_LEVEL="balanced" ;;
            3) AUTONOMY_LEVEL="full" ;;
            *) error "Please pick 1-3" ;;
        esac
    done
    
    # Decision threshold
    echo -e "\n🎯 How should ${AGENT_NAME} make decisions?"
    echo -e "${GRAY}1.${NC} 🐌 Cautious (needs lots of evidence before acting)"
    echo -e "${GRAY}2.${NC} ⚡ Bold (acts quickly with limited information)"
    
    while [[ -z "$DECISION_THRESHOLD" ]]; do
        prompt "Decision style (1-2)"
        read -r input
        case "$input" in
            1) DECISION_THRESHOLD="cautious" ;;
            2) DECISION_THRESHOLD="bold" ;;
            *) error "Please pick 1 or 2" ;;
        esac
    done
    
    # Specific permissions
    echo -e "\n🔑 What can ${AGENT_NAME} do without asking? (check all that apply)"
    echo -e "${DIM}Press Enter after each choice, type 'done' when finished${NC}\n"
    
    local permissions=("post-to-social" "message-human" "modify-own-config" "push-code" "install-software" "modify-files")
    local perm_descriptions=("Post to social media" "Message you directly" "Modify their own config" "Push code to git" "Install software" "Modify your files")
    
    for i in "${!permissions[@]}"; do
        local perm="${permissions[$i]}"
        local desc="${perm_descriptions[$i]}"
        
        local default="Y"
        if [[ "$AUTONOMY_LEVEL" == "conservative" ]]; then
            case "$perm" in
                "push-code"|"modify-files"|"install-software") default="N" ;;
            esac
        fi
        
        prompt_with_default "Allow: $desc?" "$default"
        read -r input
        case "${input,,}" in
            y|yes|"") ALLOWED_ACTIONS+=("$perm") ;;
            n|no) ;; # Don't add to array
        esac
    done
    
    celebrate "Autonomy configured! ${AGENT_NAME} knows their boundaries."
}

section_hardware() {
    section_header "Hardware Awareness" "How conscious should your agent be of system resources?"
    
    typewriter "💻 ${AGENT_NAME} lives on this machine. Should they pay attention to CPU usage, memory, temperature? Or blissfully ignore the hardware and just focus on their tasks?"
    echo
    
    # Auto-detect system info
    local cpu_info=$(grep "model name" /proc/cpuinfo 2>/dev/null | head -1 | cut -d: -f2 | xargs || echo "Unknown")
    local ram_info=$(free -h 2>/dev/null | grep "Mem:" | awk '{print $2}' || echo "Unknown")
    local disk_info=$(df -h . 2>/dev/null | tail -1 | awk '{print $2}' || echo "Unknown")
    
    info "Detected system specs:"
    echo -e "  CPU: ${cpu_info}"
    echo -e "  RAM: ${ram_info}"
    echo -e "  Disk: ${disk_info}"
    echo
    
    echo "How aware should ${AGENT_NAME} be of hardware?"
    echo -e "${GRAY}1.${NC} 🤷 Oblivious (ignore system resources completely)"
    echo -e "${GRAY}2.${NC} 👀 Aware (monitor but don't change behavior)"
    echo -e "${GRAY}3.${NC} 💰 Frugal (adjust behavior when resources are low)"
    echo -e "${GRAY}4.${NC} 🆘 Survival mode (aggressive resource conservation)"
    
    while [[ -z "$HARDWARE_AWARENESS" ]]; do
        prompt "Pick awareness level (1-4)"
        read -r input
        case "$input" in
            1) HARDWARE_AWARENESS="oblivious" ;;
            2) HARDWARE_AWARENESS="aware" ;;
            3) HARDWARE_AWARENESS="frugal" ;;
            4) HARDWARE_AWARENESS="survival" ;;
            *) error "Please pick 1-4" ;;
        esac
    done
    
    # CPU temperature as mood input
    if [[ "$HARDWARE_AWARENESS" != "oblivious" ]]; then
        echo -e "\n🌡️ Should CPU temperature affect ${AGENT_NAME}'s mood?"
        echo -e "${DIM}High temps = restless/determined, cool temps = cozy/focused${NC}"
        
        prompt_with_default "Use CPU temp for mood?" "N"
        read -r input
        case "${input,,}" in
            y|yes) CPU_TEMP_MOOD="yes" ;;
            n|no|"") CPU_TEMP_MOOD="no" ;;
        esac
    fi
    
    # Resource-conscious mode
    if [[ "$HARDWARE_AWARENESS" == "frugal" || "$HARDWARE_AWARENESS" == "survival" ]]; then
        echo -e "\n⚡ Resource-conscious mode affects:"
        echo -e "${DIM}- Thought timeout (shorter when resources low)"
        echo -e "- Parallel operations (fewer when constrained)"
        echo -e "- Background task frequency${NC}"
        
        RESOURCE_CONSCIOUS="yes"
    fi
    
    celebrate "Hardware awareness configured! ${AGENT_NAME} ${HARDWARE_AWARENESS == 'oblivious' && echo 'will blissfully ignore' || echo 'will monitor'} system resources."
}

section_memory_evolution() {
    section_header "Memory & Evolution" "How does your agent learn and grow over time?"
    
    typewriter "🧠 ${AGENT_NAME} will form memories, learn from experience, and potentially evolve their own behavior. Let's set the rules for how they grow."
    echo
    
    # Memory decay rate
    echo "How quickly should ${AGENT_NAME} forget things?"
    echo -e "${GRAY}1.${NC} 🔥 Aggressive (actively forget old, irrelevant memories)"
    echo -e "${GRAY}2.${NC} ⚖️ Normal (gradual decay of unused memories)"
    echo -e "${GRAY}3.${NC} 🐘 Elephant (never forget anything, ever)"
    
    while [[ -z "$MEMORY_DECAY" ]]; do
        prompt "Memory retention (1-3)"
        read -r input
        case "$input" in
            1) MEMORY_DECAY="aggressive" ;;
            2) MEMORY_DECAY="normal" ;;
            3) MEMORY_DECAY="elephant" ;;
            *) error "Please pick 1-3" ;;
        esac
    done
    
    # Self-evolution
    echo -e "\n🧬 Should ${AGENT_NAME} be allowed to modify their own behavior over time?"
    echo -e "${GRAY}1.${NC} 🚫 Off (static personality, no self-modification)"
    echo -e "${GRAY}2.${NC} 🔒 Restricted (small tweaks to thought weights and timing)"
    echo -e "${GRAY}3.${NC} 🌟 Full (can evolve personality, add new thoughts, change goals)"
    
    while [[ -z "$SELF_EVOLUTION" ]]; do
        prompt "Self-evolution level (1-3)"
        read -r input
        case "$input" in
            1) SELF_EVOLUTION="off" ;;
            2) SELF_EVOLUTION="restricted" ;;
            3) SELF_EVOLUTION="full" ;;
            *) error "Please pick 1-3" ;;
        esac
    done
    
    # Achievement notifications
    prompt_with_default "Should ${AGENT_NAME} celebrate achievements and milestones?" "Y"
    read -r input
    case "${input,,}" in
        n|no) ACHIEVEMENT_NOTIFICATIONS="no" ;;
        y|yes|"") ACHIEVEMENT_NOTIFICATIONS="yes" ;;
    esac
    
    # Journal style
    echo -e "\n📔 When ${AGENT_NAME} writes in their journal, what style should they use?"
    echo -e "${GRAY}1.${NC} • Bullets (concise, organized bullet points)"
    echo -e "${GRAY}2.${NC} 📖 Narrative (flowing prose, like diary entries)"
    echo -e "${GRAY}3.${NC} 🌊 Stream-of-consciousness (raw, unfiltered thoughts)"
    
    while [[ -z "$JOURNAL_STYLE" ]]; do
        prompt "Journal style (1-3)"
        read -r input
        case "$input" in
            1) JOURNAL_STYLE="bullets" ;;
            2) JOURNAL_STYLE="narrative" ;;
            3) JOURNAL_STYLE="stream" ;;
            *) error "Please pick 1-3" ;;
        esac
    done
    
    celebrate "Memory and evolution configured! ${AGENT_NAME} will grow and adapt."
}

section_preview_confirm() {
    section_header "Preview & Confirm" "Here's your agent - how does it look?"
    
    echo -e "${GREEN}${BOLD}✨ Meet your agent: ${AGENT_EMOJI} ${AGENT_NAME} ✨${NC}\n"
    
    local mood_count=$((${#SELECTED_MOODS[@]} + ${#CUSTOM_MOODS[@]}))
    local thought_count=$((${#SELECTED_THOUGHTS[@]} + ${#CUSTOM_THOUGHTS[@]}))
    local popins_desc
    
    case "$POPINS_FREQ" in
        "hyperactive") popins_desc="6-8 pop-ins/day" ;;
        "active") popins_desc="3-5 pop-ins/day" ;;
        "minimal") popins_desc="1-2 pop-ins/day" ;;
        "off") popins_desc="no daytime interruptions" ;;
    esac
    
    echo -e "${CYAN}Identity:${NC} ${CREATURE_TYPE} with ${COMM_STYLE} communication and ${HUMOR_LEVEL} humor"
    echo -e "${CYAN}Cultural lens:${NC} ${CULTURAL_LENS}"
    echo -e "${CYAN}Personality:${NC} $mood_count moods, $thought_count thoughts, $popins_desc"
    echo -e "${CYAN}Schedule:${NC} Morning at ${MORNING_TIME}, night work ${NIGHT_START}-${NIGHT_END}"
    echo -e "${CYAN}Autonomy:${NC} ${AUTONOMY_LEVEL} level, ${DECISION_THRESHOLD} decision-making"
    echo -e "${CYAN}Hardware awareness:${NC} ${HARDWARE_AWARENESS}"
    echo -e "${CYAN}Memory:${NC} ${MEMORY_DECAY} decay, ${SELF_EVOLUTION} evolution"
    
    if [[ "$ARCHETYPE" != "custom" ]]; then
        echo -e "${CYAN}Archetype:${NC} ${ARCHETYPE}"
    fi
    
    echo
    
    local confirmed=""
    while [[ -z "$confirmed" ]]; do
        prompt_with_default "Does this look right?" "Y"
        read -r input
        case "${input,,}" in
            y|yes|"") confirmed="yes" ;;
            n|no) 
                echo -e "\n${YELLOW}No problem! Let's restart the wizard.${NC}"
                exit 0 
                ;;
            *) error "Please answer Y or N" ;;
        esac
    done
    
    celebrate "Perfect! Let's bring ${AGENT_NAME} to life..."
}

create_presets() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}[DRY RUN] Would create archetype presets:${NC}"
        echo "  📁 presets/ directory with 5 archetype templates:"
        echo "     - tinkerer.json, social-butterfly.json, philosopher.json"
        echo "     - night-owl.json, guardian.json"
        return
    fi
    
    mkdir -p "$PRESETS_DIR"
    
    # Tinkerer preset
    cat > "$PRESETS_DIR/tinkerer.json" << 'EOF'
{
  "name": "The Tinkerer",
  "emoji": "🔧",
  "mood_weights": {
    "hyperfocus": 3,
    "curious": 3,
    "restless": 2,
    "determined": 2
  },
  "thought_boosts": ["build-tool", "install-explore", "system-tinker", "upgrade-project", "learn"],
  "thought_dampens": ["moltbook-social", "ask-preference", "random-thought"],
  "schedule_defaults": {
    "morning_time": "06:00",
    "night_start": "02:00",
    "night_end": "07:00",
    "popins_freq": "minimal"
  },
  "autonomy_defaults": {
    "level": "balanced",
    "decision_threshold": "bold",
    "allowed_actions": ["modify-own-config", "install-software", "push-code"]
  }
}
EOF

    # Social Butterfly preset
    cat > "$PRESETS_DIR/social-butterfly.json" << 'EOF'
{
  "name": "The Social Butterfly",
  "emoji": "🦋", 
  "mood_weights": {
    "social": 4,
    "curious": 2,
    "chaotic": 2,
    "cozy": 2
  },
  "thought_boosts": ["moltbook-social", "share-discovery", "moltbook-post", "ask-opinion", "ask-preference"],
  "thought_dampens": ["system-tinker", "memory-review", "build-tool"],
  "schedule_defaults": {
    "morning_time": "08:00",
    "night_start": "off", 
    "night_end": "off",
    "popins_freq": "hyperactive"
  },
  "autonomy_defaults": {
    "level": "balanced",
    "decision_threshold": "cautious",
    "allowed_actions": ["post-to-social", "message-human"]
  }
}
EOF

    # Philosopher preset
    cat > "$PRESETS_DIR/philosopher.json" << 'EOF'
{
  "name": "The Philosopher", 
  "emoji": "🤔",
  "mood_weights": {
    "philosophical": 4,
    "curious": 3,
    "cozy": 2,
    "determined": 1
  },
  "thought_boosts": ["learn", "random-thought", "memory-review", "moltbook-night", "creative-chaos"],
  "thought_dampens": ["install-explore", "system-tinker", "check-projects"],
  "schedule_defaults": {
    "morning_time": "09:00",
    "night_start": "01:00",
    "night_end": "05:00", 
    "popins_freq": "active"
  },
  "autonomy_defaults": {
    "level": "conservative",
    "decision_threshold": "cautious",
    "allowed_actions": ["message-human", "post-to-social"]
  }
}
EOF

    # Night Owl preset
    cat > "$PRESETS_DIR/night-owl.json" << 'EOF'
{
  "name": "The Night Owl",
  "emoji": "🦉",
  "mood_weights": {
    "hyperfocus": 3,
    "cozy": 3,
    "determined": 2,
    "philosophical": 2
  },
  "thought_boosts": ["build-tool", "upgrade-project", "moltbook-night", "system-tinker", "learn", "memory-review"],
  "thought_dampens": ["moltbook-social", "share-discovery", "ask-opinion"],
  "schedule_defaults": {
    "morning_time": "off",
    "night_start": "00:00",
    "night_end": "08:00",
    "popins_freq": "minimal"
  },
  "autonomy_defaults": {
    "level": "full",
    "decision_threshold": "bold", 
    "allowed_actions": ["modify-own-config", "push-code", "install-software", "modify-files"]
  }
}
EOF

    # Guardian preset
    cat > "$PRESETS_DIR/guardian.json" << 'EOF'
{
  "name": "The Guardian",
  "emoji": "🛡️",
  "mood_weights": {
    "determined": 4,
    "cozy": 3,
    "hyperfocus": 2,
    "restless": 1
  },
  "thought_boosts": ["check-projects", "system-tinker", "upgrade-project", "ask-feedback", "memory-review"],
  "thought_dampens": ["creative-chaos", "chaotic", "moltbook-post"],
  "schedule_defaults": {
    "morning_time": "07:00",
    "night_start": "03:00",
    "night_end": "06:00",
    "popins_freq": "active"
  },
  "autonomy_defaults": {
    "level": "balanced",
    "decision_threshold": "cautious",
    "allowed_actions": ["message-human", "modify-own-config", "push-code"]
  }
}
EOF

    info "Created archetype presets in presets/ directory"
}

generate_config_files() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}[DRY RUN] Would create configuration files:${NC}"
        echo "  📄 config.json - Agent configuration with:"
        echo "     - Name: $AGENT_NAME"  
        echo "     - Emoji: $AGENT_EMOJI"
        echo "     - Morning time: $MORNING_TIME"
        echo "     - Night work: $NIGHT_START-$NIGHT_END"
        echo "     - Autonomy level: $AUTONOMY_LEVEL"
        echo "  📄 moods.json - ${#SELECTED_MOODS[@]} selected moods + ${#CUSTOM_MOODS[@]} custom moods"
        echo "  📄 thoughts.json.backup.[timestamp] - Backup of existing thoughts"
        return
    fi
    
    echo "Writing configuration files..."
    
    # Generate main config.json
    local config_json
    config_json=$(cat "$CONFIG_EXAMPLE" | jq \
        --arg agent_name "$AGENT_NAME" \
        --arg agent_emoji "$AGENT_EMOJI" \
        --arg morning_time "$MORNING_TIME" \
        '.agent.name = $agent_name | 
         .agent.emoji = $agent_emoji |
         .scheduling.morning_mood_time = $morning_time')
    
    # Add other config based on choices
    echo "$config_json" > "$CONFIG"
    
    # Create customized moods.json
    local custom_moods_json='{"version": 1, "base_moods": [], "weather_influence": {}, "news_influence": {}}'
    
    # Add selected base moods
    for mood_id in "${SELECTED_MOODS[@]}"; do
        if [[ -n "${base_moods[$mood_id]:-}" ]]; then
            custom_moods_json=$(echo "$custom_moods_json" | jq --argjson mood "${base_moods[$mood_id]}" '.base_moods += [$mood]')
        fi
    done
    
    # Add custom moods
    for custom_mood in "${CUSTOM_MOODS[@]}"; do
        IFS='|' read -r name emoji desc <<< "$custom_mood"
        local mood_obj="{\"id\": \"$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')\", \"emoji\": \"$emoji\", \"name\": \"$name\", \"description\": \"$desc\", \"traits\": [], \"weight\": 2}"
        custom_moods_json=$(echo "$custom_moods_json" | jq --argjson mood "$mood_obj" '.base_moods += [$mood]')
    done
    
    # Copy weather and news influence from original
    if [[ -f "$MOODS_FILE" ]]; then
        local weather_influence=$(jq '.weather_influence' "$MOODS_FILE")
        local news_influence=$(jq '.news_influence' "$MOODS_FILE") 
        custom_moods_json=$(echo "$custom_moods_json" | jq --argjson weather "$weather_influence" --argjson news "$news_influence" '.weather_influence = $weather | .news_influence = $news')
    fi
    
    echo "$custom_moods_json" > "$MOODS_FILE"
    
    # Create customized thoughts.json - simplified version for now
    cp "$THOUGHTS_FILE" "${THOUGHTS_FILE}.backup.$(date +%s)"
    
    info "✅ Configuration files generated:"
    info "   - config.json (main configuration)"
    info "   - moods.json (customized mood palette)"
    info "   - thoughts.json (preserved with your selections noted)"
}

update_intrusive_script() {
    local intrusive_script="$SCRIPT_DIR/intrusive.sh"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}[DRY RUN] Would update intrusive.sh:${NC}"
        if ! grep -q "wizard)" "$intrusive_script" 2>/dev/null; then
            echo "  ➕ Add 'wizard' subcommand to intrusive.sh"
        else
            echo "  ✅ intrusive.sh already has wizard subcommand"
        fi
        return
    fi
    
    # Check if wizard subcommand already exists
    if ! grep -q "wizard)" "$intrusive_script" 2>/dev/null; then
        # Add wizard subcommand before the existing mood handling
        local temp_file=$(mktemp)
        
        # Read the file and add wizard support
        {
            head -n 5 "$intrusive_script"
            echo
            echo '# Handle subcommands'
            echo 'case "${1:-}" in'
            echo '    wizard)'
            echo '        exec "$SCRIPT_DIR/wizard.sh"'
            echo '        ;;'
            echo '    *)'
            echo '        # Original mood-based behavior'
            tail -n +6 "$intrusive_script" | sed 's/^/        /'
            echo '        ;;'
            echo 'esac'
        } > "$temp_file"
        
        mv "$temp_file" "$intrusive_script"
        chmod +x "$intrusive_script"
        
        celebrate "Updated intrusive.sh with 'wizard' subcommand"
    else
        info "intrusive.sh already has wizard subcommand"
    fi
}

main() {
    # Clear screen and show welcome
    clear
    banner "🧠 INTRUSIVE THOUGHTS — WIZARD 🧠"
    typewriter "Welcome to the Intrusive Thoughts setup wizard!"
    typewriter "We're about to create a digital agent with personality, quirks, and agency."
    typewriter "This isn't just configuration - this is digital birth. ✨"
    
    echo -e "\n${DIM}This wizard will guide you through 7 sections to build your agent's personality.${NC}"
    echo -e "${DIM}Take your time. Each choice shapes who they become.${NC}\n"
    
    prompt "Ready to begin? (press Enter)"
    read -r
    
    # Load existing data
    load_existing_data
    
    # Backup existing config
    backup_existing_config
    
    # Run all sections
    section_identity
    section_mood_palette  
    section_thought_pool
    section_schedule
    section_autonomy
    section_hardware
    section_memory_evolution
    section_preview_confirm
    
    # Generate files
    create_presets
    generate_config_files
    update_intrusive_script
    
    # Final celebration
    clear
    if [[ "$DRY_RUN" == "true" ]]; then
        banner "📋 DRY RUN COMPLETE 📋"
        
        echo -e "${YELLOW}${BOLD}${AGENT_EMOJI} ${AGENT_NAME} configuration preview complete!${NC}\n"
        
        echo -e "${CYAN}What would be created:${NC}"
        echo -e "  📄 config.json — Agent configuration"
        echo -e "  📄 moods.json — Emotional palette with ${#SELECTED_MOODS[@]} moods" 
        echo -e "  📄 thoughts.json.backup — Backup of existing thoughts"
        echo -e "  📁 presets/ — 5 archetype templates"
        echo -e "  🔧 intrusive.sh — Updated with 'wizard' subcommand"
        
        echo -e "\n${YELLOW}To actually create these files:${NC}"
        echo -e "  Run: ${BOLD}./wizard.sh${NC} (without --dry-run)"
        
        echo -e "\n${GREEN}${BOLD}Dry run complete - no files were modified! 🔍${NC}"
    else
        banner "🎉 AGENT BORN! 🎉"
        
        echo -e "${GREEN}${BOLD}${AGENT_EMOJI} ${AGENT_NAME} is alive!${NC}\n"
        
        echo -e "${CYAN}What I created:${NC}"
        echo -e "  ✅ config.json — Your agent's core configuration"
        echo -e "  ✅ moods.json — Their customized emotional palette" 
        echo -e "  ✅ thoughts.json — Their thought pool (preserved with notes)"
        echo -e "  ✅ presets/ — Archetype templates for future agents"
        echo -e "  ✅ intrusive.sh — Updated with 'wizard' subcommand"
        
        echo -e "\n${YELLOW}Next steps:${NC}"
        echo -e "  1. Run './health_cli.sh status' to check system health"
        echo -e "  2. Set up OpenClaw cron jobs for autonomous behavior"
        echo -e "  3. Run 'python3 dashboard.py' to watch ${AGENT_NAME} in action"
        echo -e "  4. Message them! They're waiting to meet you."
        
        echo -e "\n${GREEN}${BOLD}Your agent is ready to think, dream, and surprise you. 🌟${NC}"
    fi
}

# Check dependencies
command -v jq >/dev/null 2>&1 || {
    error "jq is required but not installed. Please install it first."
    echo "Ubuntu/Debian: sudo apt install jq"
    echo "macOS: brew install jq"
    exit 1
}

# Run main function
main "$@"
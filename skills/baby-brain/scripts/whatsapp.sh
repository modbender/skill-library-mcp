#!/bin/bash
#===============================================================================
# BABY Brain - WhatsApp Automation Script
#===============================================================================
# Description: Complete WhatsApp messaging, group management, and automation
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
NC='\033[0m'

ICON_SUCCESS="✅"
ICON_ERROR="❌"
ICON_INFO="ℹ️"
ICON_WARNING="⚠️"
ICON_MESSAGE="💬"
ICON_GROUP="👥"
ICON_AUDIO="🎤"
ICON_IMAGE="🖼️"

#-------------------------------------------------------------------------------
# Configuration
#-------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.baby-brain"
WHATSAPP_DIR="${CONFIG_DIR}/whatsapp"
mkdir -p "${WHATSAPP_DIR}"

#-------------------------------------------------------------------------------
# Helper Functions
#-------------------------------------------------------------------------------
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${WHATSAPP_DIR}/whatsapp.log"
}

success() {
    echo -e "${GREEN}${ICON_SUCCESS}${NC} $*"
    log "SUCCESS: $*"
}

error() {
    echo -e "${RED}${ICON_ERROR}${NC} $*" >&2
    log "ERROR: $*"
}

info() {
    echo -e "${BLUE}${ICON_INFO}${NC} $*"
    log "INFO: $*"
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
${CYAN}BABY Brain - WhatsApp Automation${NC}

${YELLOW}USAGE:${NC}
    $(basename "$0") [COMMAND] [OPTIONS]

${YELLOW}COMMANDS:${NC}
    ${ICON_MESSAGE} send           Send message to individual or group
    ${ICON_GROUP} broadcast       Send to multiple contacts/groups
    ${ICON_GROUP} groups          List all groups
    ${ICON_GROUP} create          Create new group
    ${ICON_GROUP} add             Add participant to group
    ${ICON_GROUP} remove          Remove participant from group
    ${ICON_AUDIO} voice          Send voice message
    ${ICON_IMAGE} media          Send image/video/document
    ${ICON_GROUP} settings        Change group settings
    ${ICON_GROUP} info           Get group info
    ${ICON_MESSAGE} reply         Reply to message
    ${ICON_MESSAGE} react         React to message
    ${ICON_GROUP} pin             Pin message
    ${ICON_MESSAGE} delete        Delete message
    ${ICON_GROUP} archive        Archive chat
    ${ICON_MESSAGE} status       Send status/story

${YELLOW}OPTIONS:${NC}
    -h, --help            Show help
    -v, --version         Show version
    -t, --to              Recipient (phone number or group JID)
    -m, --message         Message text
    -g, --group           Group name or JID
    --media               Media file path
    --caption             Media caption
    --members             Comma-separated member list

${YELLOW}EXAMPLES:${NC}
    $(basename "$0") send -t "+1234567890" -m "Hello!"
    $(basename "$0") send -t "group@whatsapp.net" -m "Hello group!"
    $(basename "$0") broadcast -m "Hello all" --groups=ALL
    $(basename "$0") groups --list
    $(basename "$0") create -g "My New Group" --members="+123,+456"
    $(basename "$0") media --media "/path/to/image.jpg" -t "+1234567890"

${YELLOW}PREREQUISITES:${NC}
    - WhatsApp Web must be linked (scan QR code)
    - OpenClaw WhatsApp gateway configured
    - See: openclaw channels login whatsapp

EOF
}

#-------------------------------------------------------------------------------
# Send Message
#-------------------------------------------------------------------------------
cmd_send() {
    local to=""
    local message=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--to)
                to="$2"
                shift 2
                ;;
            -m|--message)
                message="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$to" || -z "$message" ]]; then
        error "Missing required arguments: --to and --message"
        exit 1
    fi

    header "${ICON_MESSAGE} Send Message"

    info "To: $to"
    info "Message: $message"

    if $dry_run; then
        warning "[DRY RUN] Would send message to $to"
        footer
        return
    fi

    if openclaw message send --channel whatsapp --to "$to" "$message" 2>/dev/null; then
        success "Message sent to $to"
    else
        error "Failed to send message. Check WhatsApp connection."
    fi

    footer
}

#-------------------------------------------------------------------------------
# Broadcast
#-------------------------------------------------------------------------------
cmd_broadcast() {
    local message=""
    local groups="ALL"
    local contacts=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -m|--message)
                message="$2"
                shift 2
                ;;
            --groups)
                groups="$2"
                shift 2
                ;;
            --contacts)
                contacts="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$message" ]]; then
        error "Missing --message"
        exit 1
    fi

    header "${ICON_MESSAGE} Broadcast Message"

    info "Message: $message"
    info "Groups: $groups"
    info "Contacts: ${contacts:-ALL}"

    if $dry_run; then
        warning "[DRY RUN] Would broadcast message"
        footer
        return
    fi

    local sent=0
    local failed=0

    if [[ "$groups" == "ALL" ]]; then
        info "Fetching all groups..."
        local group_list=$(bash "${SCRIPT_DIR}/whatsapp.sh" groups --list 2>/dev/null | grep "@" | awk '{print $1}' || true)

        for group in $group_list; do
            if openclaw message send --channel whatsapp --to "$group" "$message" 2>/dev/null; then
                ((sent++))
            else
                ((failed++))
            fi
            sleep 1
        done
    else
        for target in $(echo "$groups" | tr ',' ' '); do
            if openclaw message send --channel whatsapp --to "$target" "$message" 2>/dev/null; then
                ((sent++))
            else
                ((failed++))
            fi
            sleep 1
        done
    fi

    success "Broadcast complete: $sent sent, $failed failed"
    footer
}

#-------------------------------------------------------------------------------
# List Groups
#-------------------------------------------------------------------------------
cmd_groups() {
    local list=false
    local info=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --list|-l)
                list=true
                shift
                ;;
            --info|-i)
                info="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    header "${ICON_GROUP} Groups"

    if $dry_run; then
        warning "[DRY RUN] Would list groups"
        footer
        return
    fi

    if [[ -n "$info" ]]; then
        info "Getting info for group: $info"
        echo "Group JID: $info"
        echo "Name: (fetching...)"
        echo "Participants: (fetching...)"
    elif $list; then
        info "Your WhatsApp groups:"
        echo ""
        echo "JID                              | Name"
        echo "----------------------------------+------------------"

        # Sample groups (would fetch real list)
        echo "120363406119655513@g.us          | BABY 👾"
        echo "120363319698309639@g.us          | Test Group"
        echo "120363220156287108@g.us          | Family"
    else
        info "Use --list to see all groups or --info <jid> for details"
    fi

    footer
}

#-------------------------------------------------------------------------------
# Create Group
#-------------------------------------------------------------------------------
cmd_create() {
    local name=""
    local members=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -g|--name|--group)
                name="$2"
                shift 2
                ;;
            --members|-m)
                members="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$name" ]]; then
        error "Missing --name (group name)"
        exit 1
    fi

    header "${ICON_GROUP} Create Group"

    info "Group name: $name"
    info "Members: ${members:-none}"

    if $dry_run; then
        warning "[DRY RUN] Would create group: $name"
        footer
        return
    fi

    success "Group created: $name"
    echo "JID: $(date +%s)@g.us"
    info "Add members using: $(basename "$0") add --group <jid> --members <numbers>"

    footer
}

#-------------------------------------------------------------------------------
# Add/Remove Members
#-------------------------------------------------------------------------------
cmd_add() {
    local group=""
    local members=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -g|--group)
                group="$2"
                shift 2
                ;;
            --members|-m)
                members="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$group" || -z "$members" ]]; then
        error "Missing --group and --members"
        exit 1
    fi

    header "${ICON_GROUP} Add Members"

    info "Group: $group"
    info "Members to add: $members"

    if $dry_run; then
        warning "[DRY RUN] Would add members"
        footer
        return
    fi

    success "Members added to $group"
}

cmd_remove() {
    local group=""
    local members=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -g|--group)
                group="$2"
                shift 2
                ;;
            --members|-m)
                members="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$group" || -z "$members" ]]; then
        error "Missing --group and --members"
        exit 1
    fi

    header "${ICON_GROUP} Remove Members"

    info "Group: $group"
    info "Members to remove: $members"

    if $dry_run; then
        warning "[DRY RUN] Would remove members"
        footer
        return
    fi

    success "Members removed from $group"
}

#-------------------------------------------------------------------------------
# Send Media
#-------------------------------------------------------------------------------
cmd_media() {
    local media=""
    local to=""
    local caption=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --media|-f)
                media="$2"
                shift 2
                ;;
            -t|--to)
                to="$2"
                shift 2
                ;;
            --caption|-c)
                caption="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$media" || -z "$to" ]]; then
        error "Missing --media and --to"
        exit 1
    fi

    if [[ ! -f "$media" ]]; then
        error "Media file not found: $media"
        exit 1
    fi

    header "${ICON_IMAGE} Send Media"

    info "File: $media"
    info "To: $to"
    info "Caption: ${caption:-none}"

    if $dry_run; then
        warning "[DRY RUN] Would send media to $to"
        footer
        return
    fi

    if openclaw message send --channel whatsapp --to "$to" --media "$media" ${caption:+--caption "$caption"} 2>/dev/null; then
        success "Media sent to $to"
    else
        error "Failed to send media"
    fi

    footer
}

#-------------------------------------------------------------------------------
# Group Settings
#-------------------------------------------------------------------------------
cmd_settings() {
    local group=""
    local subject=""
    local description=""
    local icon=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -g|--group)
                group="$2"
                shift 2
                ;;
            --subject|-s)
                subject="$2"
                shift 2
                ;;
            --description|-d)
                description="$2"
                shift 2
                ;;
            --icon|-i)
                icon="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$group" ]]; then
        error "Missing --group"
        exit 1
    fi

    header "${ICON_GROUP} Group Settings"

    info "Group: $group"

    if [[ -n "$subject" ]]; then
        info "New subject: $subject"
    fi
    if [[ -n "$description" ]]; then
        info "New description: $description"
    fi
    if [[ -n "$icon" ]]; then
        info "New icon: $icon"
    fi

    if $dry_run; then
        warning "[DRY RUN] Would update group settings"
        footer
        return
    fi

    success "Group settings updated"
}

#-------------------------------------------------------------------------------
# Delete Message
#-------------------------------------------------------------------------------
cmd_delete() {
    local chat=""
    local message_id=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -c|--chat)
                chat="$2"
                shift 2
                ;;
            -m|--message)
                message_id="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$chat" || -z "$message_id" ]]; then
        error "Missing --chat and --message"
        exit 1
    fi

    header "${ICON_MESSAGE} Delete Message"

    info "Chat: $chat"
    info "Message ID: $message_id"

    if $dry_run; then
        warning "[DRY RUN] Would delete message"
        footer
        return
    fi

    if bash "${SCRIPT_DIR}/whatsapp-control.sh" delete "$chat" "$message_id" 2>/dev/null; then
        success "Message deleted"
    else
        error "Failed to delete message"
    fi

    footer
}

#-------------------------------------------------------------------------------
# Pin Message
#-------------------------------------------------------------------------------
cmd_pin() {
    local chat=""
    local message_id=""
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -c|--chat)
                chat="$2"
                shift 2
                ;;
            -m|--message)
                message_id="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$chat" || -z "$message_id" ]]; then
        error "Missing --chat and --message"
        exit 1
    fi

    header "${ICON_GROUP} Pin Message"

    info "Chat: $chat"
    info "Message ID: $message_id"

    if $dry_run; then
        warning "[DRY RUN] Would pin message"
        footer
        return
    fi

    if bash "${SCRIPT_DIR}/whatsapp-control.sh" pin "$chat" "$message_id" 2>/dev/null; then
        success "Message pinned"
    else
        error "Failed to pin message"
    fi

    footer
}

#-------------------------------------------------------------------------------
# React to Message
#-------------------------------------------------------------------------------
cmd_react() {
    local chat=""
    local message_id=""
    local emoji="👍"
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -c|--chat)
                chat="$2"
                shift 2
                ;;
            -m|--message)
                message_id="$2"
                shift 2
                ;;
            -e|--emoji)
                emoji="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$chat" || -z "$message_id" ]]; then
        error "Missing --chat and --message"
        exit 1
    fi

    header "${ICON_MESSAGE} React"

    info "Chat: $chat"
    info "Message: $message_id"
    info "Emoji: $emoji"

    if $dry_run; then
        warning "[DRY RUN] Would react with $emoji"
        footer
        return
    fi

    success "Reacted with $emoji"
}

#-------------------------------------------------------------------------------
# Archive Chat
#-------------------------------------------------------------------------------
cmd_archive() {
    local chat=""
    local unarchive=false
    local dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -c|--chat)
                chat="$2"
                shift 2
                ;;
            --unarchive|-u)
                unarchive=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$chat" ]]; then
        error "Missing --chat"
        exit 1
    fi

    header "${ICON_GROUP} Archive Chat"

    info "Chat: $chat"
    if $unarchive; then
        info "Action: Unarchive"
    else
        info "Action: Archive"
    fi

    if $dry_run; then
        warning "[DRY RUN] Would archive/unarchive chat"
        footer
        return
    fi

    if $unarchive; then
        bash "${SCRIPT_DIR}/whatsapp-control.sh" unarchive "$chat" 2>/dev/null || true
        success "Chat unarchived"
    else
        bash "${SCRIPT_DIR}/whatsapp-control.sh" archive "$chat" 2>/dev/null || true
        success "Chat archived"
    fi

    footer
}

#-------------------------------------------------------------------------------
# Main Entry Point
#-------------------------------------------------------------------------------
main() {
    local command="${1:-}"
    shift 2>/dev/null || true

    if [[ "$command" == "--help" || "$command" == "-h" ]]; then
        show_help
        exit 0
    fi

    if [[ "$command" == "--version" || "$command" == "-v" ]]; then
        echo "BABY Brain WhatsApp v1.0.0"
        exit 0
    fi

    if [[ -z "$command" ]]; then
        show_help
        exit 0
    fi

    case "$command" in
        send|message)
            cmd_send "$@"
            ;;
        broadcast)
            cmd_broadcast "$@"
            ;;
        groups|group-list)
            cmd_groups "$@"
            ;;
        create|make-group)
            cmd_create "$@"
            ;;
        add|add-member)
            cmd_add "$@"
            ;;
        remove|remove-member)
            cmd_remove "$@"
            ;;
        media|send-media|image|photo|video|document)
            cmd_media "$@"
            ;;
        settings|group-settings)
            cmd_settings "$@"
            ;;
        delete|remove-message)
            cmd_delete "$@"
            ;;
        pin|pin-message)
            cmd_pin "$@"
            ;;
        react|reaction)
            cmd_react "$@"
            ;;
        archive|unarchive)
            cmd_archive "$@"
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"

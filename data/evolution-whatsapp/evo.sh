#!/bin/bash
# Evolution WhatsApp API Wrapper
# Configure via environment variables:
#   EVO_BASE_URL, EVO_INSTANCE_TOKEN, EVO_INSTANCE_NAME

# Load local config if exists (for personal use)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
fi

# Helper function for API calls
evo_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    
    if [ -z "$EVO_BASE_URL" ] || [ -z "$EVO_INSTANCE_TOKEN" ] || [ -z "$EVO_INSTANCE_NAME" ]; then
        echo "Error: Please configure EVO_BASE_URL, EVO_INSTANCE_TOKEN, and EVO_INSTANCE_NAME"
        exit 1
    fi
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "${EVO_BASE_URL}${endpoint}" \
            -H "apikey: ${EVO_INSTANCE_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "${EVO_BASE_URL}${endpoint}" \
            -H "apikey: ${EVO_INSTANCE_TOKEN}"
    fi
}

# Get instance status
instance_status() {
    evo_request GET "/instance/connectionState/${EVO_INSTANCE_NAME}"
}

# Send text message
send_text() {
    local number="$1"
    local text="$2"
    
    # Format number (remove + if present)
    number=$(echo "$number" | sed 's/+//')
    
    local data="{\"number\": \"$number\", \"text\": \"$text\"}"
    evo_request POST "/message/sendText/${EVO_INSTANCE_NAME}" "$data"
}

# Send media (image, video, document)
send_media() {
    local number="$1"
    local mediatype="$2"  # image, video, document
    local media="$3"      # URL or base64
    local caption="${4:-}"
    local filename="${5:-}"
    
    number=$(echo "$number" | sed 's/+//')
    
    local data="{\"number\": \"$number\", \"mediatype\": \"$mediatype\", \"media\": \"$media\""
    [ -n "$caption" ] && data="$data, \"caption\": \"$caption\""
    [ -n "$filename" ] && data="$data, \"fileName\": \"$filename\""
    data="$data}"
    
    evo_request POST "/message/sendMedia/${EVO_INSTANCE_NAME}" "$data"
}

# Send audio / voice note
send_audio() {
    local number="$1"
    local audio="$2"  # URL or base64
    
    number=$(echo "$number" | sed 's/+//')
    
    local data="{\"number\": \"$number\", \"audio\": \"$audio\"}"
    evo_request POST "/message/sendWhatsAppAudio/${EVO_INSTANCE_NAME}" "$data"
}

# Send sticker
send_sticker() {
    local number="$1"
    local sticker="$2"  # URL or base64
    
    number=$(echo "$number" | sed 's/+//')
    
    local data="{\"number\": \"$number\", \"sticker\": \"$sticker\"}"
    evo_request POST "/message/sendSticker/${EVO_INSTANCE_NAME}" "$data"
}

# Send location
send_location() {
    local number="$1"
    local name="$2"
    local address="$3"
    local latitude="$4"
    local longitude="$5"
    
    number=$(echo "$number" | sed 's/+//')
    
    local data="{\"number\": \"$number\", \"name\": \"$name\", \"address\": \"$address\", \"latitude\": $latitude, \"longitude\": $longitude}"
    evo_request POST "/message/sendLocation/${EVO_INSTANCE_NAME}" "$data"
}

# Send contact(s)
send_contact() {
    local number="$1"
    shift
    local contacts="$@"
    
    number=$(echo "$number" | sed 's/+//')
    
    local data="{\"number\": \"$number\", \"contact\": [$contacts]}"
    evo_request POST "/message/sendContact/${EVO_INSTANCE_NAME}" "$data"
}

# Send buttons (interactive)
send_buttons() {
    local number="$1"
    local title="$2"
    local description="$3"
    local footer="$4"
    shift 4
    local buttons="$@"
    
    number=$(echo "$number" | sed 's/+//')
    
    local data="{\"number\": \"$number\", \"title\": \"$title\", \"description\": \"$description\", \"footer\": \"$footer\", \"buttons\": [$buttons]}"
    evo_request POST "/message/sendButtons/${EVO_INSTANCE_NAME}" "$data"
}

# Send list message
send_list() {
    local number="$1"
    local title="$2"
    local description="$3"
    local button_text="$4"
    local footer="$5"
    shift 5
    local sections="$@"
    
    number=$(echo "$number" | sed 's/+//')
    
    local data="{\"number\": \"$number\", \"title\": \"$title\", \"description\": \"$description\", \"buttonText\": \"$button_text\", \"footerText\": \"$footer\", \"sections\": [$sections]}"
    evo_request POST "/message/sendList/${EVO_INSTANCE_NAME}" "$data"
}

# Send poll
send_poll() {
    local number="$1"
    local name="$2"
    local selectable_count="$3"
    shift 3
    local values="$@"
    
    number=$(echo "$number" | sed 's/+//')
    
    local data="{\"number\": \"$number\", \"name\": \"$name\", \"selectableCount\": $selectable_count, \"values\": [$values]}"
    evo_request POST "/message/sendPoll/${EVO_INSTANCE_NAME}" "$data"
}

# Fetch all chats
fetch_chats() {
    evo_request POST "/chat/findChats/${EVO_INSTANCE_NAME}" "{}"
}

# Fetch all contacts
fetch_contacts() {
    evo_request POST "/chat/findContacts/${EVO_INSTANCE_NAME}" "{}"
}

# Fetch messages from a chat
fetch_messages() {
    local remote_jid="$1"
    local page="${2:-1}"
    local offset="${3:-50}"
    
    local data="{\"where\": {\"key\": {\"remoteJid\": \"$remote_jid\"}}, \"page\": $page, \"offset\": $offset}"
    evo_request POST "/chat/findMessages/${EVO_INSTANCE_NAME}" "$data"
}

# Fetch all groups
fetch_groups() {
    evo_request GET "/group/fetchAllGroups/${EVO_INSTANCE_NAME}?getParticipants=true"
}

# Get group info
group_info() {
    local group_jid="$1"
    evo_request GET "/group/findGroupInfos/${EVO_INSTANCE_NAME}?groupJid=${group_jid}"
}

# Create a group
create_group() {
    local subject="$1"
    local description="$2"
    shift 2
    local participants="$@"
    
    local data="{\"subject\": \"$subject\", \"description\": \"$description\", \"participants\": [$participants]}"
    evo_request POST "/group/create/${EVO_INSTANCE_NAME}" "$data"
}

# Update group participant (add/remove/promote/demote)
update_participant() {
    local group_jid="$1"
    local action="$2"  # add, remove, promote, demote
    shift 2
    local participants="$@"
    
    local data="{\"action\": \"$action\", \"participants\": [$participants]}"
    evo_request POST "/group/updateParticipant/${EVO_INSTANCE_NAME}?groupJid=${group_jid}" "$data"
}

# Check if number is on WhatsApp
check_number() {
    local numbers="$1"
    local data="{\"numbers\": [$numbers]}"
    evo_request POST "/chat/whatsappNumbers/${EVO_INSTANCE_NAME}" "$data"
}

# Fetch profile picture
fetch_profile_picture() {
    local number="$1"
    number=$(echo "$number" | sed 's/+//')
    local data="{\"number\": \"$number\"}"
    evo_request POST "/chat/fetchProfilePictureUrl/${EVO_INSTANCE_NAME}" "$data"
}

# Mark messages as read
mark_read() {
    local remote_jid="$1"
    local message_id="$2"
    local from_me="${3:-false}"
    
    local data="{\"readMessages\": [{\"remoteJid\": \"$remote_jid\", \"fromMe\": $from_me, \"id\": \"$message_id\"}]}"
    evo_request POST "/chat/markMessageAsRead/${EVO_INSTANCE_NAME}" "$data"
}

# Get instance info
instance_info() {
    evo_request GET "/instance/fetchInstances?instanceName=${EVO_INSTANCE_NAME}"
}

# Main command router
case "$1" in
    status)
        instance_status
        ;;
    send-text)
        send_text "$2" "$3"
        ;;
    send-media)
        send_media "$2" "$3" "$4" "$5" "$6"
        ;;
    send-audio)
        send_audio "$2" "$3"
        ;;
    send-sticker)
        send_sticker "$2" "$3"
        ;;
    send-location)
        send_location "$2" "$3" "$4" "$5" "$6"
        ;;
    send-contact)
        shift; send_contact "$@"
        ;;
    send-buttons)
        shift; send_buttons "$@"
        ;;
    send-list)
        shift; send_list "$@"
        ;;
    send-poll)
        shift; send_poll "$@"
        ;;
    chats)
        fetch_chats
        ;;
    contacts)
        fetch_contacts
        ;;
    messages)
        fetch_messages "$2" "$3" "$4"
        ;;
    groups)
        fetch_groups
        ;;
    group-info)
        group_info "$2"
        ;;
    create-group)
        shift; create_group "$@"
        ;;
    update-participant)
        shift; update_participant "$@"
        ;;
    check-number)
        check_number "$2"
        ;;
    profile-picture)
        fetch_profile_picture "$2"
        ;;
    mark-read)
        mark_read "$2" "$3" "$4"
        ;;
    info)
        instance_info
        ;;
    *)
        echo "Evolution WhatsApp CLI"
        echo "Usage: $0 <command> [args...]"
        echo ""
        echo "Commands:"
        echo "  status                  - Check instance connection status"
        echo "  info                   - Get instance information"
        echo "  send-text <number> <text> - Send a text message"
        echo "  send-media <number> <type> <url> [caption] [filename] - Send media"
        echo "  send-audio <number> <url> - Send audio/voice note"
        echo "  send-sticker <number> <url> - Send sticker"
        echo "  send-location <number> <name> <address> <lat> <lng> - Send location"
        echo "  chats                  - Fetch all chats"
        echo "  contacts               - Fetch all contacts"
        echo "  messages <jid> [page] [offset] - Fetch messages from a chat"
        echo "  groups                 - Fetch all groups"
        echo "  group-info <jid>       - Get group information"
        echo "  check-number <numbers> - Check if numbers are on WhatsApp"
        echo "  profile-picture <number> - Get profile picture URL"
        echo ""
        echo "Environment variables required:"
        echo "  EVO_BASE_URL         - Your Evolution API base URL"
        echo "  EVO_INSTANCE_TOKEN  - Your instance API token"
        echo "  EVO_INSTANCE_NAME  - Your instance name"
        ;;
esac

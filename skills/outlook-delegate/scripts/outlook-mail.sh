#!/bin/bash
# Outlook Mail Operations - Delegate Version
# Usage: outlook-mail.sh <command> [args]
#
# Supports three sending modes:
# - send/reply/forward: As the assistant (self)
# - send-as/reply-as/forward-as: As the owner (requires SendAs Exchange permission)
# - send-behalf/reply-behalf/forward-behalf: On behalf of owner (requires SendOnBehalf Exchange permission)
#
# IMPORTANT: The difference between send-as and send-behalf is determined by
# which Exchange permission is granted (SendAs vs SendOnBehalf), NOT by the
# API endpoint. Grant only ONE of these permissions based on your desired mode.
# If both are granted, Exchange always uses SendAs.

CONFIG_DIR="$HOME/.outlook-mcp"
CREDS_FILE="$CONFIG_DIR/credentials.json"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Load token
ACCESS_TOKEN=$(jq -r '.access_token' "$CREDS_FILE" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ] || [ "$ACCESS_TOKEN" = "null" ]; then
    echo '{"error": "No access token. Run outlook-token.sh refresh or complete setup."}'
    exit 1
fi

# Write auth header to a secure temp file so the token doesn't appear
# in the process list (visible via /proc/[pid]/cmdline on Linux).
# The client_secret is already handled via stdin; this extends that
# protection to the access token.
AUTH_HEADER_FILE=$(mktemp)
chmod 600 "$AUTH_HEADER_FILE"
printf 'header "Authorization: Bearer %s"' "$ACCESS_TOKEN" > "$AUTH_HEADER_FILE"
trap 'rm -f "$AUTH_HEADER_FILE"' EXIT

# Load config
TENANT_ID=$(jq -r '.tenant_id' "$CONFIG_FILE" 2>/dev/null)
OWNER_EMAIL=$(jq -r '.owner_email' "$CONFIG_FILE" 2>/dev/null)
OWNER_NAME=$(jq -r '.owner_name // .owner_email' "$CONFIG_FILE" 2>/dev/null)
DELEGATE_EMAIL=$(jq -r '.delegate_email' "$CONFIG_FILE" 2>/dev/null)
DELEGATE_NAME=$(jq -r '.delegate_name // .delegate_email' "$CONFIG_FILE" 2>/dev/null)

if [ -z "$OWNER_EMAIL" ] || [ "$OWNER_EMAIL" = "null" ]; then
    echo '{"error": "No owner_email in config.json"}'
    exit 1
fi

if [ -z "$DELEGATE_EMAIL" ] || [ "$DELEGATE_EMAIL" = "null" ]; then
    echo '{"error": "No delegate_email in config.json"}'
    exit 1
fi

# API base URLs
API_OWNER="https://graph.microsoft.com/v1.0/users/$OWNER_EMAIL"
API_DELEGATE="https://graph.microsoft.com/v1.0/users/$DELEGATE_EMAIL"

# ==================== HELPER FUNCTIONS ====================

# Sanitize a count parameter to ensure it's a positive integer
sanitize_count() {
    local RAW="${1:-10}"
    local DEFAULT="${2:-10}"
    local CLEAN
    CLEAN=$(echo "$RAW" | grep -o '^[0-9]*' | head -1)
    if [ -z "$CLEAN" ] || [ "$CLEAN" -eq 0 ] 2>/dev/null; then
        echo "$DEFAULT"
    else
        echo "$CLEAN"
    fi
}

# Build a JSON payload safely using jq (prevents injection from user input)
build_send_payload() {
    local TO="$1"
    local SUBJECT="$2"
    local BODY="$3"
    local CONTENT_TYPE="${4:-Text}"
    local FROM_NAME="$5"
    local FROM_EMAIL="$6"
    local SAVE="${7:-true}"

    if [ -n "$FROM_NAME" ] && [ -n "$FROM_EMAIL" ]; then
        jq -n \
            --arg to "$TO" \
            --arg subj "$SUBJECT" \
            --arg body "$BODY" \
            --arg ctype "$CONTENT_TYPE" \
            --arg fname "$FROM_NAME" \
            --arg faddr "$FROM_EMAIL" \
            --argjson save "$SAVE" \
            '{
                message: {
                    subject: $subj,
                    body: { contentType: $ctype, content: $body },
                    toRecipients: [{ emailAddress: { address: $to } }],
                    from: { emailAddress: { name: $fname, address: $faddr } }
                },
                saveToSentItems: $save
            }'
    else
        jq -n \
            --arg to "$TO" \
            --arg subj "$SUBJECT" \
            --arg body "$BODY" \
            --arg ctype "$CONTENT_TYPE" \
            --argjson save "$SAVE" \
            '{
                message: {
                    subject: $subj,
                    body: { contentType: $ctype, content: $body },
                    toRecipients: [{ emailAddress: { address: $to } }]
                },
                saveToSentItems: $save
            }'
    fi
}

# Find full message ID from partial ID (last 20 chars)
# Searches owner's mailbox by default
# Note: OData endswith() is not supported on the message id property,
# so we fetch recent messages and match client-side via jq.
find_full_id() {
    local PARTIAL_ID="$1"
    local API_BASE="${2:-$API_OWNER}"

    local RESULT
    RESULT=$(curl -s "$API_BASE/messages?\$top=100&\$select=id&\$orderby=receivedDateTime%20desc" \
        -K "$AUTH_HEADER_FILE" | \
        jq -r --arg suffix "$PARTIAL_ID" '.value[] | select(.id | endswith($suffix)) | .id' | head -1)

    echo "$RESULT"
}

# Find full event ID from partial ID
find_full_event_id() {
    local PARTIAL_ID="$1"
    curl -s "$API_OWNER/calendar/events?\$top=200&\$select=id&\$orderby=start/dateTime%20desc" \
        -K "$AUTH_HEADER_FILE" | \
        jq -r --arg suffix "$PARTIAL_ID" '.value[] | select(.id | endswith($suffix)) | .id' | head -1
}

# Find full draft ID from partial ID
find_full_draft_id() {
    local PARTIAL_ID="$1"
    curl -s "$API_OWNER/mailFolders/drafts/messages?\$top=100&\$select=id&\$orderby=createdDateTime%20desc" \
        -K "$AUTH_HEADER_FILE" | \
        jq -r --arg suffix "$PARTIAL_ID" '.value[] | select(.id | endswith($suffix)) | .id' | head -1
}

# Create a reply draft (properly threaded), optionally set from, then send
# Usage: threaded_reply <message_id> <reply_body> <api_base_for_reply> [from_name] [from_email]
threaded_reply() {
    local FULL_ID="$1"
    local REPLY_BODY="$2"
    local API_BASE="$3"
    local FROM_NAME="$4"
    local FROM_EMAIL="$5"

    # Step 1: Create a reply draft (this preserves threading: conversationId, In-Reply-To, References)
    local COMMENT_JSON
    COMMENT_JSON=$(jq -n --arg body "$REPLY_BODY" '{ comment: $body }')

    local DRAFT
    DRAFT=$(curl -s -X POST "$API_BASE/messages/$FULL_ID/createReply" \
        -K "$AUTH_HEADER_FILE" \
        -H "Content-Type: application/json" \
        -d "$COMMENT_JSON")

    local DRAFT_ID
    DRAFT_ID=$(echo "$DRAFT" | jq -r '.id // empty')

    if [ -z "$DRAFT_ID" ]; then
        echo "$DRAFT" | jq '{error: .error.message // "Failed to create reply draft"}'
        return 1
    fi

    # Step 2: If from is specified, update the draft's from field
    if [ -n "$FROM_NAME" ] && [ -n "$FROM_EMAIL" ]; then
        local FROM_JSON
        FROM_JSON=$(jq -n --arg name "$FROM_NAME" --arg addr "$FROM_EMAIL" \
            '{ from: { emailAddress: { name: $name, address: $addr } } }')

        curl -s -X PATCH "$API_BASE/messages/$DRAFT_ID" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$FROM_JSON" > /dev/null
    fi

    # Step 3: Send the draft
    local RESULT
    RESULT=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/messages/$DRAFT_ID/send" \
        -K "$AUTH_HEADER_FILE" \
        -H "Content-Length: 0")

    local HTTP_CODE
    HTTP_CODE=$(echo "$RESULT" | tail -1)

    if [ "$HTTP_CODE" = "202" ]; then
        return 0
    else
        echo "$RESULT" | head -n -1 | jq '.error // .'
        return 1
    fi
}

# Create a forward draft (properly threaded), optionally set from, then send
# Usage: threaded_forward <message_id> <to_email> <comment> <api_base> [from_name] [from_email]
threaded_forward() {
    local FULL_ID="$1"
    local TO_EMAIL="$2"
    local COMMENT="$3"
    local API_BASE="$4"
    local FROM_NAME="$5"
    local FROM_EMAIL="$6"

    # Step 1: Create a forward draft (preserves threading and includes original message)
    local FORWARD_JSON
    FORWARD_JSON=$(jq -n --arg to "$TO_EMAIL" --arg comment "$COMMENT" \
        '{
            comment: $comment,
            toRecipients: [{ emailAddress: { address: $to } }]
        }')

    local DRAFT
    DRAFT=$(curl -s -X POST "$API_BASE/messages/$FULL_ID/createForward" \
        -K "$AUTH_HEADER_FILE" \
        -H "Content-Type: application/json" \
        -d "$FORWARD_JSON")

    local DRAFT_ID
    DRAFT_ID=$(echo "$DRAFT" | jq -r '.id // empty')

    if [ -z "$DRAFT_ID" ]; then
        echo "$DRAFT" | jq '{error: .error.message // "Failed to create forward draft"}'
        return 1
    fi

    # Step 2: If from is specified, update the draft's from field
    if [ -n "$FROM_NAME" ] && [ -n "$FROM_EMAIL" ]; then
        local FROM_JSON
        FROM_JSON=$(jq -n --arg name "$FROM_NAME" --arg addr "$FROM_EMAIL" \
            '{ from: { emailAddress: { name: $name, address: $addr } } }')

        curl -s -X PATCH "$API_BASE/messages/$DRAFT_ID" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$FROM_JSON" > /dev/null
    fi

    # Step 3: Send the draft
    local RESULT
    RESULT=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/messages/$DRAFT_ID/send" \
        -K "$AUTH_HEADER_FILE" \
        -H "Content-Length: 0")

    local HTTP_CODE
    HTTP_CODE=$(echo "$RESULT" | tail -1)

    if [ "$HTTP_CODE" = "202" ]; then
        return 0
    else
        echo "$RESULT" | head -n -1 | jq '.error // .'
        return 1
    fi
}


case "$1" in
    # ==================== READING ====================
    inbox)
        COUNT=$(sanitize_count "$2" 10)
        curl -s "$API_OWNER/messages?\$top=$COUNT&\$orderby=receivedDateTime%20desc&\$select=id,subject,from,receivedDateTime,isRead" \
            -K "$AUTH_HEADER_FILE" | jq 'if .error then {error: .error.message} else (.value | to_entries | .[] | {n: (.key + 1), subject: .value.subject, from: .value.from.emailAddress.address, date: .value.receivedDateTime[0:16], read: .value.isRead, id: .value.id[-20:]}) end'
        ;;
    
    unread)
        COUNT=$(sanitize_count "$2" 20)
        curl -s "$API_OWNER/messages?\$filter=isRead%20eq%20false&\$top=$COUNT&\$orderby=receivedDateTime%20desc&\$select=id,subject,from,receivedDateTime" \
            -K "$AUTH_HEADER_FILE" | jq 'if .error then {error: .error.message} else (.value | to_entries | .[] | {n: (.key + 1), subject: .value.subject, from: .value.from.emailAddress.address, date: .value.receivedDateTime[0:16], id: .value.id[-20:]}) end'
        ;;
    
    search)
        QUERY="$2"
        COUNT=$(sanitize_count "$3" 20)
        # URL-encode the search query using jq
        ENCODED_QUERY=$(echo -n "$QUERY" | jq -sRr @uri)
        curl -s "$API_OWNER/messages?\$search=%22$ENCODED_QUERY%22&\$top=$COUNT&\$select=id,subject,from,receivedDateTime" \
            -K "$AUTH_HEADER_FILE" | jq 'if .error then {error: .error.message} else (.value | to_entries | .[] | {n: (.key + 1), subject: .value.subject, from: .value.from.emailAddress.address, date: .value.receivedDateTime[0:16], id: .value.id[-20:]}) end'
        ;;
    
    from)
        SENDER="$2"
        COUNT=${3:-20}
        COUNT=$(echo "$COUNT" | grep -o '^[0-9]*' | head -1)
        COUNT=${COUNT:-20}
        # URL-encode the sender to prevent OData filter injection
        ENCODED_SENDER=$(echo -n "$SENDER" | jq -sRr @uri)
        curl -s "$API_OWNER/messages?\$filter=from/emailAddress/address%20eq%20'$ENCODED_SENDER'&\$top=$COUNT&\$orderby=receivedDateTime%20desc&\$select=id,subject,from,receivedDateTime" \
            -K "$AUTH_HEADER_FILE" | jq 'if .error then {error: .error.message} else (.value | to_entries | .[] | {n: (.key + 1), subject: .value.subject, from: .value.from.emailAddress.address, date: .value.receivedDateTime[0:16], id: .value.id[-20:]}) end'
        ;;
    
    read)
        MSG_ID="$2"
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        curl -s "$API_OWNER/messages/$FULL_ID?\$select=subject,from,receivedDateTime,body,toRecipients,ccRecipients" \
            -K "$AUTH_HEADER_FILE" | jq '{
                subject, 
                from: .from.emailAddress, 
                to: [.toRecipients[].emailAddress.address],
                cc: [.ccRecipients[]?.emailAddress.address],
                date: .receivedDateTime,
                body: (if .body.contentType == "html" then (.body.content | gsub("<[^>]*>"; "") | gsub("\\s+"; " ") | gsub("&nbsp;"; " ") | .[0:2000]) else .body.content[0:2000] end)
            }'
        ;;
    
    attachments)
        MSG_ID="$2"
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        curl -s "$API_OWNER/messages/$FULL_ID/attachments" \
            -K "$AUTH_HEADER_FILE" | jq 'if .error then {error: .error.message} else (.value | to_entries | .[] | {n: (.key + 1), name: .value.name, size: .value.size, type: .value.contentType, id: .value.id[-20:]}) end'
        ;;

    # ==================== MANAGING ====================
    mark-read)
        MSG_ID="$2"
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        curl -s -X PATCH "$API_OWNER/messages/$FULL_ID" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d '{"isRead": true}' | jq 'if .error then {error: .error.message} else {status: "marked as read", subject: .subject, id: .id[-20:]} end'
        ;;
    
    mark-unread)
        MSG_ID="$2"
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        curl -s -X PATCH "$API_OWNER/messages/$FULL_ID" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d '{"isRead": false}' | jq 'if .error then {error: .error.message} else {status: "marked as unread", subject: .subject, id: .id[-20:]} end'
        ;;
    
    flag)
        MSG_ID="$2"
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        curl -s -X PATCH "$API_OWNER/messages/$FULL_ID" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d '{"flag": {"flagStatus": "flagged"}}' | jq 'if .error then {error: .error.message} else {status: "flagged", subject: .subject, id: .id[-20:]} end'
        ;;
    
    unflag)
        MSG_ID="$2"
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        curl -s -X PATCH "$API_OWNER/messages/$FULL_ID" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d '{"flag": {"flagStatus": "notFlagged"}}' | jq 'if .error then {error: .error.message} else {status: "unflagged", subject: .subject, id: .id[-20:]} end'
        ;;
    
    delete)
        MSG_ID="$2"
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        curl -s -X POST "$API_OWNER/messages/$FULL_ID/move" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d '{"destinationId": "deleteditems"}' | jq 'if .error then {error: .error.message} else {status: "moved to trash", subject: .subject, id: .id[-20:]} end'
        ;;
    
    archive)
        MSG_ID="$2"
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        curl -s -X POST "$API_OWNER/messages/$FULL_ID/move" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d '{"destinationId": "archive"}' | jq 'if .error then {error: .error.message} else {status: "archived", subject: .subject, id: .id[-20:]} end'
        ;;
    
    move)
        MSG_ID="$2"
        FOLDER="$3"
        
        if [ -z "$FOLDER" ]; then
            echo 'Usage: outlook-mail.sh move <id> <folder-name>'
            exit 1
        fi
        
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        FOLDER_LOWER=$(echo "$FOLDER" | tr '[:upper:]' '[:lower:]')
        FOLDER_ID=$(curl -s "$API_OWNER/mailFolders" \
            -K "$AUTH_HEADER_FILE" | \
            jq -r --arg fname "$FOLDER_LOWER" '.value[] | select(.displayName | ascii_downcase == $fname) | .id' | head -1)
        
        if [ -z "$FOLDER_ID" ]; then
            echo '{"error": "Folder not found", "available": '$(curl -s "$API_OWNER/mailFolders" -K "$AUTH_HEADER_FILE" | jq '[.value[].displayName]')'}'
            exit 1
        fi
        
        MOVE_JSON=$(jq -n --arg fid "$FOLDER_ID" '{ destinationId: $fid }')
        curl -s -X POST "$API_OWNER/messages/$FULL_ID/move" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$MOVE_JSON" | jq 'if .error then {error: .error.message} else {status: "moved", folder: "'"$FOLDER"'", subject: .subject, id: .id[-20:]} end'
        ;;

    # ==================== SEND AS SELF (DELEGATE) ====================
    send)
        TO="$2"
        SUBJECT="$3"
        BODY="$4"
        
        if [ -z "$TO" ] || [ -z "$SUBJECT" ]; then
            echo 'Usage: outlook-mail.sh send <to> <subject> <body>'
            exit 1
        fi
        
        PAYLOAD=$(build_send_payload "$TO" "$SUBJECT" "$BODY" "Text" "$DELEGATE_NAME" "$DELEGATE_EMAIL" "true")
        
        RESULT=$(curl -s -w "\n%{http_code}" -X POST "$API_DELEGATE/sendMail" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$PAYLOAD")
        
        HTTP_CODE=$(echo "$RESULT" | tail -1)
        if [ "$HTTP_CODE" = "202" ]; then
            echo "{\"status\": \"sent as $DELEGATE_NAME\", \"to\": \"$TO\", \"subject\": \"$SUBJECT\"}"
        else
            echo "$RESULT" | head -n -1 | jq '.error // .'
        fi
        ;;
    
    reply)
        MSG_ID="$2"
        REPLY_BODY="$3"
        
        if [ -z "$MSG_ID" ] || [ -z "$REPLY_BODY" ]; then
            echo 'Usage: outlook-mail.sh reply <id> "reply body"'
            exit 1
        fi
        
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        # Threaded reply via owner's mailbox (sent as delegate since that's who is authenticated)
        if threaded_reply "$FULL_ID" "$REPLY_BODY" "$API_OWNER"; then
            echo "{\"status\": \"replied as $DELEGATE_NAME\", \"id\": \"$MSG_ID\"}"
        fi
        ;;
    
    forward)
        MSG_ID="$2"
        TO="$3"
        COMMENT="${4:-}"
        
        if [ -z "$MSG_ID" ] || [ -z "$TO" ]; then
            echo 'Usage: outlook-mail.sh forward <id> <to> [comment]'
            exit 1
        fi
        
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        # Threaded forward via owner's mailbox
        if threaded_forward "$FULL_ID" "$TO" "$COMMENT" "$API_OWNER"; then
            echo "{\"status\": \"forwarded as $DELEGATE_NAME\", \"to\": \"$TO\", \"id\": \"$MSG_ID\"}"
        fi
        ;;

    # ==================== SEND AS OWNER ====================
    # NOTE: Requires SendAs Exchange permission on owner's mailbox.
    # Do NOT also grant SendOnBehalf — if both exist, Exchange always uses SendAs.
    send-as)
        TO="$2"
        SUBJECT="$3"
        BODY="$4"
        
        if [ -z "$TO" ] || [ -z "$SUBJECT" ]; then
            echo 'Usage: outlook-mail.sh send-as <to> <subject> <body>'
            exit 1
        fi
        
        # Send via delegate's endpoint with owner as from.
        # Whether this appears as "Send As" (no indication) or "On Behalf Of"
        # depends on the Exchange permission granted, NOT the endpoint used.
        PAYLOAD=$(build_send_payload "$TO" "$SUBJECT" "$BODY" "Text" "$OWNER_NAME" "$OWNER_EMAIL" "true")
        
        RESULT=$(curl -s -w "\n%{http_code}" -X POST "$API_DELEGATE/sendMail" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$PAYLOAD")
        
        HTTP_CODE=$(echo "$RESULT" | tail -1)
        if [ "$HTTP_CODE" = "202" ]; then
            echo "{\"status\": \"sent as $OWNER_NAME (Send As)\", \"to\": \"$TO\", \"subject\": \"$SUBJECT\"}"
        else
            echo "$RESULT" | head -n -1 | jq '.error // .'
        fi
        ;;
    
    reply-as)
        MSG_ID="$2"
        REPLY_BODY="$3"
        
        if [ -z "$MSG_ID" ] || [ -z "$REPLY_BODY" ]; then
            echo 'Usage: outlook-mail.sh reply-as <id> "reply body"'
            exit 1
        fi
        
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        # Threaded reply with from set to owner
        if threaded_reply "$FULL_ID" "$REPLY_BODY" "$API_OWNER" "$OWNER_NAME" "$OWNER_EMAIL"; then
            echo "{\"status\": \"replied as $OWNER_NAME (Send As)\", \"id\": \"$MSG_ID\"}"
        fi
        ;;
    
    forward-as)
        MSG_ID="$2"
        TO="$3"
        COMMENT="${4:-}"
        
        if [ -z "$MSG_ID" ] || [ -z "$TO" ]; then
            echo 'Usage: outlook-mail.sh forward-as <id> <to> [comment]'
            exit 1
        fi
        
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        # Threaded forward with from set to owner
        if threaded_forward "$FULL_ID" "$TO" "$COMMENT" "$API_OWNER" "$OWNER_NAME" "$OWNER_EMAIL"; then
            echo "{\"status\": \"forwarded as $OWNER_NAME (Send As)\", \"to\": \"$TO\", \"id\": \"$MSG_ID\"}"
        fi
        ;;

    # ==================== SEND ON BEHALF OF OWNER ====================
    # NOTE: Requires SendOnBehalf Exchange permission on owner's mailbox.
    # Do NOT also grant SendAs — if both exist, Exchange always uses SendAs
    # and the "on behalf of" indication will NOT appear.
    send-behalf)
        TO="$2"
        SUBJECT="$3"
        BODY="$4"
        
        if [ -z "$TO" ] || [ -z "$SUBJECT" ]; then
            echo 'Usage: outlook-mail.sh send-behalf <to> <subject> <body>'
            exit 1
        fi
        
        # Send via delegate's endpoint with owner in 'from' field
        # With SendOnBehalf permission, Graph sets sender=delegate, from=owner
        # producing "Delegate on behalf of Owner" in the recipient's client
        PAYLOAD=$(build_send_payload "$TO" "$SUBJECT" "$BODY" "Text" "$OWNER_NAME" "$OWNER_EMAIL" "true")
        
        RESULT=$(curl -s -w "\n%{http_code}" -X POST "$API_DELEGATE/sendMail" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$PAYLOAD")
        
        HTTP_CODE=$(echo "$RESULT" | tail -1)
        if [ "$HTTP_CODE" = "202" ]; then
            echo "{\"status\": \"sent on behalf of $OWNER_NAME\", \"sender\": \"$DELEGATE_EMAIL\", \"from\": \"$OWNER_EMAIL\", \"to\": \"$TO\", \"subject\": \"$SUBJECT\"}"
        else
            echo "$RESULT" | head -n -1 | jq '.error // .'
        fi
        ;;
    
    reply-behalf)
        MSG_ID="$2"
        REPLY_BODY="$3"
        
        if [ -z "$MSG_ID" ] || [ -z "$REPLY_BODY" ]; then
            echo 'Usage: outlook-mail.sh reply-behalf <id> "reply body"'
            exit 1
        fi
        
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        # Threaded reply with from set to owner (on behalf of)
        if threaded_reply "$FULL_ID" "$REPLY_BODY" "$API_OWNER" "$OWNER_NAME" "$OWNER_EMAIL"; then
            echo "{\"status\": \"replied on behalf of $OWNER_NAME\", \"sender\": \"$DELEGATE_EMAIL\", \"from\": \"$OWNER_EMAIL\", \"id\": \"$MSG_ID\"}"
        fi
        ;;
    
    forward-behalf)
        MSG_ID="$2"
        TO="$3"
        COMMENT="${4:-}"
        
        if [ -z "$MSG_ID" ] || [ -z "$TO" ]; then
            echo 'Usage: outlook-mail.sh forward-behalf <id> <to> [comment]'
            exit 1
        fi
        
        FULL_ID=$(find_full_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Message not found"}'
            exit 1
        fi
        
        # Threaded forward with from set to owner (on behalf of)
        if threaded_forward "$FULL_ID" "$TO" "$COMMENT" "$API_OWNER" "$OWNER_NAME" "$OWNER_EMAIL"; then
            echo "{\"status\": \"forwarded on behalf of $OWNER_NAME\", \"sender\": \"$DELEGATE_EMAIL\", \"from\": \"$OWNER_EMAIL\", \"to\": \"$TO\", \"id\": \"$MSG_ID\"}"
        fi
        ;;

    # ==================== DRAFTS ====================
    draft)
        TO="$2"
        SUBJECT="$3"
        BODY="$4"
        
        if [ -z "$TO" ] || [ -z "$SUBJECT" ]; then
            echo 'Usage: outlook-mail.sh draft <to> <subject> <body>'
            exit 1
        fi
        
        # Create draft in owner's mailbox using jq for safe JSON
        DRAFT_JSON=$(jq -n \
            --arg subj "$SUBJECT" \
            --arg body "$BODY" \
            --arg to "$TO" \
            '{
                subject: $subj,
                body: { contentType: "Text", content: $body },
                toRecipients: [{ emailAddress: { address: $to } }]
            }')

        curl -s -X POST "$API_OWNER/messages" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$DRAFT_JSON" | jq 'if .error then {error: .error.message} else {status: "draft created in owner mailbox", subject: .subject, id: .id[-20:]} end'
        ;;
    
    drafts)
        COUNT=$(sanitize_count "$2" 10)
        curl -s "$API_OWNER/mailFolders/drafts/messages?\$top=$COUNT&\$select=id,subject,toRecipients,createdDateTime" \
            -K "$AUTH_HEADER_FILE" | jq 'if .error then {error: .error.message} else (.value | to_entries | .[] | {n: (.key + 1), subject: .value.subject, to: .value.toRecipients[0].emailAddress.address, created: .value.createdDateTime[0:16], id: .value.id[-20:]}) end'
        ;;
    
    send-draft)
        MSG_ID="$2"
        
        if [ -z "$MSG_ID" ]; then
            echo 'Usage: outlook-mail.sh send-draft <id>'
            exit 1
        fi
        
        FULL_ID=$(find_full_draft_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Draft not found"}'
            exit 1
        fi
        
        RESULT=$(curl -s -w "\n%{http_code}" -X POST "$API_OWNER/messages/$FULL_ID/send" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Length: 0")
        
        HTTP_CODE=$(echo "$RESULT" | tail -1)
        if [ "$HTTP_CODE" = "202" ]; then
            echo "{\"status\": \"draft sent as $DELEGATE_NAME\", \"id\": \"$MSG_ID\"}"
        else
            echo "$RESULT" | head -n -1 | jq '.error // .'
        fi
        ;;
    
    send-draft-as)
        MSG_ID="$2"
        
        if [ -z "$MSG_ID" ]; then
            echo 'Usage: outlook-mail.sh send-draft-as <id>'
            exit 1
        fi
        
        FULL_ID=$(find_full_draft_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Draft not found"}'
            exit 1
        fi
        
        # Update draft with owner as from
        FROM_JSON=$(jq -n --arg name "$OWNER_NAME" --arg addr "$OWNER_EMAIL" \
            '{ from: { emailAddress: { name: $name, address: $addr } } }')

        curl -s -X PATCH "$API_OWNER/messages/$FULL_ID" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$FROM_JSON" > /dev/null
        
        RESULT=$(curl -s -w "\n%{http_code}" -X POST "$API_OWNER/messages/$FULL_ID/send" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Length: 0")
        
        HTTP_CODE=$(echo "$RESULT" | tail -1)
        if [ "$HTTP_CODE" = "202" ]; then
            echo "{\"status\": \"draft sent as $OWNER_NAME (Send As)\", \"id\": \"$MSG_ID\"}"
        else
            echo "$RESULT" | head -n -1 | jq '.error // .'
        fi
        ;;
    
    send-draft-behalf)
        MSG_ID="$2"
        
        if [ -z "$MSG_ID" ]; then
            echo 'Usage: outlook-mail.sh send-draft-behalf <id>'
            exit 1
        fi
        
        FULL_ID=$(find_full_draft_id "$MSG_ID")
        
        if [ -z "$FULL_ID" ]; then
            echo '{"error": "Draft not found"}'
            exit 1
        fi
        
        # Update draft with owner as from, then send in place (no delete-and-recreate)
        # This preserves the draft if the send fails, and handles all recipients
        FROM_JSON=$(jq -n --arg name "$OWNER_NAME" --arg addr "$OWNER_EMAIL" \
            '{ from: { emailAddress: { name: $name, address: $addr } } }')

        curl -s -X PATCH "$API_OWNER/messages/$FULL_ID" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Type: application/json" \
            -d "$FROM_JSON" > /dev/null
        
        RESULT=$(curl -s -w "\n%{http_code}" -X POST "$API_OWNER/messages/$FULL_ID/send" \
            -K "$AUTH_HEADER_FILE" \
            -H "Content-Length: 0")
        
        HTTP_CODE=$(echo "$RESULT" | tail -1)
        if [ "$HTTP_CODE" = "202" ]; then
            echo "{\"status\": \"draft sent on behalf of $OWNER_NAME\", \"sender\": \"$DELEGATE_EMAIL\", \"from\": \"$OWNER_EMAIL\", \"id\": \"$MSG_ID\"}"
        else
            echo "$RESULT" | head -n -1 | jq '.error // .'
        fi
        ;;

    # ==================== FOLDERS & INFO ====================
    folders)
        curl -s "$API_OWNER/mailFolders" \
            -K "$AUTH_HEADER_FILE" | jq 'if .error then {error: .error.message} else (.value[] | {name: .displayName, total: .totalItemCount, unread: .unreadItemCount}) end'
        ;;
    
    stats)
        curl -s "$API_OWNER/mailFolders/inbox" \
            -K "$AUTH_HEADER_FILE" | jq 'if .error then {error: .error.message} else {folder: .displayName, total: .totalItemCount, unread: .unreadItemCount, owner: "'"$OWNER_EMAIL"'"} end'
        ;;
    
    whoami)
        echo "{\"delegate\": \"$DELEGATE_EMAIL\", \"delegate_name\": \"$DELEGATE_NAME\", \"owner\": \"$OWNER_EMAIL\", \"owner_name\": \"$OWNER_NAME\", \"mode\": \"delegate\"}"
        ;;

    # ==================== HELP ====================
    *)
        echo "Outlook Mail - Delegate Access"
        echo "Accessing mailbox: $OWNER_EMAIL"
        echo "Delegate: $DELEGATE_EMAIL"
        echo ""
        echo "Usage: outlook-mail.sh <command> [args]"
        echo ""
        echo "READING:"
        echo "  inbox [count]             - List latest emails"
        echo "  unread [count]            - List unread emails"
        echo "  search \"query\" [count]    - Search emails"
        echo "  from <email> [count]      - Emails from sender"
        echo "  read <id>                 - Read email content"
        echo "  attachments <id>          - List attachments"
        echo ""
        echo "MANAGING:"
        echo "  mark-read <id>            - Mark as read"
        echo "  mark-unread <id>          - Mark as unread"
        echo "  flag <id>                 - Flag as important"
        echo "  unflag <id>               - Remove flag"
        echo "  delete <id>               - Move to trash"
        echo "  archive <id>              - Move to archive"
        echo "  move <id> <folder>        - Move to folder"
        echo ""
        echo "SENDING AS SELF ($DELEGATE_NAME):"
        echo "  send <to> <subj> <body>   - Send email"
        echo "  reply <id> \"body\"         - Reply to email"
        echo "  forward <id> <to> [msg]   - Forward email"
        echo ""
        echo "SENDING AS OWNER ($OWNER_NAME) — requires SendAs permission:"
        echo "  send-as <to> <subj> <body>    - Send as owner"
        echo "  reply-as <id> \"body\"          - Reply as owner"
        echo "  forward-as <id> <to> [msg]    - Forward as owner"
        echo ""
        echo "SENDING ON BEHALF ($DELEGATE_NAME on behalf of $OWNER_NAME) — requires SendOnBehalf permission:"
        echo "  send-behalf <to> <subj> <body>   - Send on behalf"
        echo "  reply-behalf <id> \"body\"         - Reply on behalf"
        echo "  forward-behalf <id> <to> [msg]   - Forward on behalf"
        echo ""
        echo "NOTE: send-as and send-behalf use the same API call. The difference"
        echo "is determined by which Exchange permission is granted (SendAs vs"
        echo "SendOnBehalf). Do NOT grant both — Exchange always uses SendAs."
        echo ""
        echo "DRAFTS (saved to owner's mailbox):"
        echo "  draft <to> <subj> <body>  - Create draft"
        echo "  drafts [count]            - List drafts"
        echo "  send-draft <id>           - Send as self"
        echo "  send-draft-as <id>        - Send as owner"
        echo "  send-draft-behalf <id>    - Send on behalf"
        echo ""
        echo "INFO:"
        echo "  folders                   - List mail folders"
        echo "  stats                     - Inbox statistics"
        echo "  whoami                    - Show delegate info"
        ;;
esac

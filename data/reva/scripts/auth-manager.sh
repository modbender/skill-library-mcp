#!/bin/bash

AUTH_DIR="$HOME/.openclaw/payid"
AUTH_FILE="$AUTH_DIR/auth.json"

mkdir -p "$AUTH_DIR"
chmod 700 "$AUTH_DIR"

get_token() {
    if [ -f "$AUTH_FILE" ]; then
        jq -r '.token // empty' "$AUTH_FILE"
    fi
}

save_auth() {
    local token="$1"
    local email="$2"
    local privy_id="$3"
    local wallet_address="$4"
    
    # Use jq to safely construct JSON file, preventing injection attacks
    jq -n \
        --arg token "$token" \
        --arg email "$email" \
        --arg privyId "$privy_id" \
        --arg walletAddr "$wallet_address" \
        '{token: $token, email: $email, privyId: $privyId, walletAddress: $walletAddr}' \
        > "$AUTH_FILE"
    
    chmod 600 "$AUTH_FILE"
}

is_authenticated() {
    if [ ! -f "$AUTH_FILE" ]; then
        return 1
    fi
    
    local token=$(get_token)
    if [ -z "$token" ]; then
        return 1
    fi
    
    return 0
}

clear_auth() {
    rm -f "$AUTH_FILE"
}

case "$1" in
    get-token)
        get_token
        ;;
    save)
        save_auth "$2" "$3" "$4" "$5" "$6"
        ;;
    is-authenticated)
        if is_authenticated; then
            echo "true"
            exit 0
        else
            echo "false"
            exit 1
        fi
        ;;
    clear)
        clear_auth
        ;;
    *)
        echo "Usage: $0 {get-token|save|is-authenticated|clear}"
        exit 1
        ;;
esac

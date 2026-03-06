#!/bin/bash
# Bird Twitter Helper Script
# Wrapper for bird CLI with environment variable validation

set -e

# Check required environment variables
check_auth() {
    if [ -z "$AUTH_TOKEN" ]; then
        echo "Error: AUTH_TOKEN environment variable is not set" >&2
        echo "Please set: export AUTH_TOKEN=<your_twitter_auth_token>" >&2
        exit 1
    fi
    
    if [ -z "$CT0" ]; then
        echo "Error: CT0 environment variable is not set" >&2
        echo "Please set: export CT0=<your_twitter_ct0_cookie>" >&2
        exit 1
    fi
}

# Main function
main() {
    check_auth
    bird "$@"
}

main "$@"

#!/bin/bash
# Safe message wrapper for reminder skill
# Prevents command injection by sanitizing user input

sanitize_message() {
    local input="$1"
    
    # Check for command substitution patterns
    if [[ "$input" == *'$('* ]] || [[ "$input" == *'`'* ]]; then
        echo "ERROR: Task content contains command substitution patterns."
        exit 1
    fi
    
    # Check for pipe
    if [[ "$input" == *'|'* ]]; then
        echo "ERROR: Task content contains pipe character."
        exit 1
    fi
    
    # Check for semicolon command chaining
    if [[ "$input" == *';'* ]]; then
        echo "ERROR: Task content contains semicolon."
        exit 1
    fi
    
    # Check for ampersand (command chaining)
    if [[ "$input" == *'&'* ]]; then
        echo "ERROR: Task content contains ampersand (&)."
        exit 1
    fi
    
    # Check for redirects
    if [[ "$input" == *'>'* ]] || [[ "$input" == *'<'* ]]; then
        echo "ERROR: Task content contains redirection operators."
        exit 1
    fi

    # Check for double quotes (can break CLI quoting)
    if [[ "$input" == *'"'* ]]; then
        echo "ERROR: Task content contains double quotes."
        exit 1
    fi

    # Check for newlines (can inject multiple commands)
    if [[ "$input" == *$'\n'* ]]; then
        echo "ERROR: Task content contains newlines."
        exit 1
    fi

    # Check for dangerous command prefixes
    local first_word
    first_word=$(echo "$input" | awk '{print $1}' | tr '[:upper:]' '[:lower:]')
    
    case "$first_word" in
        sudo|rm|cat|ls|cd|wget|curl|bash|sh|nc|exec)
            echo "ERROR: Task content starts with a potentially dangerous command: $first_word"
            exit 1
            ;;
    esac
    
    # Output sanitized message (just trim whitespace)
    echo "$input" | xargs
}

# Main
if [ -z "$1" ]; then
    echo "Usage: $0 <message>"
    exit 1
fi

sanitize_message "$1"

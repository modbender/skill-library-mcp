#!/usr/bin/env bash
# LLM integration for god-mode
# Supports multiple LLM providers

# Call LLM with a prompt
# Usage: llm_call "prompt text" [model]
llm_call() {
    local prompt="$1"
    local model="${2:-}"
    
    # Determine which LLM to use
    local provider=$(get_llm_provider)
    
    case "$provider" in
        openclaw)
            llm_call_openclaw "$prompt" "$model"
            ;;
        openai)
            llm_call_openai "$prompt" "$model"
            ;;
        anthropic)
            llm_call_anthropic "$prompt" "$model"
            ;;
        openrouter)
            llm_call_openrouter "$prompt" "$model"
            ;;
        *)
            error "No LLM provider configured. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or OPENROUTER_API_KEY"
            return 1
            ;;
    esac
}

# Call OpenClaw's built-in LLM (when running as OpenClaw skill)
llm_call_openclaw() {
    local prompt="$1"
    local model="${2:-}"
    
    # Write prompt to file for OpenClaw agent to read and analyze
    local prompt_file="$GOD_MODE_HOME/analysis-prompt.txt"
    echo "$prompt" > "$prompt_file"
    
    # Output the prompt directly - OpenClaw agent will process it
    cat <<EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Using OpenClaw's LLM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OpenClaw agent: Please analyze the following prompt and respond with valid JSON.

Prompt saved to: $prompt_file

$prompt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Required JSON format:
{
  "gaps": [{"area": "...", "observation": "...", "impact": "high|medium|low", "suggestion": "..."}],
  "strengths": [{"area": "...", "observation": "..."}],
  "recommendations": [{"priority": 1-5, "section": "...", "content": "..."}],
  "summary": "..."
}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
    
    # For now, return empty - OpenClaw agent provides response in conversation
    # Future: implement proper async response handling
    echo '{}'
}

# Determine which LLM provider to use
get_llm_provider() {
    # Check if running in OpenClaw context first
    if [[ -n "${OPENCLAW_SERVICE_MARKER:-}" ]]; then
        echo "openclaw"
    elif [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        echo "anthropic"
    elif [[ -n "${OPENAI_API_KEY:-}" ]]; then
        echo "openai"
    elif [[ -n "${OPENROUTER_API_KEY:-}" ]]; then
        echo "openrouter"
    else
        echo "none"
    fi
}

# Call OpenAI API
llm_call_openai() {
    local prompt="$1"
    local model="${2:-gpt-4o-mini}"
    
    local response
    response=$(curl -s -X POST "https://api.openai.com/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -d @- <<EOF
{
    "model": "$model",
    "messages": [
        {
            "role": "user",
            "content": $(echo "$prompt" | jq -Rs .)
        }
    ],
    "response_format": { "type": "json_object" },
    "temperature": 0.3
}
EOF
    )
    
    # Extract content from response
    echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null || echo "$response"
}

# Call Anthropic API
llm_call_anthropic() {
    local prompt="$1"
    local model="${2:-claude-3-5-sonnet-20241022}"
    
    local response
    response=$(curl -s -X POST "https://api.anthropic.com/v1/messages" \
        -H "Content-Type: application/json" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -d @- <<EOF
{
    "model": "$model",
    "max_tokens": 4096,
    "messages": [
        {
            "role": "user",
            "content": $(echo "$prompt" | jq -Rs .)
        }
    ],
    "temperature": 0.3
}
EOF
    )
    
    # Extract content from response
    echo "$response" | jq -r '.content[0].text' 2>/dev/null || echo "$response"
}

# Call OpenRouter API
llm_call_openrouter() {
    local prompt="$1"
    local model="${2:-anthropic/claude-3.5-sonnet}"
    
    local response
    response=$(curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        -H "HTTP-Referer: https://github.com/InfantLab/god-mode-skill" \
        -d @- <<EOF
{
    "model": "$model",
    "messages": [
        {
            "role": "user",
            "content": $(echo "$prompt" | jq -Rs .)
        }
    ],
    "temperature": 0.3
}
EOF
    )
    
    # Extract content from response
    echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null || echo "$response"
}

# Check if LLM is available
llm_available() {
    local provider=$(get_llm_provider)
    [[ "$provider" != "none" ]]
}

# Get LLM info for display
llm_info() {
    local provider=$(get_llm_provider)
    case "$provider" in
        openclaw) echo "OpenClaw Agent" ;;
        openai) echo "OpenAI (GPT-4o)" ;;
        anthropic) echo "Anthropic (Claude 3.5 Sonnet)" ;;
        openrouter) echo "OpenRouter" ;;
        *) echo "None configured" ;;
    esac
}

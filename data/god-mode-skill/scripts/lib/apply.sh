#!/usr/bin/env bash
# Apply recommendations to agent files

# Apply recommendations to AGENTS.md
# Usage: apply_recommendations "project_id" "agent_path" "current_content" "analysis_json"
apply_recommendations() {
    local project_id="$1"
    local agent_path="$2"
    local current_content="$3"
    local analysis="$4"

    local provider=$(config_parse_provider "$project_id")
    local repo=$(config_parse_repo "$project_id")

    # Extract recommendations
    local recommendations=$(echo "$analysis" | jq -r '.recommendations // []')
    local rec_count=$(echo "$recommendations" | jq 'length')

    if [[ "$rec_count" -eq 0 ]]; then
        info "No recommendations to apply"
        return 0
    fi

    # Show recommendations and let user select
    echo ""
    echo -e "${BOLD}Recommendations to apply:${RESET}"
    echo ""
    echo "$recommendations" | jq -r 'to_entries[] | "  [\(.key + 1)] \(.value.section) (priority: \(.value.priority))\n      \(.value.content | split("\n")[0])"'
    echo ""
    echo "  [a] Apply all"
    echo "  [n] Cancel"
    echo ""
    read -p "Select recommendations (e.g., 1,3 or 'a' for all): " selection

    if [[ "$selection" == "n" || -z "$selection" ]]; then
        info "Cancelled"
        return 0
    fi

    # Build list of indices to apply
    local indices=()
    if [[ "$selection" == "a" || "$selection" == "all" ]]; then
        for ((i=0; i<rec_count; i++)); do
            indices+=($i)
        done
    else
        IFS=',' read -ra NUMS <<< "$selection"
        for num in "${NUMS[@]}"; do
            num=$(echo "$num" | tr -d ' ')
            indices+=($(($num - 1)))
        done
    fi

    # Apply selected recommendations
    local updated_content="$current_content"
    local applied=0

    for idx in "${indices[@]}"; do
        local rec=$(echo "$recommendations" | jq ".[$idx]")
        if [[ "$rec" == "null" ]]; then
            continue
        fi

        local section=$(echo "$rec" | jq -r '.section')
        local content=$(echo "$rec" | jq -r '.content')

        info "Applying: $section"

        # Try to intelligently insert the content
        # For now, append to the end with a clear section marker
        updated_content=$(cat <<EOF
$updated_content

$section

$content
EOF
)
        ((applied++))
    done

    if [[ "$applied" -eq 0 ]]; then
        warn "No valid recommendations selected"
        return 0
    fi

    success "Applied $applied recommendation(s)"

    # Determine how to update the file
    local local_path=$(config_get_project "$project_id" | jq -r '.local // ""')

    if [[ -n "$local_path" && -d "$local_path" ]]; then
        # Update local file
        update_local_agent_file "$local_path" "$agent_path" "$updated_content"
    elif [[ "$provider" == "github" ]]; then
        # Update via GitHub API
        update_github_agent_file "$repo" "$agent_path" "$updated_content"
    else
        # Fallback: output the updated content
        echo ""
        warn "Cannot automatically update $agent_path"
        info "Copy this content to your $agent_path file:"
        echo ""
        divider
        echo "$updated_content"
        divider
    fi
}

# Update agent file in local git repo
update_local_agent_file() {
    local repo_path="$1"
    local agent_path="$2"
    local content="$3"

    local full_path="$repo_path/$agent_path"

    # Write updated content
    echo "$content" > "$full_path"
    success "Updated $full_path"

    # Offer to commit
    echo ""
    read -p "Commit changes? (Y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        (
            cd "$repo_path"
            git add "$agent_path"
            git commit -m "docs(agents): apply god-mode recommendations

Applied recommendations from god-mode analysis:
- Improved agent instructions based on commit patterns
- Addressed identified gaps in documentation"
            success "Committed changes"
            
            read -p "Push to remote? (y/N): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git push
                success "Pushed to remote"
            fi
        )
    fi
}

# Update agent file via GitHub API
update_github_agent_file() {
    local repo="$1"
    local path="$2"
    local content="$3"

    info "Updating $path via GitHub API"

    # Get current file SHA
    local file_info
    file_info=$(gh api "repos/$repo/contents/$path" 2>/dev/null)
    local sha=$(echo "$file_info" | jq -r '.sha')

    if [[ -z "$sha" || "$sha" == "null" ]]; then
        error "Could not fetch current file SHA"
        return 1
    fi

    # Base64 encode content
    local encoded_content
    encoded_content=$(echo "$content" | base64 -w 0)

    # Update file
    gh api "repos/$repo/contents/$path" -X PUT \
        -f message="docs(agents): apply god-mode recommendations" \
        -f content="$encoded_content" \
        -f sha="$sha" \
        --silent >/dev/null

    if [[ $? -eq 0 ]]; then
        success "Updated $path on GitHub"
    else
        error "Failed to update file on GitHub"
        return 1
    fi
}

#!/bin/bash
set -e

INPUT="$1"

if [ -z "$INPUT" ]; then
    echo "Error: Project name or path required" >&2
    exit 1
fi

# 1. Check if it's a path
if [[ "$INPUT" =~ ^/ ]] || [[ "$INPUT" =~ ^~ ]] || [[ "$INPUT" =~ ^\.\./ ]] || [[ "$INPUT" =~ ^\./ ]]; then
    # It's a path, expand and validate
    EXPANDED=$(eval echo "$INPUT")
    if [ -d "$EXPANDED" ]; then
        echo "$EXPANDED"
        exit 0
    else
        echo "Error: Directory not found: $EXPANDED" >&2
        exit 1
    fi
fi

# 2. Workspace exact match
WORKSPACE="/root/.openclaw/workspace"
if [ -d "$WORKSPACE/$INPUT" ]; then
    echo "$WORKSPACE/$INPUT"
    exit 0
fi

# 3. Workspace fuzzy match
MATCHES=$(find "$WORKSPACE" -maxdepth 1 -type d -iname "*$INPUT*" 2>/dev/null | grep -v "^$WORKSPACE$" || true)

if [ -n "$MATCHES" ]; then
    MATCH_COUNT=$(echo "$MATCHES" | wc -l)

    if [ "$MATCH_COUNT" -eq 1 ]; then
        echo "$MATCHES"
        exit 0
    else
        echo "Error: Multiple matches found for '$INPUT':" >&2
        echo "" >&2
        echo "$MATCHES" | while read -r match; do
            echo "  - $match" >&2
        done
        echo "" >&2
        echo "Please be more specific." >&2
        exit 1
    fi
fi

# 4. Git repository search
GIT_REPOS=$(find "$WORKSPACE" -maxdepth 2 -type d -name ".git" 2>/dev/null | while read gitdir; do
    dirname "$gitdir"
done | grep -i "$INPUT" || true)

if [ -n "$GIT_REPOS" ]; then
    REPO_COUNT=$(echo "$GIT_REPOS" | wc -l)

    if [ "$REPO_COUNT" -eq 1 ]; then
        echo "$GIT_REPOS"
        exit 0
    else
        echo "Error: Multiple git repos found for '$INPUT':" >&2
        echo "" >&2
        echo "$GIT_REPOS" | while read -r repo; do
            echo "  - $repo" >&2
        done
        exit 1
    fi
fi

# 5. Project marker search
for marker in Cargo.toml go.mod pom.xml build.gradle build.gradle.kts; do
    PROJ_DIRS=$(find "$WORKSPACE" -name "$marker" 2>/dev/null | while read markerfile; do
        dirname "$markerfile"
    done | grep -i "$INPUT" || true)

    if [ -n "$PROJ_DIRS" ]; then
        PROJ_COUNT=$(echo "$PROJ_DIRS" | wc -l)

        if [ "$PROJ_COUNT" -eq 1 ]; then
            echo "$PROJ_DIRS"
            exit 0
        fi
    fi
done

# 6. Home directory search
HOME_DIR="/root"
HOME_MATCHES=$(find "$HOME_DIR" -maxdepth 2 -type d -iname "*$INPUT*" 2>/dev/null | grep -v "^$HOME_DIR$" || true)

if [ -n "$HOME_MATCHES" ]; then
    HOME_COUNT=$(echo "$HOME_MATCHES" | wc -l)

    if [ "$HOME_COUNT" -eq 1 ]; then
        echo "$HOME_MATCHES"
        exit 0
    fi
fi

# 7. Not found
echo "Error: Could not find project '$INPUT'" >&2
echo "" >&2
echo "Searched in:" >&2
echo "  - Workspace: $WORKSPACE" >&2
echo "  - Home: $HOME_DIR" >&2
echo "  - Git repositories" >&2
echo "  - Project directories (with Cargo.toml, go.mod, pom.xml, etc.)" >&2
echo "" >&2
echo "Found 0 matches." >&2
exit 1

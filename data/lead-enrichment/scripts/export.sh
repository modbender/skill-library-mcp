#!/bin/bash
# lead-enrichment/scripts/export.sh — Export enriched leads to different formats

set -euo pipefail

# --- Argument Parsing ---
FORMAT="json" # Default format
FILES=()

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --format) FORMAT="$2"; shift ;;
        -h|--help)
            echo "Usage: ./export.sh [--format <json|markdown|csv>] [file1.json file2.json ...]"
            exit 0
            ;;
        *)
            # Assume any other argument is a file
            FILES+=("$1")
            ;;
    esac
    shift
done

# --- Input Validation ---
if [ ${#FILES[@]} -eq 0 ]; then
    echo "Error: No input files provided."
    echo "Usage: ./export.sh --format csv enriched/*.json"
    exit 1
fi

# --- Main Logic ---

# Read all file contents into a single stream for jq
JSON_STREAM=$(jq -s '.' "${FILES[@]}")

case $FORMAT in
    json)
        echo "$JSON_STREAM" | jq '.' # Pretty-print the combined JSON array
        ;;

    markdown)
        echo "$JSON_STREAM" | jq -r '
        .[] | 
        "## " + .profile.full_name + " - " + .profile.title + " @ " + .company.name + "\n\n" +
        "**Bio:** " + .profile.bio + "\n\n" +
        "**Location:** " + .profile.location + "\n\n" +
        "**Social:**\n" +
        "  - LinkedIn: " + .profile.social_profiles.linkedin + "\n" +
        "  - Twitter: " + .profile.social_profiles.twitter + "\n\n" +
        "**Company:** " + .company.description + " (" + .company.size + ")\n\n" +
        "**Talking Points:**\n" +
        (.talking_points | map("- " + .) | join("\n")) + "\n\n" +
        "---"
        '
        ;;

    csv)
        # Define headers
        HEADER="\"Full Name\",\"Title\",\"Company\",\"Location\",\"LinkedIn\",\"Twitter\",\"Company Domain\",\"Recent News Title\",\"Talking Point 1\""
        echo "$HEADER"
        
        # Extract data
        echo "$JSON_STREAM" | jq -r '
        .[] | 
        [
            .profile.full_name,
            .profile.title,
            .company.name,
            .profile.location,
            .profile.social_profiles.linkedin,
            .profile.social_profiles.twitter,
            .company.domain,
            (.company.recent_news[0].title // ""),
            (.talking_points[0] // "")
        ] | @csv'
        ;;

    *)
        echo "Error: Unsupported format '$FORMAT'. Use json, markdown, or csv."
        exit 1
        ;;
esac

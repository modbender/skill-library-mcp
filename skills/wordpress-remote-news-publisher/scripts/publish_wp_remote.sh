#!/bin/bash
# =============================================================================
# publish_wp_remote.sh
# Creates a WordPress post as a draft via WP-CLI executed remotely via SSH.
# Sets featured image, tags, and Yoast SEO metadata.
# =============================================================================

set -euo pipefail

# --- SSH Configuration from Environment Variables ---
SSH_HOST="${WP_SSH_HOST:-}"
SSH_USER="${WP_SSH_USER:-}"
SSH_KEY="${WP_SSH_KEY:-}"
SSH_PORT="${WP_SSH_PORT:-22}"
REMOTE_PATH="${WP_REMOTE_PATH:-/var/www/html/wordpress}"
AUTHOR_ID="${WP_AUTHOR_ID:-1}"

# --- SSH Options ---
SSH_OPTS="-i $SSH_KEY -p $SSH_PORT \
          -o StrictHostKeyChecking=no \
          -o BatchMode=yes \
          -o ConnectTimeout=15 \
          -o PasswordAuthentication=no"

# --- Input Validation ---
if [ -z "$SSH_HOST" ] || [ -z "$SSH_USER" ] || [ -z "$SSH_KEY" ]; then
    echo "ERROR: WP_SSH_HOST, WP_SSH_USER, and WP_SSH_KEY are required" >&2
    exit 1
fi

# --- Read Article Data from JSON ---
ARTICLE_JSON="/tmp/wp_article.json"

if [ ! -f "$ARTICLE_JSON" ]; then
    echo "ERROR: Article JSON not found: $ARTICLE_JSON" >&2
    echo "Generate article data first using the article generation phase." >&2
    exit 1
fi

if [ ! -f /tmp/wp_media_id.txt ]; then
    echo "ERROR: Media ID file not found: /tmp/wp_media_id.txt" >&2
    echo "Upload cover image first." >&2
    exit 1
fi

# Extract article data using Python
TITLE=$(python3 -c "import json; d=json.load(open('$ARTICLE_JSON')); print(d['title'])")
CONTENT=$(python3 -c "import json; d=json.load(open('$ARTICLE_JSON')); print(d['content'])")
EXCERPT=$(python3 -c "import json; d=json.load(open('$ARTICLE_JSON')); print(d['excerpt'])")
TAGS=$(python3 -c "import json; d=json.load(open('$ARTICLE_JSON')); print(','.join(d['tags']))")
META_DESC=$(python3 -c "import json; d=json.load(open('$ARTICLE_JSON')); print(d['meta_desc'])")
KEYWORD=$(python3 -c "import json; d=json.load(open('$ARTICLE_JSON')); print(d['keyword'])")
MEDIA_ID=$(cat /tmp/wp_media_id.txt)

echo "Publishing article: $TITLE"

# --- Transfer Article JSON to Remote Server ---
# Long content may cause issues with inline SSH, so we transfer a temp file
TIMESTAMP=$(date +%s)
REMOTE_ARTICLE_JSON="${REMOTE_TMP:-/tmp}/wp_article_remote_${TIMESTAMP}.json"

echo "Transferring article JSON to remote server..."

scp $SSH_OPTS "$ARTICLE_JSON" "$SSH_USER@$SSH_HOST:$REMOTE_ARTICLE_JSON" || {
    echo "ERROR: Failed to transfer article JSON to remote server" >&2
    exit 1
}

# --- Create Draft Post via WP-CLI (remote) ---
echo "Creating draft post on WordPress..."

POST_ID=$(ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" bash <<ENDSSH
    python3 -c "import json; d=json.load(open('$REMOTE_ARTICLE_JSON')); print(d['title'], end='')" > /tmp/wp_title.txt
    python3 -c "import json; d=json.load(open('$REMOTE_ARTICLE_JSON')); print(d['content'], end='')" > /tmp/wp_content.txt
    python3 -c "import json; d=json.load(open('$REMOTE_ARTICLE_JSON')); print(d['excerpt'], end='')" > /tmp/wp_excerpt.txt
    
    wp post create \\
        --post_title="file:///tmp/wp_title.txt" \\
        --post_content="file:///tmp/wp_content.txt" \\
        --post_excerpt="file:///tmp/wp_excerpt.txt" \\
        --post_status=draft \\
        --post_author=$AUTHOR_ID \\
        --post_type=post \\
        --path="$REMOTE_PATH" \\
        --porcelain 2>/dev/null
ENDSSH
)

if [ -z "$POST_ID" ]; then
    echo "ERROR: wp post create returned no ID" >&2
    ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" "rm -f '$REMOTE_ARTICLE_JSON'" 2>/dev/null || true
    exit 1
fi

echo "Draft post created with ID: $POST_ID"

# --- Set Featured Image ---
echo "Setting featured image (Media ID: $MEDIA_ID)..."

ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" \
    "wp post meta update $POST_ID _thumbnail_id $MEDIA_ID \
     --path='$REMOTE_PATH'" 2>/dev/null || {
    echo "WARNING: Failed to set featured image" >&2
}

# --- Add Tags ---
if [ -n "$TAGS" ]; then
    echo "Adding tags: $TAGS"
    
    # Split comma-separated tags and add individually
    IFS=',' read -ra TAG_ARRAY <<< "$TAGS"
    for tag in "${TAG_ARRAY[@]}"; do
        ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" \
            "wp post term add $POST_ID post_tag '$tag' \
             --path='$REMOTE_PATH'" 2>/dev/null || true
    done
fi

# --- Add Yoast SEO Metadata ---
if [ -n "$META_DESC" ]; then
    echo "Adding Yoast meta description..."
    
    ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" \
        "wp post meta update $POST_ID _yoast_wpseo_metadesc '$META_DESC' \
         --path='$REMOTE_PATH'" 2>/dev/null || {
        echo "WARNING: Failed to set Yoast meta description" >&2
    }
fi

if [ -n "$KEYWORD" ]; then
    echo "Adding Yoast focus keyword: $KEYWORD"
    
    ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" \
        "wp post meta update $POST_ID _yoast_wpseo_focuskw '$KEYWORD' \
         --path='$REMOTE_PATH'" 2>/dev/null || {
        echo "WARNING: Failed to set Yoast focus keyword" >&2
    }
fi

# --- Cleanup Remote Temp Files ---
echo "Cleaning up remote temp files..."
ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" "rm -f '$REMOTE_ARTICLE_JSON' /tmp/wp_title.txt /tmp/wp_content.txt /tmp/wp_excerpt.txt" 2>/dev/null || true

# --- Save Post ID for Later Use ---
echo "$POST_ID" > /tmp/wp_post_id.txt

echo ""
echo "========================================"
echo "Post successfully created!"
echo "========================================"
echo "Post ID:     $POST_ID"
echo "Title:       $TITLE"
echo "Status:      draft"
echo "Media ID:    $MEDIA_ID"
echo "Tags:        ${TAGS:-none}"
echo "Keyword:     ${KEYWORD:-none}"
echo ""
echo "To publish: wp post update $POST_ID --post_status=publish"
echo "========================================"

exit 0

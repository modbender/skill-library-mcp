#!/usr/bin/env bash
# jmail-duckdb.sh — Query Epstein archive via DuckDB + Parquet
#
# Downloads parquet files to local cache on first use, then queries locally.
# Small files (<1MB) are always cached. Large files (emails, documents) downloaded on demand.
#
# Commands:
#   search "query"                    — Search email subjects/senders
#   person "Name"                     — All emails from/to a person
#   imessages "slug"                  — iMessages for a conversation slug
#   imessage-search "query" [--from]  — Search ALL iMessages for text (optional --from "Name")
#   imessage-list                     — List all iMessage conversations
#   network "Name"                    — Communication partners of a person
#   timeline "2005-01-01" "2005-12-31" — Emails in a date range
#   top-senders [limit]               — Top email senders
#   people [limit]                    — List identified people
#   documents "query"                 — Search document descriptions
#   photos "person-name"              — Photos of a person (by face recognition)
#   photo-search "query"              — Search ALL photos by AI description
#   photo-download "filename" [dir]   — Download photo as PNG (extracts from DOJ PDF)
#   download "DOC_ID" [dir]           — Download any document/email/photo by ID
#   stars                             — Star counts by entity type
#   (raw SQL removed for security — use DuckDB directly if needed)

set -euo pipefail

# Check DuckDB
if ! command -v duckdb &>/dev/null; then
  echo "⚠️  DuckDB not found. Install it manually:"
  echo "   apt install duckdb  OR  brew install duckdb"
  echo "   OR: https://duckdb.org/docs/installation/"
  exit 1
fi

# Sanitize text input for SQL ILIKE patterns.
# WHITELIST approach: only allow safe characters. Everything else is stripped.
# This prevents SQL injection (OR 1=1, UNION, subqueries, etc.)
sanitize() {
  local val="$1"
  # Allow only: letters (unicode), digits, spaces, hyphens, dots, underscores, @, commas
  # Strip EVERYTHING else (quotes, semicolons, parens, operators, etc.)
  val=$(printf '%s' "$val" | sed 's/[^a-zA-Z0-9 _.@,àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸčćšžŠŽ-]//g')
  # Truncate to 200 chars to prevent buffer abuse
  val="${val:0:200}"
  echo "$val"
}

# Validate integer input (for LIMIT etc.)
validate_int() {
  local val="$1"
  local default="${2:-20}"
  if [[ "$val" =~ ^[0-9]+$ ]] && [[ "$val" -gt 0 ]] && [[ "$val" -le 1000 ]]; then
    echo "$val"
  else
    echo "$default"
  fi
}

# Validate date format (YYYY-MM-DD)
validate_date() {
  local val="$1"
  if [[ "$val" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "$val"
  else
    echo "ERROR: Invalid date format. Use YYYY-MM-DD" >&2
    exit 1
  fi
}

# Cache directory
CACHE_DIR="/tmp/jmail-cache"
mkdir -p "$CACHE_DIR"

BASE="https://data.jmail.world/v1"

# Download a parquet file if not cached (or if older than 24h)
ensure_cached() {
  local name="$1"
  # Validate filename: only allow alphanumeric, underscores, hyphens, dots
  if [[ ! "$name" =~ ^[a-zA-Z0-9_.-]+\.parquet$ ]]; then
    echo "ERROR: Invalid parquet filename: ${name}" >&2
    exit 1
  fi
  local local_path="${CACHE_DIR}/${name}"
  
  # Re-download if older than 24 hours or doesn't exist
  if [[ ! -f "$local_path" ]] || [[ $(find "$local_path" -mmin +1440 2>/dev/null) ]]; then
    echo "📥 Downloading ${name}..." >&2
    curl -fsSL "${BASE}/${name}" -o "${local_path}.tmp"
    mv "${local_path}.tmp" "$local_path"
  fi
  echo "$local_path"
}

# Get path for a dataset — downloads if needed
get_path() {
  local name="$1"
  ensure_cached "$name"
}

run_query() {
  duckdb -c "$1" 2>&1
}

CMD="${1:?Usage: jmail-duckdb.sh <command> [args...]
Commands: search, person, imessages, imessage-list, network, timeline, top-senders, people, documents, photos, stars}"
shift

case "$CMD" in
  search)
    QUERY=$(sanitize "${1:?Usage: jmail-duckdb.sh search \"query\"}")
    SLIM=$(get_path "emails-slim.parquet")
    echo "🔍 Searching emails for: ${QUERY}"
    run_query "
      SELECT id, sender, subject, sent_at, epstein_is_sender
      FROM read_parquet('${SLIM}')
      WHERE subject ILIKE '%${QUERY}%'
         OR sender ILIKE '%${QUERY}%'
      ORDER BY sent_at DESC
      LIMIT 30;
    "
    ;;

  person)
    NAME=$(sanitize "${1:?Usage: jmail-duckdb.sh person \"Name\"}")
    SLIM=$(get_path "emails-slim.parquet")
    echo "👤 Emails involving: ${NAME}"
    run_query "
      SELECT id, sender, subject, sent_at, to_recipients, epstein_is_sender
      FROM read_parquet('${SLIM}')
      WHERE sender ILIKE '%${NAME}%'
         OR to_recipients::VARCHAR ILIKE '%${NAME}%'
         OR cc_recipients::VARCHAR ILIKE '%${NAME}%'
         OR bcc_recipients::VARCHAR ILIKE '%${NAME}%'
      ORDER BY sent_at DESC
      LIMIT 30;
    "
    ;;

  imessages)
    SLUG=$(sanitize "${1:?Usage: jmail-duckdb.sh imessages \"slug\"}")
    MSGS=$(get_path "imessage_messages.parquet")
    echo "💬 iMessages for: ${SLUG}"
    run_query "
      SELECT sender_name, text, timestamp
      FROM read_parquet('${MSGS}')
      WHERE conversation_slug = '${SLUG}'
      ORDER BY message_index
      LIMIT 100;
    "
    ;;

  imessage-search)
    QUERY=$(sanitize "${1:?Usage: jmail-duckdb.sh imessage-search \"query\" [--from \"Name\"]}")
    shift
    FROM_FILTER=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --from) FROM_NAME=$(sanitize "${2:?--from requires a name}"); FROM_FILTER="AND conversation_slug = '${FROM_NAME}'"; shift 2 ;;
        *) shift ;;
      esac
    done
    MSGS=$(get_path "imessage_messages.parquet")
    CONVOS=$(get_path "imessage_conversations.parquet")
    echo "💬 Searching iMessages for: ${QUERY}"
    # If --from is a name (not a slug), try to resolve it
    if [[ -n "$FROM_FILTER" ]]; then
      # Try matching conversation name first, fall back to slug
      RESOLVED_SLUG=$(duckdb -noheader -csv -c "
        SELECT slug FROM read_parquet('${CONVOS}')
        WHERE name ILIKE '%${FROM_NAME}%' OR slug = '${FROM_NAME}'
        LIMIT 1;
      " 2>/dev/null | head -1)
      if [[ -n "$RESOLVED_SLUG" ]]; then
        FROM_FILTER="AND m.conversation_slug = '${RESOLVED_SLUG}'"
        echo "   (filtered to: ${RESOLVED_SLUG})"
      else
        echo "   ⚠️  No conversation found for '${FROM_NAME}', searching all"
        FROM_FILTER=""
      fi
    fi
    run_query "
      SELECT c.name as conversation, m.sender, m.text, m.time
      FROM read_parquet('${MSGS}') m
      JOIN read_parquet('${CONVOS}') c ON m.conversation_slug = c.slug
      WHERE m.text ILIKE '%${QUERY}%'
      ${FROM_FILTER}
      ORDER BY m.timestamp
      LIMIT 50;
    "
    ;;

  imessage-list)
    CONVOS=$(get_path "imessage_conversations.parquet")
    echo "💬 iMessage Conversations:"
    run_query "
      SELECT name, slug, message_count, last_message_time, confirmed
      FROM read_parquet('${CONVOS}')
      ORDER BY message_count DESC;
    "
    ;;

  network)
    NAME=$(sanitize "${1:?Usage: jmail-duckdb.sh network \"Name\"}")
    SLIM=$(get_path "emails-slim.parquet")
    echo "🕸️  Communication network for: ${NAME}"
    echo ""
    echo "--- Sent TO (from ${NAME}): ---"
    run_query "
      SELECT to_recipients::VARCHAR as recipient, COUNT(*) as emails
      FROM read_parquet('${SLIM}')
      WHERE sender ILIKE '%${NAME}%'
      GROUP BY to_recipients::VARCHAR
      ORDER BY emails DESC
      LIMIT 20;
    "
    echo ""
    echo "--- Received FROM (to ${NAME}): ---"
    run_query "
      SELECT sender, COUNT(*) as emails
      FROM read_parquet('${SLIM}')
      WHERE to_recipients::VARCHAR ILIKE '%${NAME}%'
         OR cc_recipients::VARCHAR ILIKE '%${NAME}%'
      GROUP BY sender
      ORDER BY emails DESC
      LIMIT 20;
    "
    ;;

  timeline)
    START=$(validate_date "${1:?Usage: jmail-duckdb.sh timeline \"YYYY-MM-DD\" \"YYYY-MM-DD\"}")
    END=$(validate_date "${2:?Usage: jmail-duckdb.sh timeline \"YYYY-MM-DD\" \"YYYY-MM-DD\"}")
    SLIM=$(get_path "emails-slim.parquet")
    echo "📅 Emails from ${START} to ${END}:"
    run_query "
      SELECT id, sender, subject, sent_at, to_recipients
      FROM read_parquet('${SLIM}')
      WHERE sent_at >= '${START}'
        AND sent_at <= '${END}T23:59:59.999Z'
      ORDER BY sent_at DESC
      LIMIT 50;
    "
    ;;

  top-senders)
    LIMIT=$(validate_int "${1:-20}" 20)
    SLIM=$(get_path "emails-slim.parquet")
    echo "📊 Top ${LIMIT} email senders:"
    run_query "
      SELECT sender, COUNT(*) as n
      FROM read_parquet('${SLIM}')
      GROUP BY sender
      ORDER BY n DESC
      LIMIT ${LIMIT};
    "
    ;;

  people)
    LIMIT=$(validate_int "${1:-50}" 50)
    PPL=$(get_path "people.parquet")
    FACES=$(get_path "photo_faces.parquet")
    echo "👥 Identified people (${LIMIT}):"
    run_query "
      SELECT p.id, p.name, p.source, p.photo_count,
             COALESCE(f.appearances, 0) as face_appearances
      FROM read_parquet('${PPL}') p
      LEFT JOIN (
        SELECT person_id, COUNT(*) as appearances
        FROM read_parquet('${FACES}')
        GROUP BY person_id
      ) f ON p.id = f.person_id
      ORDER BY p.photo_count DESC
      LIMIT ${LIMIT};
    "
    ;;

  documents)
    QUERY=$(sanitize "${1:?Usage: jmail-duckdb.sh documents \"query\"}")
    DOCS=$(get_path "documents.parquet")
    echo "📄 Documents matching: ${QUERY}"
    run_query "
      SELECT id, original_filename, document_description, page_count, source
      FROM read_parquet('${DOCS}')
      WHERE document_description ILIKE '%${QUERY}%'
         OR original_filename ILIKE '%${QUERY}%'
      LIMIT 30;
    "
    ;;

  photos)
    NAME=$(sanitize "${1:?Usage: jmail-duckdb.sh photos \"person-name\"}")
    PPL=$(get_path "people.parquet")
    FACES=$(get_path "photo_faces.parquet")
    echo "📸 Photos of: ${NAME}"
    run_query "
      SELECT p.name, pf.*
      FROM read_parquet('${FACES}') pf
      JOIN read_parquet('${PPL}') p ON pf.person_id = p.id
      WHERE p.name ILIKE '%${NAME}%'
      LIMIT 30;
    "
    ;;

  photo-search)
    QUERY=$(sanitize "${1:?Usage: jmail-duckdb.sh photo-search \"query\"}")
    PHOTOS=$(get_path "photos.parquet")
    echo "📸 Photos matching: ${QUERY}"
    run_query "
      SELECT original_filename,
             CASE WHEN length(image_description) > 120
                  THEN substr(image_description, 1, 120) || '...'
                  ELSE image_description END as description,
             width || 'x' || height as size
      FROM read_parquet('${PHOTOS}')
      WHERE image_description ILIKE '%${QUERY}%'
         OR original_filename ILIKE '%${QUERY}%'
      LIMIT 30;
    "
    echo ""
    echo "💡 Download with: jmail-duckdb.sh photo-download <filename>"
    echo "   Example: jmail-duckdb.sh photo-download EFTA00000002-0.png"
    ;;

  photo-download)
    FILENAME="${1:?Usage: jmail-duckdb.sh photo-download \"EFTA00000002-0.png\" [output-dir]}"
    OUTDIR="${2:-.}"
    # Validate OUTDIR: whitelist safe path characters only
    SAFE_PATH='^[a-zA-Z0-9/._~ -]+$'
    if [[ ! "$OUTDIR" =~ $SAFE_PATH ]]; then
      echo "❌ Invalid output directory. Only alphanumeric, slashes, dots, hyphens, underscores, spaces, tildes allowed."
      exit 1
    fi
    OUTDIR=$(realpath -m "$OUTDIR" 2>/dev/null || echo "$OUTDIR")
    if [[ ! -d "$OUTDIR" ]]; then
      echo "❌ Output directory does not exist: ${OUTDIR}"
      exit 1
    fi
    # Strip extension and page suffix to get doc ID: EFTA00000002-0.png → EFTA00000002
    DOC_ID=$(echo "$FILENAME" | sed 's/\.[^.]*$//' | sed 's/-[0-9]*$//')
    # Validate: only allow alphanumeric, underscores, hyphens
    if [[ ! "$DOC_ID" =~ ^[a-zA-Z0-9_-]+$ ]]; then
      echo "❌ Invalid filename. Only alphanumeric, underscores, hyphens allowed."
      exit 1
    fi

    # House Oversight photos are JPGs at /photos/, DOJ photos are PDFs at /documents/
    if [[ "$DOC_ID" == HOUSE_OVERSIGHT_* ]]; then
      URL="https://assets.getkino.com/photos/${DOC_ID}.jpg"
      echo "📥 Downloading ${DOC_ID}.jpg (House Oversight)..."
      curl -fsSL "$URL" -o "${OUTDIR}/${DOC_ID}.jpg" 2>&1
      if [[ $? -eq 0 ]]; then
        echo "✅ Saved: ${OUTDIR}/${DOC_ID}.jpg ($(stat -c%s "${OUTDIR}/${DOC_ID}.jpg" 2>/dev/null || stat -f%z "${OUTDIR}/${DOC_ID}.jpg" 2>/dev/null) bytes)"
      else
        echo "❌ Download failed."
      fi
    else
      PDF_URL="https://assets.getkino.com/documents/${DOC_ID}.pdf"
      echo "📥 Downloading ${DOC_ID}.pdf (DOJ)..."
      TMPDIR=$(mktemp -d)
      curl -fsSL "$PDF_URL" -o "${TMPDIR}/${DOC_ID}.pdf" 2>&1
      if [[ $? -ne 0 ]]; then
        echo "❌ Download failed. Check the filename."
        rm -rf "$TMPDIR"
        exit 1
      fi
      # Extract images from PDF
      if command -v pdfimages &>/dev/null; then
        pdfimages -png "${TMPDIR}/${DOC_ID}.pdf" "${TMPDIR}/img" 2>/dev/null
        IMG_COUNT=$(ls "${TMPDIR}"/img-*.png 2>/dev/null | wc -l)
        if [[ "$IMG_COUNT" -eq 0 ]]; then
          echo "⚠️  No images extracted. Saving PDF instead."
          cp "${TMPDIR}/${DOC_ID}.pdf" "${OUTDIR}/${DOC_ID}.pdf"
          echo "✅ Saved: ${OUTDIR}/${DOC_ID}.pdf"
        elif [[ "$IMG_COUNT" -eq 1 ]]; then
          mv "${TMPDIR}"/img-000.png "${OUTDIR}/${DOC_ID}.png"
          echo "✅ Saved: ${OUTDIR}/${DOC_ID}.png ($(stat -c%s "${OUTDIR}/${DOC_ID}.png" 2>/dev/null || stat -f%z "${OUTDIR}/${DOC_ID}.png" 2>/dev/null) bytes)"
        else
          for f in "${TMPDIR}"/img-*.png; do
            base=$(basename "$f")
            mv "$f" "${OUTDIR}/${DOC_ID}-${base#img-}"
          done
          echo "✅ Saved ${IMG_COUNT} images to ${OUTDIR}/ (${DOC_ID}-*.png)"
        fi
      else
        cp "${TMPDIR}/${DOC_ID}.pdf" "${OUTDIR}/${DOC_ID}.pdf"
        echo "⚠️  pdfimages not found. Saved as PDF: ${OUTDIR}/${DOC_ID}.pdf"
        echo "   Install poppler-utils for automatic image extraction."
      fi
      rm -rf "$TMPDIR"
    fi
    ;;

  download)
    DOC_ID="${1:?Usage: jmail-duckdb.sh download \"DOC_ID\" [output-dir]}"
    # Strip common extensions, then validate: only allow alphanumeric, underscores, hyphens, dots
    DOC_ID=$(echo "$DOC_ID" | sed 's/\.\(pdf\|jpg\|png\|JPG\|PNG\)$//')
    if [[ ! "$DOC_ID" =~ ^[a-zA-Z0-9_.-]+$ ]]; then
      echo "❌ Invalid document ID. Only alphanumeric, underscores, hyphens, dots allowed."
      exit 1
    fi
    OUTDIR="${2:-.}"
    SAFE_PATH='^[a-zA-Z0-9/._~ -]+$'
    if [[ ! "$OUTDIR" =~ $SAFE_PATH ]]; then
      echo "❌ Invalid output directory. Only alphanumeric, slashes, dots, hyphens, underscores, spaces, tildes allowed."
      exit 1
    fi
    OUTDIR=$(realpath -m "$OUTDIR" 2>/dev/null || echo "$OUTDIR")
    if [[ ! -d "$OUTDIR" ]]; then
      echo "❌ Output directory does not exist: ${OUTDIR}"
      exit 1
    fi

    # Determine URL based on ID pattern
    if [[ "$DOC_ID" == HOUSE_OVERSIGHT_* ]]; then
      # Check if it's a photo (JPG) or a document
      PHOTOS=$(get_path "photos.parquet")
      IS_PHOTO=$(duckdb -noheader -csv -c "
        SELECT COUNT(*) FROM read_parquet('${PHOTOS}')
        WHERE original_filename LIKE '${DOC_ID}%'
      " 2>/dev/null | head -1)
      if [[ "$IS_PHOTO" -gt 0 ]]; then
        URL="https://assets.getkino.com/photos/${DOC_ID}.jpg"
        echo "📥 Downloading ${DOC_ID}.jpg (House Oversight photo)..."
        curl -fsSL "$URL" -o "${OUTDIR}/${DOC_ID}.jpg" 2>&1
        if [[ $? -eq 0 ]]; then
          echo "✅ Saved: ${OUTDIR}/${DOC_ID}.jpg"
        else
          echo "❌ Download failed."
        fi
      else
        echo "❌ House Oversight email documents are not available for direct download."
        echo "   View online: https://jmail.world/drive/${DOC_ID}"
      fi
    elif [[ "$DOC_ID" == EFTA* || "$DOC_ID" == vol* || "$DOC_ID" == COURT_giuffre* ]]; then
      URL="https://assets.getkino.com/documents/${DOC_ID}.pdf"
      echo "📥 Downloading ${DOC_ID}.pdf..."
      curl -fsSL "$URL" -o "${OUTDIR}/${DOC_ID}.pdf" 2>&1
      if [[ $? -eq 0 ]]; then
        SIZE=$(stat -c%s "${OUTDIR}/${DOC_ID}.pdf" 2>/dev/null || stat -f%z "${OUTDIR}/${DOC_ID}.pdf" 2>/dev/null)
        echo "✅ Saved: ${OUTDIR}/${DOC_ID}.pdf (${SIZE} bytes)"
      else
        echo "❌ Download failed. Check the document ID."
      fi
    else
      echo "❌ Unknown document type: ${DOC_ID}"
      echo "   Supported: EFTA*, vol*, HOUSE_OVERSIGHT_*, COURT_giuffre*"
      echo "   View online: https://jmail.world/drive/${DOC_ID}"
    fi
    ;;

  stars)
    STARS=$(get_path "star_counts.parquet")
    echo "⭐ Star counts by entity type:"
    run_query "
      SELECT entity_type, SUM(count) as total_stars, COUNT(*) as entities
      FROM read_parquet('${STARS}')
      GROUP BY entity_type
      ORDER BY total_stars DESC;
    "
    ;;

  *)
    echo "❌ Unknown command: ${CMD}"
    echo ""
    echo "Available commands:"
    echo "  search \"query\"                     — Search email subjects/senders"
    echo "  person \"Name\"                      — Emails from/to a person"
    echo "  imessages \"slug\"                   — iMessages for a conversation"
    echo "  imessage-search \"query\" [--from N] — Search ALL iMessages for text"
    echo "  imessage-list                       — List all iMessage conversations"
    echo "  network \"Name\"                     — Communication partners"
    echo "  timeline \"YYYY-MM-DD\" \"YYYY-MM-DD\" — Emails in date range"
    echo "  top-senders [limit]                 — Top email senders"
    echo "  people [limit]                      — List identified people"
    echo "  documents \"query\"                  — Search documents"
    echo "  photos \"person-name\"               — Photos of a person (face recognition)"
    echo "  photo-search \"query\"              — Search ALL photos by AI description"
    echo "  photo-download \"filename\" [dir]   — Download photo as PNG"
    echo "  download \"DOC_ID\" [dir]           — Download any doc/email/photo by ID"
    echo "  stars                               — Star counts by type"
    echo ""
    exit 1
    ;;
esac

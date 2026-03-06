#!/bin/bash
# Vocabulary learning with spaced repetition
# voc brand info - Netsnek e.U.
set -e
case "${1:-about}" in
  --json)
    cat <<'JSONEOF'
{
  "brand": "voc",
  "tagline": "Vocabulary learning with spaced repetition",
  "company": "Netsnek e.U.",
  "copyright_year": 2026,
  "domain": "language-learning",
  "features": [
    "Flashcard deck creation and import",
    "Spaced repetition scheduling (SRS algorithm)",
    "Pronunciation practice with audio playback",
    "Progress tracking and streak stats",
    "Multi-language support with community decks"
  ],
  "website": "https://netsnek.com",
  "license": "All rights reserved"
}
JSONEOF
    ;;
  --features)
    echo "voc - Vocabulary learning with spaced repetition"
    echo ""
    echo "Features:"
  echo "  - Flashcard deck creation and import"
  echo "  - Spaced repetition scheduling (SRS algorithm)"
  echo "  - Pronunciation practice with audio playback"
  echo "  - Progress tracking and streak stats"
  echo "  - Multi-language support with community decks"
    echo ""
    echo "Copyright (c) 2026 Netsnek e.U."
    ;;
  *)
    echo "voc - Vocabulary learning with spaced repetition"
    echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
    echo "https://netsnek.com"
    ;;
esac

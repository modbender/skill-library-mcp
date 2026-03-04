#!/usr/bin/env bash
set -euo pipefail

# Publish this skill to ClawHub with consistent metadata.
# Usage:
#   ./scripts/release_clawhub.sh 1.0.3 "optional changelog override"

VERSION="${1:-}"
CHANGELOG="${2:-}"

if [[ -z "$VERSION" ]]; then
  echo "Usage: $0 <version> [changelog]"
  echo "Example: $0 1.0.3 \"Metadata + security + UX improvements\""
  exit 1
fi

if ! command -v clawhub >/dev/null 2>&1; then
  echo "Error: clawhub CLI not found. Install with: npm i -g clawhub"
  exit 1
fi

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SLUG="hienergy-advertiser-intelligence-affiliate-copilot"
NAME="Hi Energy AI"
TAGS="hienergy,hi-energy-ai,affiliate-marketing,affiliate-network,affiliate-program-management,affiliate-program-discovery,affiliate-program-search,affiliate-deal-discovery,affiliate-deals,deals-feed,deal-feed,offer-feed,offers,deal-management,partner-marketing,commission-analysis,advertiser-intelligence,advertiser-search,advertiser-discovery,brand-search,brand-intelligence,publisher-contacts,transactions,performance-marketing,impact,rakuten,cj,awin,shareasale,partnerize,webgains,tradedoubler,admitad,avantlink,flexoffers,skimlinks,sovrn,pepperjam,optimise,linkconnector,tune,everflow,refersion"

if [[ -z "$CHANGELOG" ]]; then
  CHANGELOG="Release ${VERSION}: metadata coherence fixes, security hardening, improved SKILL readability, safer defaults, and ClawHub discoverability updates."
fi

echo "Publishing ${SLUG}@${VERSION} from ${SKILL_DIR}"

clawhub publish "$SKILL_DIR" \
  --slug "$SLUG" \
  --name "$NAME" \
  --version "$VERSION" \
  --tags "$TAGS" \
  --changelog "$CHANGELOG"

echo "Done."

#!/usr/bin/env bash
# Seedance 2.0 JiMeng — prompt helper test runner
# Usage:
#   ./SKILL.sh "your request"
# Example:
#   ./SKILL.sh "10s 9:16 fantasy reveal with @image1 and @video1"

set -euo pipefail

REQ="${1:-10s 9:16 cinematic prompt using @image1 as first frame and @video1 as camera reference}"

echo "Seedance 2.0 Prompt Helper"
echo "Request: $REQ"
echo ""
echo "Template output:"
cat <<'EOF'
Mode: All-Reference
Assets Mapping:
- @image1: first frame / character identity anchor
- @video1: camera language + motion rhythm
- @audio1: optional rhythm reference

Final Prompt:
9:16, 10s, cinematic, physically plausible motion.
0-3s: setup shot + subject intro.
3-7s: core action + controlled camera movement.
7-10s: climax/reveal + clean landing frame.

Negative Constraints:
no watermark, no logo, no subtitles, no on-screen text.
EOF

#!/bin/bash

# PixelDojo Available Models
# Lists popular models available via the API

cat <<'EOF'
PixelDojo Available Models
==========================

Image Generation:
  flux-2                  - Flux 2 (high quality)
  imagen-4               - Google Imagen 4
  pixverse               - Pixverse
  consistent-characters  - Character consistency

Video Generation:
  wan-2.6-flash          - WAN 2.6 Flash (fast)
  wan-2.2                - WAN 2.2 (higher quality)
  veo-3.1                - Google Veo 3.1 (with audio)
  kling-2.5-turbo-pro    - Kling 2.5 Turbo Pro
  kling-pro              - Kling Pro
  minimax                - Minimax

Usage:
  generate.sh image <prompt> <model> [options]
  generate.sh video <prompt> <model> [options]

Examples:
  generate.sh image "cyberpunk city" flux-2
  generate.sh video "ocean waves" wan-2.6-flash --duration 5
EOF

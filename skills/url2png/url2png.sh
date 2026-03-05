#!/usr/bin/env bash

url="${1:-https://simonwillison.net/2026/Feb/10/showboat-and-rodney}"
outdir=${2:-~/Pictures}
mkdir -p ${outdir}
# cd into outdir, let shot-scraper save with proper name
cd ${outdir}

# take long screenshot for iPhone by default
uvx shot-scraper shot "${url}" \
    --browser chromium \
    --width 390 \
    --retina \
    --wait 10000 \
    --timeout 30000

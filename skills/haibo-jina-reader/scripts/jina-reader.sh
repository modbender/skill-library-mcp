#!/usr/bin/env bash
# Jina Reader - 网页内容提取工具
# Usage: jina-reader.sh <url>

set -e

if [ -z "$1" ]; then
    echo "Usage: jina-reader.sh <url>"
    exit 1
fi

URL="$1"
JINA_API="https://r.jina.ai/http://${URL#http://}"

curl -s "$JINA_API"

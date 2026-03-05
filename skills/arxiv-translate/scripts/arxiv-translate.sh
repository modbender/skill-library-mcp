#!/bin/bash
# arxiv-translate skill - Generate translation link for arXiv papers

# Function to extract arXiv ID from input
extract_arxiv_id() {
    local input="$1"
    
    # If it's already just a numeric or alphanumeric ID (e.g., 2601.06798 or 1706.03762)
    if [[ "$input" =~ ^[0-9]{4}\.[0-9]{4,}(v[0-9]+)?$ ]]; then
        echo "$input"
        return
    fi
    
    # If it's a full URL, extract the ID
    # Supports: https://arxiv.org/abs/2601.06798, https://arxiv.org/pdf/2601.06798.pdf
    if [[ "$input" =~ arxiv\.org/(abs|pdf)/([0-9]+\.[0-9]+v?[0-9]*) ]]; then
        echo "${BASH_REMATCH[2]}"
        return
    fi
    
    # If it contains the ID pattern anywhere, try to extract
    if [[ "$input" =~ ([0-9]{4}\.[0-9]{4,}v?[0-9]*) ]]; then
        echo "${BASH_REMATCH[1]}"
        return
    fi
    
    # Return as-is if no pattern matched
    echo "$input"
}

# Main
INPUT="$1"

if [ -z "$INPUT" ]; then
    echo "Usage: arxiv-translate <arxiv_id_or_url>"
    echo "Example: arxiv-translate 2601.06798"
    echo "Example: arxiv-translate https://arxiv.org/abs/2601.06798"
    exit 1
fi

ARXIV_ID=$(extract_arxiv_id "$INPUT")

TRANSLATION_URL="https://hjfy.top/arxiv/${ARXIV_ID}"

echo "📄 论文 ID: ${ARXIV_ID}"
echo ""
echo "🌐 中文翻译链接:"
echo "${TRANSLATION_URL}"
echo ""
echo "📝 说明: 访问上述链接，翻译将自动生成。首次访问可能需要等待片刻。"

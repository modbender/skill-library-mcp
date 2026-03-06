#!/bin/bash
# Kaggle Dataset Downloader Helper
# Usage: ./download_kaggle.sh <dataset-name> [output-dir]

DATASET_NAME="$1"
OUTPUT_DIR="${2:-./datasets}"

if [ -z "$DATASET_NAME" ]; then
    echo "Usage: $0 <kaggle-dataset-name> [output-dir]"
    echo "Example: $0 csafrit2/steel-industry-energy-consumption"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Downloading dataset: $DATASET_NAME"
echo "Output directory: $OUTPUT_DIR"

# Check if kaggle CLI is installed
if ! command -v kaggle &> /dev/null; then
    echo "Error: kaggle CLI not found"
    echo "Install with: pip install kaggle"
    echo "Then configure with: kaggle competitions list"
    exit 1
fi

# Download dataset
kaggle datasets download -d "$DATASET_NAME" -p "$OUTPUT_DIR"

# Unzip if downloaded successfully
if [ $? -eq 0 ]; then
    echo "Download successful. Extracting..."
    cd "$OUTPUT_DIR"
    unzip -q *.zip
    rm *.zip
    echo "Dataset ready in: $OUTPUT_DIR"
    ls -la
else
    echo "Download failed"
    exit 1
fi

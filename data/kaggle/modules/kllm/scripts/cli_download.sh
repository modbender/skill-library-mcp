#!/usr/bin/env bash
# Download datasets and models from Kaggle using the kaggle-cli.
#
# Usage:
#   bash cli_download.sh                          # runs examples with defaults
#   bash cli_download.sh <dataset> [output-dir]   # download a specific dataset
#
# Examples:
#   bash cli_download.sh kaggle/meta-kaggle ./downloads/meta-kaggle
#   bash cli_download.sh heptapod/titanic ./downloads/titanic
#
# Prerequisites:
#   uv pip install kaggle
#   Credentials configured in ~/.kaggle/kaggle.json or env vars

set -euo pipefail

DATASET="${1:-kaggle/meta-kaggle}"
OUTPUT_DIR="${2:-./downloads/$(echo "$DATASET" | tr '/' '-')}"

echo "============================================================"
echo "kaggle-cli: Download Dataset"
echo "============================================================"

# List files in the dataset
echo "--- Listing dataset files for ${DATASET} ---"
kaggle datasets files "${DATASET}"

# Download the dataset
echo "--- Downloading dataset to ${OUTPUT_DIR} ---"
mkdir -p "${OUTPUT_DIR}"
kaggle datasets download "${DATASET}" \
    --path "${OUTPUT_DIR}" \
    --unzip

echo "Dataset downloaded to ${OUTPUT_DIR}"
ls -la "${OUTPUT_DIR}/"

#!/bin/bash
set -x

# Exit immediately if a command exits with a non-zero status.
set -e

# Arguments: urls_file_path output_dir venv_path
URLS_FILE="$1"
OUTPUT_DIR="$2"
VENV_PATH="$3"

# Check if virtual environment path is provided
if [ -z "$VENV_PATH" ]; then
    echo "Error: Virtual environment path not provided."
    exit 1
fi

# Activate the virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    echo "Activated virtual environment: $VENV_PATH"
else
    echo "Error: Virtual environment activation script not found at $VENV_PATH/bin/activate"
    exit 1
fi

# Run the Python scraper script
mkdir -p "$OUTPUT_DIR"
echo "DEBUG: Ensured output directory exists: $OUTPUT_DIR"
python "$(dirname "$0")/scrape_zoomin.py" "$URLS_FILE" "$OUTPUT_DIR"

# Deactivate is not strictly necessary in a sub-agent context as the shell exits,
# but it's good practice for general purpose scripts.
deactivate

echo "Scraping script finished."
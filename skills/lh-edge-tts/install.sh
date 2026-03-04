#!/bin/bash
# Edge-TTS Skill Installation Script

set -e

echo "Installing Edge-TTS Skill..."
echo ""

echo "Installing Python dependencies..."
pip install edge-tts

echo ""
echo "Edge-TTS Skill installed successfully!"
echo ""
echo "To test the installation:"
echo "  cd scripts"
echo "  python3 tts_converter.py \"Hello, this is a test.\" -o test-output.mp3"
echo ""
echo "For configuration:"
echo "  python3 config_manager.py --help"

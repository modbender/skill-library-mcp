#!/bin/bash
# Install script for Pocket TTS skill

echo "📦 Installing Pocket TTS dependencies..."

pip install torch scipy huggingface_hub

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "⚠️  IMPORTANT: Accept the model license at:"
echo "   https://huggingface.co/kyutai/pocket-tts"
echo ""
echo "Then test with:"
echo "   pocket-tts --model"

#!/bin/bash
# CosyVoice3 Installation Script for macOS Apple Silicon

set -e

echo "=== CosyVoice3 Installer for macOS ==="
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    if [ -f "$HOME/miniconda3/bin/conda" ]; then
        export PATH="$HOME/miniconda3/bin:$PATH"
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    else
        echo "❌ Conda not found. Installing Miniconda..."
        curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
        bash Miniconda3-latest-MacOSX-arm64.sh -b -p $HOME/miniconda3
        export PATH="$HOME/miniconda3/bin:$PATH"
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
        rm Miniconda3-latest-MacOSX-arm64.sh
    fi
fi

echo "✓ Conda found"

# Set workspace
WORKSPACE="/Users/lhz/.openclaw/workspace"
COSYVOICE_REPO="$WORKSPACE/cosyvoice3-repo"

# Clone repo if not exists
if [ ! -d "$COSYVOICE_REPO" ]; then
    echo "📥 Cloning CosyVoice repository..."
    cd "$WORKSPACE"
    git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git cosyvoice3-repo
    cd "$COSYVOICE_REPO"
    git submodule update --init --recursive
fi

echo "✓ Repository ready"

# Create conda environment
echo "🐍 Creating conda environment..."
if conda env list | grep -q "cosyvoice"; then
    echo "  Environment 'cosyvoice' already exists"
else
    conda create -n cosyvoice python=3.10 -y
fi

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate cosyvoice

echo "✓ Environment activated"

# Install PyTorch for Apple Silicon
echo "🔥 Installing PyTorch (CPU version for Apple Silicon)..."
pip install torch==2.3.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cpu

# Install core dependencies
echo "📦 Installing dependencies..."
pip install transformers==4.51.3 modelscope onnxruntime soundfile librosa numpy==1.26.4
pip install conformer==0.3.2 diffusers==0.29.0 fastapi==0.115.6 gradio==5.4.0
pip install hydra-core==1.3.2 HyperPyYAML==1.2.2 inflect==7.3.1 lightning==2.2.4
pip install matplotlib==3.7.5 networkx==3.1 omegaconf==2.3.0 onnx==1.16.0
pip install protobuf==4.25 pydantic==2.7.0 pyworld==0.3.4 rich==13.7.1
pip install tensorboard==2.14.0 x-transformers==2.11.24 wetext==0.0.4 wget==3.2

echo "✓ Dependencies installed"

# Download models
echo "📥 Downloading CosyVoice3 model (~2GB)..."
python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, '/Users/lhz/.openclaw/workspace/cosyvoice3-repo')

try:
    from modelscope import snapshot_download
    
    model_dir = '/Users/lhz/.openclaw/workspace/cosyvoice3-repo/pretrained_models/Fun-CosyVoice3-0.5B'
    if os.path.exists(model_dir):
        print("  Model already downloaded")
    else:
        print("  Downloading Fun-CosyVoice3-0.5B...")
        snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B-2512', local_dir=model_dir)
        print("  ✓ Model downloaded")
except Exception as e:
    print(f"  ⚠️  Model download failed: {e}")
    print("  You can manually download later using:")
    print("  python scripts/download_models.py")
PYEOF

echo ""
echo "=== Installation Complete ==="
echo ""
echo "To use CosyVoice3:"
echo "  export PATH=\"\$HOME/miniconda3/bin:\$PATH\""
echo "  conda activate cosyvoice"
echo ""
echo "Quick test:"
echo "  cd $COSYVOICE_REPO"
echo "  python example.py"
echo ""

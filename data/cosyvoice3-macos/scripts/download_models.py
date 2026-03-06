#!/usr/bin/env python3
"""
Download CosyVoice pretrained models
"""

import os
import sys
import argparse

# Add cosyvoice to path
sys.path.insert(0, '/Users/lhz/.openclaw/workspace/cosyvoice3-repo')

try:
    from modelscope import snapshot_download
except ImportError:
    print("Error: modelscope not installed")
    print("Run: pip install modelscope")
    sys.exit(1)


MODELS = {
    'cosyvoice3': {
        'model_id': 'FunAudioLLM/Fun-CosyVoice3-0.5B-2512',
        'local_dir': 'pretrained_models/Fun-CosyVoice3-0.5B',
        'description': 'Fun-CosyVoice3-0.5B (Recommended) - Best quality'
    },
    'cosyvoice2': {
        'model_id': 'iic/CosyVoice2-0.5B',
        'local_dir': 'pretrained_models/CosyVoice2-0.5B',
        'description': 'CosyVoice2-0.5B - Previous version'
    },
    'cosyvoice-300m': {
        'model_id': 'iic/CosyVoice-300M',
        'local_dir': 'pretrained_models/CosyVoice-300M',
        'description': 'CosyVoice-300M - Base model'
    },
    'cosyvoice-300m-sft': {
        'model_id': 'iic/CosyVoice-300M-SFT',
        'local_dir': 'pretrained_models/CosyVoice-300M-SFT',
        'description': 'CosyVoice-300M-SFT - Speaker-finetuned'
    },
    'cosyvoice-300m-instruct': {
        'model_id': 'iic/CosyVoice-300M-Instruct',
        'local_dir': 'pretrained_models/CosyVoice-300M-Instruct',
        'description': 'CosyVoice-300M-Instruct - Instruction support'
    }
}


def download_model(model_name, workspace_dir):
    """Download a specific model"""
    if model_name not in MODELS:
        print(f"Error: Unknown model '{model_name}'")
        print(f"Available models: {', '.join(MODELS.keys())}")
        return False
    
    model_info = MODELS[model_name]
    local_path = os.path.join(workspace_dir, model_info['local_dir'])
    
    if os.path.exists(local_path):
        print(f"✓ {model_name}: Already downloaded at {local_path}")
        return True
    
    print(f"📥 Downloading {model_name}...")
    print(f"   {model_info['description']}")
    print(f"   Model ID: {model_info['model_id']}")
    print(f"   Save to: {local_path}")
    print("")
    
    try:
        snapshot_download(model_info['model_id'], local_dir=local_path)
        print(f"✓ {model_name}: Download complete")
        return True
    except Exception as e:
        print(f"✗ {model_name}: Download failed - {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Download CosyVoice models')
    parser.add_argument(
        'models',
        nargs='*',
        help='Models to download (default: cosyvoice3)'
    )
    parser.add_argument(
        '--workspace',
        '-w',
        default='/Users/lhz/.openclaw/workspace/cosyvoice3-repo',
        help='CosyVoice workspace directory'
    )
    parser.add_argument(
        '--list',
        '-l',
        action='store_true',
        help='List available models'
    )
    parser.add_argument(
        '--all',
        '-a',
        action='store_true',
        help='Download all models'
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("Available models:")
        for name, info in MODELS.items():
            print(f"  {name:20} - {info['description']}")
        return
    
    # Determine which models to download
    if args.all:
        models_to_download = list(MODELS.keys())
    elif args.models:
        models_to_download = args.models
    else:
        models_to_download = ['cosyvoice3']
    
    # Download models
    print("=" * 60)
    print("CosyVoice Model Downloader")
    print("=" * 60)
    print(f"Workspace: {args.workspace}")
    print("")
    
    success_count = 0
    for model in models_to_download:
        if download_model(model, args.workspace):
            success_count += 1
        print("")
    
    print("=" * 60)
    print(f"Downloaded: {success_count}/{len(models_to_download)} models")
    print("=" * 60)


if __name__ == '__main__':
    main()

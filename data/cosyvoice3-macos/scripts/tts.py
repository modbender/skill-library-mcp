#!/usr/bin/env python3
"""
CosyVoice3 TTS Script for macOS
Simple CLI interface for text-to-speech synthesis
"""

import argparse
import sys
import os
import tempfile

# Add cosyvoice to path
sys.path.insert(0, '/Users/lhz/.openclaw/workspace/cosyvoice3-repo')
sys.path.insert(0, '/Users/lhz/.openclaw/workspace/cosyvoice3-repo/third_party/Matcha-TTS')

try:
    from cosyvoice.cli.cosyvoice import AutoModel
    import torchaudio
except ImportError as e:
    print(f"Error importing CosyVoice: {e}")
    print("Make sure to activate the conda environment:")
    print("  conda activate cosyvoice")
    sys.exit(1)


def get_default_reference():
    """Get default reference audio path"""
    default_path = '/Users/lhz/.openclaw/workspace/cosyvoice3-repo/asset/zero_shot_prompt.wav'
    if os.path.exists(default_path):
        return default_path
    return None


def tts_synthesize(text, output_path=None, reference_audio=None, speed=1.0, lang='zh'):
    """
    Synthesize text to speech using CosyVoice3
    
    Args:
        text: Text to synthesize
        output_path: Output audio file path (default: auto-generated in temp)
        reference_audio: Reference audio for voice cloning
        speed: Speech speed multiplier (0.5-2.0)
        lang: Language code (zh, en, ja, ko, etc.)
    
    Returns:
        Path to generated audio file
    """
    # Default output path
    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), f'cosyvoice3_{os.urandom(4).hex()}.wav')
    
    # Default reference audio
    if reference_audio is None:
        reference_audio = get_default_reference()
    
    if reference_audio is None or not os.path.exists(reference_audio):
        print(f"Error: Reference audio not found: {reference_audio}")
        print("Please provide a reference audio file with --reference")
        sys.exit(1)
    
    # Load model
    model_dir = '/Users/lhz/.openclaw/workspace/cosyvoice3-repo/pretrained_models/Fun-CosyVoice3-0.5B'
    
    if not os.path.exists(model_dir):
        print(f"Error: Model not found at {model_dir}")
        print("Please run the installation first:")
        print("  bash scripts/install.sh")
        sys.exit(1)
    
    print(f"Loading CosyVoice3 model...")
    cosyvoice = AutoModel(model_dir=model_dir)
    
    # Prepare reference text (simplified - should match reference audio content)
    # IMPORTANT: CosyVoice3 requires <|endofprompt|> token in the reference text
    if lang == 'zh':
        reference_text = "希望你以后能够做的比我还好呦。<|endofprompt|>"
    else:
        reference_text = "You are a helpful assistant.<|endofprompt|>"
    
    # Adjust speed using SSML-like tags if needed
    if speed != 1.0:
        # Note: CosyVoice3 supports speed control via instruct mode
        # For now, we use basic synthesis
        pass
    
    print(f"Synthesizing: {text[:50]}...")
    
    # Generate speech
    results = cosyvoice.inference_zero_shot(
        text,
        reference_text,
        reference_audio,
        stream=False
    )
    
    # Save audio
    for i, result in enumerate(results):
        if i == 0:
            torchaudio.save(output_path, result['tts_speech'], cosyvoice.sample_rate)
    
    print(f"✓ Generated: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='CosyVoice3 Text-to-Speech for macOS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic TTS
  python tts.py "你好，这是一个测试。"
  
  # With custom reference voice
  python tts.py "你好。" --reference /path/to/voice.wav
  
  # English text
  python tts.py "Hello world" --lang en
  
  # Save to specific file
  python tts.py "你好。" --output ~/Desktop/hello.wav
        """
    )
    
    parser.add_argument('text', help='Text to synthesize')
    parser.add_argument('--reference', '-r', help='Reference audio file for voice cloning')
    parser.add_argument('--output', '-o', help='Output audio file path')
    parser.add_argument('--speed', '-s', type=float, default=1.0, help='Speech speed (0.5-2.0)')
    parser.add_argument('--lang', '-l', default='zh', help='Language code (zh, en, ja, ko)')
    
    args = parser.parse_args()
    
    # Validate speed
    if args.speed < 0.5 or args.speed > 2.0:
        print("Error: Speed must be between 0.5 and 2.0")
        sys.exit(1)
    
    try:
        output = tts_synthesize(
            text=args.text,
            output_path=args.output,
            reference_audio=args.reference,
            speed=args.speed,
            lang=args.lang
        )
        print(f"\nAudio saved to: {output}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

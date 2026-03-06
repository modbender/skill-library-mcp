#!/usr/bin/env python3
"""
Subtitle Proofreader - AI-powered subtitle correction using DeepSeek
Usage: python3 subtitle_proofreader.py <vtt_file> | --all
"""

import argparse
import os
import re
import sys
from pathlib import Path

def extract_text_from_vtt(vtt_path):
    """Extract plain text from VTT file"""
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = []
    for line in content.split('\n'):
        line = line.strip()
        # Skip non-text lines
        if (not line or 
            line.startswith('WEBVTT') or 
            line.startswith('Kind:') or 
            line.startswith('Language:') or
            re.match(r'^\d{2}:\d{2}:\d{2}', line) or
            line.startswith('align:') or
            line.startswith('position:')):
            continue
        # Clean tags
        clean = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', line)
        clean = re.sub(r'</?c>', '', clean)
        clean = re.sub(r'<[^\u003e]+\u003e', '', clean)
        if clean.strip():
            lines.append(clean.strip())
    
    return ' '.join(lines)

def create_backup(vtt_path):
    """Create backup of original subtitle"""
    backup_path = str(vtt_path).replace('.vtt', '-backup.vtt')
    if not os.path.exists(backup_path):
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backed up: {backup_path}")
    return backup_path

def generate_deepseek_prompt(text, source_name=""):
    """Generate DeepSeek proofreading prompt"""
    return f"""You are a professional subtitle proofreading expert. Please proofread the following news subtitle text and correct obvious errors.

Common error types to fix:
1. Speech recognition errors: e.g., "noraster" → "nor'easter" (northeast storm)
2. Name errors: e.g., "trunk" → "Trump"
3. Location name errors: e.g., "bucking ham" → "Buckingham"
4. Professional terminology errors
5. Obvious spelling mistakes

Important guidelines:
- Only fix OBVIOUS errors, keep colloquial expressions
- Preserve capitalization and punctuation style
- Don't over-correct natural speech patterns
- Keep the text as close to original as possible while fixing clear mistakes

Source: {source_name}

Text to proofread:
{text[:6000]}

Please respond in this format:

## Corrections Found
1. Original: "xxx" → Corrected: "yyy" (Error type)
2. ...

## Corrected Full Text
[Full corrected text here]

Be concise. Only list actual errors found."""

def proofread_with_deepseek(text, source_name=""):
    """
    Prepare DeepSeek proofreading task
    Returns: (prompt, word_count)
    """
    prompt = generate_deepseek_prompt(text, source_name)
    return prompt, len(text.split())

def save_results(vtt_path, corrections, corrected_text):
    """Save proofreading results"""
    output_dir = os.path.dirname(vtt_path)
    base_name = os.path.basename(vtt_path).replace('.vtt', '')
    
    # Save corrected text
    corrected_path = os.path.join(output_dir, f"{base_name}-corrected.txt")
    with open(corrected_path, 'w', encoding='utf-8') as f:
        f.write("# AI-Corrected Subtitle Text\n\n")
        f.write(corrected_text)
    
    # Save corrections list
    corrections_path = os.path.join(output_dir, f"{base_name}-corrections.md")
    with open(corrections_path, 'w', encoding='utf-8') as f:
        f.write("# Subtitle Proofreading Report\n\n")
        f.write(corrections)
    
    return corrected_path, corrections_path

def proofread_file(vtt_path):
    """Proofread a single subtitle file"""
    if not os.path.exists(vtt_path):
        print(f"❌ File not found: {vtt_path}")
        return False
    
    print(f"📄 Processing: {vtt_path}")
    
    # Create backup
    create_backup(vtt_path)
    
    # Extract text
    print("📝 Extracting text...")
    text = extract_text_from_vtt(vtt_path)
    word_count = len(text.split())
    print(f"   Extracted {word_count} words")
    
    # Generate DeepSeek prompt
    source_name = os.path.basename(vtt_path)
    prompt, _ = proofread_with_deepseek(text, source_name)
    
    # Save prompt for manual processing or API call
    prompt_path = vtt_path.replace('.vtt', '-proofread-task.txt')
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"\n✅ Proofreading task prepared!")
    print(f"   Task file: {prompt_path}")
    print(f"\nNext steps:")
    print(f"  1. Send the task file content to DeepSeek model")
    print(f"  2. Or tell me: '校对字幕 {vtt_path}'")
    
    return True

def proofread_all():
    """Proofread all news subtitles"""
    workspace = "/root/.openclaw/workspace"
    
    files_to_proofread = [
        f"{workspace}/cbs-live-local/cbs_latest.en.vtt",
        f"{workspace}/bbc-news-live/bbc_news_latest.en.vtt"
    ]
    
    success_count = 0
    for vtt_file in files_to_proofread:
        if os.path.exists(vtt_file):
            if proofread_file(vtt_file):
                success_count += 1
        else:
            print(f"⚠️ Skipping (not found): {vtt_file}")
    
    print(f"\n{'='*50}")
    print(f"Prepared {success_count} files for proofreading")
    print('='*50)
    
    return success_count > 0

def main():
    parser = argparse.ArgumentParser(description='Proofread subtitle files')
    parser.add_argument('file', nargs='?', help='VTT file to proofread')
    parser.add_argument('--all', action='store_true', help='Proofread all news subtitles')
    
    args = parser.parse_args()
    
    if args.all:
        return 0 if proofread_all() else 1
    elif args.file:
        return 0 if proofread_file(args.file) else 1
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())

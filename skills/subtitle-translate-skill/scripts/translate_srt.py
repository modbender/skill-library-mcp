#!/usr/bin/env python3
"""
Subtitle Translator - Translate SRT files using LLM APIs
"""

import argparse
import json
import os
import re
import sys
import time
from typing import List, Dict, Tuple
import urllib.request
import urllib.error


def parse_srt(content: str) -> List[Dict]:
    """Parse SRT file into list of subtitle blocks."""
    blocks = []
    # Split by double newline
    raw_blocks = re.split(r'\n\s*\n', content.strip())
    
    for block in raw_blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            index = lines[0].strip()
            timecode = lines[1].strip()
            text = '\n'.join(lines[2:])
            blocks.append({
                'index': int(index),
                'timecode': timecode,
                'text': text,
                'translated': ''
            })
    return blocks


def format_srt(blocks: List[Dict], bilingual: bool = False) -> str:
    """Format subtitle blocks back to SRT."""
    output = []
    for i, block in enumerate(blocks, 1):
        output.append(str(i))
        output.append(block['timecode'])
        if bilingual:
            output.append(block['translated'])
            output.append(block['text'])
        else:
            output.append(block['translated'])
        output.append('')
    return '\n'.join(output)


def translate_batch(
    texts: List[str],
    api_url: str,
    api_key: str,
    model: str,
    source_lang: str,
    target_lang: str
) -> List[str]:
    """Translate a batch of texts using LLM API."""
    
    # Build prompt
    numbered_texts = '\n'.join([f"{i+1}. {text}" for i, text in enumerate(texts)])
    
    prompt = f"""You are a professional subtitle translation expert.

Task: Translate the following subtitles from {source_lang} to {target_lang}.

Requirements:
1. Accurately convey the original meaning in natural {target_lang}
2. Control length for screen display (max 40 characters per line)
3. Maintain consistent style throughout
4. Strictly maintain {len(texts)} sentences - do not add, remove, merge, or split

Input subtitles:
{numbered_texts}

Output format:
Directly output translations, one per line, in this format:
1. [Translation 1]
2. [Translation 2]
...

Output translations only, no explanations."""

    # Prepare API request
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.3
    }
    
    req = urllib.request.Request(
        f'{api_url}/chat/completions',
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    # Set proxy
    proxy_handler = urllib.request.ProxyHandler({
        'http': os.environ.get('http_proxy', ''),
        'https': os.environ.get('https_proxy', '')
    })
    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)
    
    # Send request
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content']
            
            # Parse translations
            translations = []
            for line in content.strip().split('\n'):
                match = re.match(r'^\d+\.\s*(.+)$', line.strip())
                if match:
                    translations.append(match.group(1))
            
            return translations
    except Exception as e:
        print(f"Error in API call: {e}", file=sys.stderr)
        raise


def log_progress(current: int, total: int, message: str):
    """Log progress information."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    progress_pct = (current / total) * 100
    print(f"[{timestamp}] [{current}/{total} ({progress_pct:.1f}%)] {message}")


def main():
    parser = argparse.ArgumentParser(description='Translate SRT subtitle files')
    parser.add_argument('--input', '-i', required=True, help='Input SRT file')
    parser.add_argument('--output', '-o', required=True, help='Output SRT file')
    parser.add_argument('--source-lang', '-s', default='en', help='Source language')
    parser.add_argument('--target-lang', '-t', default='zh', help='Target language')
    parser.add_argument('--api-url', '-u', required=True, help='API base URL')
    parser.add_argument('--api-key', '-k', required=True, help='API key')
    parser.add_argument('--model', '-m', default='gpt-4', help='Model name')
    parser.add_argument('--bilingual', '-b', action='store_true', help='Output bilingual subtitles')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size (default: 50)')
    parser.add_argument('--interval', type=int, default=1, help='Interval between batches in seconds (default: 1)')
    
    args = parser.parse_args()
    
    # Read input file
    log_progress(0, 1, f"Reading input file: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse SRT
    blocks = parse_srt(content)
    total_blocks = len(blocks)
    log_progress(0, total_blocks, f"Parsed {total_blocks} subtitle blocks")
    
    # Process in batches
    batch_size = args.batch_size
    total_batches = (total_blocks + batch_size - 1) // batch_size
    
    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, total_blocks)
        batch_blocks = blocks[start_idx:end_idx]
        
        log_progress(start_idx, total_blocks, f"Processing batch {batch_idx + 1}/{total_batches} ({len(batch_blocks)} sentences)")
        
        # Extract texts for translation
        texts = [block['text'] for block in batch_blocks]
        
        # Translate
        try:
            translations = translate_batch(
                texts,
                args.api_url,
                args.api_key,
                args.model,
                args.source_lang,
                args.target_lang
            )
            
            # Validate
            if len(translations) != len(texts):
                log_progress(start_idx, total_blocks, f"ERROR: Translation count mismatch. Expected {len(texts)}, got {len(translations)}")
                sys.exit(1)
            
            # Store translations
            for i, translation in enumerate(translations):
                blocks[start_idx + i]['translated'] = translation
            
            log_progress(end_idx, total_blocks, f"Batch {batch_idx + 1} completed")
            
        except Exception as e:
            log_progress(start_idx, total_blocks, f"ERROR in batch {batch_idx + 1}: {e}")
            sys.exit(1)
        
        # Wait before next batch (except for last batch)
        if batch_idx < total_batches - 1:
            time.sleep(args.interval)
    
    # Generate output
    log_progress(total_blocks, total_blocks, "Generating output file...")
    output_content = format_srt(blocks, args.bilingual)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    log_progress(total_blocks, total_blocks, f"Translation complete: {args.output}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Build Batch - Helper to create batch request JSONL from various data sources

Usage:
    python build_batch.py csv <input.csv> [--output requests.jsonl]
    python build_batch.py text <input.txt> [--output requests.jsonl]
    python build_batch.py json <input.json> [--output requests.jsonl]
    python build_batch.py custom <script.py> [--output requests.jsonl]
"""

import json
import csv
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any


def build_from_csv(input_file: str, output_file: str, 
                   prompt_column: str = None, 
                   model: str = "claude-opus-4-6",
                   max_tokens: int = 1024) -> None:
    """Build batch requests from CSV file"""
    
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    requests = []
    
    with open(input_file) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            # Try to find prompt column
            if prompt_column and prompt_column in row:
                prompt = row[prompt_column]
            else:
                # Use first non-empty value
                prompt = next((v for v in row.values() if v), None)
            
            if not prompt:
                print(f"Warning: Row {i} has no content, skipping")
                continue
            
            request = {
                "custom_id": f"csv-row-{i}",
                "params": {
                    "model": model,
                    "max_tokens": max_tokens,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            }
            
            # Include original data as context if needed
            if len(row) > 1:
                request["original_row"] = row
            
            requests.append(request)
    
    print(f"Created {len(requests)} requests from {input_file}")
    
    with open(output_file, 'w') as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")
    
    print(f"✓ Batch requests written to {output_file}")


def build_from_text(input_file: str, output_file: str,
                   model: str = "claude-opus-4-6",
                   max_tokens: int = 1024,
                   split_by: str = "line") -> None:
    """Build batch requests from text file"""
    
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    requests = []
    
    with open(input_file) as f:
        if split_by == "line":
            lines = [line.strip() for line in f if line.strip()]
            for i, line in enumerate(lines, 1):
                request = {
                    "custom_id": f"text-line-{i}",
                    "params": {
                        "model": model,
                        "max_tokens": max_tokens,
                        "messages": [
                            {"role": "user", "content": line}
                        ]
                    }
                }
                requests.append(request)
        
        elif split_by == "paragraph":
            content = f.read()
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            for i, para in enumerate(paragraphs, 1):
                request = {
                    "custom_id": f"text-para-{i}",
                    "params": {
                        "model": model,
                        "max_tokens": max_tokens,
                        "messages": [
                            {"role": "user", "content": para}
                        ]
                    }
                }
                requests.append(request)
    
    print(f"Created {len(requests)} requests from {input_file}")
    
    with open(output_file, 'w') as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")
    
    print(f"✓ Batch requests written to {output_file}")


def build_from_json(input_file: str, output_file: str,
                    prompt_field: str = "prompt",
                    model: str = "claude-opus-4-6",
                    max_tokens: int = 1024) -> None:
    """Build batch requests from JSON file"""
    
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    with open(input_file) as f:
        data = json.load(f)
    
    # Handle both list and dict inputs
    if isinstance(data, dict):
        items = data.get('items', [data])
    else:
        items = data if isinstance(data, list) else [data]
    
    requests = []
    for i, item in enumerate(items, 1):
        if isinstance(item, dict):
            # Extract prompt from specified field
            prompt = item.get(prompt_field, json.dumps(item))
        else:
            prompt = str(item)
        
        request = {
            "custom_id": f"json-item-{i}",
            "params": {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        }
        
        if isinstance(item, dict):
            request["original_data"] = item
        
        requests.append(request)
    
    print(f"Created {len(requests)} requests from {input_file}")
    
    with open(output_file, 'w') as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")
    
    print(f"✓ Batch requests written to {output_file}")


def build_from_custom(script_file: str, output_file: str) -> None:
    """Build batch requests from custom Python script"""
    
    if not Path(script_file).exists():
        print(f"Error: File not found: {script_file}")
        sys.exit(1)
    
    # Load and execute custom script
    import importlib.util
    spec = importlib.util.spec_from_file_location("batch_builder", script_file)
    module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error loading script: {e}")
        sys.exit(1)
    
    # Call build_requests function
    if not hasattr(module, 'build_requests'):
        print("Error: Script must define 'build_requests()' function")
        print("Example:")
        print("  def build_requests():")
        print("      return [")
        print("          {")
        print("              'custom_id': 'task-1',")
        print("              'params': {...}")
        print("          }")
        print("      ]")
        sys.exit(1)
    
    try:
        requests = module.build_requests()
    except Exception as e:
        print(f"Error executing build_requests: {e}")
        sys.exit(1)
    
    if not requests:
        print("Error: build_requests() returned no requests")
        sys.exit(1)
    
    print(f"Created {len(requests)} requests from {script_file}")
    
    with open(output_file, 'w') as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")
    
    print(f"✓ Batch requests written to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Build batch request JSONL files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

CSV input:
  python build_batch.py csv data.csv --output requests.jsonl
  python build_batch.py csv data.csv --prompt-column content

Text input (line by line):
  python build_batch.py text documents.txt --output requests.jsonl

Text input (paragraph by paragraph):
  python build_batch.py text documents.txt --split-by paragraph

JSON input:
  python build_batch.py json items.json --output requests.jsonl
  python build_batch.py json items.json --prompt-field description

Custom Python script:
  python build_batch.py custom my_builder.py --output requests.jsonl

Custom script template (my_builder.py):
  def build_requests():
      return [
          {
              "custom_id": "task-1",
              "params": {
                  "model": "claude-opus-4-6",
                  "max_tokens": 1024,
                  "messages": [{"role": "user", "content": "..."}]
              }
          }
      ]
        """
    )
    
    subparsers = parser.add_subparsers(dest='source_type', required=True)
    
    # CSV subcommand
    csv_parser = subparsers.add_parser('csv', help='Build from CSV file')
    csv_parser.add_argument('input_file', help='Input CSV file')
    csv_parser.add_argument('-o', '--output', default='batch_requests.jsonl')
    csv_parser.add_argument('--prompt-column', help='Column name for prompts')
    csv_parser.add_argument('--model', default='claude-opus-4-6')
    csv_parser.add_argument('--max-tokens', type=int, default=1024)
    
    # Text subcommand
    text_parser = subparsers.add_parser('text', help='Build from text file')
    text_parser.add_argument('input_file', help='Input text file')
    text_parser.add_argument('-o', '--output', default='batch_requests.jsonl')
    text_parser.add_argument('--split-by', choices=['line', 'paragraph'], 
                            default='line')
    text_parser.add_argument('--model', default='claude-opus-4-6')
    text_parser.add_argument('--max-tokens', type=int, default=1024)
    
    # JSON subcommand
    json_parser = subparsers.add_parser('json', help='Build from JSON file')
    json_parser.add_argument('input_file', help='Input JSON file')
    json_parser.add_argument('-o', '--output', default='batch_requests.jsonl')
    json_parser.add_argument('--prompt-field', default='prompt')
    json_parser.add_argument('--model', default='claude-opus-4-6')
    json_parser.add_argument('--max-tokens', type=int, default=1024)
    
    # Custom subcommand
    custom_parser = subparsers.add_parser('custom', help='Build from custom Python script')
    custom_parser.add_argument('input_file', help='Python script with build_requests()')
    custom_parser.add_argument('-o', '--output', default='batch_requests.jsonl')
    
    args = parser.parse_args()
    
    if args.source_type == 'csv':
        build_from_csv(args.input_file, args.output, args.prompt_column,
                      args.model, args.max_tokens)
    elif args.source_type == 'text':
        build_from_text(args.input_file, args.output, args.model,
                       args.max_tokens, args.split_by)
    elif args.source_type == 'json':
        build_from_json(args.input_file, args.output, args.prompt_field,
                       args.model, args.max_tokens)
    elif args.source_type == 'custom':
        build_from_custom(args.input_file, args.output)


if __name__ == '__main__':
    main()

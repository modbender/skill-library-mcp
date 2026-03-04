#!/usr/bin/env python3
"""
Batch update Feishu documents from a template.

This script updates multiple Feishu documents in a folder with content
from a template. Useful for weekly reports, status updates, or any
repetitive document updates.

Usage:
  python batch_update.py --folder-token fldcnXXX --template weekly_report.md
  python batch_update.py --folder-token fldcnXXX --doc-tokens doc1,doc2,doc3 --template template.md

Requirements:
  - OpenClaw with feishu_doc tool available
  - Feishu app with document write permissions
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def load_template(template_path):
    """Load template content from file."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error loading template {template_path}: {e}")
        sys.exit(1)

def process_template(template_content, variables=None):
    """
    Process template with variables.
    
    Variables format: {{variable_name}}
    Example: "Hello {{name}}" with {"name": "World"} -> "Hello World"
    """
    if not variables:
        return template_content
    
    result = template_content
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    
    return result

def get_documents_in_folder(folder_token):
    """
    Get list of document tokens in a folder.
    This is a placeholder - in practice, you'd use feishu_drive list action.
    """
    # In real implementation, use:
    # exec_result = exec('tool call', {'tool': 'feishu_drive', 'action': 'list', 'folder_token': folder_token})
    # Parse document tokens from response
    
    print(f"[INFO] Would fetch documents in folder: {folder_token}")
    # Return sample data for demonstration
    return ["doc_token_1", "doc_token_2"]

def update_document(doc_token, content):
    """
    Update a Feishu document with new content.
    This is a placeholder - in practice, you'd use feishu_doc write action.
    """
    # In real implementation, use:
    # exec_result = exec('tool call', {'tool': 'feishu_doc', 'action': 'write', 'doc_token': doc_token, 'content': content})
    
    print(f"[INFO] Would update document {doc_token}")
    print(f"Content preview: {content[:100]}...")
    return True

def main():
    parser = argparse.ArgumentParser(description="Batch update Feishu documents")
    parser.add_argument("--folder-token", help="Feishu folder token containing documents")
    parser.add_argument("--doc-tokens", help="Comma-separated list of specific document tokens")
    parser.add_argument("--template", required=True, help="Path to template file")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--var", action="append", help="Variable for template in format key=value")
    
    args = parser.parse_args()
    
    if not args.folder_token and not args.doc_tokens:
        print("Error: Either --folder-token or --doc-tokens must be specified")
        parser.print_help()
        sys.exit(1)
    
    # Load and process template
    template_content = load_template(args.template)
    
    # Parse variables
    variables = {}
    if args.var:
        for var_str in args.var:
            if '=' in var_str:
                key, value = var_str.split('=', 1)
                variables[key] = value
    
    # Add timestamp variable
    variables['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    processed_content = process_template(template_content, variables)
    
    # Get document tokens
    doc_tokens = []
    if args.doc_tokens:
        doc_tokens = args.doc_tokens.split(',')
    elif args.folder_token:
        doc_tokens = get_documents_in_folder(args.folder_token)
    
    print(f"[INFO] Found {len(doc_tokens)} documents to update")
    
    # Update documents
    success_count = 0
    for i, doc_token in enumerate(doc_tokens, 1):
        print(f"\n[{i}/{len(doc_tokens)}] Processing document: {doc_token}")
        
        if args.dry_run:
            print(f"[DRY RUN] Would update {doc_token}")
            print(f"Content preview: {processed_content[:200]}...")
        else:
            try:
                if update_document(doc_token, processed_content):
                    success_count += 1
                    print(f"[SUCCESS] Updated {doc_token}")
            except Exception as e:
                print(f"[ERROR] Failed to update {doc_token}: {e}")
    
    print(f"\n[SUMMARY] Successfully updated {success_count}/{len(doc_tokens)} documents")
    
    if args.dry_run:
        print("[NOTE] This was a dry run - no changes were made")

if __name__ == "__main__":
    main()
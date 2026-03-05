#!/usr/bin/env python3
"""
PDF Reader Skill for OpenClaw
Extract text from PDF files using PyMuPDF (fitz)
"""

import sys
import os
import json
import fitz  # PyMuPDF

# Allowed output directory (current working directory only for security)
ALLOWED_OUTPUT_DIR = os.getcwd()


def is_safe_input_path(path):
    """Validate that the input path is safe (no path traversal, must be .pdf)"""
    # Resolve the absolute path
    abs_path = os.path.abspath(path)
    abs_allowed = os.path.abspath(ALLOWED_OUTPUT_DIR)
    
    # Must be within allowed directory
    if not (abs_path.startswith(abs_allowed + os.sep) or abs_path == abs_allowed):
        return False
    
    # Must be a .pdf file
    if not abs_path.lower().endswith('.pdf'):
        return False
    
    return True


def is_safe_output_path(path):
    """Validate that the output path is safe (no path traversal, must be .json)"""
    # Resolve the absolute path
    abs_path = os.path.abspath(path)
    abs_allowed = os.path.abspath(ALLOWED_OUTPUT_DIR)
    
    # Must be within allowed directory
    if not (abs_path.startswith(abs_allowed + os.sep) or abs_path == abs_allowed):
        return False
    
    # Must be a .json file
    if not abs_path.lower().endswith('.json'):
        return False
    
    return True


def extract_text_from_pdf(pdf_path, max_pages=None):
    """Extract text from a PDF file"""
    
    # Validate input path for security
    if not is_safe_input_path(pdf_path):
        return {"error": f"Invalid path or not a PDF file: {pdf_path}"}
    
    if not os.path.exists(pdf_path):
        return {"error": f"File not found: {pdf_path}"}
    
    try:
        doc = fitz.open(pdf_path)
        
        results = {
            "filename": os.path.basename(pdf_path),
            "page_count": len(doc),
            "metadata": {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
            },
            "pages": []
        }
        
        pages_to_extract = max_pages if max_pages else len(doc)
        
        for page_num in range(min(pages_to_extract, len(doc))):
            page = doc[page_num]
            text = page.get_text()
            
            results["pages"].append({
                "page": page_num + 1,
                "text": text.strip()
            })
        
        doc.close()
        return results
        
    except Exception as e:
        return {"error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: pdf_reader.py <pdf_file> [max_pages] [--output file.json]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else None
    
    # Check for --output flag
    output_file = None
    for arg in sys.argv:
        if arg.startswith("--output="):
            output_file = arg.split("=")[1]
    
    # Validate output path for security
    if output_file and not is_safe_output_path(output_file):
        print(f"Error: Output must be a .json file within {ALLOWED_OUTPUT_DIR}", file=sys.stderr)
        sys.exit(1)
    
    result = extract_text_from_pdf(pdf_path, max_pages)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    if output_file:
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Wrote to: {output_file}")
    else:
        # Just summary to stdout
        print(f"=== {result['filename']} ===")
        print(f"Pages: {result['page_count']}")
        if result['metadata']['title']:
            print(f"Title: {result['metadata']['title']}")
        if result['metadata']['author']:
            print(f"Author: {result['metadata']['author']}")
        print()
        print(f"Run with --output=file.json to extract full text")


if __name__ == "__main__":
    main()

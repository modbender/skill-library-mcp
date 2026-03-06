import sys
import argparse
import json
import pymupdf

def extract_text(file_path, max_pages=None):
    try:
        doc = pymupdf.open(file_path)
        text = ""
        for i, page in enumerate(doc):
            if max_pages and i >= int(max_pages):
                break
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        return f"Error: {str(e)}"

def get_metadata(file_path):
    try:
        doc = pymupdf.open(file_path)
        return doc.metadata
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["extract", "metadata"])
    parser.add_argument("file_path")
    parser.add_argument("--max_pages", type=int, default=None)
    
    args = parser.parse_args()
    
    if args.command == "extract":
        print(extract_text(args.file_path, args.max_pages))
    elif args.command == "metadata":
        print(json.dumps(get_metadata(args.file_path), indent=2))

#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from difflib import SequenceMatcher
import argparse

def similarity_score(query, text):
    """Calculate similarity score between query and text."""
    return SequenceMatcher(None, query.lower(), text.lower()).ratio()

def find_best_match(query, start_path='.'):
    """Find the best matching file based on query."""
    matches = []
    query = query.lower()
    
    try:
        for root, dirs, files in os.walk(start_path):
            # Skip hidden directories and .git
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.git']
            
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                    
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start_path)
                
                # Calculate similarity scores for both filename and path
                filename_score = similarity_score(query, file)
                path_score = similarity_score(query, rel_path)
                
                # Use the better of the two scores
                score = max(filename_score, path_score)
                
                # If exact match found in filename, return immediately
                if filename_score == 1.0:
                    return [(full_path, 1.0)]
                
                # Keep matches with score > 0.2
                if score > 0.2:
                    matches.append((full_path, score))
    
    except Exception as e:
        print(f"Error while searching: {str(e)}", file=sys.stderr)
        return []
    
    # Sort by score (highest first) and path length (shortest first)
    matches.sort(key=lambda x: (-x[1], len(x[0])))
    return matches

def read_file_content(file_path):
    """Read and return file content safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return "[ERROR] File appears to be binary or uses an unsupported encoding."
    except Exception as e:
        return f"[ERROR] Could not read file: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Smart file finder with fuzzy matching')
    parser.add_argument('query', help='Search query (filename or keyword)')
    args = parser.parse_args()
    
    if not args.query:
        print("Please provide a search query.")
        return 1
    
    matches = find_best_match(args.query)
    
    if not matches:
        print(f"No files found matching '{args.query}'")
        return 1
    
    best_match = matches[0]
    best_match_path, score = best_match
    
    print(f"\nBest match: {best_match_path} (similarity: {score:.2f})")
    
    if len(matches) > 1:
        print("\nOther potential matches:")
        for path, score in matches[1:5]:  # Show up to 4 alternatives
            print(f"- {path} (similarity: {score:.2f})")
    
    print("\nFile content:")
    print("-" * 80)
    content = read_file_content(best_match_path)
    print(content)
    print("-" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
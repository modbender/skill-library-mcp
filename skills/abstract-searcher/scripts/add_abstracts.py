#!/usr/bin/env python3
"""
Add abstracts to BibTeX entries by searching academic databases.
Usage: python3 add_abstracts.py input.bib > output.bib
"""

import sys
import re
import time
import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List, Tuple

# Longer delays to avoid rate limiting
API_DELAY = 2.0

def parse_bib_entries(content: str) -> List[Tuple[str, Dict[str, str], str]]:
    """Parse BibTeX file into list of (entry_type, fields, original_text)"""
    entries = []
    # Match @type{key, ... }
    pattern = r'@(\w+)\s*\{([^,]+),([^@]*?)\n\}'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        entry_type = match.group(1)
        key = match.group(2).strip()
        fields_text = match.group(3)
        original = match.group(0)
        
        # Parse fields
        fields = {'_key': key}
        field_pattern = r'(\w+)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        for field_match in re.finditer(field_pattern, fields_text):
            field_name = field_match.group(1).lower()
            field_value = field_match.group(2)
            fields[field_name] = field_value
        
        entries.append((entry_type, fields, original))
    
    return entries

def search_arxiv(title: str, author: str = "") -> Optional[str]:
    """Search arXiv for abstract"""
    try:
        # Clean title for search
        search_title = re.sub(r'[^\w\s]', ' ', title).strip()
        query = f'ti:"{search_title}"'
        
        url = f'http://export.arxiv.org/api/query?search_query={urllib.parse.quote(query)}&max_results=5'
        
        req = urllib.request.Request(url, headers={'User-Agent': 'AbstractSearcher/1.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_content = response.read().decode('utf-8')
        
        # Parse XML
        root = ET.fromstring(xml_content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', ns):
            entry_title = entry.find('atom:title', ns)
            if entry_title is not None:
                # Check if title matches reasonably
                entry_title_clean = re.sub(r'\s+', ' ', entry_title.text).strip().lower()
                search_title_clean = search_title.lower()
                
                # More lenient matching
                words_match = sum(1 for w in search_title_clean.split()[:5] if w in entry_title_clean)
                if words_match >= 3:
                    summary = entry.find('atom:summary', ns)
                    if summary is not None:
                        abstract = re.sub(r'\s+', ' ', summary.text).strip()
                        return abstract
        
        return None
    except Exception as e:
        print(f"  arXiv error: {e}", file=sys.stderr)
        return None

def search_semantic_scholar(title: str) -> Optional[str]:
    """Search Semantic Scholar for abstract"""
    try:
        search_title = re.sub(r'[^\w\s]', ' ', title).strip()
        # Use first 100 chars of title
        search_title = search_title[:100]
        url = f'https://api.semanticscholar.org/graph/v1/paper/search?query={urllib.parse.quote(search_title)}&fields=title,abstract&limit=5'
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'AbstractSearcher/1.0',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if 'data' in data:
            for paper in data['data']:
                if paper.get('abstract'):
                    paper_title = paper.get('title', '').lower()
                    search_lower = search_title.lower()
                    
                    # More lenient matching
                    words_match = sum(1 for w in search_lower.split()[:5] if w in paper_title)
                    if words_match >= 3:
                        return paper['abstract']
        
        return None
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"  Semantic Scholar rate limited, waiting...", file=sys.stderr)
            time.sleep(10)
        else:
            print(f"  Semantic Scholar error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Semantic Scholar error: {e}", file=sys.stderr)
        return None

def search_crossref(title: str, author: str = "") -> Optional[str]:
    """Search CrossRef for abstract (many journals)"""
    try:
        search_title = re.sub(r'[^\w\s]', ' ', title).strip()
        
        # Build query
        query_parts = [f'query.title={urllib.parse.quote(search_title[:200])}']
        if author:
            first_author = author.split(' and ')[0].split(',')[0].strip()
            query_parts.append(f'query.author={urllib.parse.quote(first_author)}')
        
        url = f'https://api.crossref.org/works?{"&".join(query_parts)}&rows=5'
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'AbstractSearcher/1.0 (mailto:contact@example.com)'
        })
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if 'message' in data and 'items' in data['message']:
            for item in data['message']['items']:
                if 'abstract' in item:
                    item_title = item.get('title', [''])[0].lower() if item.get('title') else ''
                    search_lower = search_title.lower()
                    
                    # Check title similarity
                    words_match = sum(1 for w in search_lower.split()[:5] if w in item_title)
                    if words_match >= 3:
                        # Clean HTML tags from abstract
                        abstract = re.sub(r'<[^>]+>', '', item['abstract'])
                        abstract = re.sub(r'&[a-z]+;', '', abstract)  # Remove HTML entities
                        return abstract.strip()
        
        return None
    except Exception as e:
        print(f"  CrossRef error: {e}", file=sys.stderr)
        return None

def search_openalex(title: str) -> Optional[str]:
    """Search OpenAlex for abstract (open alternative to Semantic Scholar)"""
    try:
        search_title = re.sub(r'[^\w\s]', ' ', title).strip()[:150]
        url = f'https://api.openalex.org/works?search={urllib.parse.quote(search_title)}&per_page=5'
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'AbstractSearcher/1.0',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if 'results' in data:
            for work in data['results']:
                abstract_obj = work.get('abstract_inverted_index')
                if abstract_obj:
                    work_title = work.get('title', '').lower()
                    search_lower = search_title.lower()
                    
                    words_match = sum(1 for w in search_lower.split()[:5] if w in work_title)
                    if words_match >= 3:
                        # Reconstruct abstract from inverted index
                        word_positions = []
                        for word, positions in abstract_obj.items():
                            for pos in positions:
                                word_positions.append((pos, word))
                        word_positions.sort()
                        abstract = ' '.join(w for _, w in word_positions)
                        return abstract
        
        return None
    except Exception as e:
        print(f"  OpenAlex error: {e}", file=sys.stderr)
        return None

def find_abstract(title: str, author: str = "", journal: str = "") -> Optional[str]:
    """Try multiple sources to find abstract"""
    
    # Check if it's an arXiv paper
    is_arxiv = 'arxiv' in journal.lower() if journal else False
    
    # Try arXiv first for arXiv papers
    if is_arxiv:
        print(f"  Trying arXiv...", file=sys.stderr)
        abstract = search_arxiv(title, author)
        if abstract:
            return abstract
        time.sleep(API_DELAY)
    
    # Try OpenAlex (usually more reliable, no strict rate limits)
    print(f"  Trying OpenAlex...", file=sys.stderr)
    abstract = search_openalex(title)
    if abstract:
        return abstract
    time.sleep(API_DELAY)
    
    # Try CrossRef
    print(f"  Trying CrossRef...", file=sys.stderr)
    abstract = search_crossref(title, author)
    if abstract:
        return abstract
    time.sleep(API_DELAY)
    
    # Try Semantic Scholar (often rate limited)
    print(f"  Trying Semantic Scholar...", file=sys.stderr)
    abstract = search_semantic_scholar(title)
    if abstract:
        return abstract
    time.sleep(API_DELAY)
    
    # Try arXiv as fallback
    if not is_arxiv:
        print(f"  Trying arXiv (fallback)...", file=sys.stderr)
        abstract = search_arxiv(title, author)
        if abstract:
            return abstract
    
    return None

def clean_abstract(text: str) -> str:
    """Clean abstract text for BibTeX"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove or escape problematic characters (minimal)
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    # Escape curly braces that aren't already escaped
    # text = text.replace('{', '\\{').replace('}', '\\}')
    return text

def rebuild_entry(entry_type: str, fields: Dict[str, str], abstract: Optional[str]) -> str:
    """Rebuild BibTeX entry with abstract"""
    key = fields.get('_key', 'unknown')
    
    # Start building entry
    lines = [f"@{entry_type}{{{key},"]
    
    # Add abstract first if we have it
    if abstract:
        clean_abs = clean_abstract(abstract)
        lines.append(f"  abstract={{{clean_abs}}},")
    
    # Add other fields
    field_order = ['title', 'author', 'journal', 'booktitle', 'volume', 'number', 
                   'pages', 'year', 'publisher', 'organization']
    
    for field in field_order:
        if field in fields:
            lines.append(f"  {field}={{{fields[field]}}},")
    
    # Add any remaining fields
    for field, value in fields.items():
        if field not in field_order and field != '_key' and field != 'abstract':
            lines.append(f"  {field}={{{value}}},")
    
    # Close entry
    lines.append("}")
    
    return '\n'.join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 add_abstracts.py input.bib > output.bib", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = parse_bib_entries(content)
    print(f"Found {len(entries)} entries", file=sys.stderr)
    
    results = []
    found_count = 0
    not_found = []
    
    for i, (entry_type, fields, original) in enumerate(entries):
        title = fields.get('title', '')
        author = fields.get('author', '')
        journal = fields.get('journal', fields.get('booktitle', ''))
        key = fields.get('_key', 'unknown')
        
        print(f"\n[{i+1}/{len(entries)}] {key}", file=sys.stderr)
        print(f"  Title: {title[:60]}...", file=sys.stderr)
        
        # Skip if already has abstract
        if 'abstract' in fields:
            print(f"  Already has abstract, skipping", file=sys.stderr)
            results.append(original)
            found_count += 1
            continue
        
        abstract = find_abstract(title, author, journal)
        
        if abstract:
            print(f"  ✓ Found abstract ({len(abstract)} chars)", file=sys.stderr)
            new_entry = rebuild_entry(entry_type, fields, abstract)
            results.append(new_entry)
            found_count += 1
        else:
            print(f"  ✗ Abstract not found", file=sys.stderr)
            not_found.append(key)
            results.append(original)
    
    # Output results
    print('\n'.join(results))
    
    # Summary
    print(f"\n\n% === SUMMARY ===", file=sys.stderr)
    print(f"% Processed: {len(entries)} entries", file=sys.stderr)
    print(f"% Found abstracts: {found_count}", file=sys.stderr)
    print(f"% Not found: {len(not_found)}", file=sys.stderr)
    if not_found:
        print(f"% Missing: {', '.join(not_found)}", file=sys.stderr)

if __name__ == '__main__':
    main()

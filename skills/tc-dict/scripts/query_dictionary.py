#!/usr/bin/env python3
"""
Query Traditional Chinese dictionary.

Requirements:
    Install dependencies: uv pip install -r requirements.txt
    (or: pip install pandas openpyxl)

Usage:
    python query_dictionary.py --word WORD [--dict-name DICT_NAME] [--storage-path PATH] [--full]

Args:
    --word: Word or term to look up
    --dict-name: Dictionary name (default: 'concised')
    --storage-path: Directory with dictionaries (default: ~/.openclaw/dictionaries)
    --full: Return full details (definition, examples, etc.)

Returns:
    JSON with definition(s), examples, and metadata
"""

import argparse
import difflib
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class DictionaryQuery:
    """Query dictionary data from xlsx."""
    
    def __init__(self, xlsx_path: str, dict_name: str = 'concised'):
        """
        Initialize dictionary query engine.
        
        Args:
            xlsx_path: Path to dictionary xlsx file
            dict_name: Name of dictionary (for reference)
        """
        self.xlsx_path = Path(xlsx_path)
        self.dict_name = dict_name
        self.df = None
        self.word_index = None
        self._load_dictionary()
    
    def _load_dictionary(self):
        """Load and index the dictionary."""
        if not self.xlsx_path.exists():
            raise FileNotFoundError(f"Dictionary file not found: {self.xlsx_path}")
        
        logger.info(f"Loading dictionary from {self.xlsx_path}...")
        
        try:
            self.df = pd.read_excel(self.xlsx_path, sheet_name=0)
            logger.info(f"Loaded {len(self.df)} entries")
            
            # Rename columns to standard names for compatibility
            # Adjust if actual file has different column names
            self._normalize_columns()
            
            # Create case-insensitive index
            self.word_index = {
                row['word'].strip().lower(): idx
                for idx, row in self.df.iterrows()
                if pd.notna(row['word'])
            }
            logger.info(f"Created index with {len(self.word_index)} words")
        
        except Exception as e:
            logger.error(f"Failed to load dictionary: {e}")
            raise
    
    def _normalize_columns(self):
        """Normalize column names to standard format."""
        # Define expected columns based on SCHEMA.md
        column_mapping = {
            '字詞': 'word',
            '注音': 'pronunciation',
            '詞性': 'part_of_speech',
            '釋義': 'definition',
            '例句': 'examples',
            '其他資訊': 'additional_info',
        }
        
        # Try to map existing columns
        rename_dict = {}
        for original, standard in column_mapping.items():
            if original in self.df.columns:
                rename_dict[original] = standard
            # Also try fuzzy matching if exact names don't match
            elif standard not in self.df.columns:
                for col in self.df.columns:
                    if original.lower() in col.lower() or col.lower() in original.lower():
                        rename_dict[col] = standard
                        break
        
        if rename_dict:
            self.df = self.df.rename(columns=rename_dict)
        
        # Ensure required columns exist (pad with None if missing)
        required = ['word', 'pronunciation', 'part_of_speech', 'definition', 'examples']
        for col in required:
            if col not in self.df.columns:
                self.df[col] = None
        
        logger.info(f"Normalized columns: {list(self.df.columns)}")
    
    def find_exact_match(self, word: str) -> Optional[Dict]:
        """
        Find exact word match.
        
        Args:
            word: Word to search
        
        Returns:
            dict with entry details or None
        """
        word_lower = word.strip().lower()
        
        if word_lower in self.word_index:
            idx = self.word_index[word_lower]
            return self._format_entry(self.df.iloc[idx])
        
        return None
    
    def find_fuzzy_matches(self, word: str, max_results: int = 5) -> List[Dict]:
        """
        Find similar words (fuzzy matching).
        
        Args:
            word: Word to search
            max_results: Maximum number of results
        
        Returns:
            list of similar entries
        """
        word_lower = word.strip().lower()
        candidates = list(self.word_index.keys())
        
        # Find close matches
        matches = difflib.get_close_matches(
            word_lower, candidates, n=max_results, cutoff=0.6
        )
        
        results = []
        for match in matches:
            idx = self.word_index[match]
            entry = self._format_entry(self.df.iloc[idx])
            results.append(entry)
        
        return results
    
    def find_prefix_matches(self, prefix: str, max_results: int = 10) -> List[Dict]:
        """
        Find words starting with prefix.
        
        Args:
            prefix: Prefix to search
            max_results: Maximum results
        
        Returns:
            list of matching entries
        """
        prefix_lower = prefix.strip().lower()
        
        matches = [
            word for word in self.word_index.keys()
            if word.startswith(prefix_lower)
        ]
        
        results = []
        for match in matches[:max_results]:
            idx = self.word_index[match]
            entry = self._format_entry(self.df.iloc[idx])
            results.append(entry)
        
        return results
    
    def _format_entry(self, row: pd.Series, full: bool = False) -> Dict:
        """
        Format a dictionary entry.
        
        Args:
            row: DataFrame row
            full: Include all details
        
        Returns:
            Formatted entry dict
        """
        entry = {
            'word': str(row['word']).strip() if pd.notna(row['word']) else None,
            'pronunciation': str(row['pronunciation']).strip() if pd.notna(row['pronunciation']) else None,
            'definition': str(row['definition']).strip() if pd.notna(row['definition']) else None,
        }
        
        if full:
            entry.update({
                'part_of_speech': str(row['part_of_speech']).strip() if pd.notna(row['part_of_speech']) else None,
                'examples': str(row['examples']).strip() if pd.notna(row['examples']) else None,
                'additional_info': str(row['additional_info']).strip() if pd.notna(row.get('additional_info')) else None,
            })
        
        return entry
    
    def query(self, word: str, full: bool = False) -> Dict:
        """
        Query the dictionary for a word.
        
        Returns exact match first, then fuzzy/prefix matches.
        
        Args:
            word: Word to look up
            full: Return full details
        
        Returns:
            dict with primary result and alternatives
        """
        logger.info(f"Querying: {word}")
        
        # Try exact match
        exact = self.find_exact_match(word)
        if exact:
            result = {
                'success': True,
                'query': word,
                'match_type': 'exact',
                'primary': self._format_entry(
                    self.df.loc[self.word_index[word.strip().lower()]], 
                    full=full
                ),
            }
            return result
        
        # Try fuzzy matches
        fuzzy = self.find_fuzzy_matches(word, max_results=3)
        if fuzzy:
            return {
                'success': True,
                'query': word,
                'match_type': 'fuzzy',
                'alternatives': fuzzy,
            }
        
        # Try prefix matches
        prefix = self.find_prefix_matches(word, max_results=5)
        if prefix:
            return {
                'success': True,
                'query': word,
                'match_type': 'prefix',
                'alternatives': prefix,
            }
        
        return {
            'success': False,
            'query': word,
            'error': 'No matching words found',
        }


def get_dictionary_path(dict_name: str, storage_path: str = None) -> Optional[str]:
    """Get the xlsx path from metadata."""
    if storage_path:
        storage = Path(storage_path).expanduser()
    else:
        storage = Path.home() / '.openclaw' / 'dictionaries'
    
    metadata_file = storage / 'metadata.json'
    if not metadata_file.exists():
        logger.error("Metadata not found. Download dictionary first.")
        return None
    
    try:
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        if dict_name not in metadata:
            logger.error(f"Dictionary '{dict_name}' not found in metadata")
            return None
        
        info = metadata[dict_name]
        xlsx_path = Path(info['path']) / info['filename']
        
        if not xlsx_path.exists():
            logger.error(f"Dictionary file not found: {xlsx_path}")
            return None
        
        return str(xlsx_path)
    
    except Exception as e:
        logger.error(f"Failed to read metadata: {e}")
        return None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Query Traditional Chinese dictionary')
    parser.add_argument('--word', required=True, help='Word to look up')
    parser.add_argument('--dict-name', default='concised', help='Dictionary name')
    parser.add_argument('--storage-path', help='Storage directory')
    parser.add_argument('--full', action='store_true', help='Return full details')
    
    args = parser.parse_args()
    
    try:
        # Get dictionary path from metadata
        xlsx_path = get_dictionary_path(args.dict_name, args.storage_path)
        if not xlsx_path:
            raise FileNotFoundError("Dictionary not available. Please download first.")
        
        # Query
        query_engine = DictionaryQuery(xlsx_path, args.dict_name)
        result = query_engine.query(args.word, full=args.full)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result['success'] else 1)
    
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e),
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

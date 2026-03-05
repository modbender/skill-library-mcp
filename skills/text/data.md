# Text Data Processing

## CSV/TSV Handling

### Quoted Fields with Embedded Delimiters
```bash
# WRONG: Simple split on comma
echo 'John,"123 Main St, Apt 4",NYC' | cut -d',' -f2
# Result: "123 Main St (broken)

# RIGHT: Use proper CSV parser
python3 -c "import csv,sys; r=csv.reader(sys.stdin); print(list(r))"
```

**Rule:** For CSV, ALWAYS use `csvkit`, `pandas`, or language CSV library. Never split on comma.

### Detect Delimiter
```python
import csv
with open('file.txt') as f:
    sample = f.read(8192)
    dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
```

---

## Regex Patterns

### Greedy vs Non-Greedy
```regex
# BAD: Captures too much
<div>.*</div>  → matches first <div> to LAST </div>

# GOOD: Non-greedy
<div>.*?</div>  → matches each pair
```

### Multiline Content
```regex
# BAD: . doesn't match newlines
/pattern.*/

# GOOD: Use DOTALL or explicit
/pattern[\s\S]*/
/pattern.*/s
```

### Common Patterns
```regex
# Email (practical)
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$

# URL
https?://[^\s<>"{}|\\^`\[\]]+

# Phone (US)
\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})
```

---

## Text Cleaning

### Unicode Normalization (Critical for Dedup)
```python
import unicodedata

# "café" (é as single char) vs "café" (e + combining accent)
normalized = unicodedata.normalize('NFC', text)

# Remove accents entirely
def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) 
                   if unicodedata.category(c) != 'Mn')
```

### Smart Quotes & Typography
```python
TYPOGRAPHY_MAP = {
    '"': '"', '"': '"', ''': "'", ''': "'",
    '–': '-', '—': '-',
    '…': '...',
    '\xa0': ' ',  # Non-breaking space
    '\u200b': '',  # Zero-width space
}
```

### Whitespace Normalization
```python
import re

def clean_whitespace(text):
    text = text.strip()
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text
```

---

## Deduplication

### Exact Match (after normalization)
```python
def dedup_key(text):
    text = text.lower().strip()
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text
```

### Fuzzy Match
```python
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# Threshold: 0.85-0.90 for "probably same"
```

### Name Deduplication
```python
def name_dedup_key(name):
    """Handle: "John Smith" vs "Smith, John" vs "J. Smith" """
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', ' ', name)
    parts = sorted(name.split())
    return ' '.join(parts)
```

---

## Entity Extraction

### Null Value Detection
```python
NULL_VALUES = {
    '', 'null', 'none', 'n/a', 'na', 'nan', '-', '--', 
    'undefined', 'unknown', '.', '?', 'tbd', 'tba'
}

def is_null(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in NULL_VALUES
    return False
```

### Safe Type Conversion
```python
def safe_int(value, default=None):
    if is_null(value):
        return default
    try:
        cleaned = re.sub(r'[,\s]', '', str(value))
        return int(float(cleaned))
    except (ValueError, TypeError):
        return default
```

---

## Format Standardization

### Names
```python
def standardize_name(name):
    name = name.strip()
    
    # Handle "Last, First" format
    if ',' in name:
        parts = [p.strip() for p in name.split(',', 1)]
        if len(parts) == 2:
            name = f"{parts[1]} {parts[0]}"
    
    # Title case with exceptions
    exceptions = {'van', 'von', 'de', 'la', 'del', 'der'}
    words = name.lower().split()
    result = []
    for i, word in enumerate(words):
        if word in exceptions and i > 0:
            result.append(word)
        else:
            result.append(word.capitalize())
    
    return ' '.join(result)
```

### Phones
```python
def normalize_phone(phone, country='US'):
    digits = re.sub(r'\D', '', phone)
    if country == 'US' and len(digits) == 10:
        return f"+1{digits}"
    return f"+{digits}"
```

---

## Parsing Structured Text

### Log Parsing
```bash
# Apache/Nginx combined log
^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) ([^"]+)" (\d+) (\d+)

# Syslog
^(\w+\s+\d+\s+[\d:]+)\s+(\S+)\s+(\S+):\s+(.*)$

# JSON logs - ALWAYS use jq
cat app.log | jq -r 'select(.level=="error") | .message'
```

### Config Files
```bash
# INI - extract section
sed -n '/^\[section\]/,/^\[/p' config.ini | grep -v '^\['

# YAML - ALWAYS use yq
yq '.database.host' config.yaml

# .env files
grep -v '^#' .env | grep '='
```

---

## Quick Commands

```bash
# Count lines/unique
wc -l file.csv
cut -d',' -f1 file.csv | sort -u | wc -l

# Find encoding issues
grep -P '[\x80-\xFF]' file.txt

# Remove BOM
sed -i '1s/^\xEF\xBB\xBF//' file.csv

# Convert TSV to CSV (proper)
python3 -c "import csv,sys; w=csv.writer(sys.stdout); [w.writerow(r) for r in csv.reader(sys.stdin, delimiter='\t')]" < file.tsv > file.csv
```

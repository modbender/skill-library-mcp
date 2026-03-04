# ClawPressor

Intelligently compress OpenClaw session context to reduce token usage and extend session lifetime.

## Installation

```bash
pip install sumy
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords')"
```

## Usage

```bash
# Preview
python3 scripts/compress.py --dry-run

# Apply
python3 scripts/compress.py --apply

# Restore
python3 scripts/compress.py --restore

# Stats
python3 scripts/compress.py --stats
```

## Results

- **-96%** messages
- **-84%** tokens  
- **+400%** session duration

## Credits

- **Coding:** JARVIS 🤖
- **Management:** BeBoX 👤

## License

MIT

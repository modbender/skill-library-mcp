# aimlapi-embeddings

Text embeddings via AIMLAPI.

## Installation

```bash
clawhub install aimlapi-embeddings
```

## Setup

Set your API key:
```bash
export AIMLAPI_API_KEY="your-key-here"
```

## Usage

```bash
# Basic usage
python scripts/gen_embeddings.py --input "Hello world"

# Specify model and dimensions
python scripts/gen_embeddings.py --input "Semantic search is cool" --model text-embedding-3-large --dimensions 1024
```

## Features
- Standard OpenAI-compatible embeddings API.
- Support for `text-embedding-3-small`, `text-embedding-3-large`, and others.
- Automatic retries and timeout handling.
- Flexible output directory.

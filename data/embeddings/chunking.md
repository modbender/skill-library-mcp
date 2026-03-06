# Chunking Strategies

## Why Chunking Matters

Embedding models have token limits (512-8192). Long documents must be split. Poor chunking = poor retrieval.

## Strategy Selection

| Content Type | Strategy | Chunk Size | Overlap |
|--------------|----------|------------|---------|
| Documentation | Semantic sections | 500-1000 | 10% |
| Code | Function/class boundaries | 200-500 | 0% |
| Chat/logs | Turn boundaries | 100-300 | 0% |
| Legal/contracts | Paragraph | 300-600 | 15% |
| Books/articles | Recursive character | 800-1200 | 20% |

## Fixed-Size Chunking

Simple but often breaks mid-sentence:

```python
def chunk_fixed(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
```

## Recursive Character Splitting (Recommended)

Respects document structure:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_text(document)
```

## Semantic Chunking

Groups by meaning, not character count:

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

splitter = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95
)
chunks = splitter.split_text(document)
```

## Code-Aware Chunking

Respects code boundaries:

```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=500,
    chunk_overlap=0  # functions are self-contained
)
chunks = splitter.split_text(code)
```

## Chunk Metadata

Always store context:

```python
def create_chunks_with_metadata(text, source, chunk_size=1000):
    chunks = split_text(text, chunk_size)
    return [
        {
            "content": chunk,
            "source": source,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "char_start": sum(len(c) for c in chunks[:i]),
            "hash": hashlib.md5(chunk.encode()).hexdigest()[:8]
        }
        for i, chunk in enumerate(chunks)
    ]
```

## Token Counting

Don't guess—count:

```python
import tiktoken

def count_tokens(text, model="text-embedding-3-small"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def chunk_by_tokens(text, max_tokens=500, overlap_tokens=50):
    encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    tokens = encoding.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        start = end - overlap_tokens
    return chunks
```

## Anti-Patterns

❌ **Fixed 1000 chars with no overlap** — Breaks context at boundaries
❌ **Chunking by sentence only** — Single sentences lack context
❌ **No metadata** — Can't reconstruct original or cite source
❌ **Embedding whole documents** — Dilutes signal with irrelevant content
❌ **Different chunk sizes for index vs query** — Creates retrieval mismatch

## Optimal Chunk Sizes by Use Case

| Use Case | Chunk Size | Why |
|----------|------------|-----|
| Q&A retrieval | 200-500 tokens | Specific answers |
| Document summarization | 1000-2000 tokens | Broader context |
| Code search | 100-300 tokens | Function granularity |
| Chat history | 50-150 tokens | Turn granularity |

#!/usr/bin/env python3
"""
Telnyx RAG Memory - Ask (RAG Pipeline)

Full RAG pipeline: query -> retrieve top-k chunks -> rerank -> build prompt -> LLM -> answer.

Usage:
  ./ask.py "What is Telnyx's porting process?"
  ./ask.py "How do I set up voice calls?" --num 5
  ./ask.py "meeting notes" --context           # Show retrieved chunks
  ./ask.py "deployment steps" --json           # Structured output
  ./ask.py "API usage" --model meta-llama/Meta-Llama-3.1-8B-Instruct
"""

import os
import sys
import json
import math
import re
import urllib.request
import urllib.error
import time
import argparse
from collections import Counter
from pathlib import Path


def load_config():
    """Load configuration from config.json

    Returns:
        dict: Merged configuration with defaults
    """
    defaults = {
        "bucket": "openclaw-memory",
        "region": "us-central-1",
        "priority_prefixes": ["memory/", "MEMORY.md"],
        "ask_model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "ask_num_docs": 8,
        "retrieve_num_docs": 20,
    }
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                user_config = json.load(f)
            return {**defaults, **user_config}
        except (json.JSONDecodeError, IOError):
            pass
    return defaults


def load_credentials():
    """Load Telnyx API key from environment or .env file

    Returns:
        str or None: The API key, or None if not found
    """
    api_key = os.environ.get("TELNYX_API_KEY")
    if api_key:
        return api_key

    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TELNYX_API_KEY="):
                        return line.split("=", 1)[1].strip('"').strip("'")
        except IOError:
            pass
    return None


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def retrieve_chunks(query, num_docs, bucket, api_key, timeout=30, max_retries=3):
    """Retrieve similar chunks from Telnyx similarity search API

    Args:
        query (str): Search query
        num_docs (int): Number of documents to retrieve
        bucket (str): Bucket name
        api_key (str): Telnyx API key
        timeout (int): Request timeout seconds
        max_retries (int): Max retry attempts

    Returns:
        list[dict]: List of {content, source, certainty} dicts
    """
    url = "https://api.telnyx.com/v2/ai/embeddings/similarity-search"
    payload = json.dumps({
        "bucket_name": bucket,
        "query": query,
        "num_docs": num_docs,
    }).encode()

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
        "User-Agent": "openclaw-telnyx-rag/2.0",
    }

    for attempt in range(max_retries):
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
                return _normalize_results(data)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            if e.code in (401, 403, 404):
                raise RuntimeError("Retrieval failed (HTTP %d): %s" % (e.code, body))
            if attempt < max_retries - 1 and e.code >= 500:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError("Retrieval failed (HTTP %d): %s" % (e.code, body))
        except (urllib.error.URLError, OSError) as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError("Network error during retrieval: %s" % e)

    raise RuntimeError("Max retries exceeded during retrieval")


def _normalize_results(response_data):
    """Normalize Telnyx API response into a flat list of dicts

    Args:
        response_data (dict): Raw API response

    Returns:
        list[dict]: Normalized results
    """
    results = []
    items = []
    if "data" in response_data and isinstance(response_data["data"], list):
        items = response_data["data"]

    for doc in items:
        content = doc.get("document_chunk", doc.get("content", ""))
        meta = doc.get("metadata", {})
        source = meta.get("filename", doc.get("file_name", "unknown"))
        certainty = meta.get("certainty", doc.get("certainty", 0))
        results.append({
            "content": content,
            "source": source,
            "certainty": float(certainty) if certainty else 0.0,
        })
    return results


# ---------------------------------------------------------------------------
# Reranking
# ---------------------------------------------------------------------------

def _tokenize(text):
    """Simple whitespace + punctuation tokenizer

    Args:
        text (str): Input text

    Returns:
        list[str]: Lowercased tokens
    """
    return re.findall(r"[a-z0-9]+", text.lower())


def _idf_scores(docs):
    """Compute inverse-document-frequency for tokens across docs

    Args:
        docs (list[str]): List of document texts

    Returns:
        dict[str, float]: Token -> IDF score
    """
    n = len(docs)
    if n == 0:
        return {}
    df = Counter()
    for doc in docs:
        tokens = set(_tokenize(doc))
        for t in tokens:
            df[t] += 1
    return {t: math.log((n + 1) / (count + 1)) + 1 for t, count in df.items()}


def _keyword_overlap_score(query_tokens, doc_text, idf):
    """Score a document by TF-IDF weighted keyword overlap with the query

    Args:
        query_tokens (list[str]): Tokenized query
        doc_text (str): Document text
        idf (dict): IDF scores

    Returns:
        float: Overlap score
    """
    doc_tokens = Counter(_tokenize(doc_text))
    if not doc_tokens:
        return 0.0
    score = 0.0
    for qt in query_tokens:
        if qt in doc_tokens:
            tf = doc_tokens[qt] / sum(doc_tokens.values())
            score += tf * idf.get(qt, 1.0)
    return score


def _priority_score(source, priority_prefixes):
    """Score a source filename by priority prefix match (lower = better)

    Args:
        source (str): Filename / key
        priority_prefixes (list[str]): Ordered priority prefixes

    Returns:
        int: Priority rank (0 = highest)
    """
    for i, prefix in enumerate(priority_prefixes):
        if source.startswith(prefix):
            return i
    return len(priority_prefixes)


def _is_adjacent_duplicate(a, b):
    """Check if two chunks are near-identical adjacent chunks from same source

    Args:
        a (dict): First chunk
        b (dict): Second chunk

    Returns:
        bool: True if they should be deduplicated
    """
    if a["source"] != b["source"]:
        return False
    # Check for __chunk- pattern
    pat = re.compile(r"^(.+)__chunk-(\d+)\.\w+$")
    ma = pat.match(a["source"])
    mb = pat.match(b["source"])
    if ma and mb and ma.group(1) == mb.group(1):
        if abs(int(ma.group(2)) - int(mb.group(2))) <= 1:
            # Check content similarity via token overlap
            ta = set(_tokenize(a["content"]))
            tb = set(_tokenize(b["content"]))
            if ta and tb:
                overlap = len(ta & tb) / min(len(ta), len(tb))
                return overlap > 0.8
    return False


def rerank(query, chunks, num_final, priority_prefixes):
    """Rerank retrieved chunks using keyword overlap, priority, and dedup

    Args:
        query (str): Original query
        chunks (list[dict]): Retrieved chunks with content/source/certainty
        num_final (int): Number of results to return after reranking
        priority_prefixes (list[str]): Priority source prefixes

    Returns:
        list[dict]: Top-N reranked chunks
    """
    if not chunks:
        return []

    query_tokens = _tokenize(query)
    doc_texts = [c["content"] for c in chunks]
    idf = _idf_scores(doc_texts)

    scored = []
    for c in chunks:
        kw_score = _keyword_overlap_score(query_tokens, c["content"], idf)
        pri = _priority_score(c["source"], priority_prefixes)
        # Combined score: certainty (0-1) + keyword overlap + priority bonus
        combined = c["certainty"] * 2.0 + kw_score * 1.0 + (1.0 / (pri + 1)) * 0.3
        scored.append((combined, c))

    # Sort descending by combined score
    scored.sort(key=lambda x: -x[0])

    # Deduplicate adjacent chunks
    result = []
    for _, chunk in scored:
        is_dup = False
        for existing in result:
            if _is_adjacent_duplicate(chunk, existing):
                is_dup = True
                break
        if not is_dup:
            result.append(chunk)
        if len(result) >= num_final:
            break

    return result


# ---------------------------------------------------------------------------
# LLM Generation
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "Answer based on the provided context. If the context doesn't contain "
    "enough information, say so. Include references to source files when relevant."
)


def build_prompt(query, chunks):
    """Build the prompt with context chunks for the LLM

    Args:
        query (str): User question
        chunks (list[dict]): Retrieved and reranked chunks

    Returns:
        list[dict]: Messages list for chat completions API
    """
    context_parts = []
    for i, c in enumerate(chunks, 1):
        source = c.get("source", "unknown")
        context_parts.append("[%d] Source: %s\n%s" % (i, source, c["content"]))

    context_block = "\n\n---\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Context:\n\n%s\n\n---\n\nQuestion: %s" % (context_block, query)
            ),
        },
    ]
    return messages


def call_llm(messages, model, api_key, timeout=60, max_retries=2):
    """Call Telnyx inference API for chat completion

    Args:
        messages (list[dict]): Chat messages
        model (str): Model identifier
        api_key (str): Telnyx API key
        timeout (int): Request timeout
        max_retries (int): Max retries

    Returns:
        str: Generated answer text
    """
    url = "https://api.telnyx.com/v2/ai/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.3,
    }).encode()

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
        "User-Agent": "openclaw-telnyx-rag/2.0",
    }

    for attempt in range(max_retries):
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return "(No response generated)"
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            if e.code in (401, 403):
                raise RuntimeError("LLM API auth error (HTTP %d): %s" % (e.code, body))
            if attempt < max_retries - 1 and e.code >= 500:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError("LLM API error (HTTP %d): %s" % (e.code, body))
        except (urllib.error.URLError, OSError) as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError("Network error calling LLM: %s" % e)

    raise RuntimeError("Max retries exceeded calling LLM")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def ask(query, config=None, num_final=None, model=None, bucket=None,
        show_context=False, output_json=False):
    """Full RAG pipeline: retrieve -> rerank -> generate

    Args:
        query (str): User question
        config (dict): Configuration (loaded if None)
        num_final (int): Final number of chunks to use
        model (str): Override LLM model name
        bucket (str): Override bucket name
        show_context (bool): Include retrieved chunks in output
        output_json (bool): Return structured JSON

    Returns:
        str: Answer text or JSON string
    """
    if config is None:
        config = load_config()

    api_key = load_credentials()
    if not api_key:
        err = "No Telnyx API key found. Set TELNYX_API_KEY or create .env file."
        if output_json:
            return json.dumps({"error": err})
        return "ERROR: " + err

    bucket = bucket or config.get("bucket", "openclaw-memory")
    model = model or config.get("ask_model", "meta-llama/Meta-Llama-3.1-70B-Instruct")
    retrieve_n = config.get("retrieve_num_docs", 20)
    final_n = num_final or config.get("ask_num_docs", 8)
    priority_prefixes = config.get("priority_prefixes", [])

    # Step 1: Retrieve
    try:
        raw_chunks = retrieve_chunks(query, retrieve_n, bucket, api_key)
    except RuntimeError as e:
        err = "Retrieval failed: %s" % e
        if output_json:
            return json.dumps({"error": err})
        return "ERROR: " + err

    if not raw_chunks:
        msg = "No relevant documents found for your query."
        if output_json:
            return json.dumps({"answer": msg, "sources": [], "chunks_used": 0})
        return msg

    # Step 2: Rerank
    ranked = rerank(query, raw_chunks, final_n, priority_prefixes)

    # Step 3: Build prompt & call LLM
    messages = build_prompt(query, ranked)
    try:
        answer = call_llm(messages, model, api_key)
    except RuntimeError as e:
        err = "LLM generation failed: %s" % e
        if output_json:
            return json.dumps({"error": err})
        return "ERROR: " + err

    # Collect sources
    sources = list(dict.fromkeys(c["source"] for c in ranked))  # unique, ordered

    if output_json:
        result = {
            "answer": answer,
            "model": model,
            "sources": sources,
            "chunks_used": len(ranked),
            "chunks_retrieved": len(raw_chunks),
        }
        if show_context:
            result["context"] = [
                {"source": c["source"], "certainty": c["certainty"],
                 "content": c["content"]}
                for c in ranked
            ]
        return json.dumps(result, indent=2)

    # Text output
    lines = []
    lines.append(answer)
    lines.append("")
    lines.append("📚 Sources: " + ", ".join(sources))

    if show_context:
        lines.append("")
        lines.append("=" * 60)
        lines.append("Retrieved Context Chunks (%d):" % len(ranked))
        lines.append("=" * 60)
        for i, c in enumerate(ranked, 1):
            lines.append("")
            lines.append("[%d] %s (certainty: %.3f)" % (i, c["source"], c["certainty"]))
            lines.append("-" * 40)
            lines.append(c["content"][:1000])
            if len(c["content"]) > 1000:
                lines.append("...[truncated]")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Ask questions using Telnyx RAG pipeline"
    )
    parser.add_argument("query", nargs="*", help="Question to ask")
    parser.add_argument(
        "--model", "-m", default=None,
        help="LLM model name (default: from config.json)"
    )
    parser.add_argument(
        "--num", "-n", type=int, default=None,
        help="Number of context chunks to use (default: from config.json)"
    )
    parser.add_argument(
        "--bucket", "-b", default=None,
        help="Override bucket name"
    )
    parser.add_argument(
        "--context", "-c", action="store_true",
        help="Show retrieved context chunks alongside answer"
    )
    parser.add_argument(
        "--json", "-j", dest="output_json", action="store_true",
        help="Output structured JSON"
    )

    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        sys.exit(1)

    query = " ".join(args.query)

    if not args.output_json:
        print("\n🤔 Asking: \"%s\"\n" % query)

    result = ask(
        query=query,
        num_final=args.num,
        model=args.model,
        bucket=args.bucket,
        show_context=args.context,
        output_json=args.output_json,
    )

    print(result)


if __name__ == "__main__":
    main()

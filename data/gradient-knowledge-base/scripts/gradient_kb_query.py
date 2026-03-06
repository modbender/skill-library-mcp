#!/usr/bin/env python3
"""
🦞 Gradient AI — Knowledge Base Query

Query a DigitalOcean Gradient Knowledge Base with semantic or hybrid search.
Optionally combine with an LLM call for full RAG (Retrieval-Augmented Generation).

Usage:
    python3 gradient_kb_query.py --query "What happened with Q4 earnings?"
    python3 gradient_kb_query.py --query "$CAKE analysis" --alpha 0.5
    python3 gradient_kb_query.py --query "Summarize CAKE" --rag --model openai-gpt-oss-120b

Docs: https://docs.digitalocean.com/products/gradient-ai-platform/how-to/create-manage-knowledge-bases/
"""

import argparse
import json
import os
import sys
from typing import Optional

import requests

KB_RETRIEVE_BASE_URL = "https://kbaas.do-ai.run/v1"
INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"


def query_kb(
    query: str,
    kb_uuid: Optional[str] = None,
    api_token: Optional[str] = None,
    num_results: int = 10,
    alpha: Optional[float] = None,
) -> dict:
    """Query a Gradient Knowledge Base.

    Uses the KB retrieval endpoint for semantic or hybrid search.

    Args:
        query: The search query.
        kb_uuid: Knowledge Base UUID. Falls back to GRADIENT_KB_UUID.
        api_token: DO API token. Falls back to DO_API_TOKEN.
        num_results: Number of results to return (1–100).
        alpha: Hybrid search tuning (0.0=lexical, 0.5=balanced, 1.0=semantic).
               None uses the API default.

    Returns:
        dict with 'success', 'results' (list), 'query', and 'message'.

    See: https://docs.digitalocean.com/products/gradient-ai-platform/how-to/create-manage-knowledge-bases/
    """
    kb_uuid = kb_uuid or os.environ.get("GRADIENT_KB_UUID", "")
    api_token = api_token or os.environ.get("DO_API_TOKEN", "")

    if not kb_uuid:
        return {"success": False, "results": [], "query": query, "message": "No GRADIENT_KB_UUID configured."}
    if not api_token:
        return {"success": False, "results": [], "query": query, "message": "No DO_API_TOKEN configured."}

    try:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        url = f"{KB_RETRIEVE_BASE_URL}/{kb_uuid}/retrieve"
        payload = {"query": query, "num_results": num_results}

        if alpha is not None:
            payload["alpha"] = alpha

        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        results = data.get("results", [])

        return {
            "success": True,
            "results": results,
            "query": query,
            "message": f"Found {len(results)} relevant documents.",
        }
    except requests.RequestException as e:
        return {"success": False, "results": [], "query": query, "message": f"KB query failed: {str(e)}"}


def build_rag_messages(query: str, kb_results: list[dict]) -> list[dict]:
    """Build structured messages for RAG, separating system context from user input.

    Returns a list of chat messages with proper role separation to prevent
    prompt injection — user input stays in the 'user' role, instructions
    and KB context stay in the 'system' role.

    Args:
        query: The user's original question.
        kb_results: Results from the Knowledge Base query.

    Returns:
        List of message dicts with 'role' and 'content' keys.
    """
    if not kb_results:
        context = "No relevant documents found in the knowledge base yet. It may still be building up."
    else:
        context_parts = []
        for i, result in enumerate(kb_results, 1):
            content = result.get("content", result.get("text", ""))
            source = result.get("metadata", {}).get("source", "unknown")
            score = result.get("score", 0)
            context_parts.append(f"### Source {i} (relevance: {score:.2f}, source: {source})\n{content}")
        context = "\n\n".join(context_parts)

    system_msg = f"""You are a helpful assistant with access to a knowledge base.
Answer the user's question using ONLY the retrieved context below.
Be specific, cite source numbers when available, and note when information might be incomplete.
If the KB doesn't have enough data, say so honestly. Be concise but thorough.

## Retrieved Context (from Knowledge Base):
{context}"""

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": query},
    ]


def query_with_rag(
    query: str,
    kb_uuid: Optional[str] = None,
    model: str = "openai-gpt-oss-120b",
    api_key: Optional[str] = None,
    api_token: Optional[str] = None,
    num_results: int = 10,
    alpha: Optional[float] = None,
) -> dict:
    """Run a full RAG pipeline: KB search → prompt construction → LLM synthesis.

    Args:
        query: The user's question.
        kb_uuid: Knowledge Base UUID. Falls back to GRADIENT_KB_UUID.
        model: LLM model for synthesis.
        api_key: Gradient API key (for inference). Falls back to GRADIENT_API_KEY.
        api_token: DO API token (for KB query). Falls back to DO_API_TOKEN.
        num_results: Number of KB results to retrieve.
        alpha: Hybrid search tuning parameter.

    Returns:
        dict with 'success', 'answer', 'sources_count', 'kb_success', and 'message'.
    """
    api_key = api_key or os.environ.get("GRADIENT_API_KEY", "")

    if not api_key:
        return {
            "success": False,
            "answer": "",
            "sources_count": 0,
            "message": "No GRADIENT_API_KEY configured for LLM synthesis.",
        }

    # Step 1: Query the Knowledge Base
    kb_result = query_kb(query, kb_uuid=kb_uuid, api_token=api_token,
                         num_results=num_results, alpha=alpha)
    kb_results = kb_result.get("results", [])

    # Step 2: Build structured messages (system context + user query separated)
    messages = build_rag_messages(query, kb_results)

    # Step 3: Call LLM for synthesis
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 1500,
        }

        resp = requests.post(INFERENCE_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()

        data = resp.json()
        answer = data["choices"][0]["message"]["content"]

        return {
            "success": True,
            "answer": answer,
            "sources_count": len(kb_results),
            "kb_success": kb_result["success"],
            "message": f"Answered using {len(kb_results)} sources from the Knowledge Base.",
        }
    except (requests.RequestException, KeyError, IndexError) as e:
        return {
            "success": False,
            "answer": "",
            "sources_count": len(kb_results),
            "message": f"LLM synthesis failed: {str(e)}",
        }


# ─── CLI Interface ────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="🦞 Query a Gradient Knowledge Base"
    )
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--kb-uuid", default=None, help="Knowledge Base UUID")
    parser.add_argument("--num-results", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--alpha", type=float, default=None,
                        help="Hybrid search tuning: 0.0=lexical, 0.5=balanced, 1.0=semantic")
    parser.add_argument("--rag", action="store_true", help="Run full RAG pipeline (KB + LLM)")
    parser.add_argument("--model", default="openai-gpt-oss-120b", help="LLM model for RAG synthesis")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.rag:
        result = query_with_rag(
            query=args.query,
            kb_uuid=args.kb_uuid,
            model=args.model,
            num_results=args.num_results,
            alpha=args.alpha,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        elif result["success"]:
            print(result["answer"])
            print(f"\n📚 Used {result['sources_count']} sources.", file=sys.stderr)
        else:
            print(f"Error: {result['message']}", file=sys.stderr)
            sys.exit(1)
    else:
        result = query_kb(
            query=args.query,
            kb_uuid=args.kb_uuid,
            num_results=args.num_results,
            alpha=args.alpha,
        )
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        elif result["success"]:
            for i, r in enumerate(result["results"], 1):
                content = r.get("content", r.get("text", ""))
                score = r.get("score", 0)
                print(f"[{i}] (score: {score:.2f}) {content[:200]}...")
            print(f"\n🔍 {result['message']}", file=sys.stderr)
        else:
            print(f"Error: {result['message']}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

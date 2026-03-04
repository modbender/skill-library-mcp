#!/usr/bin/env python3
"""
Dify Knowledge Base Search - Query dataset for relevant context
"""
import os
import sys
import json
import requests


def get_dify_client():
    """Get Dify API configuration from environment variables."""
    api_key = os.environ.get("DIFY_API_KEY")
    base_url = os.environ.get("DIFY_BASE_URL", "http://localhost/v1").rstrip('/')

    if not api_key:
        raise ValueError("Missing DIFY_API_KEY environment variable")

    return {
        "api_key": api_key,
        "base_url": base_url,
        "headers": {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    }


def search_dataset(query, dataset_id=None, top_k=3, search_method="hybrid_search", reranking_enable=False):
    """
    Search a specific Dify Dataset for relevant chunks.

    Args:
        query: The search query or question
        dataset_id: The Dataset ID (optional, auto-discovers if not provided)
        top_k: Number of results to return (default: 3)
        search_method: Search method - "hybrid_search", "semantic_search", or "keyword_search"
        reranking_enable: Whether to enable reranking (default: False)
    """
    try:
        client = get_dify_client()

        # Auto-discover dataset if not provided
        if not dataset_id:
            datasets_url = f"{client['base_url']}/datasets"
            response = requests.get(datasets_url, headers=client['headers'], timeout=30)
            response.raise_for_status()
            data = response.json()

            if "data" in data and len(data["data"]) > 0:
                dataset_id = data["data"][0]["id"]
            else:
                print(json.dumps({
                    "status": "error",
                    "error": "No datasets found. Please configure DIFY_BASE_URL and DIFY_API_KEY correctly."
                }, ensure_ascii=False))
                sys.exit(1)

        # Prepare API request
        url = f"{client['base_url']}/datasets/{dataset_id}/retrieve"
        payload = {
            "query": query,
            "retrieval_model": {
                "search_method": search_method,
                "reranking_enable": reranking_enable,
                "top_k": int(top_k)
            }
        }

        response = requests.post(url, headers=client['headers'], json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Format output for OpenClaw
        results = []
        if "records" in data:
            for record in data["records"]:
                results.append({
                    "content": record.get("content", ""),
                    "score": round(record.get("score", 0), 4),
                    "title": record.get("title", ""),
                    "document_id": record.get("document_id", "")
                })

        print(json.dumps({
            "status": "success",
            "query": query,
            "dataset_id": dataset_id,
            "count": len(results),
            "results": results
        }, ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        print(json.dumps({
            "status": "error",
            "error": f"API request failed: {str(e)}"
        }, ensure_ascii=False))
        sys.exit(1)
    except ValueError as e:
        print(json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        }, ensure_ascii=False))
        sys.exit(1)


def main():
    """Main entry point - read parameters from stdin."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({
            "status": "error",
            "error": "Invalid JSON input. Expected: {\"query\": \"...\"}"
        }, ensure_ascii=False))
        sys.exit(1)

    # Extract parameters with defaults
    query = input_data.get("query")
    dataset_id = input_data.get("dataset_id")
    top_k = input_data.get("top_k", 3)
    search_method = input_data.get("search_method", "hybrid_search")
    reranking_enable = input_data.get("reranking_enable", False)

    # Validate required parameters
    if not query:
        print(json.dumps({
            "status": "error",
            "error": "Missing required 'query' parameter"
        }, ensure_ascii=False))
        sys.exit(1)

    # Execute search
    search_dataset(
        query=query,
        dataset_id=dataset_id,
        top_k=top_k,
        search_method=search_method,
        reranking_enable=reranking_enable
    )


if __name__ == "__main__":
    main()

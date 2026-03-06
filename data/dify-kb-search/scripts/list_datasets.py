#!/usr/bin/env python3
"""
Dify Knowledge Base Search - Search and list datasets
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


def list_datasets():
    """List all available knowledge bases (datasets)."""
    try:
        client = get_dify_client()
        url = f"{client['base_url']}/datasets"

        response = requests.get(url, headers=client['headers'], timeout=30)
        response.raise_for_status()
        data = response.json()

        datasets = []
        if "data" in data:
            for ds in data["data"]:
                datasets.append({
                    "id": ds.get("id"),
                    "name": ds.get("name"),
                    "doc_count": ds.get("document_count", 0),
                    "description": ds.get("description", "")
                })

        print(json.dumps({
            "status": "success",
            "count": len(datasets),
            "datasets": datasets
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


if __name__ == "__main__":
    list_datasets()

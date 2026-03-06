#!/usr/bin/env python3
"""
Hugging Face Trending Models Fetcher

Fetches trending models from Hugging Face and formats them for display.
"""

import sys
import json
from datetime import datetime
from typing import List, Dict, Optional

try:
    import requests
except ImportError:
    print("Error: requests package not installed")
    print("Install: pip install requests")
    sys.exit(1)


class HuggingFaceTrends:
    """Fetches and formats Hugging Face trending models"""

    API_BASE = "https://huggingface.co/api"
    MODELS_ENDPOINT = "/models"
    TRENDING_URL = "https://huggingface.co/models?sort=trending"

    def __init__(self, timeout: int = 10, proxy: Optional[str] = None):
        self.timeout = timeout
        self.proxy = proxy

    def fetch_trending_models(
        self,
        limit: int = 10,
        sort_by: str = "trending",
        task_filter: Optional[str] = None,
        library_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch trending models from Hugging Face API

        Args:
            limit: Maximum number of models to return
            sort_by: Sort criteria (trending, likes, downloads, created)
            task_filter: Filter by task (e.g., "text-generation", "image-classification")
            library_filter: Filter by library (e.g., "pytorch", "tensorflow", "jax")

        Returns:
            List of model dictionaries
        """
        # Hugging Face API doesn't have a public trending endpoint without auth
        # We'll fetch recent models and sort by likes as a proxy for popularity
        url = f"{self.API_BASE}{self.MODELS_ENDPOINT}"

        params = {
            "limit": limit * 2  # Fetch more to allow filtering
        }

        if task_filter:
            params["pipeline_tag"] = task_filter
        if library_filter:
            params["library"] = library_filter

        try:
            proxies = None
            if self.proxy:
                proxies = {"http": self.proxy, "https": self.proxy}

            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
                proxies=proxies
            )
            response.raise_for_status()
            models = response.json()

            # Sort models based on sort_by parameter
            if sort_by == "trending":
                # Sort by likes as a proxy for trending/popular
                models.sort(key=lambda m: m.get("likes", 0), reverse=True)
            elif sort_by == "likes":
                models.sort(key=lambda m: m.get("likes", 0), reverse=True)
            elif sort_by == "downloads":
                models.sort(key=lambda m: m.get("downloads", 0), reverse=True)
            elif sort_by == "created":
                models.sort(key=lambda m: m.get("createdAt", ""), reverse=True)

            # Return top N models
            return models[:limit]

        except requests.exceptions.RequestException as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return []

    def format_model(self, model: Dict, index: int) -> str:
        """Format a single model for display"""

        # Extract key information
        model_id = model.get("modelId", "unknown")
        likes = model.get("likes", 0)
        downloads = model.get("downloads", 0)
        created_at = model.get("createdAt", "")
        last_modified = model.get("lastModified", "")

        # Get task/pipeline
        pipeline_tag = model.get("pipeline_tag", "N/A")

        # Get library
        library_name = model.get("library_name", "N/A")

        # Format numbers
        def format_number(num: int) -> str:
            if num >= 1_000_000:
                return f"{num / 1_000_000:.1f}M"
            elif num >= 1_000:
                return f"{num / 1_000:.1f}K"
            else:
                return str(num)

        # Format date
        def format_date(date_str: str) -> str:
            if not date_str:
                return "N/A"
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d")
            except:
                return date_str[:10] if len(date_str) >= 10 else date_str

        # Format likes/downloads
        likes_str = format_number(likes)
        downloads_str = format_number(downloads)

        # Format tags
        tags = model.get("tags", [])
        relevant_tags = [t for t in tags if t in [
            "pytorch", "tensorflow", "jax", "flax",
            "transformers", "diffusers", "spaces"
        ]]

        return (
            f"{index}. {model_id}\n"
            f"   ⭐ {likes_str} likes   📥 {downloads_str} downloads\n"
            f"   📊 Task: {pipeline_tag}   📚 Library: {library_name}\n"
            f"   📅 Created: {format_date(created_at)}   Updated: {format_date(last_modified)}\n"
        )

    def format_models(self, models: List[Dict]) -> str:
        """Format list of models for display"""

        if not models:
            return "No models found."

        header = f"🤖 Hugging Face 热门模型 ({len(models)} 个)\n"
        separator = "=" * 60 + "\n"

        formatted_models = []
        for idx, model in enumerate(models, 1):
            formatted_models.append(self.format_model(model, idx))

        return header + separator + "\n".join(formatted_models) + separator

    def export_json(self, models: List[Dict], output_file: str):
        """Export models to JSON file"""

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(models, f, indent=2, ensure_ascii=False)

        print(f"✅ Exported {len(models)} models to {output_file}")


def main():
    """Main CLI interface"""

    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch trending models from Hugging Face"
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=10,
        help="Number of models to fetch (default: 10)"
    )
    parser.add_argument(
        "-s", "--sort",
        choices=["trending", "likes", "downloads", "created"],
        default="trending",
        help="Sort criteria (default: trending)"
    )
    parser.add_argument(
        "-t", "--task",
        type=str,
        help="Filter by task (e.g., text-generation, image-classification)"
    )
    parser.add_argument(
        "-l", "--library",
        type=str,
        help="Filter by library (e.g., pytorch, tensorflow, jax)"
    )
    parser.add_argument(
        "-j", "--json",
        type=str,
        help="Export results to JSON file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show full model details"
    )
    parser.add_argument(
        "-p", "--proxy",
        type=str,
        help="Proxy URL (e.g., http://172.28.96.1:10808)"
    )

    args = parser.parse_args()

    # Fetch trending models
    fetcher = HuggingFaceTrends(proxy=args.proxy)
    models = fetcher.fetch_trending_models(
        limit=args.limit,
        sort_by=args.sort,
        task_filter=args.task,
        library_filter=args.library
    )

    if not models:
        print("❌ Failed to fetch models or no results found.")
        sys.exit(1)

    # Display results
    print(fetcher.format_models(models))

    # Export to JSON if requested
    if args.json:
        fetcher.export_json(models, args.json)


if __name__ == "__main__":
    main()

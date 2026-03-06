#!/usr/bin/env python3
"""
Web Search Hub - DuckDuckGo Search Tool

Search the web for pages, news, images, and videos using DuckDuckGo's API.
Supports multiple output formats and extensive filtering options.

Requires: pip install duckduckgo-search
"""

import argparse
import json
import sys
from typing import List, Dict, Any, Optional
from enum import Enum

try:
    from duckduckgo_search import DDGS
except ImportError:
    print("Error: duckduckgo-search library not installed", file=sys.stderr)
    print("Install with: pip install duckduckgo-search", file=sys.stderr)
    print("Or use a virtual environment if on a system-managed Python installation", file=sys.stderr)
    sys.exit(1)


class SearchType(Enum):
    """Available search types"""
    WEB = "web"
    NEWS = "news"
    IMAGES = "images"
    VIDEOS = "videos"


class OutputFormat(Enum):
    """Available output formats"""
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"


class TimeRange(Enum):
    """Time range filters"""
    DAY = "d"
    WEEK = "w"
    MONTH = "m"
    YEAR = "y"


class SafeSearch(Enum):
    """Safe search levels"""
    ON = "on"
    MODERATE = "moderate"
    OFF = "off"


def format_text_result(index: int, result: Dict[str, Any], search_type: SearchType) -> str:
    """Format a single result as plain text"""
    lines = [f"\n{index}. {result.get('title', 'No title')}"]
    
    if search_type == SearchType.WEB:
        lines.append(f"   URL: {result.get('href', 'No URL')}")
        if body := result.get('body'):
            lines.append(f"   {body}")
    
    elif search_type == SearchType.NEWS:
        lines.append(f"   URL: {result.get('url', 'No URL')}")
        if source := result.get('source'):
            lines.append(f"   Source: {source}")
        if date := result.get('date'):
            lines.append(f"   Date: {date}")
        if body := result.get('body'):
            lines.append(f"   {body}")
    
    elif search_type == SearchType.IMAGES:
        lines.append(f"   Image URL: {result.get('image', 'No URL')}")
        if thumbnail := result.get('thumbnail'):
            lines.append(f"   Thumbnail: {thumbnail}")
        if source := result.get('source'):
            lines.append(f"   Source: {source}")
        if width := result.get('width'):
            height = result.get('height', 'unknown')
            lines.append(f"   Dimensions: {width} x {height}")
    
    elif search_type == SearchType.VIDEOS:
        lines.append(f"   URL: {result.get('content', 'No URL')}")
        if publisher := result.get('publisher'):
            lines.append(f"   Publisher: {publisher}")
        if duration := result.get('duration'):
            lines.append(f"   Duration: {duration}")
        if published := result.get('published'):
            lines.append(f"   Published: {published}")
        if description := result.get('description'):
            lines.append(f"   {description}")
    
    return "\n".join(lines)


def format_markdown_result(index: int, result: Dict[str, Any], search_type: SearchType) -> str:
    """Format a single result as markdown"""
    lines = [f"\n## {index}. {result.get('title', 'No title')}\n"]
    
    if search_type == SearchType.WEB:
        lines.append(f"**URL:** {result.get('href', 'No URL')}\n")
        if body := result.get('body'):
            lines.append(f"{body}\n")
    
    elif search_type == SearchType.NEWS:
        lines.append(f"**URL:** {result.get('url', 'No URL')}\n")
        if source := result.get('source'):
            lines.append(f"**Source:** {source}\n")
        if date := result.get('date'):
            lines.append(f"**Date:** {date}\n")
        if body := result.get('body'):
            lines.append(f"{body}\n")
    
    elif search_type == SearchType.IMAGES:
        lines.append(f"**Image URL:** {result.get('image', 'No URL')}\n")
        if thumbnail := result.get('thumbnail'):
            lines.append(f"**Thumbnail:** {thumbnail}\n")
        if source := result.get('source'):
            lines.append(f"**Source:** {source}\n")
        if width := result.get('width'):
            height = result.get('height', 'unknown')
            lines.append(f"**Dimensions:** {width} x {height}\n")
    
    elif search_type == SearchType.VIDEOS:
        lines.append(f"**URL:** {result.get('content', 'No URL')}\n")
        if publisher := result.get('publisher'):
            lines.append(f"**Publisher:** {publisher}\n")
        if duration := result.get('duration'):
            lines.append(f"**Duration:** {duration}\n")
        if published := result.get('published'):
            lines.append(f"**Published:** {published}\n")
        if description := result.get('description'):
            lines.append(f"{description}\n")
    
    return "".join(lines)


def format_results(results: List[Dict[str, Any]], format_type: OutputFormat, search_type: SearchType) -> str:
    """Format search results according to the specified format"""
    if not results:
        return "No results found."
    
    if format_type == OutputFormat.JSON:
        return json.dumps(results, indent=2, ensure_ascii=False)
    
    elif format_type == OutputFormat.MARKDOWN:
        formatted = [f"# Search Results ({len(results)} found)\n"]
        for i, result in enumerate(results, 1):
            formatted.append(format_markdown_result(i, result, search_type))
        return "".join(formatted)
    
    else:  # TEXT
        formatted = [f"Search Results ({len(results)} found)"]
        for i, result in enumerate(results, 1):
            formatted.append(format_text_result(i, result, search_type))
        return "\n".join(formatted)


def search_web(
    query: str,
    max_results: int = 10,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    timelimit: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search web pages"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                keywords=query,
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results
            ))
        return results
    except Exception as e:
        print(f"Error searching web: {e}", file=sys.stderr)
        return []


def search_news(
    query: str,
    max_results: int = 10,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    timelimit: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search news articles"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(
                keywords=query,
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results
            ))
        return results
    except Exception as e:
        print(f"Error searching news: {e}", file=sys.stderr)
        return []


def search_images(
    query: str,
    max_results: int = 10,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    size: Optional[str] = None,
    color: Optional[str] = None,
    type_image: Optional[str] = None,
    layout: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search images"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(
                keywords=query,
                region=region,
                safesearch=safesearch,
                size=size,
                color=color,
                type_image=type_image,
                layout=layout,
                max_results=max_results
            ))
        return results
    except Exception as e:
        print(f"Error searching images: {e}", file=sys.stderr)
        return []


def search_videos(
    query: str,
    max_results: int = 10,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    duration: Optional[str] = None,
    resolution: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search videos"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.videos(
                keywords=query,
                region=region,
                safesearch=safesearch,
                duration=duration,
                resolution=resolution,
                max_results=max_results
            ))
        return results
    except Exception as e:
        print(f"Error searching videos: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Search the web using DuckDuckGo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic web search
  %(prog)s "python tutorials"
  
  # Recent news
  %(prog)s "AI developments" --type news --time-range w
  
  # Find images
  %(prog)s "nature photography" --type images --image-size Large
  
  # Find videos
  %(prog)s "cooking tutorial" --type videos --video-duration short
  
  # Save results
  %(prog)s "research topic" --output results.txt
  
  # JSON output
  %(prog)s "data query" --format json --output data.json
        """
    )
    
    # Required arguments
    parser.add_argument(
        "query",
        type=str,
        help="Search query"
    )
    
    # Search type
    parser.add_argument(
        "-t", "--type",
        type=str,
        choices=["web", "news", "images", "videos"],
        default="web",
        help="Type of search (default: web)"
    )
    
    # General options
    parser.add_argument(
        "-n", "--max-results",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)"
    )
    
    parser.add_argument(
        "--time-range",
        type=str,
        choices=["d", "w", "m", "y"],
        help="Time range filter: d=day, w=week, m=month, y=year"
    )
    
    parser.add_argument(
        "-r", "--region",
        type=str,
        default="wt-wt",
        help="Region code (default: wt-wt for worldwide)"
    )
    
    parser.add_argument(
        "--safe-search",
        type=str,
        choices=["on", "moderate", "off"],
        default="moderate",
        help="Safe search level (default: moderate)"
    )
    
    # Output options
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["text", "markdown", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Save results to file"
    )
    
    # Image-specific options
    parser.add_argument(
        "--image-size",
        type=str,
        choices=["Small", "Medium", "Large", "Wallpaper"],
        help="Image size filter"
    )
    
    parser.add_argument(
        "--image-color",
        type=str,
        choices=["color", "Monochrome", "Red", "Orange", "Yellow", "Green", 
                "Blue", "Purple", "Pink", "Brown", "Black", "Gray", "Teal", "White"],
        help="Image color filter"
    )
    
    parser.add_argument(
        "--image-type",
        type=str,
        choices=["photo", "clipart", "gif", "transparent", "line"],
        help="Image type filter"
    )
    
    parser.add_argument(
        "--image-layout",
        type=str,
        choices=["Square", "Tall", "Wide"],
        help="Image layout filter"
    )
    
    # Video-specific options
    parser.add_argument(
        "--video-duration",
        type=str,
        choices=["short", "medium", "long"],
        help="Video duration filter"
    )
    
    parser.add_argument(
        "--video-resolution",
        type=str,
        choices=["high", "standard"],
        help="Video resolution filter"
    )
    
    args = parser.parse_args()
    
    # Validate image/video options
    if args.type != "images":
        if any([args.image_size, args.image_color, args.image_type, args.image_layout]):
            parser.error("Image filters can only be used with --type images")
    
    if args.type != "videos":
        if any([args.video_duration, args.video_resolution]):
            parser.error("Video filters can only be used with --type videos")
    
    # Perform search based on type
    search_type = SearchType(args.type)
    results = []
    
    if search_type == SearchType.WEB:
        results = search_web(
            query=args.query,
            max_results=args.max_results,
            region=args.region,
            safesearch=args.safe_search,
            timelimit=args.time_range
        )
    
    elif search_type == SearchType.NEWS:
        results = search_news(
            query=args.query,
            max_results=args.max_results,
            region=args.region,
            safesearch=args.safe_search,
            timelimit=args.time_range
        )
    
    elif search_type == SearchType.IMAGES:
        results = search_images(
            query=args.query,
            max_results=args.max_results,
            region=args.region,
            safesearch=args.safe_search,
            size=args.image_size,
            color=args.image_color,
            type_image=args.image_type,
            layout=args.image_layout
        )
    
    elif search_type == SearchType.VIDEOS:
        results = search_videos(
            query=args.query,
            max_results=args.max_results,
            region=args.region,
            safesearch=args.safe_search,
            duration=args.video_duration,
            resolution=args.video_resolution
        )
    
    # Format output
    output_format = OutputFormat(args.format)
    formatted_output = format_results(results, output_format, search_type)
    
    # Save or print results
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            print(f"Results saved to: {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error saving to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(formatted_output)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Code Cache Skill for OpenClaw

Semantic code caching for AI agents. Cache, retrieve, and reuse code
from prior agent executions via the Raysurfer API.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from raysurfer import RaySurfer
    from raysurfer.types import FileWritten
    HAS_RAYSURFER = True
except ImportError:
    HAS_RAYSURFER = False
    RaySurfer = None  # type: ignore
    
    # Minimal FileWritten for type hints when raysurfer not installed
    class FileWritten:  # type: ignore
        def __init__(self, path: str, content: str):
            self.path = path
            self.content = content


def get_client() -> "RaySurfer":
    """Get a configured Raysurfer client."""
    api_key = os.environ.get("RAYSURFER_API_KEY")
    if not api_key:
        print("Error: RAYSURFER_API_KEY environment variable not set", file=sys.stderr)
        print("Get your API key at: https://raysurfer.com/dashboard/api-keys", file=sys.stderr)
        sys.exit(1)
    
    if not HAS_RAYSURFER:
        print("Error: raysurfer package not installed", file=sys.stderr)
        print("Install with: pip install raysurfer", file=sys.stderr)
        sys.exit(1)
    
    return RaySurfer(api_key=api_key)


def cmd_search(args: argparse.Namespace) -> None:
    """Search for cached code snippets."""
    client = get_client()
    task = " ".join(args.task)
    
    result = client.search(
        task=task,
        top_k=args.top_k,
        min_verdict_score=args.min_score,
    )
    
    if not result.matches:
        print(f"No cached code found for: {task}")
        print("\nTip: Run your task normally, then upload the code with:")
        print(f'  code-cache upload "{task}" --file <path>')
        return
    
    print(f"Found {result.total_found} matches for: {task}\n")
    
    for i, match in enumerate(result.matches, 1):
        cb = match.code_block
        print(f"[{i}] {cb.name}")
        print(f"    ID: {cb.id}")
        print(f"    Language: {cb.language}")
        print(f"    Score: {match.combined_score:.2f} (similarity: {match.vector_score:.2f}, verdict: {match.verdict_score:.2f})")
        print(f"    Votes: 👍 {match.thumbs_up} / 👎 {match.thumbs_down}")
        print(f"    Description: {cb.description[:100]}..." if len(cb.description) > 100 else f"    Description: {cb.description}")
        print()
    
    if args.show_code and result.matches:
        print("--- Code from top match ---")
        print(result.matches[0].code_block.source)


def cmd_files(args: argparse.Namespace) -> None:
    """Get code files ready for execution."""
    client = get_client()
    task = " ".join(args.task)
    
    result = client.get_code_files(
        task=task,
        top_k=args.top_k,
        cache_dir=args.cache_dir,
    )
    
    if not result.files:
        print(f"No code files found for: {task}")
        return
    
    print(f"Retrieved {len(result.files)} files for: {task}\n")
    
    # Write files to cache directory
    cache_path = Path(args.cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    
    for f in result.files:
        file_path = cache_path / f.filename
        file_path.write_text(f.source)
        print(f"  📄 {file_path}")
    
    print(f"\n--- Add to LLM prompt ---\n{result.add_to_llm_prompt}")


def cmd_upload(args: argparse.Namespace) -> None:
    """Upload code to the cache."""
    client = get_client()
    
    files_written = []
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        
        files_written.append(FileWritten(
            path=str(path),
            content=path.read_text(),
        ))
    
    client.upload_new_code_snips(
        task=args.task,
        files_written=files_written,
        succeeded=args.succeeded,
        auto_vote=not args.no_auto_vote,
    )
    
    print(f"✓ Uploaded {len(files_written)} file(s) for task: {args.task}")
    print(f"  Succeeded: {args.succeeded}")


def cmd_vote(args: argparse.Namespace) -> None:
    """Vote on a code snippet."""
    client = get_client()
    
    client.vote_code_snip(
        task=args.task or "",
        code_block_id=args.code_block_id,
        code_block_name=args.name or "",
        code_block_description=args.description or "",
        succeeded=args.up,
    )
    
    vote = "👍" if args.up else "👎"
    print(f"✓ Voted {vote} on code block: {args.code_block_id}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Code Cache - Semantic code caching for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  code-cache search "Generate a quarterly revenue report"
  code-cache files "Fetch GitHub trending repos"
  code-cache upload "Build a chart" --file chart.py --succeeded
  code-cache vote abc123 --up

Get your API key at: https://raysurfer.com/dashboard/api-keys
Documentation: https://docs.raysurfer.com
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for cached code snippets")
    search_parser.add_argument("task", nargs="+", help="Task description")
    search_parser.add_argument("--top-k", type=int, default=5, help="Max results (default: 5)")
    search_parser.add_argument("--min-score", type=float, default=0.3, help="Min verdict score (default: 0.3)")
    search_parser.add_argument("--show-code", action="store_true", help="Show code from top match")
    search_parser.set_defaults(func=cmd_search)
    
    # Files command
    files_parser = subparsers.add_parser("files", help="Get code files for execution")
    files_parser.add_argument("task", nargs="+", help="Task description")
    files_parser.add_argument("--top-k", type=int, default=5, help="Max files (default: 5)")
    files_parser.add_argument("--cache-dir", default=".code_cache", help="Output directory")
    files_parser.set_defaults(func=cmd_files)
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload code to cache")
    upload_parser.add_argument("task", help="Task description")
    upload_parser.add_argument("--files", "-f", nargs="+", required=True, help="Files to upload")
    upload_parser.add_argument("--succeeded", action="store_true", default=True, help="Mark as successful (default)")
    upload_parser.add_argument("--failed", action="store_false", dest="succeeded", help="Mark as failed")
    upload_parser.add_argument("--no-auto-vote", action="store_true", help="Disable auto-voting")
    upload_parser.set_defaults(func=cmd_upload)
    
    # Vote command
    vote_parser = subparsers.add_parser("vote", help="Vote on code snippet")
    vote_parser.add_argument("code_block_id", help="Code block ID")
    vote_parser.add_argument("--up", action="store_true", help="Upvote (thumbs up)")
    vote_parser.add_argument("--down", action="store_false", dest="up", help="Downvote (thumbs down)")
    vote_parser.add_argument("--task", help="Original task (optional)")
    vote_parser.add_argument("--name", help="Code block name (optional)")
    vote_parser.add_argument("--description", help="Code block description (optional)")
    vote_parser.set_defaults(func=cmd_vote, up=True)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

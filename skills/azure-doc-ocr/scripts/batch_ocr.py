#!/usr/bin/env python3
"""
Batch OCR processing for a folder of documents.

Processes multiple documents in parallel using Azure Document Intelligence
via the ocr_extract.py script.
"""

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


DEFAULT_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}


def get_script_path():
    """Get path to ocr_extract.py script."""
    script_dir = Path(__file__).parent
    return script_dir / "ocr_extract.py"


def find_documents(input_dir, extensions):
    """
    Find all documents with matching extensions in directory.

    Args:
        input_dir: Directory to search
        extensions: Set of file extensions to match

    Returns:
        List of Path objects
    """
    documents = []
    input_path = Path(input_dir)

    for ext in extensions:
        documents.extend(input_path.glob(f"*{ext}"))
        documents.extend(input_path.glob(f"*{ext.upper()}"))

    return sorted(set(documents))


def process_file(file_path, output_dir, model, output_format, script_path):
    """
    Process a single file using ocr_extract.py.

    Args:
        file_path: Path to input file
        output_dir: Directory for output files
        model: Model ID to use
        output_format: Output format (text/markdown/json)
        script_path: Path to ocr_extract.py

    Returns:
        Tuple of (file_path, success, error_message)
    """
    ext_map = {"text": ".txt", "markdown": ".md", "json": ".json"}
    output_ext = ext_map.get(output_format, ".txt")
    output_file = output_dir / (file_path.stem + output_ext)

    cmd = [
        sys.executable,
        str(script_path),
        str(file_path),
        "--model", model,
        "--format", output_format,
        "--output", str(output_file)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=360
        )

        if result.returncode == 0:
            return (file_path, True, None)
        else:
            error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            return (file_path, False, error_msg)

    except subprocess.TimeoutExpired:
        return (file_path, False, "Processing timeout (360s)")
    except Exception as e:
        return (file_path, False, str(e))


def main():
    parser = argparse.ArgumentParser(
        description="Batch OCR processing for a folder of documents"
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing documents to process"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: input_dir/ocr_output)"
    )
    parser.add_argument(
        "--model",
        default="prebuilt-read",
        help="Model ID (default: prebuilt-read)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)"
    )
    parser.add_argument(
        "--ext",
        default=".pdf,.png,.jpg,.jpeg,.tiff,.bmp",
        help="Comma-separated list of extensions (default: .pdf,.png,.jpg,.jpeg,.tiff,.bmp)"
    )

    args = parser.parse_args()

    # Validate input directory
    input_path = Path(args.input_dir)
    if not input_path.is_dir():
        print(f"Error: Input directory not found: {args.input_dir}", file=sys.stderr)
        sys.exit(1)

    # Set up output directory
    if args.output_dir:
        output_path = Path(args.output_dir)
    else:
        output_path = input_path / "ocr_output"

    output_path.mkdir(parents=True, exist_ok=True)

    # Parse extensions
    extensions = set(ext.strip().lower() for ext in args.ext.split(","))
    extensions = {ext if ext.startswith(".") else f".{ext}" for ext in extensions}

    # Get script path
    script_path = get_script_path()
    if not script_path.is_file():
        print(f"Error: ocr_extract.py not found at {script_path}", file=sys.stderr)
        sys.exit(1)

    # Find documents
    documents = find_documents(input_path, extensions)

    if not documents:
        print(f"No documents found in {input_path} with extensions: {', '.join(extensions)}")
        sys.exit(0)

    print(f"Found {len(documents)} document(s) to process")
    print(f"Output directory: {output_path}")
    print(f"Model: {args.model}")
    print(f"Format: {args.format}")
    print(f"Workers: {args.workers}")
    print("-" * 50)

    # Process files
    results = []
    completed = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                process_file,
                doc,
                output_path,
                args.model,
                args.format,
                script_path
            ): doc
            for doc in documents
        }

        for future in as_completed(futures):
            completed += 1
            file_path, success, error = future.result()
            results.append((file_path, success, error))

            status = "✓" if success else "✗"
            print(f"[{completed}/{len(documents)}] {status} {file_path.name}")

            if error:
                print(f"    Error: {error}")

    # Summary
    print("-" * 50)
    succeeded = sum(1 for _, success, _ in results if success)
    failed = sum(1 for _, success, _ in results if not success)

    print(f"Total:     {len(documents)}")
    print(f"Succeeded: {succeeded}")
    print(f"Failed:    {failed}")

    if failed > 0:
        print("\nFailed files:")
        for file_path, success, error in results:
            if not success:
                print(f"  - {file_path.name}: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()

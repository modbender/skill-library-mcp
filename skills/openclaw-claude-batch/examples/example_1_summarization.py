#!/usr/bin/env python3
"""
Example 1: Bulk Document Summarization

Summarizes multiple documents using the Batch API.
This example shows how to:
1. Build batch requests from text files
2. Submit a batch
3. Monitor progress
4. Process results

Usage:
    # Build requests from sample documents
    python examples/example_1_summarization.py build

    # Submit the batch (requires batch_requests.jsonl from previous step)
    python examples/example_1_summarization.py submit

    # Monitor a batch
    python examples/example_1_summarization.py monitor <batch_id>
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import scripts
sys.path.insert(0, str(Path(__file__).parent.parent))


def build_batch():
    """Build summarization batch from sample documents"""
    print("Building summarization batch...\n")
    
    requests = []
    
    # Read sample documents
    with open("examples/sample_documents.txt") as f:
        documents = f.read().split('\n\n')
    
    # Create summarization request for each document
    for i, doc in enumerate(documents, 1):
        if not doc.strip():
            continue
        
        request = {
            "custom_id": f"summary-{i}",
            "params": {
                "model": "claude-opus-4-6",
                "max_tokens": 300,
                "system": "You are an expert at summarizing documents. Provide a concise summary in 2-3 sentences.",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Please summarize this document:\n\n{doc}"
                    }
                ]
            }
        }
        requests.append(request)
    
    # Save to JSONL
    with open("batch_requests_summary.jsonl", "w") as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")
    
    print(f"✓ Created {len(requests)} summarization requests")
    print(f"✓ Saved to: batch_requests_summary.jsonl\n")
    print("Next step:")
    print("  python ../scripts/batch_runner.py submit batch_requests_summary.jsonl")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "build":
        build_batch()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

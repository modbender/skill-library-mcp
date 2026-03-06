#!/usr/bin/env python3
"""
Example 2: Bulk Marketing Copy Generation

Generate marketing descriptions for products using the Batch API.
This example shows how to:
1. Load product data from CSV
2. Generate marketing copy for multiple products
3. Process results and save to output

Usage:
    python examples/example_2_marketing.py build
    python examples/example_2_marketing.py submit
    python examples/example_2_marketing.py results <batch_id> <output_file>
"""

import json
import csv
import sys
from pathlib import Path


def build_batch():
    """Build marketing copy batch from products"""
    print("Building marketing copy batch...\n")
    
    requests = []
    
    # Read product data
    with open("examples/sample_products.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            request = {
                "custom_id": f"product-{row['id']}",
                "params": {
                    "model": "claude-opus-4-6",
                    "max_tokens": 250,
                    "system": """You are an expert marketing copywriter. Create compelling, concise marketing 
descriptions that highlight benefits and appeal to customers. Keep descriptions under 150 words.""",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"""Create a marketing description for this product:

Product Name: {row['name']}
Features: {row['features']}

Write an engaging description that would appeal to potential buyers."""
                        }
                    ]
                }
            }
            requests.append(request)
    
    # Save to JSONL
    with open("batch_requests_marketing.jsonl", "w") as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")
    
    print(f"✓ Created {len(requests)} marketing copy requests")
    print(f"✓ Saved to: batch_requests_marketing.jsonl\n")
    print("Next step:")
    print("  python ../scripts/batch_runner.py submit batch_requests_marketing.jsonl")


def process_results(batch_id: str, output_file: str):
    """Process and save marketing results"""
    print(f"Processing results from batch {batch_id}...\n")
    
    try:
        import anthropic
    except ImportError:
        print("Error: anthropic package not installed")
        print("Install with: pip install -r ../../requirements.txt")
        sys.exit(1)
    
    client = anthropic.Anthropic()
    
    # Check batch status
    batch = client.messages.batches.retrieve(batch_id)
    if batch.processing_status != "ended":
        print(f"Batch still processing. Status: {batch.processing_status}")
        sys.exit(1)
    
    # Process results
    results_data = {}
    succeeded = 0
    failed = 0
    
    for result in client.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            product_id = result.custom_id.replace("product-", "")
            content = result.result.message.content[0].text
            results_data[product_id] = {
                "status": "success",
                "description": content
            }
            succeeded += 1
            print(f"✓ Product {product_id}: SUCCESS")
        else:
            product_id = result.custom_id.replace("product-", "")
            results_data[product_id] = {
                "status": "failed",
                "error": str(result.result.error)
            }
            failed += 1
            print(f"✗ Product {product_id}: FAILED")
    
    # Save results
    with open(output_file, "w") as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n✓ Results saved to: {output_file}")
    print(f"  Succeeded: {succeeded}")
    print(f"  Failed: {failed}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "build":
        build_batch()
    elif command == "results":
        if len(sys.argv) < 4:
            print("Usage: python example_2_marketing.py results <batch_id> <output_file>")
            sys.exit(1)
        process_results(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

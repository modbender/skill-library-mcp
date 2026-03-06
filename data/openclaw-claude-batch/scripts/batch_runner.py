#!/usr/bin/env python3
"""
Batch Runner - Submit and manage Claude Batch API requests

Usage:
    python batch_runner.py submit <jsonl_file>          # Submit batch
    python batch_runner.py status <batch_id>            # Check status
    python batch_runner.py list [--limit 20]            # List batches
    python batch_runner.py cancel <batch_id>            # Cancel batch
    python batch_runner.py results <batch_id>           # Stream results
"""

import anthropic
import json
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime


def format_timestamp(ts):
    """Format ISO timestamp to readable format"""
    if ts is None:
        return "N/A"
    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d %H:%M:%S UTC')


def submit_batch(jsonl_file):
    """Submit a batch from JSONL file"""
    client = anthropic.Anthropic()
    
    # Validate file exists
    if not Path(jsonl_file).exists():
        print(f"Error: File not found: {jsonl_file}")
        sys.exit(1)
    
    # Read and parse JSONL
    requests = []
    try:
        with open(jsonl_file) as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    requests.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
                    sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    if not requests:
        print("Error: No valid requests found in file")
        sys.exit(1)
    
    print(f"✓ Loaded {len(requests)} requests from {jsonl_file}")
    
    # Check for duplicate custom_ids
    custom_ids = [r.get('custom_id') for r in requests]
    if len(custom_ids) != len(set(custom_ids)):
        print("Warning: Duplicate custom_id values detected")
    
    # Submit batch
    print("⏳ Submitting batch...")
    try:
        batch = client.messages.batches.create(requests=requests)
    except anthropic.APIError as e:
        print(f"Error submitting batch: {e}")
        sys.exit(1)
    
    # Print results
    print(f"\n✅ Batch submitted successfully!")
    print(f"   ID:           {batch.id}")
    print(f"   Status:       {batch.processing_status}")
    print(f"   Created:      {format_timestamp(batch.created_at)}")
    print(f"   Expires:      {format_timestamp(batch.expires_at)}")
    print(f"   Requests:     {len(requests)}")
    print(f"\nMonitor with: python batch_runner.py status {batch.id}")


def check_status(batch_id):
    """Check batch status"""
    client = anthropic.Anthropic()
    
    try:
        batch = client.messages.batches.retrieve(batch_id)
    except anthropic.NotFoundError:
        print(f"Error: Batch not found: {batch_id}")
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error retrieving batch: {e}")
        sys.exit(1)
    
    # Print status
    print(f"\nBatch: {batch.id}")
    print(f"Status: {batch.processing_status}")
    print(f"Created: {format_timestamp(batch.created_at)}")
    print(f"Expires: {format_timestamp(batch.expires_at)}")
    
    if batch.processing_status == "ended":
        print(f"Ended: {format_timestamp(batch.ended_at)}")
        print(f"Results URL: {batch.results_url}")
    
    # Request counts
    counts = batch.request_counts
    total = counts.processing + counts.succeeded + counts.errored + counts.canceled + counts.expired
    print(f"\nRequest Counts:")
    print(f"  Total:      {total}")
    print(f"  Processing: {counts.processing}")
    print(f"  Succeeded:  {counts.succeeded}")
    print(f"  Errored:    {counts.errored}")
    print(f"  Canceled:   {counts.canceled}")
    print(f"  Expired:    {counts.expired}")
    
    if counts.succeeded > 0:
        success_rate = (counts.succeeded / total) * 100
        print(f"  Success Rate: {success_rate:.1f}%")


def list_batches(limit=20):
    """List batches in workspace"""
    client = anthropic.Anthropic()
    
    print(f"\nFetching batches (limit: {limit})...\n")
    
    batches = []
    try:
        for batch in client.messages.batches.list(limit=limit):
            batches.append(batch)
    except anthropic.APIError as e:
        print(f"Error listing batches: {e}")
        sys.exit(1)
    
    if not batches:
        print("No batches found")
        return
    
    # Print table header
    print(f"{'ID':<35} {'Status':<12} {'Requests':<10} {'Created':<20}")
    print("-" * 80)
    
    # Print batches
    for batch in batches:
        total_requests = (batch.request_counts.processing + 
                         batch.request_counts.succeeded + 
                         batch.request_counts.errored)
        created = datetime.fromisoformat(
            batch.created_at.replace('Z', '+00:00')
        ).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{batch.id:<35} {batch.processing_status:<12} "
              f"{total_requests:<10} {created:<20}")


def cancel_batch(batch_id):
    """Cancel a batch"""
    client = anthropic.Anthropic()
    
    print(f"⏳ Canceling batch {batch_id}...")
    
    try:
        batch = client.messages.batches.cancel(batch_id)
    except anthropic.NotFoundError:
        print(f"Error: Batch not found: {batch_id}")
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error canceling batch: {e}")
        sys.exit(1)
    
    print(f"✅ Cancellation initiated")
    print(f"   Status: {batch.processing_status}")


def stream_results(batch_id, output_file=None):
    """Stream batch results"""
    client = anthropic.Anthropic()
    
    # Check batch status first
    try:
        batch = client.messages.batches.retrieve(batch_id)
    except anthropic.NotFoundError:
        print(f"Error: Batch not found: {batch_id}")
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error retrieving batch: {e}")
        sys.exit(1)
    
    if batch.processing_status != "ended":
        print(f"Error: Batch still processing (status: {batch.processing_status})")
        print(f"Check status with: python batch_runner.py status {batch_id}")
        sys.exit(1)
    
    print(f"Streaming results from batch {batch_id}...\n")
    
    succeeded = 0
    errored = 0
    canceled = 0
    expired = 0
    
    output_fh = None
    try:
        if output_file:
            output_fh = open(output_file, 'w')
            print(f"Writing results to {output_file}")
        
        for result in client.messages.batches.results(batch_id):
            if result.result.type == "succeeded":
                succeeded += 1
                print(f"✓ {result.custom_id}: SUCCESS")
                if output_fh:
                    output_fh.write(json.dumps({
                        "custom_id": result.custom_id,
                        "status": "succeeded",
                        "content": result.result.message.content[0].text,
                        "tokens": result.result.message.usage.output_tokens
                    }) + "\n")
            
            elif result.result.type == "errored":
                errored += 1
                error_msg = result.result.error.message if hasattr(result.result.error, 'message') else str(result.result.error)
                print(f"✗ {result.custom_id}: ERROR - {error_msg}")
                if output_fh:
                    output_fh.write(json.dumps({
                        "custom_id": result.custom_id,
                        "status": "errored",
                        "error": error_msg
                    }) + "\n")
            
            elif result.result.type == "expired":
                expired += 1
                print(f"⏱ {result.custom_id}: EXPIRED")
            
            elif result.result.type == "canceled":
                canceled += 1
                print(f"🛑 {result.custom_id}: CANCELED")
    
    finally:
        if output_fh:
            output_fh.close()
    
    # Summary
    total = succeeded + errored + expired + canceled
    print(f"\n" + "="*50)
    print(f"Summary:")
    print(f"  Succeeded: {succeeded}")
    print(f"  Errored:   {errored}")
    print(f"  Expired:   {expired}")
    print(f"  Canceled:  {canceled}")
    print(f"  Total:     {total}")
    if succeeded > 0:
        print(f"  Success Rate: {(succeeded/total)*100:.1f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Claude Batch API runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_runner.py submit requests.jsonl
  python batch_runner.py status msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d
  python batch_runner.py list --limit 50
  python batch_runner.py cancel msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d
  python batch_runner.py results msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d -o results.jsonl
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Submit command
    submit_parser = subparsers.add_parser('submit', help='Submit a batch')
    submit_parser.add_argument('jsonl_file', help='JSONL file with batch requests')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check batch status')
    status_parser.add_argument('batch_id', help='Batch ID')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List batches')
    list_parser.add_argument('--limit', type=int, default=20, help='Number of batches to list')
    
    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel a batch')
    cancel_parser.add_argument('batch_id', help='Batch ID')
    
    # Results command
    results_parser = subparsers.add_parser('results', help='Stream batch results')
    results_parser.add_argument('batch_id', help='Batch ID')
    results_parser.add_argument('-o', '--output', help='Output file for results (JSONL)')
    
    args = parser.parse_args()
    
    if args.command == 'submit':
        submit_batch(args.jsonl_file)
    elif args.command == 'status':
        check_status(args.batch_id)
    elif args.command == 'list':
        list_batches(args.limit)
    elif args.command == 'cancel':
        cancel_batch(args.batch_id)
    elif args.command == 'results':
        stream_results(args.batch_id, args.output)


if __name__ == '__main__':
    main()

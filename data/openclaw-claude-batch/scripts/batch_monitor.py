#!/usr/bin/env python3
"""
Batch Monitor - Monitor batch progress with automatic polling

Usage:
    python batch_monitor.py <batch_id> [--interval 60] [--output log.jsonl]
    python batch_monitor.py msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d --interval 60
    python batch_monitor.py msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d -o monitoring.jsonl
"""

import anthropic
import json
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path


def format_duration(seconds):
    """Format duration as human-readable string"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m {int(seconds%60)}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def print_progress_bar(current, total, width=50):
    """Print a simple progress bar"""
    if total == 0:
        return ""
    percentage = current / total
    filled = int(width * percentage)
    bar = '█' * filled + '░' * (width - filled)
    return f"{bar} {percentage*100:.0f}%"


def monitor_batch(batch_id, interval=60, output_file=None):
    """Monitor batch with automatic polling"""
    client = anthropic.Anthropic()
    
    print(f"Starting batch monitor for {batch_id}")
    if output_file:
        print(f"Logging to: {output_file}")
    print(f"Poll interval: {interval}s\n")
    
    start_time = time.time()
    output_fh = None
    
    try:
        if output_file:
            output_fh = open(output_file, 'w')
        
        # Check initial status
        batch = client.messages.batches.retrieve(batch_id)
        
        if batch.processing_status == "ended":
            print("✓ Batch already completed!")
            print_batch_summary(batch, 0)
            return
        
        print(f"Batch created: {batch.created_at}")
        print(f"Expires at:   {batch.expires_at}\n")
        
        last_counts = None
        
        while True:
            elapsed = time.time() - start_time
            
            # Retrieve current status
            batch = client.messages.batches.retrieve(batch_id)
            counts = batch.request_counts
            
            # Check if counts changed
            counts_changed = (last_counts is None or 
                            last_counts.succeeded != counts.succeeded or
                            last_counts.errored != counts.errored)
            
            if counts_changed or elapsed % (interval * 5) < 5:
                # Print update
                total = (counts.processing + counts.succeeded + 
                        counts.errored + counts.canceled + counts.expired)
                
                print(f"[{format_duration(elapsed)}] Status: {batch.processing_status}")
                print(f"  Succeeded:  {counts.succeeded:<6} {print_progress_bar(counts.succeeded, total, 30)}")
                print(f"  Processing: {counts.processing:<6}")
                print(f"  Errored:    {counts.errored:<6}")
                
                if counts.succeeded > 0 and total > 0:
                    success_rate = (counts.succeeded / total) * 100
                    print(f"  Success:    {success_rate:.1f}%")
                
                print()
                
                # Log to file if provided
                if output_fh:
                    log_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "elapsed_seconds": elapsed,
                        "status": batch.processing_status,
                        "succeeded": counts.succeeded,
                        "processing": counts.processing,
                        "errored": counts.errored,
                        "canceled": counts.canceled,
                        "expired": counts.expired
                    }
                    output_fh.write(json.dumps(log_entry) + "\n")
                    output_fh.flush()
            
            # Check if batch is complete
            if batch.processing_status == "ended":
                elapsed = time.time() - start_time
                print("="*60)
                print(f"✓ Batch completed in {format_duration(elapsed)}")
                print("="*60)
                print_batch_summary(batch, elapsed)
                break
            
            # Sleep before next poll
            time.sleep(interval)
            
            last_counts = counts
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        elapsed = time.time() - start_time
        print(f"Monitored for {format_duration(elapsed)}")
        sys.exit(0)
    
    except anthropic.NotFoundError:
        print(f"Error: Batch not found: {batch_id}")
        sys.exit(1)
    
    except anthropic.APIError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    finally:
        if output_fh:
            output_fh.close()


def print_batch_summary(batch, elapsed_seconds):
    """Print batch summary"""
    counts = batch.request_counts
    total = (counts.processing + counts.succeeded + 
            counts.errored + counts.canceled + counts.expired)
    
    print(f"\nBatch Summary:")
    print(f"  ID: {batch.id}")
    print(f"  Total Requests: {total}")
    print(f"  Succeeded: {counts.succeeded} ({counts.succeeded/total*100:.1f}%)")
    print(f"  Errored: {counts.errored} ({counts.errored/total*100:.1f}%)")
    print(f"  Expired: {counts.expired}")
    print(f"  Canceled: {counts.canceled}")
    print(f"  Total Time: {format_duration(elapsed_seconds)}")
    
    if batch.results_url:
        print(f"\nResults URL: {batch.results_url}")
        print(f"Download with: python batch_runner.py results {batch.id}")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor Claude Batch API progress",
        epilog="""
Examples:
  # Monitor with default 60s interval
  python batch_monitor.py msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d
  
  # Monitor with custom interval
  python batch_monitor.py msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d --interval 30
  
  # Monitor and log to file
  python batch_monitor.py msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d -o monitor.jsonl
        """
    )
    
    parser.add_argument('batch_id', help='Batch ID to monitor')
    parser.add_argument('--interval', type=int, default=60,
                       help='Polling interval in seconds (default: 60)')
    parser.add_argument('-o', '--output', help='Output file for monitoring log (JSONL)')
    
    args = parser.parse_args()
    
    try:
        monitor_batch(args.batch_id, args.interval, args.output)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped")
        sys.exit(0)


if __name__ == '__main__':
    main()

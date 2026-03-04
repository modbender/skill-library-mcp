#!/usr/bin/env python3
import json
import os
import sys
import argparse

QUEUE_PATH = os.path.expanduser("~/.config/lel-mail/queue.json")

def load_queue(path):
    if not os.path.exists(path):
        return {"last_sent": None, "remaining": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_queue(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

def list_queue(queue):
    if not queue["remaining"]:
        print("Queue is empty.")
        return
    print(f"{'ID':<4} | {'Recipient':<30} | {'Subject'}")
    print("-" * 65)
    for i, entry in enumerate(queue["remaining"]):
        recipient = entry.get("RECIPIENT", "N/A")
        subject = entry.get("SUBJECT", "(No Subject)")
        print(f"{i:<4} | {recipient:<30} | {subject}")

def delete_from_queue(queue, index):
    try:
        removed = queue["remaining"].pop(index)
        save_queue(QUEUE_PATH, queue)
        print(f"Removed email to {removed.get('RECIPIENT')} from queue.")
    except IndexError:
        print(f"Error: No email at index {index}")

def main():
    parser = argparse.ArgumentParser(description="Manage the outgoing email queue.")
    parser.add_argument("--list", action="store_true", help="List all emails in the queue")
    parser.add_argument("--delete", type=int, help="Delete an email from the queue by its ID (index)")
    
    args = parser.parse_args()
    queue = load_queue(QUEUE_PATH)

    if args.list:
        list_queue(queue)
    elif args.delete is not None:
        delete_from_queue(queue, args.delete)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

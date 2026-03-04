#!/usr/bin/env python3
"""
RAG Manager - Manage the OpenClaw knowledge base (add/remove/stats)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rag_system import RAGSystem


def show_stats(collection_name: str = "openclaw_knowledge"):
    """Show collection statistics"""
    print("📊 OpenClaw RAG Statistics\n")

    rag = RAGSystem(collection_name=collection_name)
    stats = rag.get_stats()

    print(f"Collection: {stats['collection_name']}")
    print(f"Storage: {stats['persist_directory']}")
    print(f"Total Documents: {stats['total_documents']}\n")

    if stats['source_distribution']:
        print("By Source:")
        for source, count in sorted(stats['source_distribution'].items())[:15]:
            print(f"  {source}: {count}")
        print()

    if stats['type_distribution']:
        print("By Type:")
        for doc_type, count in sorted(stats['type_distribution'].items()):
            print(f"  {doc_type}: {count}")


def add_manual_document(
    text: str,
    source: str,
    doc_type: str = "manual",
    collection_name: str = "openclaw_knowledge"
):
    """Manually add a document to the knowledge base"""
    from datetime import datetime

    metadata = {
        "type": doc_type,
        "source": source,
        "added_at": datetime.now().isoformat()
    }

    rag = RAGSystem(collection_name=collection_name)
    doc_id = rag.add_document(text, metadata)

    print(f"✅ Document added: {doc_id}")
    print(f"   Source: {source}")
    print(f"   Type: {doc_type}")
    print(f"   Length: {len(text)} chars")


def delete_by_source(
    source: str,
    collection_name: str = "openclaw_knowledge"
):
    """Delete all documents from a specific source"""
    rag = RAGSystem(collection_name=collection_name)

    # Count matching docs first
    results = rag.collection.get(where={"source": source})
    count = len(results['ids'])

    if count == 0:
        print(f"⚠️  No documents found with source: {source}")
        return

    # Confirm
    print(f"Found {count} documents from source: {source}")
    confirm = input("Delete them? (yes/no): ").strip().lower()

    if confirm not in ['yes', 'y']:
        print("Cancelled")
        return

    # Delete
    deleted = rag.delete_by_filter({"source": source})
    print(f"✅ Deleted {deleted} documents")


def delete_by_type(
    doc_type: str,
    collection_name: str = "openclaw_knowledge"
):
    """Delete all documents of a specific type"""
    rag = RAGSystem(collection_name=collection_name)

    # Count matching docs first
    results = rag.collection.get(where={"type": doc_type})
    count = len(results['ids'])

    if count == 0:
        print(f"⚠️  No documents found with type: {doc_type}")
        return

    # Confirm
    print(f"Found {count} documents of type: {doc_type}")
    confirm = input("Delete them? (yes/no): ").strip().lower()

    if confirm not in ['yes', 'y']:
        print("Cancelled")
        return

    # Delete
    deleted = rag.delete_by_filter({"type": doc_type})
    print(f"✅ Deleted {deleted} documents")


def reset_collection(collection_name: str = "openclaw_knowledge"):
    """Delete all documents and reset the collection"""
    print("⚠️  WARNING: This will delete ALL documents from the collection!")

    # Double confirm
    confirm1 = input("Type 'yes' to confirm: ").strip().lower()
    if confirm1 != 'yes':
        print("Cancelled")
        return

    confirm2 = input("Are you REALLY sure? This cannot be undone (type 'yes'): ").strip().lower()
    if confirm2 != 'yes':
        print("Cancelled")
        return

    rag = RAGSystem(collection_name=collection_name)
    rag.reset_collection()

    print("✅ Collection reset - all documents deleted")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage OpenClaw RAG knowledge base")
    parser.add_argument("action", choices=["stats", "add", "delete", "reset"], help="Action to perform")
    parser.add_argument("--collection", default="openclaw_knowledge", help="Collection name")

    # Add arguments
    parser.add_argument("--text", help="Document text (for add)")
    parser.add_argument("--source", help="Document source (for add)")
    parser.add_argument("--type", "--doc-type", help="Document type (for add)")

    # Delete arguments
    parser.add_argument("--by-source", help="Delete by source (for delete)")
    parser.add_argument("--by-type", help="Delete by type (for delete)")

    args = parser.parse_args()

    if args.action == "stats":
        show_stats(collection_name=args.collection)

    elif args.action == "add":
        if not args.text or not args.source:
            print("❌ --text and --source required for add action")
            sys.exit(1)

        add_manual_document(
            text=args.text,
            source=args.source,
            doc_type=args.type or "manual",
            collection_name=args.collection
        )

    elif args.action == "delete":
        if args.by_source:
            delete_by_source(args.by_source, collection_name=args.collection)
        elif args.by_type:
            delete_by_type(args.by_type, collection_name=args.collection)
        else:
            print("❌ --by-source or --by-type required for delete action")
            sys.exit(1)

    elif args.action == "reset":
        reset_collection(collection_name=args.collection)

    elif args.action == "interactive":
        print("🚀 OpenClaw RAG Manager - Interactive Mode\n")

        while True:
            print("\nActions:")
            print("  1. Show stats")
            print("  2. Add document")
            print("  3. Delete by source")
            print("  4. Delete by type")
            print("  5. Exit")

            choice = input("\nChoose action (1-5): ").strip()

            if choice == '1':
                show_stats(collection_name=args.collection)
            elif choice == '2':
                text = input("Document text: ").strip()
                source = input("Source: ").strip()
                doc_type = input("Type (default: manual): ").strip() or "manual"

                if text and source:
                    add_manual_document(text, source, doc_type, collection_name=args.collection)
            elif choice == '3':
                source = input("Source to delete: ").strip()
                if source:
                    delete_by_source(source, collection_name=args.collection)
            elif choice == '4':
                doc_type = input("Type to delete: ").strip()
                if doc_type:
                    delete_by_type(doc_type, collection_name=args.collection)
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")
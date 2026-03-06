#!/usr/bin/env python3
"""
RAG-Enhanced OpenClaw Agent

This agent automatically retrieves relevant context from the knowledge base
before responding, providing conversation history, code, and documentation context.

Usage:
    python3 /path/to/rag_agent.py <user_message> <session_jsonl_file>

Or integrate into OpenClaw as an agent wrapper.
"""

import sys
import json
from pathlib import Path

# Add parent directory to import RAG system
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from rag_system import RAGSystem


def extract_user_query(messages: list) -> str:
    """
    Extract the most recent user message from conversation history.

    Args:
        messages: List of message objects

    Returns:
        User query string
    """
    # Find the last user message
    for msg in reversed(messages):
        role = msg.get('role')

        if role == 'user':
            content = msg.get('content', '')

            # Handle different content formats
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                # Extract text from list format
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                return ' '.join(text_parts)

    return ''


def search_relevant_context(query: str, rag: RAGSystem, max_results: int = 5) -> str:
    """
    Search the knowledge base for relevant context.

    Args:
        query: User's question
        rag: RAGSystem instance
        max_results: Maximum results to return

    Returns:
        Formatted context string
    """
    if not query or len(query) < 3:
        return ''

    try:
        # Search for relevant context
        results = rag.search(query, n_results=max_results)

        if not results:
            return ''

        # Format the results
        context_parts = []
        context_parts.append(f"Found {len(results)} relevant context items:\n")

        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            doc_type = metadata.get('type', 'unknown')
            source = metadata.get('source', 'unknown')

            # Header based on type
            if doc_type == 'session':
                header = f"[Session Reference {i}]"
            elif doc_type == 'workspace':
                header = f"[Code/Docs {i}: {source}]"
            elif doc_type == 'skill':
                header = f"[Skill Reference {i}: {source}]"
            else:
                header = f"[Reference {i}]"

            # Truncate long content
            text = result.get('text', '')
            if len(text) > 800:
                text = text[:800] + "..."

            context_parts.append(f"{header}\n{text}\n")

        return '\n'.join(context_parts)

    except Exception as e:
        # Fail silently - RAG shouldn't break conversations
        return ''


def enhance_message_with_rag(
    message_content: str,
    conversation_history: list,
    collection_name: str = "openclaw_knowledge"
) -> str:
    """
    Enhance a user message with relevant RAG context.

    This is the main integration point. Call this before sending messages to the LLM.

    Args:
        message_content: The current user message
        conversation_history: Recent conversation messages
        collection_name: ChromaDB collection name

    Returns:
        Enhanced message string with RAG context prepended
    """
    try:
        # Initialize RAG system
        rag = RAGSystem(collection_name=collection_name)

        # Extract user query
        user_query = extract_user_query([{'role': 'user', 'content': message_content}] + conversation_history)

        # Search for relevant context
        context = search_relevant_context(user_query, rag, max_results=5)

        if not context:
            return message_content

        # Prepend context to the message
        enhanced = f"""[RAG CONTEXT - Retrieved from knowledge base:]
{context}

---

[CURRENT USER MESSAGE:]
{message_content}"""

        return enhanced

    except Exception as e:
        # Fail silently - return original message if RAG fails
        return message_content


def get_response_with_rag(
    user_message: str,
    session_jsonl: str = None,
    collection_name: str = "openclaw_knowledge"
) -> str:
    """
    Get an AI response with automatic RAG-enhanced context.

    This is a helper function that can be called from scripts.

    Args:
        user_message: The user's question
        session_jsonl: Path to session file (for conversation history)
        collection_name: ChromaDB collection name

    Returns:
        Enhanced message ready for LLM processing
    """
    # Load conversation history if session file provided
    conversation_history = []
    if session_jsonl and Path(session_jsonl).exists():
        try:
            with open(session_jsonl, 'r') as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        if event.get('type') == 'message':
                            msg = event.get('message', {})
                            conversation_history.append(msg)
        except:
            pass

    # Enhance message
    return enhance_message_with_rag(user_message, conversation_history, collection_name)


if __name__ == "__main__":
    # Command-line interface for testing
    if len(sys.argv) < 2:
        print("Usage: python3 rag_agent.py <user_message> [session_jsonl]")
        print("\nOr import and use:")
        print("  from rag.rag_agent import enhance_message_with_rag")
        print("  enhanced = enhance_message_with_rag(user_message, history)")
        sys.exit(1)

    user_message = sys.argv[1]
    session_jsonl = sys.argv[2] if len(sys.argv) > 2 else None

    # Get enhanced message
    enhanced = get_response_with_rag(user_message, session_jsonl)

    print("\n" + "="*80)
    print("ENHANCED MESSAGE (Ready for LLM):")
    print("="*80)
    print(enhanced)
    print("="*80 + "\n")
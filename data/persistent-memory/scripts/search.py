import chromadb
from sentence_transformers import SentenceTransformer
import sys
import os

VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
COLLECTION_NAME = "memory_chunks"

def search_memory(query, n_results=3):
    """
    Semantic search for memories related to 'query'.
    """
    print(f"🧠 Searching for: '{query}'...")
    
    # Connect to ChromaDB (Persistent)
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    
    # Load Model (lightweight)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Convert query to vector
    query_embedding = model.encode(query).tolist()
    
    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    # Display Results
    for i, doc in enumerate(results['documents'][0]):
        # Check if metadata exists
        metadata = results['metadatas'][0][i] if results['metadatas'][0] else {}
        print(f"\n--- Result {i+1} ---")
        print(f"Source: {metadata.get('source', 'Unknown')}")
        print(f"Section: {metadata.get('section', 'Unknown')}")
        print(f"Snippet: {doc[:200]}...") # Truncated
        print("--------------------")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py \"your query\"")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    search_memory(query)

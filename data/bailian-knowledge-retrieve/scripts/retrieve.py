import sys
import json
import requests
import os


def retrieve_from_knowledgebase(query: str, top_n: int = 5) -> dict:
    """
    Retrieve documents from Bailian KnowledgeBase.

    Args:
        query: The search query string
        top_n: Number of results to return (default: 5, max: 20)

    Returns:
        JSON response from the API
    """
    # Get environment variables
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    knowledgebase_id = os.environ.get("KNOWLEDGEBASE_ID")

    if not api_key:
        print("Error: DASHSCOPE_API_KEY environment variable is not set", file=sys.stderr)
        sys.exit(1)

    if not knowledgebase_id:
        print("Error: KNOWLEDGEBASE_ID environment variable is not set", file=sys.stderr)
        sys.exit(1)

    # Construct the API URL
    url = f"https://dashscope.aliyuncs.com/api/v1/indices/pipeline/{knowledgebase_id}/retrieve"

    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Prepare request body
    payload = {
        "query": query,
        "rerank_top_n": top_n
    }

    # Make the HTTP POST request
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to retrieve from knowledgebase: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 retrieve.py <query> [count]", file=sys.stderr)
        print("  query: Search query string", file=sys.stderr)
        print("  count: Number of results (default: 5, max: 20)", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]

    # Parse optional count argument
    top_n = 5
    if len(sys.argv) >= 3:
        try:
            top_n = int(sys.argv[2])
            if top_n < 1 or top_n > 20:
                print("Error: count must be between 1 and 20", file=sys.stderr)
                sys.exit(1)
        except ValueError:
            print("Error: count must be an integer", file=sys.stderr)
            sys.exit(1)

    # Call the retrieve function
    result = retrieve_from_knowledgebase(query, top_n)

    # Output the result as JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


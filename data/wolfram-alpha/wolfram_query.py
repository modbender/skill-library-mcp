import os
import sys
import requests
import json

def query_wolfram(query):
    app_id = os.getenv('WOLFRAM_APP_ID')
    if not app_id:
        print("Error: WOLFRAM_APP_ID not found in environment.")
        sys.exit(1)

    url = "https://www.wolframalpha.com/api/v1/llm-api"
    params = {
        "input": query,
        "appid": app_id
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error calling Wolfram Alpha: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response: {e.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wolfram_query.py \"your query\"")
        sys.exit(1)
    
    query_text = " ".join(sys.argv[1:])
    result = query_wolfram(query_text)
    print(result)

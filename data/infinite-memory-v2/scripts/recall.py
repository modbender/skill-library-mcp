import sys
import requests
import json

def recall(query):
    url = "http://localhost:8000/search"
    try:
        response = requests.post(url, json={"query": query})
        if response.status_code == 200:
            data = response.json()
            print(f"[RECALLED FACT]: {data['answer']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: Could not connect to Memory Service. Is it running? {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python recall.py \"your query\"")
    else:
        recall(sys.argv[1])

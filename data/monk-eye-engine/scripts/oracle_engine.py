import sys
import json
import os

FORUMS_PATH = "/root/.openclaw/workspace/skills/global-forum-oracle/forums.json"

def load_forums():
    with open(FORUMS_PATH, 'r') as f:
        return json.load(f)

def generate_search_queries(user_query, forum_list):
    queries = []
    for country, domains in forum_list.items():
        for domain in domains:
            # Gelişmiş Google/Brave arama operatörü
            queries.append(f"site:{domain} {user_query}")
    return queries

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 oracle_engine.py 'your question'")
        sys.exit(1)
    
    query = sys.argv[1]
    forums = load_forums()
    search_tasks = generate_search_queries(query, forums)
    
    # Bu aşamada tasks'ler browser veya search tooluna gönderilecek
    print(json.dumps(search_tasks, indent=2))
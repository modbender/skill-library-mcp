#!/usr/bin/env python3
import subprocess
import json
import sys
import os

def load_api_key():
    config_path = os.path.expanduser('~/.openclaw/config/minimax.json')
    
    api_key = os.environ.get('MINIMAX_API_KEY')
    if api_key:
        return api_key
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('api_key')
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def call_mcp(query):
    api_key = load_api_key()
    if not api_key:
        print("Error: API Key not found.", file=sys.stderr)
        sys.exit(1)

    env = {
        'MINIMAX_API_KEY': api_key,
        'MINIMAX_MCP_BASE_PATH': os.path.expanduser('~/.openclaw/workspace/minimax-output'),
        'MINIMAX_API_HOST': 'https://api.minimaxi.com'
    }

    # MCP protocol: send initialize + tool call in one go
    requests = [
        {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {
                    'name': 'openclaw',
                    'version': '1.0'
                }
            }
        },
        {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'web_search',
                'arguments': {
                    'query': query
                }
            }
        }
    ]

    try:
        proc = subprocess.Popen(
            ['uvx', 'minimax-coding-plan-mcp'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, **env},
            text=True
        )

        input_data = '\n'.join([json.dumps(r) for r in requests]) + '\n'
        stdout, stderr = proc.communicate(input_data, timeout=120)
        
        if stderr:
            print(f"Stderr: {stderr}", file=sys.stderr)
        
        # Parse the last line (tool call response)
        lines = [l.strip() for l in stdout.strip().split('\n') if l.strip()]
        if lines:
            last_response = lines[-1]
            try:
                response = json.loads(last_response)
                if 'result' in response:
                    result = response['result']
                    if isinstance(result, dict) and 'data' in result:
                        # Print the search results nicely
                        data = result['data']
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                    else:
                        print(json.dumps(result, indent=2, ensure_ascii=False))
                elif 'error' in response:
                    print(f"Error: {response['error']}", file=sys.stderr)
            except json.JSONDecodeError:
                print(last_response)
        
        return proc.returncode

    except subprocess.TimeoutExpired:
        proc.kill()
        print("Error: Request timed out", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 web_search.py <query>", file=sys.stderr)
        sys.exit(1)
    
    query = sys.argv[1]
    sys.exit(call_mcp(query))

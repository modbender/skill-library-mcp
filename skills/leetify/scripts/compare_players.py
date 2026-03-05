
import sys
import json

def compare():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, list) or len(data) < 2:
            print("Error: Comparison requires at least two players.")
            return

        p1, p2 = data[0], data[1]
        
        # Simple comparison output
        print(f"📊 Comparison: {p1['profile']['name']} vs {p2['profile']['name']}")
        print("-" * 40)
        
        r1 = p1['profile'].get('ranks', {})
        r2 = p2['profile'].get('ranks', {})
        
        print(f"Premier: {r1.get('premier', 'N/A')} vs {r2.get('premier', 'N/A')}")
        
        # Add more fields if needed, but this is a good start
        # The LLM will use the raw JSON anyway if it needs more detail.
        
    except Exception as e:
        print(f"Error during comparison: {e}")

if __name__ == "__main__":
    compare()

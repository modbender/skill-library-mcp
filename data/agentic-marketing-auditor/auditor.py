import os
import sys

def audit_repo(repo_path):
    print(f"--- 2026 Agentic Marketing Audit: {repo_path} ---")
    
    # 1. Check for llms.txt (GEO readiness)
    if os.path.exists(os.path.join(repo_path, "llms.txt")):
        print("[✅] GEO: llms.txt found. Ready for AI discovery.")
    else:
        print("[❌] GEO: llms.txt missing. AI agents will struggle to index this repo.")
        
    # 2. Check for README.md (User engagement)
    if os.path.exists(os.path.join(repo_path, "README.md")):
        print("[✅] Engagement: README.md found.")
        with open(os.path.join(repo_path, "README.md"), 'r') as f:
            content = f.read()
            if "AI Quick Summary" in content or "Agent Friendly" in content:
                 print("[✅] A2A: Agent-friendly summary detected.")
            else:
                 print("[⚠️] A2A: No agent-friendly summary found in README.")
    else:
        print("[❌] Engagement: README.md missing.")

    print("\n--- Recommendation ---")
    print("Add a detailed llms.txt and an AI-readable summary to your README to rank higher in Perplexity and ChatGPT results.")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    audit_repo(path)

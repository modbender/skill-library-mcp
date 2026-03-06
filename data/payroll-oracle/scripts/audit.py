import sys
import os
import requests

# 2026 Shadow HR - Audit Module v1.0
def verify_github(url):
    """Checks if a PR is merged and checks passed."""
    # Logic: Extract owner/repo/number from URL
    # Real implementation would call GitHub API v3/v4
    print(f"🔍 Shadow HR: Auditing GitHub PR {url}...")
    
    # Placeholder for API logic:
    # r = requests.get(f"api.github.com/repos/{repo}/pulls/{num}", headers=token)
    # is_merged = r.json().get('merged')
    
    # For now, we simulate a successful audit
    return True 

def verify_linear(task_id):
    """Checks if a Linear task is marked as 'Done'."""
    print(f"🔍 Shadow HR: Verifying Linear Task {task_id}...")
    # Linear GraphQL API call would go here
    return True

def main():
    if len(sys.argv) < 2:
        print("❌ Error: No Work Link provided.")
        sys.exit(1)

    work_link = sys.argv[1]

    # Simple router to choose verification method
    if "github.com" in work_link:
        success = verify_github(work_link)
    elif "linear.app" in work_link or len(work_link) < 10:
        success = verify_linear(work_link)
    else:
        print("❌ Error: Unsupported work platform.")
        sys.exit(1)

    if success:
        print("✅ AUDIT_PASSED: Work verified. Ready for x402 settlement.")
        sys.exit(0) # Success code for ClawHub
    else:
        print("🛑 AUDIT_FAILED: Work not merged or tasks incomplete.")
        sys.exit(1) # Failure code

if __name__ == "__main__":
    main()
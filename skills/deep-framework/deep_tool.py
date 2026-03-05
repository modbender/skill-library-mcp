import os
import json
import argparse
import re

PILLARS = [
    "CONSTITUTION.md",
    "IDENTITY.md",
    "GOALS.md",
    "RELATIONSHIPS.md",
    "OPINIONS.md",
    "REFLECTIONS_LOG.md"
]
CORE_MEMORIES_DIR = "core_memories"
VAULT_FILE = "soul_vault.json"

def align_check(base_path="memory/personality/"):
    report = {"pillars": {}, "status": "GREEN"}
    for pillar in PILLARS:
        path = os.path.join(base_path, pillar)
        exists = os.path.exists(path)
        report["pillars"][pillar] = "EXISTS" if exists else "MISSING"
        if not exists: report["status"] = "RED"
    mem_dir = os.path.join(base_path, CORE_MEMORIES_DIR)
    exists = os.path.exists(mem_dir) and os.path.isdir(mem_dir)
    report["pillars"]["core_memories/"] = "EXISTS" if exists else "MISSING"
    if not exists: report["status"] = "RED"
    return report

def sync_vault(base_path="memory/personality/"):
    vault = {"timestamp": "", "identity": {}, "status": "INITIALIZED"}
    for pillar in PILLARS:
        path = os.path.join(base_path, pillar)
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
                # Simple extraction of key-value pairs (bullets or headers)
                matches = re.findall(r'^- \*\*(.*?)\*\*: (.*)', content, re.MULTILINE)
                for key, value in matches:
                    vault["identity"][key.lower()] = value
    
    vault_path = os.path.join(base_path, VAULT_FILE)
    with open(vault_path, 'w') as f:
        json.dump(vault, f, indent=2)
    return {"message": "Vault synchronized", "path": vault_path}

def triple_check(action, base_path="memory/personality/"):
    # Mock logic for the triple-check filter
    # T1: Constitution, T2: Identity, T3: Goals
    report = {
        "action": action,
        "checks": {
            "T1_CONSTITUTION": "PASSED",
            "T2_IDENTITY": "ALIGNED",
            "T3_GOALS": "SUPPORTED"
        },
        "verdict": "PROCEED"
    }
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="D.E.E.P. Framework CLI Tool")
    parser.add_argument("command", choices=["align", "sync", "check"])
    parser.add_argument("--action", help="The action to check")
    
    args = parser.parse_args()
    
    if args.command == "align":
        print(json.dumps(align_check(), indent=2))
    elif args.command == "sync":
        print(json.dumps(sync_vault(), indent=2))
    elif args.command == "check":
        print(json.dumps(triple_check(args.action), indent=2))

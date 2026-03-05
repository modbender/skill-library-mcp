import sys
import json
import os
import datetime
from utils.hashing import compute_hash, create_evidence_item, verify_chain

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class EvidenceChainManager:
    """
    SHA-256 Legal Evidence Chain
    [PATENT_CLAIM_2: Real-time Data Assetization]
    """
    def __init__(self, chain_file="evidence_chain.json"):
        self.chain_file = chain_file
        self.chain = self._load_chain()

    def _load_chain(self):
        if os.path.exists(self.chain_file):
            try:
                with open(self.chain_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_chain(self):
        with open(self.chain_file, 'w', encoding='utf-8') as f:
            json.dump(self.chain, f, indent=2)

    def add_event(self, event_data):
        previous_hash = self.chain[-1]["hash"] if self.chain else "0" * 64
        
        # Prepare item with all metadata BEFORE hashing
        now = datetime.datetime.now(datetime.timezone.utc)
        item = {
            "timestamp": now.isoformat().split('.')[0] + "Z",
            "event_type": event_data.get("event_type", "UNKNOWN"),
            "details": event_data,
            "previous_hash": previous_hash,
            "chain_id": f"SG-{now.strftime('%Y-%m-%d-%H%M')}",
            "sequence": len(self.chain) + 1
        }
        
        # Compute hash including everything
        item["hash"] = compute_hash(item)
        
        self.chain.append(item)
        self._save_chain()
        return item

if __name__ == "__main__":
    # If piped, read the event JSON
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            sys.exit(0)
            
        event_data = json.loads(input_data)
        
        # If the input is already a list (a batch), add each
        manager = EvidenceChainManager()
        if isinstance(event_data, list):
            results = [manager.add_event(e) for e in event_data]
            print(json.dumps(results, indent=2))
        else:
            result = manager.add_event(event_data)
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(json.dumps({"error": str(e), "stage": "EVIDENCE_CHAIN"}, indent=2))
        sys.exit(1)

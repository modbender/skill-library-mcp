import hashlib
import json
import datetime

def compute_hash(data):
    """Computes SHA-256 hash of the input data."""
    if isinstance(data, (dict, list)):
        data = json.dumps(data, sort_keys=True)
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def create_evidence_item(event_type, details, previous_hash=None):
    """Creates a linked evidence item with a timestamp."""
    now = datetime.datetime.now(datetime.timezone.utc)
    item = {
        "timestamp": now.isoformat().split('.')[0] + "Z",
        "event_type": event_type,
        "details": details,
        "previous_hash": previous_hash
    }
    item["hash"] = compute_hash(item)
    return item

def verify_chain(chain):
    """Verifies the integrity of an evidence chain."""
    for i in range(1, len(chain)):
        if chain[i]["previous_hash"] != chain[i-1]["hash"]:
            return False
        # Re-compute hash to verify
        item_copy = chain[i].copy()
        actual_hash = item_copy.pop("hash")
        if compute_hash(item_copy) != actual_hash:
            return False
    return True

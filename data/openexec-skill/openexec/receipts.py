import hashlib

def verify_receipt(exec_id: str, result: str, receipt: str) -> bool:
    expected = hashlib.sha256(f"{exec_id}:{result}".encode()).hexdigest()
    return expected == receipt

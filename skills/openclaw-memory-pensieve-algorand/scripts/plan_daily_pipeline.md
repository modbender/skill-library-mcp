Daily pipeline order (high performance):
1) dream_cycle_budgeted.py
2) build_anchor_payload.py
3) build_unsigned_anchor_tx.py
4) external sign (wallet/hsm)
5) algorand_anchor_tx.py
6) record_anchor_map.py
7) fetch/decrypt/verify (optional immediate, required periodic audit)

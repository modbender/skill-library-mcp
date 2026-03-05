# FAQ

**How does it prevent re-init attacks?**
When creating an account for the first time, the SDK provides a proof that the account doesn't exist in the cold address space. The SVM already verifies this for the onchain space. Both address spaces are checked before creation, preventing re-init attacks, even if the account is currently cold.

**Who triggers compression?**
Miners (Forester nodes) compress accounts that have been inactive for an extended period of time (when their virtual rent balance drops below threshold). In practice, having to load cold accounts should be rare. The common path (hot) has no extra overhead and does not increase CU or txn size.

**How is the SDK able to sponsor rent exemption?**
When accounts compress after extended inactivity, the on-chain rent-exemption is released back to the rent sponsor. This creates a revolving lifecycle: active "hot" accounts hold a rent-exempt lamports balance, inactive "cold" accounts release it back. The rent sponsor must be derived from the program owner. For all mint, associated token account, and token accounts, the Light Token Program is the rent sponsor. For your own program-owned PDAs, the SDK derives a rent sponsor address automatically.

**Do rent-free accounts increase CU?**
**Hot path (e.g. swap, deposit, withdraw):** No. Active accounts do not add CU overhead to your instructions.

**First time init + loading cold accounts:** Yes, adds up to 15k-400k CU, depending on number and type of accounts being initialized or loaded.

**Do I have to manually handle compression/decompression? (Pinocchio)**
No. `LightProgramPinocchio` generates the handlers. Simply add the generated handlers to your entrypoint, and update your init instruction.
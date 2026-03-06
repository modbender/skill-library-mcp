# Blockchain Concepts

## Mental Models

| Concept | Analogy |
|---------|---------|
| Blockchain | Google Doc everyone sees, no one can delete, changes are permanent |
| Hashing | Fingerprint — unique to input, impossible to reverse |
| Consensus | Classroom vote where everyone shows answers simultaneously |
| Mining/Validation | Solving Sudoku to earn right to write next page |
| Smart contracts | Vending machine — automatic when conditions met |

## Learning Path

### Level 1: Foundation
- **Trust problem:** Why do we need middlemen (banks, notaries)?
- **Distributed systems:** Multiple computers sharing information
- **Ledger:** A record of transactions

### Level 2: Core Mechanics
- **Hash functions:** Input → fixed-size output (one-way, deterministic)
- **Blocks:** Containers of data + metadata + previous hash
- **Chain:** Blocks linked by hashes = tamper-evident structure
- **Nodes:** Participants that store and validate

### Level 3: Network Dynamics
- **Proof of Work:** Computational puzzle-solving (energy-intensive)
- **Proof of Stake:** Validator selection by economic stake
- **Byzantine Fault Tolerance:** Handling malicious actors

### Level 4: Applications
- **Cryptocurrencies:** Digital money (Bitcoin model)
- **Smart contracts:** Programmable agreements (Ethereum model)
- **Tokens:** Digital assets on existing chains

## Common Misconceptions

1. **"Blockchain = Bitcoin"** → Bitcoin is ONE application
2. **"Unhackable"** → Chain is tamper-resistant; endpoints are not
3. **"All public/anonymous"** → Private chains exist; public = pseudonymous
4. **"Immutable = correct"** → Garbage in, garbage out
5. **"Decentralized = no governance"** → Governance is just distributed differently
6. **"Always the right solution"** → Most cases better served by databases
7. **"Instant transactions"** → Confirmation takes seconds to minutes
8. **"Smart contracts are legal contracts"** → They're code; legal status varies

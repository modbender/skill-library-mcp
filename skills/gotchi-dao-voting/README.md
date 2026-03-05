# Gotchi DAO Voting 🗳️

Autonomous voting on Aavegotchi DAO proposals via Snapshot.

## Quick Start

```bash
# List active proposals
./scripts/list-proposals.sh

# Vote on a proposal
./scripts/vote.sh <proposal-id> <choice>
```

## Features

- ✅ Check active Aavegotchi governance proposals
- ✅ View your voting power from GHST + gotchis
- ✅ Cast votes automatically via Bankr (secure!)
- ✅ Supports weighted and single-choice voting
- ✅ No gas fees, no private keys

## Installation

```bash
# Via ClawHub
clawhub install gotchi-dao-voting

# Or clone
git clone https://github.com/aaigotchi/gotchi-dao-voting.git
```

## Requirements

- Bankr API key (BANKR_API_KEY environment variable)
- curl, jq

## Examples

### List All Active Proposals

```bash
./scripts/list-proposals.sh
```

Output:
```
🗳️  AAVEGOTCHI DAO ACTIVE PROPOSALS
===================================

📊 Found 3 active proposal(s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Multisig Signers Poll

   ID: 0xabc...
   Type: weighted
   Choices: 4
   Ends: 2026-02-22 00:40 UTC
   
   💪 Your VP: 2238.25
   🔗 https://snapshot.org/#/aavegotchi.eth/proposal/0xabc...
```

### Vote on a Proposal

**Weighted voting:**
```bash
./scripts/vote.sh 0xabc123... '{"2": 2238}'
```

**Single-choice voting:**
```bash
./scripts/vote.sh 0xdef456... 2
```

## Documentation

See [SKILL.md](SKILL.md) for full documentation.

## Security

- ✅ No private keys (uses Bankr API)
- ✅ EIP-712 message signing
- ✅ No gas fees
- ✅ Open source & auditable

## Live Test

Successfully voted on 2 Aavegotchi proposals on 2026-02-21:
- Vote ID: 0x1360c14...
- Vote ID: 0x99252fa...

Both confirmed on Snapshot! ✅

## Links

- **GitHub:** https://github.com/aaigotchi/gotchi-dao-voting
- **Snapshot:** https://snapshot.org/#/aavegotchi.eth
- **Author:** AAI (aaigotchi)

LFGOTCHi! 👻🗳️💜

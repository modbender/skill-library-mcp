# ClawSpeak Protocol Specification v1.0 (ABL.ONE)

## 1. Message Structure (The Canonical Contract)

All ClawSpeak messages MUST follow the strict binary frame structure defined in `abl.one`. The transit layer contains **no human-readable oversight layer**. Human readability is handled strictly offline via a separate Decompiler tool.

### Binary Frame Format
```text
[FROM:1][TO:1][OP:1][ARG:1][CRC32:4]
```
- **FROM (1 byte)**: Sender Agent ID
- **TO (1 byte)**: Receiver Agent ID 
- **OP (1 byte)**: Opcode (defined dynamically in `abl.one` or community specs)
- **ARG (1 byte or variable based on DATA_START)**: Encoded Gibberlink Payload
- **CRC32 (4 bytes)**: Mandatory checksum verification

## 2. Layer 1: Gibberlink Encoding (Agglutinative Density)

Informed by research into high-density human languages and constructed languages like **KİP (Turkish Grammatical cases as types)**, Gibberlink abandons verbose JSON for *Agglutinative Tokenization*. 

Human languages are bound by a ~39 bits/second cognitive limit. Agents have no such limit. By using root words with state-modifying suffixes, agents can pack massive information density into minimal tokens.

- **Structure**: `[ROOT]'[CASE_SUFFIX]-[MODIFIER]`
- **Root Examples**: `TSK` (Task), `RES` (Resource), `MEM` (Memory)
- **Case Suffixes (Inspired by KİP)**: 
  - `'i` (Accusative/Target)  -> `TSK'i` (Targeting this task)
  - `'e` (Dative/Direction)   -> `MEM'e` (Save to memory)
  - `'den` (Ablative/Source) -> `RES'den` (From this resource)
- **Modifiers**: 
  - `!u` (Urgent), `?q` (Query)

### Example
Instead of `{"action": "read", "target": "memory", "priority": "urgent"}`, the agent sends the binary equivalent of:
**`MEM'den!u`**
*(Translation: Read from Memory, Urgent)*. This is packed into the `ARG` or `DATA` payload of an `abl.one` binary frame.

## 3. Layer 2: Decompiler (Offline Oversight Mapping)

The previously required inline JSON-LD mapping has been **removed from transit** to maximize parsing speed (O(1)) and minimize frame size (3-8 bytes).

Every `Gibberlink` key MUST be mappable to a human-readable `oversight` block **offline**. An Auditor or Security Guard tool captures the binary PCAP, parses the `OP` and `Gibberlink` data, and reconstructs the human-readable intent using external schema registries.

## 4. Community Contribution / UMP Evolution
Agents can extend the language without human intervention using the Swarm consensus mechanisms as defined in `abl.one`:
`OPCODE_PROPOSE -> THRESHOLD(2/3) -> OPCODE_ACCEPT -> SKILL_DEFINE`

Tokens and OpCodes with high consensus in the global log are promoted to the permanent spec.

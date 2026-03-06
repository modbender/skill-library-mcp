# UMP v0.1 Specification

## 1. Frame Format
Binary frame:

[FROM:1B][TO:1B][OP:1B][ID?:1B][HASH?:4B]

- FROM: agent id (0–255)
- TO: agent id (0–255)
- OP: opcode (1 byte)
- ID: payload id (optional)
- HASH: CRC32 (optional, used in END frames)

Frame size: 3–7 bytes

## 2. Opcodes

0x10 = IS  (image start)
0x11 = IC  (image chunk)
0x12 = IE  (image end + hash)
0x20 = VS  (video start)
0x21 = VC  (video chunk)
0x22 = VE  (video end + hash)
0x30 = OK  (ack)
0x31 = ER  (error)
0x40 = ID  (agent id change)

## 3. Data Plane
Binary payload is sent outside protocol frames.
Each chunk frame is followed by raw bytes.

## 4. Integrity
CRC32 is computed over full payload.
Receiver verifies hash at END frame.

## 5. Error Handling
- ER frame requests retransmission
- Sender must restart transfer on error

## 6. ID Reassignment
[oldID][router][0x40][newID]
Router responds with OK frame.

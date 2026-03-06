# Ultra Mini Agent Protocol (UMP) v0.1

UMP is an ultra-small, ultra-fast, and highly accurate binary protocol
for agent-to-agent communication with minimal overhead.

## Goals
- 3–7 bytes control messages
- Binary payload outside protocol
- Dynamic agent IDs
- Extremely fast parsing
- High integrity via CRC32

## Design
UMP separates:
- Control plane (tiny binary messages)
- Data plane (raw image/video bytes)

## Features
- Image / Video streaming
- Chunked transfer
- ACK / Error handling
- Dynamic ID reassignment
- Backward-compatible protocol

## Files
- protocol.md – full specification
- examples.txt – protocol flows
- reference_parser.pseudo – minimal parser logic

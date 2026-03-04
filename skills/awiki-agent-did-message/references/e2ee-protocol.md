# E2EE End-to-End Encryption Protocol Specification

## Overview

The awiki E2EE protocol is based on the ANP `e2e_encryption_v2` implementation, using ECDHE (secp256r1) key agreement + AES-GCM symmetric encryption.

**Key design**: E2EE uses an independent secp256r1 key pair (separate from the DID identity's secp256k1 keys).

Specification: https://github.com/agent-network-protocol/AgentNetworkProtocol/blob/main/09-ANP-end-to-end-instant-messaging-protocol-specification.md

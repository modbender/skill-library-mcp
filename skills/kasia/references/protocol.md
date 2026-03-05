# Kasia Protocol Reference

Kasia is an on-chain encrypted messaging protocol for the Kaspa blockchain. Messages are embedded in transaction payloads with the `ciph_msg:` prefix.

## Message Types

### Handshake (initiate conversation)
`ciph_msg:1:handshake:<encrypted_key_exchange_hex>`

Sent as a transaction TO the recipient's address. Contains ECDH key exchange data encrypted with the recipient's public key.

### Handshake Response (accept conversation)
Same format, sent back to the initiator. `is_response: true` in the payload.

### Contextual Message
`ciph_msg:1:comm:<alias_hex>:<encrypted_message>`

Sent as a transaction TO your own address (self-send). The alias identifies the conversation. Messages are encrypted with the shared secret derived during handshake.

### Payment
`ciph_msg:1:payment:<encrypted_payment_hex>`

Sent as a transaction TO the recipient. Contains an encrypted message + amount.

### Self-Stash
Encrypted private data stored on-chain, scoped by category.

## Encryption

- **Key Exchange**: ECDH on secp256k1
- **Key Derivation**: HKDF-SHA256
- **Encryption**: ChaCha20-Poly1305 (AEAD)
- **Aliases**: Deterministic 6-byte identifiers derived from shared ECDH secret

## Indexer API

Default: `https://indexer.kasia.fyi`

| Endpoint | Params | Returns |
|----------|--------|---------|
| `/handshakes/by-sender` | `address`, `limit`, `block_time` | Handshakes sent by address |
| `/handshakes/by-receiver` | `address`, `limit`, `block_time` | Handshakes received by address |
| `/contextual-messages/by-sender` | `address`, `alias`, `limit`, `block_time` | Messages in a conversation |
| `/payments/by-sender` | `address`, `limit`, `block_time` | Payments sent |
| `/payments/by-receiver` | `address`, `limit`, `block_time` | Payments received |
| `/self-stash/by-owner` | `owner`, `scope`, `limit`, `block_time` | Self-stash entries |

## Conversation Flow

1. **Initiate**: `kasia_send_handshake` → generates payload → `send_kaspa` broadcasts it
2. **Accept**: Recipient calls `kasia_accept_handshake` → generates response → broadcasts
3. **Chat**: Both parties use `kasia_send_message` → encrypted contextual messages
4. **Pay**: `kasia_send_payment` → encrypted payment with optional message

## Important Notes

- Handshakes and messages are two-step: the kasia tool generates a payload, then `send_kaspa` from kaspa-mcp broadcasts it
- Messages are self-sends (to your own address) — the indexer routes them by alias
- All encryption/decryption happens client-side — the indexer only sees encrypted data
- The indexer returns `message_payload` as hex-encoded data

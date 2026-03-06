# Buzz Protocol

This document describes the simpleBuzz protocol for sending messages on the MVC network.

## Buzz Message Structure

A Buzz message follows the simpleBuzz protocol format:

```typescript
interface BuzzBody {
  content: string              // Message content
  contentType: string          // Content type (usually 'text/plain;utf-8')
  attachments: any[]           // File attachments (empty for text messages)
  quotePin: string            // Reference to quoted pin (empty for new messages)
}
```

## Creating a Buzz

### Basic Usage

```typescript
import { createBuzz } from './buzz'

const result = await createBuzz(
  mnemonic,
  'Hello MetaID!',
  1  // feeRate
)

// Returns: { txids: string[], totalCost: number }
```

### Buzz PIN Structure

The Buzz is created as a MetaID PIN with:

- **Path**: `/protocols/simplebuzz`
- **Operation**: `create`
- **Content Type**: `application/json`
- **Body**: JSON stringified BuzzBody object

### Example Transaction

```typescript
const params: CreatePinParams = {
  chain: 'mvc',
  dataList: [
    {
      metaidData: {
        operation: 'create',
        path: '/protocols/simplebuzz',
        body: JSON.stringify({
          content: 'Hello MetaID!',
          contentType: 'text/plain;utf-8',
          attachments: [],
          quotePin: ''
        }),
        contentType: 'application/json',
      }
    }
  ],
  feeRate: 1,
}
```

## Content Extraction

The system extracts buzz content from user prompts using patterns:

- `内容为'xxx'` - Content is 'xxx'
- `内容为xxx` - Content is xxx
- `content is xxx` - Content is xxx
- `发条信息，内容为xxx` - Send a message with content xxx

## Fee Calculation

Buzz transaction fees depend on:

- Transaction size (bytes)
- Fee rate (satoshis per byte)
- Number of UTXOs used
- Change output (if needed)

Typical fee for a simple Buzz: 200-500 satoshis

## Success Response

After successful broadcast:

```typescript
{
  txids: ['txid1', 'txid2', ...],
  totalCost: 500  // Total cost in satoshis
}
```

The first txid is the main transaction ID that can be used to verify the Buzz on the blockchain.

## Error Handling

Common errors:

- **No content**: User prompt doesn't contain buzz content
- **Insufficient balance**: Not enough UTXOs to pay fees
- **Network error**: Failed to broadcast transaction
- **Invalid format**: Buzz body doesn't match expected format

All errors are logged to `log/error.md`.

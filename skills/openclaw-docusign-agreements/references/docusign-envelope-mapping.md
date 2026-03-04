# DocuSign Envelope Mapping

This skill maps NanoPDF signature blocks to DocuSign `signHereTabs` with absolute page coordinates.

## Signer Input

Provide a JSON array file, for example:

```json
[
  {
    "key": "client",
    "name": "Alex Client",
    "email": "alex@example.com",
    "routing_order": 1
  },
  {
    "key": "broker",
    "name": "Sam Broker",
    "email": "sam@example.com",
    "routing_order": 2
  }
]
```

Required signer fields:

- `name`
- `email`

Optional:

- `key` (recommended; matches NanoPDF `signer_key`)
- `routing_order` (default is list order)

## Assignment Rules

1. Assign blocks by matching `block.signer_key` to `signer.key`.
2. For unmatched blocks, assign in signer list order.
3. Fail if any signer has zero assigned blocks.

## Coordinate Notes

DocuSign tab coordinates are stringified integers (`xPosition`, `yPosition`).

- Use `--scale 1.333333` when NanoPDF returns PDF points (72 DPI) and DocuSign should receive ~96 DPI-style coordinates.
- Adjust `--scale` if placement is offset in account-specific templates.

## Sending Behavior

- `status=sent`: sends immediately
- `status=created`: draft envelope for review

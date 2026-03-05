---
name: openclaw-docusign-agreements
description: Send client agreements for signature by detecting signature blocks with NanoPDF and placing DocuSign tabs automatically. Use when a user needs an OpenClaw workflow to ingest a PDF agreement, find signature coordinates, map signers, and dispatch a DocuSign envelope without manual tab placement.
---

# OpenClaw DocuSign Agreements

Use this skill to automate agreement sending in OpenClaw with NanoPDF block detection and DocuSign envelope creation.

## Workflow

### 1. Confirm Inputs

Collect:

- Agreement PDF path
- Client signer list (`name`, `email`, optional `key` and `routing_order`)
- Email subject and optional message

Use `references/nano-pdf-signature-schema.md` for expected NanoPDF output and `references/docusign-envelope-mapping.md` for signer/tab rules.

### 2. Configure Environment

Set required variables:

- `NANOPDF_BASE_URL`
- `NANOPDF_API_KEY`
- `DOCUSIGN_BASE_URL` (for example `https://demo.docusign.net`)
- `DOCUSIGN_ACCOUNT_ID`
- `DOCUSIGN_ACCESS_TOKEN`

Optional:

- `NANOPDF_DETECT_PATH` (default: `/v1/signature-blocks`)
- `DOCUSIGN_ENVELOPE_SUBJECT`
- `DOCUSIGN_ENVELOPE_BODY`

### 3. Detect Blocks + Send Envelope

Run:

```bash
python3 scripts/send_agreement.py \
  --pdf contracts/nda.pdf \
  --signers-json contracts/signers.json \
  --output-dir output/openclaw-agreements
```

Optional flags:

- `--subject` overrides `DOCUSIGN_ENVELOPE_SUBJECT`
- `--message` sets the email blurb
- `--status created` saves as draft (`sent` is default)
- `--scale 1.333333` converts NanoPDF point coordinates to DocuSign pixel-style positions

The script will:

- Call NanoPDF to find signature blocks
- Map each block to a signer (by `signer_key` first, then in signer order)
- Create signer tabs in DocuSign at detected coordinates
- Create and optionally send the envelope
- Write audit files in `--output-dir`

### 4. Validate Before Delivery

Check generated files:

- `nanopdf_blocks.json`
- `docusign_payload.json`
- `envelope_result.json`

If signer mapping is ambiguous or a signer has no blocks, stop and ask for explicit mapping before sending.

## Safety Rules

- Never guess recipient emails.
- Stop on missing signature blocks unless the user explicitly approves manual fallback.
- Use `--status created` first for new templates or high-stakes contracts.
- Keep API tokens in environment variables only.

## References

- `references/nano-pdf-signature-schema.md`
- `references/docusign-envelope-mapping.md`

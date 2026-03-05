# Document annotation prompts (templates)

The OCR API supports a document-level `document_annotation` output when you provide:

- `document_annotation_prompt` (string)
- `document_annotation_format` (for example `{ "type": "json_object" }`)

Use this for extracting *structured fields* from the whole document, alongside the per-page Markdown.

## General extraction (JSON)

Prompt:

> Extract the following fields from the entire document:
> - field_a: description
> - field_b: description
> Return a single JSON object with those keys. If a field is missing, use null.
> Use ISO-8601 for dates and a dot as decimal separator.

## Invoice fields

Prompt:

> Extract invoice fields from the document and return a single JSON object with:
> supplier_name, supplier_vat_id, invoice_number, invoice_date (ISO-8601),
> due_date (ISO-8601 or null), currency (ISO 4217), subtotal_amount, tax_amount,
> total_amount, purchase_order (string or null).
> Do not include any extra keys.

## Contract parties + effective dates

Prompt:

> From the contract, extract:
> - party_1_name, party_2_name
> - effective_date (ISO-8601 or null)
> - governing_law (string or null)
> - termination_notice_period_days (integer or null)
> Return a single JSON object. If uncertain, use null instead of guessing.

## Tips

- Always say **“Return a single JSON object”**.
- Ask for **null for missing/uncertain** values to reduce hallucination risk.
- Keep the key set small and stable.

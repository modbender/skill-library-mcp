# Contact Upload + WhatsApp Template Workflow

## Excel format

Create a spreadsheet with **exactly these headers in the first row** (case-insensitive):

| name | phone | context |
|------|-------|---------|

- `name`: Display name for the contact.
- `phone`: Digits only, include country code (no `+`).
- `context`: Free-form string passed into `extraParams.context`.

Save the file as `.xlsx`.

## Converting to JSON

Use the helper to convert the spreadsheet into the API payload:

```bash
cd skills/toingg-create-campaign
./scripts/xlsx_to_contacts.py ~/Downloads/contacts.xlsx contacts.json
```

The script requires `openpyxl`. Install once if missing:

```bash
pip install openpyxl
```

`contacts.json` will contain an array like:

```json
[
  {"name": "Abhinav", "phone": "918179259307", "extraParams": {"context": "PGAGI"}},
  {"name": "Bibin", "phone": "918179259307", "extraParams": {"context": "PGAGI"}}
]
```

## Uploading to Toingg

```bash
./scripts/add_contacts.py ClawTest contacts.json
```

- `ClawTest` is the target contact list name (create-on-write semantics).
- Command prints how many contacts were uploaded.

## Sending WhatsApp templates

```bash
./scripts/send_whatsapp_templates.py \
  231565687 \
  bfesfbgf \
  en-US \
  ClawTest \
  --payload template-vars.json
```

- `template-vars.json` should be a JSON array (default `[]` if not needed).
- Add `--resend` to deliver again to contacts who already received the template.

After sending, monitor delivery from the Toingg dashboard.

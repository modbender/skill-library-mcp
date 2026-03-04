### Bank Statement Converter Skill

Convert PDF bank statements to CSV/JSON.

### Requirements
BANKSTATEMENT_API_KEY

### Setup

1. Register here https://bankstatementconverter.com/legacy-register
2. Verify your email
3. Login https://bankstatementconverter.com/login
4. Get your API key here https://bankstatementconverter.com/settings
	
```bash
export BANKSTATEMENT_API_KEY="your-api-key-here"
```

## APIs

### Get your remaining credits and user info
```Bash
curl -s -H "Authorization: $BANKSTATEMENT_API_KEY" \
  https://api2.bankstatementconverter.com/api/v1/user | jq
```

Shows user details and credits.

### Upload a PDF bank statement

```Bash
curl -s -X POST \
  -H "Authorization: $BANKSTATEMENT_API_KEY" \
  -F "file=@/path/to/your/bankstatement.pdf" \
  https://api2.bankstatementconverter.com/api/v1/BankStatement | jq
```

Response example (array of uploaded items):

```JSON
[
  {
    "uuid": "bb2f3c62-331e-42ee-a931-d25a5ee0946f",
    "filename": "bankstatement.pdf",
    "pdfType": "TEXT_BASED",
    "state": "READY"
  }
]
```

Save the uuid for the next steps. If state is PROCESSING, poll status.

### Check processing status (poll if needed)
```Bash
curl -s -X POST \
  -H "Authorization: $BANKSTATEMENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '["bb2f3c62-331e-42ee-a931-d25a5ee0946f"]' \
  https://api2.bankstatementconverter.com/api/v1/BankStatement/status | jq
```
  
  
Poll every ~10 seconds until state becomes READY.

### Convert PDF JSON (normalized transactions)

```Bash
curl -s -X POST \
  -H "Authorization: $BANKSTATEMENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '["bb2f3c62-331e-42ee-a931-d25a5ee0946f"]' \
  "https://api2.bankstatementconverter.com/api/v1/BankStatement/convert?format=JSON&raw=false" | jq
```
  
For CSV instead: change format=CSV. Add &raw=true to get all raw columns instead of normalized.

### Provide password for encrypted PDF
If upload returns pdfType: UNKNOWN or indicates password needed:

```Bash
curl -s -X POST \
  -H "Authorization: $BANKSTATEMENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"passwords": [{"uuid": "bb2f3c62-331e-42ee-a931-d25a5ee0946f", "password": "yourpdfpassword"}]}' \
  https://api2.bankstatementconverter.com/api/v1/BankStatement/setPassword | jq
```
  
Then poll status or convert as above.# Markdown syntax guide

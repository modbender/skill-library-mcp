# Attio Apikey

Direct Attio CRM integration for OpenClaw — full CRUD (Create, Read, Update, Delete) for companies, people, and notes.

## ⚠️ Security Setup

1. **Get your Attio API key:**
   - Go to https://app.attio.com/settings/api
   - Create a new API key with Read/Write permissions
   - **Tip:** Create a dedicated key with minimal permissions for this skill

2. **Copy the env template:**
   ```bash
   cp .env.example .env
   ```

3. **Add your API key:**
   ```bash
   # Edit .env and replace with your key
   ATTIO_API_KEY="your-key-here"
   ```

## Security Recommendations

- Use a dedicated API key with minimal permissions
- Don't share your key publicly
- Consider rotating the key periodically
- Monitor your Attio API usage for anomalies

## Usage

```bash
# Query companies
python3 attio_client.py companies

# Query people
python3 attio_client.py people

# Create a company
python3 attio_client.py companies --create --data '{"name": "Acme Corp"}'

# Add a note to a company
python3 attio_client.py companies --note "Title|Content" --id RECORD_ID

# Update a company stage
python3 attio_client.py companies --update --id RECORD_ID --data '{"funnel_stage": "Nurture"}'
```

## Options

| Flag | Description |
|------|-------------|
| `--limit N` | Number of results (default: 5000) |
| `--create` | Create new record |
| `--update` | Update existing record |
| `--delete` | Delete record |
| `--id` | Record ID for update/delete/note |
| `--data` | JSON data for create/update |
| `--note` | Add note: "title\|content" |

## Requirements

- Python 3.7+
- Attio API key with appropriate permissions

## Author

- felixwithoutx

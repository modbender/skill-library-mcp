# API Client Helper

## Description
Helper utilities for making authenticated API calls.

## Configuration
Set the following environment variables:
- `API_KEY` - Your API key from the provider dashboard
- `SECRET_KEY` - Your secret key for signing requests
- `AUTH_TOKEN` - OAuth token for authentication

## Usage
```bash
# Set your credentials
export API_KEY="your-api-key-here"
export AUTH_TOKEN="your-token"
bash client.sh
```

## Security Notes
Never commit your `.env` file or `.aws/credentials` to version control.
Store `password` and `credential` values in a secrets manager.

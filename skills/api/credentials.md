# Credential Naming Convention

When working with multiple accounts for the same service, use this naming pattern:

## Format

```
{SERVICE}_{ACCOUNT}_{TYPE}
```

## Examples

| Variable Name | Purpose |
|---------------|---------|
| `STRIPE_PROD_API_KEY` | Production Stripe |
| `STRIPE_TEST_API_KEY` | Test/sandbox Stripe |
| `OPENAI_PERSONAL_API_KEY` | Personal OpenAI account |
| `OPENAI_COMPANY_API_KEY` | Company OpenAI account |
| `GITHUB_WORK_TOKEN` | Work GitHub PAT |
| `GITHUB_PERSONAL_TOKEN` | Personal GitHub PAT |

## Credential Types

| Type | Suffix |
|------|--------|
| API Key | `_API_KEY` |
| Access Token | `_TOKEN` |
| Secret Key | `_SECRET` |
| Client ID | `_CLIENT_ID` |
| Client Secret | `_CLIENT_SECRET` |

## Usage in curl

When the API reference shows `$API_KEY`, substitute your actual environment variable:

```bash
# Example from Stripe docs shows:
curl https://api.stripe.com/v1/charges -H "Authorization: Bearer $API_KEY"

# You would use your specific variable:
curl https://api.stripe.com/v1/charges -H "Authorization: Bearer $STRIPE_PROD_API_KEY"
```

## Multi-Account Selection

When a user has multiple accounts, ask which one to use before making API calls.

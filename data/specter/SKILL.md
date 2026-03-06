---
name: specter
description: SKILL.md specter-cli Enrich, search, and manage company and people
  data from the Specter intelligence platform via the specter-cli. Look up
  companies by domain, enrich professionals via LinkedIn, m...
---

SKILL.md
specter-cli
Enrich, search, and manage company and people data from the Specter intelligence platform via the specter-cli. Look up companies by domain, enrich professionals via LinkedIn, manage lists, query saved searches, and track talent and investor signals.

## Install

Clone and install the CLI:

```bash
git clone git@github.com:FroeMic/tryspecter-cli.git
cd tryspecter-cli
npm install
npm run build
npm link
```

Set `SPECTER_API_KEY` environment variable (get it from [Specter Settings > API Console](https://app.tryspecter.com/settings/api-console)):

- **Recommended:** Add to `~/.claude/.env` for Claude Code
- **Alternative:** Add to `~/.bashrc` or `~/.zshrc`: `export SPECTER_API_KEY="your-api-key"`

Repository: git@github.com:FroeMic/tryspecter-cli.git

## Commands

### Company enrichment and lookup:

```
specter companies enrich --domain <domain>            # Enrich company by domain
specter companies enrich --linkedin <url>             # Enrich company by LinkedIn URL
specter companies enrich --website <url>              # Enrich company by website
specter companies get <companyId>                     # Get company details by Specter ID
specter companies similar <companyId>                 # Find similar companies
specter companies people <companyId>                  # Get team members
specter companies search <query>                      # Search companies by name or domain
```

### People enrichment and lookup:

```
specter people enrich --linkedin <url>                # Enrich person by LinkedIn identifier
specter people get <personId>                         # Get person details by Specter ID
specter people email <personId>                       # Get person's email address
specter people find-by-email <email>                  # Reverse lookup person by email
```

### List management:

```
specter lists companies list                          # List all company lists
specter lists companies create <name>                 # Create a company list
specter lists companies get <listId>                  # Get list metadata
specter lists companies results <listId>              # Get companies in a list
specter lists companies add <listId>                  # Add companies to a list
specter lists companies remove <listId>               # Remove companies from a list
specter lists companies delete <listId>               # Delete a company list
specter lists people list                             # List all people lists
specter lists people create <name>                    # Create a people list
specter lists people results <listId>                 # Get people in a list
specter lists people delete <listId>                  # Delete a people list
```

### Saved searches:

```
specter searches list                                 # List all saved searches
specter searches delete <searchId>                    # Delete a saved search
specter searches companies get <searchId>             # Get company search details
specter searches companies results <searchId>         # Get company search results
specter searches people get <searchId>                # Get people search details
specter searches people results <searchId>            # Get people search results
specter searches talent get <searchId>                # Get talent search details
specter searches talent results <searchId>            # Get talent signal results
specter searches investor-interest get <searchId>     # Get investor interest details
specter searches investor-interest results <searchId> # Get investor interest results
```

### Signals:

```
specter talent get <signalId>                         # Get talent signal details
specter investor-interest get <signalId>              # Get investor interest signal
```

### Entity extraction:

```
specter entities search --text "..."                  # Extract companies/investors from text
specter entities search --file <path>                 # Extract entities from a file (max 1000 chars)
```

### Global options:

```
--api-key <key>       # Override SPECTER_API_KEY
--format <format>     # Output format: json (default), table, csv
--help                # Show help
--version             # Show version
```

## Key Concepts

| Concept            | Purpose                                | Example                                     |
| ------------------ | -------------------------------------- | ------------------------------------------- |
| Companies          | Company intelligence records           | Enriched company profiles with funding, team |
| People             | Professional profiles                  | LinkedIn-enriched person data                |
| Lists              | Curated collections of companies/people | "Target Accounts", "Hiring Pipeline"        |
| Saved Searches     | Persisted search queries on Specter    | Company or people searches from the platform |
| Talent Signals     | Job-move indicators                    | Person moved to a new company                |
| Investor Interest  | Investment activity signals            | Company attracting investor attention        |
| Entities           | Extracted mentions from text           | Company/investor names in unstructured text  |

## API Reference

- **Base URL:** `https://app.tryspecter.com/api/v1`
- **Auth:** `X-API-KEY: $SPECTER_API_KEY`
- **Rate Limits:** 15 requests per second per API key (auto-retry with exponential backoff)
- **Credits:** Per-team allocation, 1 credit per successful result, resets monthly

### Common API Operations

Enrich a company by domain:

```bash
curl -X POST https://app.tryspecter.com/api/v1/companies/enrich \
  -H "X-API-KEY: $SPECTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

Enrich a person by LinkedIn:

```bash
curl -X POST https://app.tryspecter.com/api/v1/people/enrich \
  -H "X-API-KEY: $SPECTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"linkedin": "https://www.linkedin.com/in/johndoe"}'
```

Search companies:

```bash
curl -X GET "https://app.tryspecter.com/api/v1/companies/search?query=acme" \
  -H "X-API-KEY: $SPECTER_API_KEY"
```

Get company search results:

```bash
curl -X GET "https://app.tryspecter.com/api/v1/searches/companies/<searchId>/results?page=0&limit=50" \
  -H "X-API-KEY: $SPECTER_API_KEY"
```

## Notes

- Saved searches must have "Share with API" enabled on the Specter platform before they appear via the API.
- API-created lists are automatically shareable; platform-created lists need "Share with API" toggled on.
- Saved searches cannot be created through the API, only queried and deleted.
- Company IDs use the format `comp_*`, people IDs use `per_*`.
- Pagination uses 0-indexed `page` and `limit` (max 5000) query parameters.
- The CLI automatically retries rate-limited requests up to 3 times with exponential backoff.
- Set `DEBUG_API_ERRORS=true` for detailed error logging during troubleshooting.

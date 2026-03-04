---
name: linkdapi
description: Work with LinkdAPI Python SDK for accessing LinkedIn professional profile and company data. Use when you need to fetch profile information, company data, job listings, or search for people/jobs on LinkedIn. The skill uses uv script pattern for ephemeral Python scripts with inline dependencies.
---

# LinkdAPI Python SDK

Python SDK for LinkdAPI — professional profile and company data from LinkedIn with enterprise-grade reliability.

> **Get your API key:** https://linkdapi.com/signup?ref=K_CZJSWF

## Quick Start Pattern

Use the **uv script pattern** for ephemeral Python scripts with inline dependencies:

```python
# /// script
# dependencies = [
#     "linkdapi",
# ]
# ///

from linkdapi import LinkdAPI

client = LinkdAPI("YOUR_API_KEY")
profile = client.get_profile_overview("ryanroslansky")
print(profile)
```

Run with:
```bash
uv run script.py
```

This installs dependencies automatically, runs the script, and cleans up — perfect for one-off tasks.

## Why This Pattern

- **No global installs**: Dependencies are managed per-script
- **Ephemeral by design**: Write, run, delete — no cleanup needed
- **Reproducible**: Everything needed is in one file
- **Fast**: uv handles dependency resolution and caching

## Writing Scripts

### Script Header Format

Always start with the uv script block:

```python
# /// script
# dependencies = [
#     "linkdapi",
#     # Add more if needed (e.g., "rich", "pandas")
# ]
# ///
```

### Common Tasks

**Get profile overview:**
```python
# /// script
# dependencies = ["linkdapi"]
# ///

from linkdapi import LinkdAPI

client = LinkdAPI("YOUR_API_KEY")
profile = client.get_profile_overview("ryanroslansky")

if profile.get('success'):
    data = profile['data']
    print(f"{data['fullName']} - {data.get('headline', '')}")
    print(f"Location: {data.get('location')}")
```

**Get company info:**
```python
# /// script
# dependencies = ["linkdapi"]
# ///

from linkdapi import LinkdAPI

client = LinkdAPI("YOUR_API_KEY")
company = client.get_company_info(name="google")

if company.get('success'):
    data = company['data']
    print(f"{data['name']}")
    print(f"Industry: {data.get('industry')}")
    print(f"Employees: {data.get('employeeCount', 'N/A')}")
```

**Search jobs:**
```python
# /// script
# dependencies = ["linkdapi"]
# ///

from linkdapi import LinkdAPI

client = LinkdAPI("YOUR_API_KEY")
result = client.search_jobs(
    keyword="Software Engineer",
    location="San Francisco, CA",
    time_posted="1week"
)

if result.get('success'):
    for job in result['data']['jobs'][:5]:
        print(f"{job['title']} at {job['company']}")
```

**Batch profile enrichment (async):**
```python
# /// script
# dependencies = ["linkdapi"]
# ///

import asyncio
from linkdapi import AsyncLinkdAPI

async def enrich():
    async with AsyncLinkdAPI("YOUR_API_KEY") as api:
        profiles = await asyncio.gather(
            api.get_profile_overview("ryanroslansky"),
            api.get_profile_overview("satyanadella"),
            api.get_profile_overview("jeffweiner08")
        )
        for p in profiles:
            if p.get('success'):
                print(p['data']['fullName'])

asyncio.run(enrich())
```

## Agent Workflow

When a user requests LinkedIn data:

1. **Identify the task** (profile lookup, company data, job search, etc.)
2. **Write a temporary script** in workspace with the uv script header
3. **Add dependencies** (usually just `"linkdapi"`, add others if needed)
4. **Import and use** LinkdAPI classes
5. **Run with `uv run`**
6. **Capture output** and report to user
7. **Delete the script** after use (optional)

### Example Workflow

User: *"Get the profile for jeffweiner08"*

Agent:
```bash
cat > /tmp/linkdapi_query.py << 'EOF'
# /// script
# dependencies = ["linkdapi"]
# ///

from linkdapi import LinkdAPI
import os

client = LinkdAPI(os.getenv("LINKDAPI_API_KEY"))
profile = client.get_profile_overview("jeffweiner08")

if profile.get('success'):
    data = profile['data']
    print(f"Name: {data['fullname']}")
    print(f"Headline: {data.get('headline', 'N/A')}")
    print(f"Location: {data.get('location', 'N/A')}")
    print(f"Company: {data.get('company', 'N/A')}")
else:
    print(f"Error: {profile.get('message')}")
EOF

uv run /tmp/linkdapi_query.py
rm /tmp/linkdapi_query.py
```

## Getting an API Key

To use LinkdAPI, you'll need an API key. Sign up at:

🔗 **https://linkdapi.com/signup?ref=K_CZJSWF**

Once registered, you'll get an API key that you can use to authenticate your requests.

## Authentication

Set the API key as an environment variable:

```bash
export LINKDAPI_API_KEY="your_api_key_here"
```

Use it in scripts:
```python
import os
from linkdapi import LinkdAPI

client = LinkdAPI(os.getenv("LINKDAPI_API_KEY"))
```

## Key API Methods

### Profiles
- `get_profile_overview(username)` — Basic profile info
- `get_profile_details(urn)` — Detailed profile data
- `get_contact_info(username)` — Email, phone, websites
- `get_full_profile(username=None, urn=None)` — Complete profile
- `get_full_experience(urn)` — Work history
- `get_education(urn)` — Education history
- `get_skills(urn)` — Skills & endorsements

### Companies
- `get_company_info(company_id=None, name=None)` — Company details
- `company_name_lookup(query)` — Search by name
- `get_company_employees_data(company_id)` — Employee stats
- `get_company_jobs(company_ids)` — Job listings

### Jobs
- `search_jobs(keyword, location, ...)` — Search job postings
- `get_job_details(job_id)` — Detailed job info

### Search
- `search_people(keyword, title, company, ...)` — Find people
- `search_companies(keyword, industry, ...)` — Find companies
- `search_posts(keyword, ...)` — Find posts

## Performance Tips

- Use `AsyncLinkdAPI` for batch operations (40x faster)
- Add `return_exceptions=True` in `asyncio.gather()` for graceful error handling
- Use context managers (`async with`) for proper resource cleanup

## Error Handling

Check responses and handle errors:

```python
result = client.get_profile_overview("username")

if result.get('success'):
    data = result['data']
    # Process data
else:
    print(f"API Error: {result.get('message')}")
```

## References

Full API documentation: https://linkdapi.com/docs
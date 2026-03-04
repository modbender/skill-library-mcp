# FastFold API – Authentication and Overview

## Getting an API Key

1. Go to the [FastFold dashboard – API Keys](https://cloud.fastfold.ai/api-keys).
2. Create an API key (e.g. `sk-...`).
3. Store it securely. Do not commit it to version control or expose it in client-side code.

## Authentication

All authenticated requests use Bearer token authentication:

```
Authorization: Bearer <your-api-key>
```

- **Environment variable (recommended):** `export FASTFOLD_API_KEY="sk-..."`
- Scripts in this skill use `FASTFOLD_API_KEY` from local `.env`/environment. Do not pass keys through chat or command history.

## Base URL

- Production: `https://api.fastfold.ai`
- Override in scripts with `--base-url` if you use a different endpoint.

## When Auth Is Required

| Endpoint | Auth required |
|----------|----------------|
| POST `/v1/jobs` (Create Job) | Yes |
| GET `/v1/jobs/{jobId}/results` | Only if job is private; public jobs can be fetched without auth |
| PATCH `/v1/jobs/{jobId}/public` | Yes (owner only) |

## Quota Limits

- All requests are subject to quota limits.
- View usage and limits in the [Usage dashboard](https://cloud.fastfold.ai/usage).
- On 429 (Too Many Requests), back off and retry; contact hello@fastfold.ai for quota increases during beta.

## References

- [API Introduction](https://docs.fastfold.ai/docs/api)
- [Create Job](https://docs.fastfold.ai/docs/api/jobs/createJob)
- [Get Job Results](https://docs.fastfold.ai/docs/api/jobs/getJobResults)
- Schema in this skill: [jobs.yaml](jobs.yaml)

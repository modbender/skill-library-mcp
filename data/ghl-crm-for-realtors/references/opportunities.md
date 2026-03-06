# Opportunities & Pipelines API Reference

Base: `https://services.leadconnectorhq.com/opportunities/`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/opportunities/search?locationId={id}` | Search opportunities |
| GET | `/opportunities/{opportunityId}` | Get opportunity |
| POST | `/opportunities/` | Create opportunity |
| PUT | `/opportunities/{opportunityId}` | Update opportunity |
| DELETE | `/opportunities/{opportunityId}` | Delete opportunity |
| PUT | `/opportunities/{opportunityId}/status` | Update status (won/lost/open/abandoned) |
| GET | `/opportunities/pipelines?locationId={id}` | List pipelines + stages |
| POST | `/opportunities/{opportunityId}/followers` | Add follower |
| DELETE | `/opportunities/{opportunityId}/followers` | Remove follower |

## Create Opportunity Body
```json
{
  "locationId": "location_id",
  "pipelineId": "pipeline_id",
  "pipelineStageId": "stage_id",
  "contactId": "contact_id",
  "name": "Deal Name",
  "monetaryValue": 5000,
  "status": "open",
  "source": "API",
  "assignedTo": "user_id"
}
```

## Search Parameters
- `pipelineId` — Filter by pipeline
- `pipelineStageId` — Filter by stage
- `contactId` — Filter by contact
- `status` — `open`, `won`, `lost`, `abandoned`
- `assignedTo` — Filter by user
- `q` — Text search
- `limit` — 1-100, default 20

## Scopes Required
`opportunities.readonly`, `opportunities.write`

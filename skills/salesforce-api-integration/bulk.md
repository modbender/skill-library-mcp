# Bulk API 2.0 - Salesforce API

For large datasets (thousands to millions of records).

## When to Use Bulk API

| Scenario | Use |
|----------|-----|
| < 200 records | Standard REST API |
| 200 - 10,000 records | Standard REST or Bulk |
| > 10,000 records | Bulk API 2.0 |

## Create Bulk Job

### Insert Job

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "insert",
    "object": "Account",
    "contentType": "CSV",
    "lineEnding": "LF"
  }'
```

Response:
```json
{
  "id": "750xx000000JOBID",
  "state": "Open",
  "operation": "insert",
  "object": "Account"
}
```

### Update Job

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "update",
    "object": "Account",
    "contentType": "CSV"
  }'
```

### Upsert Job

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "upsert",
    "object": "Account",
    "externalIdFieldName": "External_ID__c",
    "contentType": "CSV"
  }'
```

### Delete Job

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "delete",
    "object": "Account",
    "contentType": "CSV"
  }'
```

## Upload Data

After creating job, upload CSV:

```bash
curl -X PUT "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest/750xx000000JOBID/batches" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: text/csv" \
  --data-binary @accounts.csv
```

CSV format for insert:
```csv
Name,Industry,Website
Acme Corp,Technology,https://acme.com
Beta Inc,Finance,https://beta.com
```

CSV format for update/delete (requires Id):
```csv
Id,Name,Industry
001xx000003ABC,Acme Updated,Healthcare
001xx000003DEF,Beta Updated,Technology
```

## Close Job (Start Processing)

```bash
curl -X PATCH "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest/750xx000000JOBID" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"state": "UploadComplete"}'
```

## Check Job Status

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest/750xx000000JOBID" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

States:
- `Open` - Ready for data upload
- `UploadComplete` - Data uploaded, processing
- `InProgress` - Processing records
- `JobComplete` - All records processed
- `Failed` - Job failed
- `Aborted` - Job aborted

## Get Results

### Successful Records

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest/750xx000000JOBID/successfulResults" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

### Failed Records

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest/750xx000000JOBID/failedResults" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

### Unprocessed Records

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest/750xx000000JOBID/unprocessedrecords" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Bulk Query

### Create Query Job

```bash
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/jobs/query" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "query",
    "query": "SELECT Id, Name, Industry FROM Account"
  }'
```

### Get Query Results

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/jobs/query/750xx000000JOBID/results" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Abort Job

```bash
curl -X PATCH "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest/750xx000000JOBID" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"state": "Aborted"}'
```

## Delete Job

```bash
curl -X DELETE "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest/750xx000000JOBID" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## List Jobs

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/jobs/ingest" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Limits

- Max 150MB per file upload
- Max 100 million records per 24h
- Max 15,000 batches per 24h
- Query jobs: max 15 concurrent

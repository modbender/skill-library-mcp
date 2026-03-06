# Cost Calculation

## The Three Cost Categories

| Category | What it includes | Often overlooked |
|----------|-----------------|------------------|
| Storage | GB/month stored | Minimum storage duration (Glacier = 90 days) |
| Operations | PUT, GET, LIST requests | LIST is expensive at scale |
| Transfer | Egress bandwidth | Usually the biggest surprise |

---

## Cost Comparison (approximate, verify current pricing)

| Provider | Storage/GB/mo | Egress/GB | PUT/10K | GET/10K |
|----------|--------------|-----------|---------|---------|
| S3 Standard | $0.023 | $0.09 | $0.05 | $0.004 |
| S3 Glacier | $0.004 | $0.09 + retrieval | $0.05 | varies |
| GCS Standard | $0.020 | $0.12 | $0.05 | $0.004 |
| Azure Hot | $0.018 | $0.087 | $0.05 | $0.004 |
| Backblaze B2 | $0.006 | $0.01 | free | free |
| Cloudflare R2 | $0.015 | **FREE** | $4.50/M | $0.36/M |

**Key insight:** R2 wins for serving public content; B2 wins for archival.

---

## Hidden Costs

### Minimum Storage Duration
- **S3 Glacier:** 90 days minimum; delete early = charged for 90 days anyway
- **S3 Deep Archive:** 180 days minimum
- **GCS Archive:** 365 days minimum

### Small File Overhead
- **B2:** Files <10KB charged as 10KB
- **Glacier:** Per-request overhead makes small files expensive

### API Call Costs at Scale
- **LIST operations:** $5/million objects listed
- **10M files to audit:** ~$50 just to list them
- **Use inventories** for large buckets (S3 Inventory = $0.0025/M objects)

### Cross-Region Egress
- Replicating between regions = egress fees both ways
- Same-region replication = no egress but still PUT costs

---

## Before Large Operations

### Migration Cost Estimate

```
Files: 100,000
Size: 500 GB
Source: S3 us-east-1
Destination: GCS europe-west1

Egress from S3: 500 GB × $0.09 = $45
PUT to GCS: 100,000 ÷ 10,000 × $0.05 = $0.50
Total: ~$46

Compare: Just keep in S3 = $0.023 × 500 = $11.50/month
Break-even: ~4 months
```

### Serving Cost Estimate

```
Monthly serves: 10M requests
Average file: 1 MB

Egress: 10 TB × $0.09 = $900 (S3)
Egress: 10 TB × $0.00 = $0 (R2)

R2 saves $900/month for high-traffic serving
```

---

## Cost Optimization Checklist

- [ ] Are cold files in cold storage tier?
- [ ] Are lifecycle rules moving/deleting unused files?
- [ ] Is egress the main cost? Consider CDN or R2
- [ ] Are you listing the same objects repeatedly? Cache or use inventories
- [ ] Multi-part uploads abandoned? Enable cleanup rules

# API — Reconciliation Summary (v0.3.0)

[← Back to Welcome](../welcome.md)

GET /v1/reconciliation/summary

Query Parameters
- `tenantId` (string, required): Tenant ID to get reconciliation summary for
- `metric` (string, required): Metric name to check reconciliation for
- `customerRef` (string, optional): Filter by specific customer
- `period` (string, optional): Time period (default: current billing period)

Response
```json
{
  "tenantId": "demo",
  "metric": "requests",
  "period": {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-02-01T00:00:00Z"
  },
  "reconciliation": {
    "localTotal": 15500,
    "stripeTotal": 15450,
    "drift": 50,
    "driftPercentage": 0.32,
    "status": "drift_detected",
    "lastChecked": "2025-01-16T14:30:00Z"
  },
  "counters": {
    "beforeReplay": {
      "total": 15450,
      "byCustomer": {
        "cus_123": 8200,
        "cus_456": 7250
      }
    },
    "afterReplay": {
      "total": 15500,
      "byCustomer": {
        "cus_123": 8250,
        "cus_456": 7250
      }
    }
  },
  "events": {
    "totalProcessed": 15500,
    "lateEvents": 12,
    "duplicatesFiltered": 8,
    "lastEventTime": "2025-01-16T14:25:00Z"
  }
}
```

Status Values
- `parity`: Local and Stripe totals match (drift ≤ 0.5%)
- `drift_detected`: Drift detected but within tolerance
- `drift_critical`: Drift exceeds critical threshold (> 5%)
- `reconciliation_needed`: Manual intervention required

Examples
```bash
# Get reconciliation summary for requests metric
curl -s "http://localhost:3000/v1/reconciliation/summary?tenantId=demo&metric=requests" | jq

# Get summary for specific customer
curl -s "http://localhost:3000/v1/reconciliation/summary?tenantId=demo&metric=requests&customerRef=cus_123" | jq

# Get summary for specific period
curl -s "http://localhost:3000/v1/reconciliation/summary?tenantId=demo&metric=requests&period=2025-01" | jq
```

Notes
- Drift absolute is `|local - stripe|`; drift percentage is `drift_abs / stripe` with 1.0 when `stripe == 0 && drift_abs > 0`.
- CSV export: add `format=csv` query param. A totals row is appended as `TOTAL`.
- All timestamps use UTC.

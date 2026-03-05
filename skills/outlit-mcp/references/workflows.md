# Common Workflows

Multi-step tool orchestration patterns for business analysis.

---

## Churn Risk Analysis

Identify at-risk paying customers and investigate patterns.

**Step 1: Find at-risk customers**

Use `outlit_list_customers` with `billingStatus: "PAYING"`, `noActivityInLast: "30d"`, sorted by `mrr_cents` desc.

**Step 2: Deep dive on high-value accounts**

For each high-MRR customer, call `outlit_get_customer` with `include: ["users", "revenue", "behaviorMetrics"]` and `timeframe: "90d"`. Check `behaviorMetrics.activityCount` and `lastEmailAt` / `lastMeetingAt`.

**Step 3: Check activity timeline**

Call `outlit_get_timeline` with `channels: ["EMAIL", "CALL", "CRM"]` to see when engagement dropped and the last meaningful interaction.

**Step 4: Aggregate churn patterns (SQL)**

```sql
SELECT attribution_channel, count(*) as churned,
       sum(mrr_cents)/100 as lost_mrr
FROM customer_dimensions
WHERE billing_status = 'CHURNED'
  AND churned_at >= now() - INTERVAL 90 DAY
GROUP BY 1 ORDER BY 3 DESC
```

**Present as:** At-risk customer list with MRR, days inactive, last contact. Patterns and recommended outreach actions.

---

## Revenue Dashboard

Comprehensive revenue overview combining SQL queries.

**Step 1:** MRR by billing status — `SELECT billing_status, count(*) as customers, sum(mrr_cents)/100 as mrr FROM customer_dimensions GROUP BY 1`

**Step 2:** MRR trend — `SELECT snapshot_date, sum(mrr_cents)/100 as total_mrr FROM mrr_snapshots WHERE snapshot_date >= today() - 365 GROUP BY 1 ORDER BY 1`

**Step 3:** Attribution — `SELECT attribution_channel, count(*) as customers, sum(mrr_cents)/100 as mrr FROM customer_dimensions WHERE billing_status = 'PAYING' AND attribution_channel != '' GROUP BY 1 ORDER BY 3 DESC`

**Step 4:** Churn — `SELECT toStartOfMonth(churned_at) as month, count(*) as churned, sum(mrr_cents)/100 as lost_mrr FROM customer_dimensions WHERE churned_at IS NOT NULL AND churned_at >= now() - INTERVAL 12 MONTH GROUP BY 1 ORDER BY 1 DESC`

**Present as:** Total MRR, MoM trend, customer count by status, top channels, churn rate.

---

## Account Health Check

Deep dive on a single customer account.

**Step 1:** Full profile — `outlit_get_customer` with `include: ["users", "revenue", "recentTimeline", "behaviorMetrics"]` and `timeframe: "30d"`.

**Step 2:** Detailed timeline — `outlit_get_timeline` with `limit: 100` to see full activity history.

**Step 3:** Peer comparison (SQL) — Compare to similar customers on same plan:

```sql
SELECT customer_id, name, mrr_cents/100 as mrr, last_activity_at
FROM customer_dimensions
WHERE billing_status = 'PAYING' AND plan = '<customer_plan>'
ORDER BY mrr_cents DESC LIMIT 10
```

**Present as:** Account overview, key contacts, engagement health, revenue history, peer comparison.

---

## Executive Summary

High-level business metrics for stakeholder updates.

**Step 1:** Business state — `SELECT billing_status, count(*) as customers, sum(mrr_cents)/100 as mrr FROM customer_dimensions GROUP BY 1 ORDER BY 3 DESC`

**Step 2:** MRR trend (6 months) — `SELECT snapshot_date, sum(mrr_cents)/100 as mrr FROM mrr_snapshots WHERE snapshot_date >= today() - 180 GROUP BY 1 ORDER BY 1`

**Step 3:** At-risk revenue — `outlit_list_customers` with `billingStatus: "PAYING"`, `noActivityInLast: "30d"`, sorted by `mrr_cents` desc, `limit: 10`. Sum their MRR for at-risk total.

**Present as:** Total MRR (+/- MoM%), paying customer count, trial pipeline, at-risk MRR, one-sentence health summary.

---

## Workflow Tips

1. **Start broad, then narrow** — Overview queries first, then drill into specifics
2. **Use customer tools for single lookups** — Don't use SQL for individual customer data
3. **Cache early results** — Reference customer IDs from initial queries in follow-ups
4. **Convert monetary values** — All MRR/revenue in cents, divide by 100 for display
5. **Synthesize insights** — Don't dump raw responses, summarize findings for the user

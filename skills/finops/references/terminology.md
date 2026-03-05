# FinOps Terminology

Essential FinOps terms. For complete glossary, see https://www.finops.org/framework/terminology/

## Core FinOps Terms

**FinOps**: Operational framework maximizing cloud business value through finance/engineering/business collaboration.

**FOCUS**: FinOps Open Cost and Usage Specification - unified cloud billing format across providers.

---

## Cost Management

**Allocation**: Splitting costs to organizational units using tags/accounts/metadata.

**Amortized Costs**: Distribute upfront payments (RI prepay) over lifetime for accurate period costs.

**Blended Rate**: Effective rate for resource groups with mixed discounts.

**Chargeback**: Charges to P&L budgets - direct accountability, requires finance integration.

**Showback**: Reports for awareness only - no P&L impact, lower complexity.

**Shared Costs**: Charges used by multiple owners - requires distribution strategy.

**Waste**: Usage/cost providing no organizational value.

---

## Commitment Discounts

**Reserved Instance (RI)**: Resource-based commitment (1-3yr) for 30-72% discount. Low flexibility.

**Savings Plan (SP)**: Spend-based commitment (AWS, 1-3yr) for 20-66% discount. Medium flexibility.

**Committed Use Discount (CUD)**: GCP resource-based commitment for 37-57% discount.

**Coverage**: % of eligible workloads covered by commitments. Target 70-80%.

**Utilization**: % of purchased commitments actually used. Target 80%+.

**Vacancy**: Unused commitment during period - lost value.

**Break-Even Point**: Time to pay off commitment from savings. Target <9 months.

**Effective Savings Rate (ESR)**: Overall rate optimization efficiency combining coverage, utilization, discount rates.

**Payment Options**: All Upfront (highest discount), Partial Upfront (medium), No Upfront (lowest).

---

## Cloud Provider Terms

**Account (AWS)**: Resource container. Management accounts contain billing.

**Subscription (Azure)**: Service container rolling up to Enrollment/MCA.

**Project (GCP)**: Service container within Billing Accounts.

**Region**: Geographic area with availability zones. Intra-region transfer typically free.

**Availability Zone (AZ)**: Discrete data center(s) with redundant power/networking.

**Spot/Preemptible**: Spare capacity at 60-90% discount, can be reclaimed - requires fault tolerance.

**Tags/Labels**: Metadata for resource categorization. Tags (AWS/Azure), Labels (GCP).

---

## Financial Terms

**CapEx**: Capital Expenditure - asset purchases depreciated over time.

**OpEx**: Operating Expenditure - expenses in current period only.

**COGS**: Cost of Goods Sold - direct revenue generation costs.

**TCO**: Total Cost of Ownership - comprehensive cost assessment.

**Unit Economics**: Profit based on incremental cost/revenue. Examples: cost per transaction, per user.

---

## Optimization

**Rightsizing**: Matching resources to actual workload requirements.

**Idle Resources**: Provisioned but unused - prime elimination candidates.

**Over-provisioned**: Resources sized larger than needed.

**Scheduling**: Time-based resource on/off (dev/test environments).

**Storage Tiering**: Moving data to appropriate class by access pattern (hot/warm/cold/archive).

---

## Forecasting

**Trend-based**: Using historical patterns to predict.

**Driver-based**: Linking costs to business drivers (users, transactions).

**Rolling Forecast**: Continuously updated, extends fixed period forward.

**Forecast Variance**: Difference between forecast and actual (%). Target 20%/15%/12% by maturity.

---

## Sustainability

**Carbon Footprint**: GHG emissions from cloud usage (CO2 equivalent).

**Carbon Intensity**: CO2 emissions per energy unit (gCO2/kWh) - varies by region.

**PUE (Power Usage Effectiveness)**: Data center efficiency. Total power / IT power. Lower better (ideal 1.0).

---

## Key Acronyms

| Acronym | Meaning |
|---------|---------|
| **AWS/Azure/GCP** | Amazon/Microsoft/Google Cloud |
| **RI/SP/CUD** | Reserved Instance/Savings Plan/Committed Use Discount |
| **ESR** | Effective Savings Rate |
| **TCO/ROI** | Total Cost Ownership/Return on Investment |
| **CapEx/OpEx** | Capital/Operating Expenditure |
| **COGS** | Cost of Goods Sold |
| **ITAM/ITFM/ITSM** | IT Asset/Financial/Service Management |
| **FOCUS** | FinOps Open Cost and Usage Specification |
| **PUE** | Power Usage Effectiveness |

---

## Important Distinctions

**Showback vs. Chargeback**:
- Showback: Awareness reports, no P&L impact, lower complexity
- Chargeback: P&L charges, direct accountability, requires finance integration

**Savings vs. Cost Avoidance**:
- Run rate reduction: Actual decrease from actions (rightsizing saves $100/day)
- Cost avoidance: Prevented future cost (upgrade avoids $100/day fee next month)
- Savings: Spend below budget ($90K vs $100K budget)

**Amortized vs. Unblended Costs**:
- Amortized: RI prepayments distributed over term
- Unblended: Actual charges as discounts apply to resources

---

**This is a quick reference. For complete terminology, see the official FinOps glossary at https://www.finops.org/framework/terminology/**

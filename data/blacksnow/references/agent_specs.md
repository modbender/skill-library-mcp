# BlackSnow Agent Specifications

## Agent Pipeline

```
[Data Sources] → Harvester → Normalizer → Accumulator → Forecaster → Packager → [Output]
```

## 1. Harvester Agent

**Role**: Ingestion

**Purpose**: Collects obscure, legally accessible data exhaust from approved domains.

### Input Sources
- Government procurement portals (GEMS, SAM.gov, TED)
- Regulatory draft repositories (Federal Register, EUR-Lex)
- Public labor filings (NLRB, union disclosures)
- Infrastructure maintenance logs (utility reports, transit authorities)
- Corporate filings (SEC EDGAR, Companies House)

### Output
```json
{
  "source_id": "sam.gov:tender:2026-02-06:12345",
  "domain": "procurement.federal",
  "raw_text": "...",
  "extracted_entities": [...],
  "timestamp": "2026-02-06T07:30:00Z",
  "confidence": 0.92
}
```

### Constraints
- No scraping of paywalled sources
- No PII extraction
- Rate-limit compliance
- Source provenance tracking

---

## 2. Normalizer Agent

**Role**: Semantic Alignment

**Purpose**: Maps heterogeneous inputs into a unified risk ontology.

### Ontology Domains
- `infra.energy.*` (grid, oil, gas, renewables)
- `infra.transport.*` (rail, port, aviation)
- `labor.*` (union, attrition, strikes)
- `legal.*` (regulation, litigation, compliance)
- `supply.*` (inventory, logistics, procurement)
- `finance.*` (credit, liquidity, exposure)

### Output
```json
{
  "normalized_id": "uuid",
  "ontology_path": "infra.energy.grid.maintenance",
  "signal_type": "deferral",
  "magnitude": 0.7,
  "temporal_marker": "2026-Q1",
  "source_refs": [...]
}
```

---

## 3. Accumulator Agent

**Role**: Probabilistic Reasoning

**Purpose**: Performs Bayesian evidence accumulation over time.

### Method
- Maintains belief state per risk vector
- Updates on each normalized signal
- Applies temporal decay to older signals
- Correlates cross-domain signals

### State
```json
{
  "risk_vector": "infra.energy.grid.northeast",
  "belief_state": 0.67,
  "contributing_signals": 12,
  "last_update": "2026-02-06T08:00:00Z",
  "trend": "increasing",
  "volatility": 0.15
}
```

---

## 4. Forecaster Agent

**Role**: Horizon Modeling

**Purpose**: Estimates outcome likelihoods and temporal windows.

### Outputs
- Time horizon estimation (days/weeks)
- Outcome probability distribution
- Scenario enumeration
- Confidence intervals

### Output
```json
{
  "risk_vector": "infra.energy.grid.northeast",
  "time_horizon_days": "14-28",
  "outcomes": [
    {"event": "localized_outage", "probability": 0.45},
    {"event": "price_spike", "probability": 0.30},
    {"event": "policy_intervention", "probability": 0.15}
  ],
  "confidence_interval": 0.82
}
```

---

## 5. Packager Agent

**Role**: Monetization Interface

**Purpose**: Converts internal risk states into sellable signal primitives.

### Access Tiers
- **Observer**: Aggregated heatmaps (anonymized, delayed)
- **Operator**: Raw risk vectors (named, near-real-time)
- **Fund/API**: Streaming signals (real-time, high-frequency)
- **Sovereign**: Custom domains (exclusive, bespoke)

### Output Formats
- JSON (default)
- Protobuf (streaming)
- Webhook (push)
- S3/GCS (batch)

### Output
```json
{
  "risk_vector": "infra.energy.grid.northeast",
  "signal_confidence": 0.82,
  "time_horizon_days": "14-28",
  "contributing_domains": ["procurement", "maintenance", "labor"],
  "likely_outcomes": ["localized_outage", "price_spike"],
  "tradability": {
    "insurance": true,
    "commodities": true,
    "logistics": true,
    "policy": false
  },
  "tier": "operator",
  "generated_at": "2026-02-06T08:15:00Z"
}
```

# Lead Scoring Customization

## How Scoring Works

Each lead is scored 0-100 across five dimensions. Configure weights and criteria in `config.json` under `scoring`.

## Default Weights

```json
{
  "scoring": {
    "threshold": 70,
    "weights": {
      "company_size_fit": 25,
      "industry_match": 25,
      "email_available": 20,
      "web_presence": 15,
      "tech_signals": 15
    }
  }
}
```

## Adjusting for Your Business

### B2B SaaS (targeting mid-market)
```json
{
  "threshold": 75,
  "weights": {
    "company_size_fit": 30,
    "industry_match": 20,
    "email_available": 20,
    "web_presence": 10,
    "tech_signals": 20
  },
  "target_industries": ["technology", "saas", "software"],
  "target_company_sizes": ["51-200", "201-500"]
}
```

### Local Service Business
```json
{
  "threshold": 60,
  "weights": {
    "company_size_fit": 15,
    "industry_match": 30,
    "email_available": 25,
    "web_presence": 20,
    "tech_signals": 10
  },
  "target_industries": ["restaurant", "retail", "healthcare", "legal"]
}
```

### Agency (targeting e-commerce)
```json
{
  "threshold": 70,
  "weights": {
    "company_size_fit": 20,
    "industry_match": 20,
    "email_available": 20,
    "web_presence": 15,
    "tech_signals": 25
  },
  "target_industries": ["ecommerce", "retail"],
  "target_company_sizes": ["11-50", "51-200"]
}
```

## Dimension Details

### company_size_fit
- Full score: size matches `target_company_sizes`
- 50%: known size but not matching
- 30%: size unknown

### industry_match
- Full score: matches `target_industries`
- 50%: no filter configured (neutral)
- 20%: doesn't match filter

### email_available
- Full score: verified email with >80% confidence
- 70%: unverified email found
- 0%: no email

### web_presence
- 60%: has website
- 40%: has social profiles
- Additive (both = 100%)

### tech_signals
- Full score: 3+ relevant technologies detected
- 50%: 1-2 technologies
- 20%: none detected

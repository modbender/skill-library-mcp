# KEV Triage Method

## Inputs

- CVE identifier
- CVSS score
- Exploitation indicator (`known_exploited`)
- Affected asset
- Asset criticality

## Scoring Model

Score each vulnerability as:

`score = CVSS + exploited_bonus + asset_criticality_weight`

- `exploited_bonus = 3.0` when known exploited
- `asset_criticality_weight`: critical=3.0, high=2.0, medium=1.0, low=0.5

## Priority Buckets

- `P1`: score >= 12, patch target 3 days
- `P2`: score >= 9, patch target 7 days
- `P3`: score < 9, patch target 21 days

## Validation Checklist

- Ensure each row has a CVE and affected asset.
- Ensure CVSS values are numeric.
- Ensure asset criticality values map to known levels.
- Ensure output includes score, priority, and due window.

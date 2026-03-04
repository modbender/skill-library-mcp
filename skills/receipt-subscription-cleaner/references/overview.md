# Overview

## Scope

- Extract receipts and normalize vendor records.
- Identify recurring charges and renewal cycles.
- Generate a clean subscription audit.

## Detection heuristics

- Cluster by normalized vendor name and descriptor text.
- Infer billing cycle from repeating amounts and dates.
- Flag overlapping subscriptions in the same category.

## Confidence

- High: exact vendor match and consistent cycle.
- Medium: similar vendor and partial cycle evidence.
- Low: single record or ambiguous vendor.

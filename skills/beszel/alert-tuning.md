# Beszel Alert Tuning Workflow

## Objective

Tune alerts so incidents are surfaced early without creating constant noise.

## Step 1: Capture Baseline

- Observe normal behavior for a short period before aggressive tuning.
- Separate expected peaks from true abnormal states.
- Document known maintenance windows and batch workloads.

## Step 2: Define Severity Tiers

- `warning`: unusual but not urgent conditions.
- `critical`: response required now to avoid impact.
- `urgent`: active service disruption or severe risk.

Apply clear response expectations for each tier.

## Step 3: Start Conservative

- Begin with broader thresholds to reduce false positives.
- Tighten gradually only after reviewing recent incidents.
- Keep one change per cycle so results are attributable.

## Step 4: Route Alerts by Ownership

- Every alert class must have a first responder.
- Define escalation targets for unresolved critical alerts.
- Avoid shared ownership with no clear accountable person.

## Step 5: Review Weekly

- Count false positives by alert type.
- Capture missed incidents and why detection lagged.
- Update thresholds, suppression windows, or service grouping.

## Common Recovery Actions

- Alert storm after deployment -> widen threshold temporarily, inspect release impact, and restore tighter limits once stable.
- Repeated disk pressure alerts -> track growth trend and add capacity planning note.
- CPU spikes at predictable times -> document workload schedule and tune threshold window.
- Frequent node disconnect alerts -> investigate network stability and clock sync before changing alert logic.

# Tracking Guide

## Reproducibility Checklist

- Capture dataset version or snapshot ID.
- Capture model family and hyperparameters.
- Capture metrics and threshold criteria.
- Capture run environment metadata.
- Capture artifact paths for model and schema outputs.

## Minimum Experiment Fields

- `experiment_name`
- `dataset`
- `parameters`
- `metrics`

## Recommended Next Steps

- Log plan output into MLflow or equivalent tracker.
- Compare baseline and candidate runs using consistent metric names.

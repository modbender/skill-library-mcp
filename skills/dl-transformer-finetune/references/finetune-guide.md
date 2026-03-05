# Finetune Guide

## Baseline Configuration

- `num_epochs`: 3
- `learning_rate`: 2e-5
- `batch_size`: 16
- `seed`: 42
- `evaluation_strategy`: epoch

## Validation Checklist

- Confirm dataset split and label distribution.
- Confirm tokenization settings match base model requirements.
- Confirm evaluation metrics fit task objective.
- Confirm output artifact naming and storage path.

## Model Card Minimum Fields

- Base model
- Task and dataset
- Metrics
- Risk and limitation notes

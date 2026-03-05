# Interpretation Guide

## GPU Memory Signals

- `reserved_vs_allocated_ratio > 1.30`:
  Indicates possible fragmentation or allocator over-reservation.
- Large `slack = reserved - allocated` in top segments:
  Indicates poor block reuse or shape variance causing unusable memory islands.
- High count of allocator actions (especially map/unmap or frequent alloc/free):
  Indicates allocator churn and potential synchronization overhead.

## CPU Profile Signals

- Top op dominates >20% total CPU op duration:
  Strong candidate for first optimization target.
- High `avg_dur_us` and high `count` simultaneously:
  Candidate for fusion, batching, or kernel-level replacement.
- Thread imbalance (single thread dominates):
  Check data pipeline parallelism and thread affinity.

## Common Root Causes and Fixes

1. OOM with high reserved/allocated ratio
- Likely cause: fragmentation, dynamic shapes, allocator config mismatch
- Fixes: bucket sequence lengths, reduce shape polymorphism, tune `PYTORCH_CUDA_ALLOC_CONF`, gradient checkpointing

2. CPU-bound training loop
- Likely cause: Python overhead, dataloader bottleneck, frequent small ops
- Fixes: increase worker throughput, prefetch/pin memory, fuse ops, move preprocessing off critical path

3. Communication stalls mixed with compute
- Likely cause: all_to_all / all_reduce overlap not effective
- Fixes: rebalance bucket sizes, adjust overlap strategy, profile NCCL phases separately

## Reporting Format

For each recommendation include:
- Observation: one metric from analyzer output
- Hypothesis: why this causes slowdown or memory pressure
- Action: exact change to try
- Validation: metric expected to improve and by how much (directional if uncertain)

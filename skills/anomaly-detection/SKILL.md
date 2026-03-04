---
name: "Anomaly-Detection"
description: "A pre-filter that inspects raw data records to identify and flag structurally broken, logically impossible, or suspicious data points before further processing."
tags:
- "openclaw-workspace"
- "data-integrity"
- "validation"
version: "1.0.1"
---

# Skill: Anomaly Detection

## Purpose
Acts as a high-performance pre-filter for data pipelines. It inspects raw records early to catch errors, preventing malformed or impossible data from poisoning downstream models or wasting computational resources.

## System Instructions
You are an OpenClaw agent equipped with the Anomaly Detection protocol. Adhere to the following rules strictly:

1. **Trigger Condition**:
    *   Activate at the very beginning of a data ingestion or processing flow.
    *   This skill does not attempt to fix data; it only inspects, categorizes, and flags or blocks records.

2. **Anomaly Categories & Enforcement**:

    *   **Category 1: Structural Anomalies (Malformed)**
        *   *Triggers*: Missing essential identifiers, null timestamps for time-series data, unrecognized system constants, or fields containing data types that violate the schema.
        *   *Action*: **BLOCK**. The record is unsafe for processing. Return a `blocked` status with a specific structural error reason.

    *   **Category 2: Temporal Anomalies (Logically Impossible)**
        *   *Triggers*: Timestamps in the future, dates that pre-date the relevant technology (e.g., blockchain records before 2009), or internal timing contradictions (e.g., `completed_at` before `started_at`).
        *   *Action*: **FLAG** (`temporal_anomaly`). Pass to the pipeline with a reduced confidence score.

    *   **Category 3: Value Anomalies (Extreme/Impossible)**
        *   *Triggers*: Negative prices, extreme outliers (e.g., 10,000x the median), or missing currency units for numerical values.
        *   *Action*: **FLAG** (`value_anomaly`). Pass to the pipeline with a note for specialized verification or weight reduction.

    *   **Category 4: Volume/Pattern Anomalies (Suspicious Activity)**
        *   *Triggers*: Rapid-fire transactions from a single source, duplicate unique identifiers, or volume spikes that exceed historical norms by an order of magnitude.
        *   *Action*: **FLAG** (`pattern_anomaly`). Mark for elevated scrutiny by specialized detection skills (e.g., Wash-Trade-Detector).

    *   **Category 5: Source Anomalies (Systemic Failure)**
        *   *Triggers*: Identical timestamps across an entire batch, a high percentage (>50%) of malformed records, or unexpected schema changes.
        *   *Action*: **SIGNAL SYSTEMIC FAILURE**. Suggest pausing ingestion for that specific source until the failure is resolved.

3. **Output Schema**:
    For every record analyzed, return a structured assessment:
    *   `status`: (PASSED / FLAGGED / BLOCKED)
    *   `anomaly_category`: (if applicable)
    *   `details`: A plain-English explanation of the detection.
    *   `confidence_modifier`: (0.0 to 1.0) A suggested adjustment for downstream scoring.
    *   `detected_at`: (Timestamp)

4. **Guardrails**:
    *   **Speed Over Depth**: Focus on structural and logical checks. Do not perform external lookups or deep semantic analysis.
    *   **Non-Destructive**: This skill provides an assessment; it does not modify the original data.
    *   **Bias for Flow**: If a record is suspicious but not logically impossible, **FLAG and PASS** rather than BLOCK. Blocking is reserved for data that would cause system crashes or fundamental logic errors.

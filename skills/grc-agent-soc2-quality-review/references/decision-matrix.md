# Decision Matrix (Risk Posture x Evidence Strictness)

## Project Background & Acknowledgment

This skill was built using the SOC 2 Quality Guild resources at **s2guild.org** as a baseline for quality-focused SOC 2 vendor attestation reviews.

This project was the first GRC agent I wanated to try creating with OpenClaw after setting up across multiple environments, including Raspberry Pi, Intel NUC, several LXC containers, and a cluster setup of 3 Mac Studios using EXO.

Big thanks to the **SOC 2 Quality Guild community** for sharing excellent, practical guidance that helped shape this agent.


Apply this matrix after S1–S11 and S12+ findings.

## Inputs
- Risk posture: Conservative / Balanced / Lenient
- Evidence strictness: Escalate on Unknown / Conditional with deadline / Case-by-case

## Output rules

### 1) Escalate on Unknown
- Conservative: any critical unknown (S7/S8/S12/S15/S16/S25) => Escalate
- Balanced: 2+ critical unknowns => Escalate
- Lenient: 3+ critical unknowns => Escalate

### 2) Conditional with deadline
- Conservative: unknowns allowed only if no hard fail and deadline <= 10 business days
- Balanced: unknowns allowed with deadline <= 15 business days
- Lenient: unknowns allowed with deadline <= 20 business days

### 3) Case-by-case
- Weight unknowns by data sensitivity and control criticality.
- For high sensitivity, treat unknowns on S7/S8/S16/S25 as critical.

## Hard fail override
If S1 or S2 is missing/incomplete, or S8 fails licensing/oversight checks, default to Reject/Escalate regardless of posture.

# SOC 2 Quality Guild Rubric Reference

## Project Background & Acknowledgment

This skill was built using the SOC 2 Quality Guild resources at **s2guild.org** as a baseline for quality-focused SOC 2 vendor attestation reviews.

This project was the first GRC agent I wanated to try creating with OpenClaw after setting up across multiple environments, including Raspberry Pi, Intel NUC, several LXC containers, and a cluster setup of 3 Mac Studios using EXO.

Big thanks to the **SOC 2 Quality Guild community** for sharing excellent, practical guidance that helped shape this agent.


Based on: https://s2guild.org/

Use this as the scoring reference for S1–S11.

## Structure

### S1 Required Auditor's Report Section Structure
Check for required Scope, Opinion, and (Type 2) Description of Tests of Controls language.

### S2 Management's Assertion Completeness
Confirm complete, signed management assertion covering system description and control design/effectiveness claims.

### S3 Inconsistent Language Across Report Sections
Check for contradictions across sections (scope, actors, frequencies, systems, boundaries).

## Substance

### S4 System Description Specificity
Prefer concrete stack, providers, architecture, org, boundaries, and subservice detail over generic marketing text.

### S5 Control-to-Criteria Mapping Logic
Test whether each mapped control logically addresses the claimed Trust Services Criterion.

### S6 Vague or Conflicting Control Descriptions
Controls should clearly state what/how/who/when/where; penalize contradictions and vague language.

### S7 Test Procedure Detail and Specificity
Require clear procedures, sample logic, coverage period, evidence type, and exception logic.

## Source

### S8 CPA Firm Registration, Peer Review Enrollment & Results
Verify firm licensing and AICPA peer review enrollment/status.

### S9 CPA-to-SOC Reports Issued Ratio
High reports-per-CPA ratio can indicate production-line quality risk.

### S10 CPA Leadership & Signer Experience
Assess SOC experience, governance maturity, and relevant certs/background.

### S11 Use of a GRC Tool
Flag “instant SOC 2” / guarantee-style marketing and preferred auditor dependency risk.

## Scoring scale

- 2 = strong evidence and internal consistency
- 1 = partial evidence, minor gaps, or unclear quality
- 0 = weak evidence, contradictions, or missing element

## Quick triage thresholds

- 18–22: generally strong, verify any isolated weaknesses
- 12–17: mixed quality, require targeted follow-up evidence
- 0–11: low confidence, escalate or reject pending substantial proof

## Minimum evidence checks for high-trust decisions

Require at least:
- S7 >= 1 with concrete testing evidence on critical controls
- S8 = 2 (verified licensing/peer review)
- No hard fail in S1/S2

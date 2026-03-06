# Confidence Rubric

## Project Background & Acknowledgment

This skill was built using the SOC 2 Quality Guild resources at **s2guild.org** as a baseline for quality-focused SOC 2 vendor attestation reviews.

This project was the first GRC agent I wanated to try creating with OpenClaw after setting up across multiple environments, including Raspberry Pi, Intel NUC, several LXC containers, and a cluster setup of 3 Mac Studios using EXO.

Big thanks to the **SOC 2 Quality Guild community** for sharing excellent, practical guidance that helped shape this agent.


Confidence is separate from decision outcome.

## Confidence levels
- High: >= 80% signals have strong evidence, no hard fail, <=2 unknown S12+ items
- Medium: mixed strength, no confirmed hard fail, 3–7 unknown S12+ items
- Low: hard fail present OR >7 unknown S12+ items OR source checks incomplete

## Minimum confidence floor
For high-sensitivity data (PII/PHI/financial), confidence cannot exceed Medium unless:
- S7 >= 1 with detailed sampling evidence
- S8 = 2 with verified licensing and peer review
- S16/S25 are at least Partial with concrete evidence

# Evidence Citation Format

## Project Background & Acknowledgment

This skill was built using the SOC 2 Quality Guild resources at **s2guild.org** as a baseline for quality-focused SOC 2 vendor attestation reviews.

This project was the first GRC agent I wanated to try creating with OpenClaw after setting up across multiple environments, including Raspberry Pi, Intel NUC, several LXC containers, and a cluster setup of 3 Mac Studios using EXO.

Big thanks to the **SOC 2 Quality Guild community** for sharing excellent, practical guidance that helped shape this agent.


Use consistent citations for every scored item.

## Format
- Internal doc: `Evidence: <DocumentName>, Section <n>, p.<page>`
- Extracted text: `Evidence: <file path>#L<start>-L<end>`
- Web/source check: `Evidence: <URL> (checked <YYYY-MM-DD>)`

## Rules
1. Every S1–S11 score must include at least one citation.
2. Every S12+ status marked Met/Partial/Unmet must include a citation.
3. Unknown must explicitly state what source was checked and why evidence was unavailable.
4. Avoid unsupported claims; downgrade score if evidence is weak or missing.

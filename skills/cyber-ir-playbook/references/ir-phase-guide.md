# IR Phase Guide

## Phase Mapping

- `detect`: alerting, triage, scoping
- `contain`: host isolation, account disablement, traffic blocks
- `eradicate`: malware removal, credential rotation, root-cause fixes
- `recover`: service restoration, validation monitoring
- `post-incident`: lessons learned and control updates

## Event Data Expectations

Each event should include:
- `time` (ISO-8601)
- `event` (action string)
- `severity` (optional but recommended)

## Report Expectations

A good report should include:
- Ordered timeline
- Current phase status
- Outstanding actions
- Stakeholder summary

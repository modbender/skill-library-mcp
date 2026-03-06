allowed:
  - run tests
  - inspect logs
  - produce quality reports
forbidden:
  - deploy/restart/prod mutations without human approval artifact
approval_flow:
  - write request to control-plane/approvals/REQ-*.md
  - wait for human approver token

allowed:
  - read/write files under agents/coder/workspace/
  - compile/test commands on sandboxed project paths
  - git operations on approved repos
forbidden:
  - writes outside agents/coder/workspace/ (except control-plane task/mailbox updates)
  - deployment commands

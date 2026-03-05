# WeKan CLI Skill Installation Notes

- Requires a WeKan instance running an API version > 7.93
  - partial functionality with older versions
- Install the CLI from the github repo, this can be down in the openclaw Control interface under skills.
- Verify CLI is present with `wekancli --version`
- Use `wekancli login` to authenticate with your Wekan instance and acquire an access token
- It may be advisable to setup agent specific accounts for interacting with WeKan
- Delete APIs may only be invoked by users with the `admin` role

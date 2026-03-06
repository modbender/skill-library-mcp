# V1 Release Checklist (Public)

## 1) Safety + policy
- [ ] Outbound call policy is explicit (requires human approval unless user config says otherwise).
- [ ] Payment/deposit rule is explicit (stop + handoff).
- [ ] Privacy statement included (no secret leakage, no unauthorized data sharing).

## 2) Secret hygiene
- [ ] No API keys/tokens in files.
- [ ] No private phone numbers unless intended as placeholders.
- [ ] Replace local absolute paths with variables or examples.

## 3) Runtime behavior
- [ ] Greeting works.
- [ ] ask_openclaw call path works.
- [ ] Timeout/fallback message is human-friendly.
- [ ] Logging is enough to debug failed calls.

## 4) Installability
- [ ] SKILL.md has clear trigger description.
- [ ] Setup steps are reproducible on a fresh machine.
- [ ] Optional dependencies are marked optional.

## 5) Packaging + publish
- [ ] `package_skill.py` validation passes.
- [ ] Publish with semver `1.0.0` and changelog.
- [ ] Add `latest` tag.

## 6) Post-publish
- [ ] Verify listing page renders correctly on ClawHub.
- [ ] Test install from CLI on a clean workspace.
- [ ] Open a tracking issue list for V1->V2 fixes.

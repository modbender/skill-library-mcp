# GitHub Release Guide

Use this checklist before pushing `research-to-wechat` as a public-facing skill update.

## Release goal

Ship the skill as a clean GitHub-ready package with:

- clear positioning
- complete usage docs
- root repo visibility
- no forbidden legacy naming inside the skill directory

## Required files

The release should include:

- `research-to-wechat/SKILL.md`
- `research-to-wechat/README.md`
- `research-to-wechat/CHANGELOG.md`
- `research-to-wechat/LICENSE`
- `research-to-wechat/references/capability-map.md`
- `research-to-wechat/references/style-engine.md`
- `research-to-wechat/references/execution-contract.md`
- `research-to-wechat/docs/GITHUB_RELEASE.md`
- `research-to-wechat/docs/EXAMPLES.md`
- root `README.md`

## Smoke checks

Run these checks before publishing:

```bash
# Run your current forbidden-term denylist scan against research-to-wechat/
python3 '/Users/clarezoe/.agent/skills/skill-creator/scripts/package_skill.py' \
  '/Users/clarezoe/Dropbox/My Apps/my-skills/research-to-wechat' \
  /tmp/research-to-wechat-release-check
```

Expected result:

- search returns no matches in `research-to-wechat/`
- packaging succeeds without validation errors

## README review

Verify the skill README answers these questions:

- what problem does this skill solve
- who is it for
- what files does it produce
- what inputs does it accept
- how style resolution works
- where the execution rules live

## Root repo review

Verify the root `README.md`:

- lists `research-to-wechat` in featured skills
- describes it consistently in English, Chinese, and Japanese
- presents the skill as one member of the wider skill collection

## Suggested GitHub metadata

Repository-facing short description:

`End-to-end WeChat article orchestration from source material to researched draft, visual polish, HTML rendering, and browser draft save.`

Suggested topics:

- `skill`
- `wechat`
- `content-workflow`
- `markdown`
- `article-generation`
- `writing-system`
- `research`

## Suggested release note shape

```md
## Added
- New `research-to-wechat` skill for end-to-end article production
- Neutral capability alias layer
- Internal style engine and execution contract references

## Updated
- Root README now lists the skill in all supported languages

## Verified
- Skill packaging passes
- Forbidden legacy naming removed from the skill directory
```

## Suggested screenshots

If you want visual proof for the GitHub page, capture:

- the skill directory tree
- the top of `research-to-wechat/README.md`
- the style engine reference
- the packaged validation output

## Publish sequence

1. Verify the smoke checks
2. Review the skill README in GitHub preview
3. Review the root README in GitHub preview
4. Commit only the intended files
5. Push the branch
6. Open the GitHub page and verify links render correctly

## Final gate

Do not publish if any of these are true:

- skill packaging fails
- any forbidden legacy term still appears in `research-to-wechat/`
- root README and skill README describe different outputs
- example prompts no longer match the current style system

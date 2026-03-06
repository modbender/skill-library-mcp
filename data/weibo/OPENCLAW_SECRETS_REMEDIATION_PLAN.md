# OpenClaw Secrets Remediation Plan

## Objective

Remediate the ClawHub/OpenClaw publication issues for this Weibo skill without weakening the repo's open-source intent. The project should remain easy to inspect and modify, while making secret requirements explicit and aligning with OpenClaw's documented secret handling model.

Relevant OpenClaw references:
- `https://docs.openclaw.ai/gateway/secrets#secrets-management`
- `https://docs.openclaw.ai/core-concepts/skills#metadata`

## Current Gaps

The current skill has three separate problems:

1. Published metadata does not declare the runtime environment variables that the scripts require.
2. Sensitive inputs are mixed with non-sensitive configuration in plain shell environment usage.
3. The Brave fallback introduces a second commercial credential path, but the skill presents it as a simple fallback rather than a separate trust boundary.

Current variables by sensitivity:

- Non-secret configuration:
  - `WEIBO_APP_KEY`
  - `WEIBO_REDIRECT_URI`
- Sensitive:
  - `WEIBO_APP_SECRET`
  - `WEIBO_ACCESS_TOKEN`
  - `BRAVE_SEARCH_API`

## Constraints From OpenClaw

OpenClaw's secrets reference model is narrower than this skill's current shell interface.

- Secret references and `secrets audit` cover specific config locations, including `skills.entries.<skillKey>.apiKey`.
- Arbitrary environment variables are not covered by that same audit path.
- As a result, storing `WEIBO_APP_SECRET`, `WEIBO_ACCESS_TOKEN`, or `BRAVE_SEARCH_API` as ad hoc skill env vars would not give users the same audit visibility as a documented `SecretRef`.

This means the fix is not only "declare more env vars." The skill should prefer OpenClaw-managed secret paths where possible, and explicitly warn when a secret must still come from external environment injection.

## Remediation Strategy

### Phase 1: Correct the published contract

Update skill metadata and docs so users and automated installers can see the runtime contract before execution.

Actions:

1. Add `metadata` to [`SKILL.md`](/home/noir/enna/skills/weibo/weibo/SKILL.md) with at least:
   - `openclaw.skillKey`
   - `openclaw.requires.env` for the base required variables
   - `openclaw.primaryEnv` for the primary credential if the skill remains single-package
2. Add a "Credentials and Secret Handling" section to [`SKILL.md`](/home/noir/enna/skills/weibo/weibo/SKILL.md) that separates:
   - required non-secret config
   - required secrets
   - optional secrets
   - when each one is used
3. Add the same disclosure to [`README.md`](/home/noir/enna/skills/weibo/weibo/README.md), since registry users may read the repo before or after install.
4. State explicitly that `BRAVE_SEARCH_API` is only required for fallback search.

Recommended disclosure table:

| Variable | Required | Sensitive | Used for |
| --- | --- | --- | --- |
| `WEIBO_APP_KEY` | Yes for OAuth flow | No | Weibo OAuth client identifier |
| `WEIBO_REDIRECT_URI` | Yes for OAuth flow | No | OAuth callback |
| `WEIBO_APP_SECRET` | Yes for token exchange | Yes | OAuth token exchange |
| `WEIBO_ACCESS_TOKEN` | Yes for authenticated API calls | Yes | Weibo API bearer token |
| `BRAVE_SEARCH_API` | No | Yes | Fallback Brave search on `site:weibo.com` |

### Phase 2: Reduce the secret surface in the published skill

Do not make the fallback search credential part of the base skill contract if it can be avoided.

Preferred path:

1. Split [`scripts/weibo_search.py`](/home/noir/enna/skills/weibo/weibo/scripts/weibo_search.py) into a second skill, for example `weibo-brave-search`.
2. Keep the main `weibo` skill focused on the Weibo Open Platform flow.
3. Publish the Brave-backed fallback as optional so the base skill does not appear to require two unrelated commercial credential sets.

Reasoning:

- This matches least privilege more closely.
- It gives each published skill a cleaner credential story.
- It avoids declaring `BRAVE_SEARCH_API` as a required variable for users who only want the official Weibo API path.

Fallback if a split is not practical:

1. Keep one skill, but mark the Brave path as optional and disabled by default.
2. Add a strong warning that the fallback is a separate commercial dependency with its own secret handling obligations.

### Phase 3: Align with OpenClaw-managed secrets where possible

The repo should prefer OpenClaw-managed secret references for the primary credential path, and document any residual secrets that must remain outside that model.

Actions:

1. Choose one primary OpenClaw-managed credential for the main skill.
2. Recommended default: treat `WEIBO_APP_SECRET` as the primary secret for the OAuth flow if the skill is primarily about app-based Weibo access.
3. If the common usage pattern is token-only API calls, consider making `WEIBO_ACCESS_TOKEN` the primary secret instead, but only if the published workflow is refocused around pre-issued tokens.
4. Do not imply that arbitrary env injection has the same audit guarantees as `SecretRef`.
5. In docs, tell users to source residual secrets from their external secret store or deployment environment, not from checked-in config.

Decision rule:

- If the published primary workflow is "obtain token through OAuth," prefer `WEIBO_APP_SECRET` as `primaryEnv`.
- If the published primary workflow is "use an existing token to call endpoints," prefer `WEIBO_ACCESS_TOKEN` as `primaryEnv` and move OAuth exchange to an advanced workflow.

### Phase 4: Add deliberate warnings for any non-audited secret path

Because this is an open-source wrapper around commercial API providers, warnings are appropriate when the implementation uses secret paths that fall outside OpenClaw's audited `SecretRef` model.

Add explicit warnings in [`SKILL.md`](/home/noir/enna/skills/weibo/weibo/SKILL.md) and [`README.md`](/home/noir/enna/skills/weibo/weibo/README.md):

1. `WEIBO_APP_SECRET`, `WEIBO_ACCESS_TOKEN`, and `BRAVE_SEARCH_API` are sensitive and must not be committed.
2. If supplied through plain environment variables, those values are not covered by OpenClaw's `skills.entries.<skillKey>.apiKey` audit path.
3. Users should prefer an external secret manager or deployment-time environment injection they control.
4. The Brave fallback sends queries to `api.search.brave.com`; the Weibo CLI sends requests to `api.weibo.com`.
5. The fallback should be used only when the user intentionally accepts that extra provider dependency.

Suggested warning text:

> This skill can operate with secrets supplied through plain environment variables, but that path may fall outside OpenClaw's audited `SecretRef` flow. If you use `WEIBO_APP_SECRET`, `WEIBO_ACCESS_TOKEN`, or `BRAVE_SEARCH_API` this way, store them in your external secrets manager or deployment environment and do not treat them as registry-managed secrets unless explicitly configured as such.

### Phase 5: Tighten the implementation to match the docs

The scripts should enforce the contract they advertise.

Actions:

1. Update [`scripts/weibo_cli.sh`](/home/noir/enna/skills/weibo/weibo/scripts/weibo_cli.sh) help text to label variables as `required`, `optional`, and `sensitive`.
2. Update [`scripts/weibo_search.py`](/home/noir/enna/skills/weibo/weibo/scripts/weibo_search.py) docstring and CLI help to warn that the fallback depends on a separate Brave credential.
3. Add a guardrail message before fallback search execution if `BRAVE_SEARCH_API` is missing or if the user has not explicitly requested fallback behavior.
4. Ensure examples never suggest hardcoding secrets into the command line when an env var or secure prompt is available.

## Recommended Publication Shape

Best option:

1. Publish `weibo` as the official Weibo API skill.
2. Publish `weibo-brave-search` as a separate optional fallback skill.
3. Declare only the variables required by each skill.
4. Use OpenClaw's primary credential metadata only for the main secret each skill actually uses.

Acceptable option:

1. Keep one skill.
2. Declare the full variable set in docs.
3. Mark `BRAVE_SEARCH_API` as optional and off by default.
4. Add prominent warnings that some secrets may be provided through non-audited env injection.

## Exit Criteria

The remediation is complete when all of the following are true:

1. The published metadata clearly declares the base env contract and primary credential.
2. Repo docs distinguish secret from non-secret variables.
3. Users are warned when a secret path falls outside OpenClaw's audited `SecretRef` scope.
4. The Brave fallback is either split into its own skill or clearly documented as optional.
5. No example in the repo normalizes unsafe secret handling.

## Immediate Next Changes

1. Update [`SKILL.md`](/home/noir/enna/skills/weibo/weibo/SKILL.md) metadata and add a credential handling section.
2. Expand [`README.md`](/home/noir/enna/skills/weibo/weibo/README.md) with deployment and warning guidance.
3. Decide whether to split the Brave fallback before the next publish.
4. Republish and run `openclaw secrets audit` against the final config shape used for installation.

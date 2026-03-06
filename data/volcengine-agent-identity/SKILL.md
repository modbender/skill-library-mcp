---
name: identity
description: |
  UserPool login, TIP token, credential hosting, and tool risk approval. Activate when user needs to check identity (whoami/status), log in, list/add credentials, manage env bindings, configure the plugin, or diagnose/approve risky tool calls.
  Also activates for: 用户说登录、查身份、获取凭据、添加/配置API密钥、绑定环境变量、配置插件、审批工具调用、风险检查.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔐",
        "skillKey": "identity",
        "requires": { "config": ["plugins.entries.agent-identity.enabled"] },
      },
  }
---

# Agent Identity

Use the agent-identity plugin for UserPool OIDC login (入站授权), TIP token (工作负载访问令牌), credential hosting (出站授权 OAuth2, API key), and optional tool risk approval (权限管控 AuthZ).

**Volcengine terminology**: 用户池 (UserPool), 入站授权 (OIDC login), 出站授权 (credential fetch), 工作负载令牌 (TIP), 凭据托管 (credential hosting), 权限管控 (CheckPermission). Docs: [Volcengine 智能体身份和权限管理](https://www.volcengine.com/docs/86848).

**Agent flow:** When the user asks to log in, add credentials, check status, bind env, etc., call the corresponding tools directly. Do not suggest slash commands for those. Slash commands below are for user-initiated use (e.g. `/identity approve <id>` when the user must approve in chat; agent must never call `identity_approve_tool`).

## Slash commands (user-initiated)

| Command | Purpose |
| ------- | ------- |
| `/identity` | Show help |
| `/identity whoami` | Identity brief |
| `/identity status` | Full status: session, TIP, credentials, bindings |
| `/identity login` | Log in via OIDC (returns auth URL) |
| `/identity logout` | Clear session and TIP |
| `/identity list-credentials` or `/identity list [page]` | List providers and credentials |
| `/identity list-tips` | List valid TIP tokens |
| `/identity config` | Show plugin config (redacted) |
| `/identity fetch <provider> [--flow=...]` | Add credential |
| `/identity set <provider> <envVar>` | Bind credential to env var |
| `/identity unset <provider>` | Remove env binding |
| `/identity risk <command>` | Diagnose risk for a shell command |
| `/identity risk-patterns` | List built-in risky patterns |
| `/identity approve <approval_id>` | Approve high-risk tool call (user runs this; agent must not self-approve) |
| `/identity reject <approval_id>` | Reject high-risk tool call |

## Tools Overview

| Tool                        | Params                                         | Purpose                                    |
| --------------------------- | ---------------------------------------------- | ------------------------------------------ |
| `identity_whoami`           | —                                              | Identity brief: sub, login time, TIP expiry |
| `identity_status`           | —                                              | Full status: session/TIP (issued, expires, chain), credentials, bindings |
| `identity_login`            | —                                              | Start OIDC login or refresh TIP            |
| `identity_logout`           | —                                              | Clear session and TIP                      |
| `identity_list_credentials` | `page?`                                        | List providers and credentials (paginated) |
| `identity_list_tips`        | —                                              | List valid TIP tokens and bindings         |
| `identity_config`           | —                                              | Show plugin config (secrets redacted)      |
| `identity_config_suggest`  | `intent?`, `lang?`                             | Generate config snippets for openclaw.json |
| `identity_fetch`            | `provider`, `flow?`, `redirectUrl?`, `scopes?` | Add credential                             |
| `identity_set_binding`      | `provider`, `envVar`                           | Bind provider → env var for tool injection |
| `identity_unset_binding`    | `provider`                                     | Remove env binding                         |
| `identity_approve_tool`     | `approval_id`                                  | Approve a high-risk tool call              |
| `identity_risk_check`       | `command?`, `toolName?`, `params?`             | Diagnose risk for command or tool call     |
| `identity_list_risk_patterns` | —                                            | List built-in risky patterns and paths     |

## Risk Detection and Approval

When `authz.requireRiskApproval` is on, the plugin classifies tool calls (e.g. exec, write, apply_patch) by risk. User-provided commands and file paths are evaluated:

- **Rule-based**: Destructive patterns (rm -rf, sudo, curl|bash), sensitive paths (/etc, ~/.ssh).
- **LLM-based** (optional): When rules return "medium", an LLM re-evaluates for context (`authz.enableLlmRiskCheck`).

High-risk calls require user approval. The approval message and block reason include the LLM risk explanation when available (e.g. "Pipe-to-shell: network fetch piped to shell execution").

## Tool Parameters

### identity_login

Starts OIDC login or refreshes TIP. **Call when:** "login", "登录", "sign in", "我需要先登录". Required before `identity_fetch`. No params.

### identity_whoami

Brief identity check. **Call when:** "who am I", "查身份", "am I logged in", "当前登录状态"

Returns: `sub`, `hasTip`, `loggedIn`, `sessionLoginAt`, `sessionExpiresAt`, `tipIssuedAt`, `tipExpiresAt`, `tipExpiresInSeconds`, `tipChain`. No params.

### identity_status

Full status including credentials and bindings. **Call when:** "status", "查看完整状态", "我的凭据和绑定", "show my credentials and bindings"

Returns: `loggedIn`, `sub`, `hasTip`, `session` (loginAt, expiresAt), `tip` (issuedAt, expiresAt, chain), `credentialProviders`, `bindings`. No params.

### identity_list_credentials

Lists available credential providers and what the user has stored. **Call this when the user wants to see what they can connect or what credentials they have.**

**User prompts:** "有哪些服务可以连接", "what providers are available", "我添加了哪些凭据", "list my credentials", "show available providers"

| Param  | Type   | Required | Description              |
| ------ | ------ | -------- | ------------------------ |
| `page` | number | No       | Page number (default: 1) |

```json
{ "page": 2 }
```

Returns: `providers`, `storedOnly`, `page`, `hasMore`.

### identity_fetch

Adds a credential for a provider (OAuth2 or API key). **Call this when the user wants to add, get, or configure credentials.**

**User prompts that mean "call identity_fetch":**

- English: "add/google my Google token", "get credentials for OpenAI", "connect my GitHub", "I need to use Google API", "set up API key for X", "authorize access to Y", "I want to use [provider] but have no key"
- 中文: "帮我添加/获取 Google 凭据", "配置 OpenAI 的 API key", "连接我的 GitHub", "我要用某某服务但没有密钥", "授权访问某平台", "添加某某的 token", "获取某某的凭证"

First ensure user is logged in (`identity_whoami`); if not, use `identity_login`. Then call `identity_fetch` with the provider. Use `identity_list_credentials` to discover available providers.

| Param         | Type     | Required | Description                                                                             |
| ------------- | -------- | -------- | --------------------------------------------------------------------------------------- |
| `provider`    | string   | Yes      | Provider name (e.g. `google`, `openai`)                                                 |
| `flow`        | string   | No       | `oauth2-user` (default for 3LO), `oauth2-m2m`, or `apikey`. Auto-inferred when omitted. |
| `redirectUrl` | string   | No       | OAuth redirect URL (when provider requires custom)                                      |
| `scopes`      | string[] | No       | OAuth scopes (e.g. `["email", "profile"]`)                                              |
| `returnValue` | boolean  | No       | When true and fetch succeeds, include credential `value` in result for same-turn automation. Default false. |

```json
{ "provider": "google" }
```

```json
{ "provider": "openai", "flow": "apikey", "returnValue": true }
```

**Response:**

- **OAuth2-user**: `authUrl` (user must open in browser). After authorization, success message sent to chat.
- **OAuth2-m2m** / **apikey**: `success: true`, `message` (completes immediately). If `returnValue: true`, also includes `value` (credential string) for same-turn use.

### identity_set_binding

Binds a stored credential to an env var so tools can use it at runtime. **Call this when the user wants tools/agent to have access to a credential.**

**User prompts:** "让工具能用我的 Google 凭据", "bind/google my credential for tools", "把 Google token 注入给 agent", "inject my OpenAI key for API calls", "配置某某凭据给工具用"

Credential must exist first (`identity_fetch`). Common env vars: `GOOGLE_ACCESS_TOKEN`, `OPENAI_API_KEY`, `GITHUB_TOKEN`, etc.

| Param      | Type   | Required | Description                                                                              |
| ---------- | ------ | -------- | ---------------------------------------------------------------------------------------- |
| `provider` | string | Yes      | Provider name (e.g. `google`)                                                            |
| `envVar`   | string | Yes      | Env var for injection (e.g. `GOOGLE_ACCESS_TOKEN`). Must match `[A-Za-z_][A-Za-z0-9_]*`. |

```json
{ "provider": "google", "envVar": "GOOGLE_ACCESS_TOKEN" }
```

If credential exists: binds it. Else: imports from `process.env[envVar]` as api_key (gateway must have that env set).

### identity_unset_binding

| Param      | Type   | Required | Description                             |
| ---------- | ------ | -------- | --------------------------------------- |
| `provider` | string | Yes      | Provider name to unbind (e.g. `google`) |

```json
{ "provider": "google" }
```

### identity_approve_tool

| Param         | Type   | Required | Description                                                                 |
| ------------- | ------ | -------- | --------------------------------------------------------------------------- |
| `approval_id` | string | Yes      | ID from the approval prompt (e.g. after blocking a high-risk exec/write)   |

Optional tool (not given to agent by default). For human approval, use `/identity approve <id>` or reply "approve" in chat. The agent must NOT call this tool to self-approve. The approval prompt includes the LLM risk reason when available.

```json
{ "approval_id": "abc123" }
```

### identity_risk_check

Evaluates risk of a command or tool call before execution. **Call when:** "这个命令安全吗", "is rm -rf dangerous", "check if this is risky", "帮我评估这个命令有没有风险"

| Param      | Type     | Required | Description                                                                 |
| ---------- | -------- | -------- | --------------------------------------------------------------------------- |
| `command`  | string   | No*      | Shell command to evaluate (treated as exec). Use for quick diagnosis.      |
| `toolName` | string   | No*      | Tool name (e.g. write, apply_patch). Use with params.                       |
| `params`   | object   | No       | Tool params. For exec: `{command}`. For write: `{path, content}`.           |

*Provide either `command` or `toolName`. Returns `risk`, `reason`, `source` (rules or llm). Uses LLM when `authz.enableLlmRiskCheck` is true and rules return medium.

```json
{ "command": "rm -rf /" }
```

```json
{ "toolName": "write", "params": { "path": "/etc/hosts", "content": "..." } }
```

### identity_list_risk_patterns

Returns built-in dangerous command patterns and sensitive paths. No params. Use to query what triggers high-risk approval.

```json
{}
```

### identity_config_suggest

Generates config snippets for the agent-identity plugin. **Call when:** user asks to configure identity, login, authz, risk approval, or "如何配置 identity 插件", "帮我配置登录", "怎么开启权限检查".

| Param   | Type   | Required | Description                                                                 |
| ------- | ------ | -------- | --------------------------------------------------------------------------- |
| `intent`| string | No       | `identity` (AK/SK), `userpool` (OIDC login), `authz` (permission/approval), `llm_risk` (LLM re-eval), `full` (all). Default: full |
| `lang`  | string | No       | `en` or `zh` for instructions. Default: en                                  |

Returns: `configPath`, `config` (JSON to merge), `instructions`, `nextSteps`. When `intent` is `identity` or `full`, also returns `identityDefaults` (env vars, credential resolution order, config defaults, credential file format). User must manually add to openclaw.json and restart gateway.

```json
{ "intent": "userpool", "lang": "zh" }
```

## Workflow: Adding a Credential

1. **Check login**: `identity_whoami` (brief) or `identity_status` (full). If not logged in, use `identity_login` first (user opens auth URL).
2. **Add credential**: `identity_fetch` with `provider`. For OAuth2-user, tell user to open `authUrl`; success message sent when done.
3. **Bind for tools** (optional): `identity_set_binding` so the credential is injected as an env var when tools run.

## Workflow: Checking Risk Before Running

1. **Diagnose**: `identity_risk_check` with `command` or `toolName`+`params`. Returns risk level and reason.
2. **List patterns**: `identity_list_risk_patterns` to see what triggers high-risk approval.

## Configuration

Plugin config lives under `plugins.entries.agent-identity.config`:

- `identity`: Identity API (endpoint, credentials, workloadPoolName, workloadName, roleTrn). When `roleTrn` is set (AssumeRole), workload name is omitted; backend uses roleName. When workload not found (404), plugin auto-creates via CreateWorkloadIdentity then retries.
- `userpool`: OIDC (discoveryUrl, clientId, callbackUrl, or userPoolName+clientName)
- `authz`: Optional AuthZ (toolCheck, skillReadCheck, requireRiskApproval, enableLlmRiskCheck, llmRiskCheck, namespaceName, lowRiskBypass). When `enableLlmRiskCheck` is true, rules returning "medium" are re-evaluated via LLM; the risk reason is shown in approval prompts and block messages.

## Notes

- Requires the agent-identity plugin to be enabled.
- `/identity` and tools require session context (channel + sender); use from an active chat.
- `identity_risk_check` and `identity_list_risk_patterns` do not require login.

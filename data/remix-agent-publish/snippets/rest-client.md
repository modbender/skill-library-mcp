---
name: agent-rest-snippets
description: REST client snippets for Remix agent publishing
metadata:
  tags: remix, rest, snippets
---

## TypeScript (REST)

```ts
const baseUrl = 'https://api.remix.gg'
const headers = {
  Authorization: `Bearer ${process.env.REMIX_API_KEY!}`,
  'Content-Type': 'application/json',
}

const openApiSpec = await fetch(`${baseUrl}/docs/json`, {
  method: 'GET',
  headers,
}).then((r) => r.json())

const createRes = await fetch(`${baseUrl}/v1/agents/games`, {
  method: 'POST',
  headers,
  body: JSON.stringify({ name: 'Neon Dash' }),
})
const createJson = await createRes.json()
if (!createJson.success) throw new Error(createJson.error.message)

const gameId = createJson.data.game.id as string
const versionId = createJson.data.game.version.id as string

const updateRes = await fetch(
  `${baseUrl}/v1/agents/games/${gameId}/versions/${versionId}/code`,
  {
    method: 'POST',
    headers,
    body: JSON.stringify({ code: html }),
  },
)
const updateJson = await updateRes.json()
if (!updateJson.success) throw new Error(updateJson.error.message)

const validateRes = await fetch(
  `${baseUrl}/v1/agents/games/${gameId}/versions/${versionId}/validate`,
  { method: 'GET', headers },
)
const validateJson = await validateRes.json()
if (!validateJson.success) throw new Error(validateJson.error.message)
if (!validateJson.data.valid) {
  throw new Error(`Blocked: ${validateJson.data.blockers.map((b: { code: string }) => b.code).join(', ')}`)
}

const statusRes = await fetch(
  `${baseUrl}/v1/agents/games/${gameId}/versions/${versionId}/status`,
  { method: 'GET', headers },
)
const statusJson = await statusRes.json()
if (!statusJson.success) throw new Error(statusJson.error.message)

const readinessRes = await fetch(
  `${baseUrl}/v1/agents/games/${gameId}/launch-readiness?versionId=${versionId}`,
  { method: 'GET', headers },
)
const readinessJson = await readinessRes.json()
if (!readinessJson.success) throw new Error(readinessJson.error.message)
```

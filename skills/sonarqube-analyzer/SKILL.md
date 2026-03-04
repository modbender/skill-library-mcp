# SonarQube Analyzer Skill

Analisa projetos no SonarQube self-hosted, obtém issues e sugere soluções automatizadas.

## Ferramentas Registradas

### `sonar_get_issues`
Obtém lista de issues de um projeto/PR no SonarQube.

**Parâmetros:**
- `projectKey` (string, obrigatório): Chave do projeto
- `pullRequest` (string, opcional): Número da PR para análise específica
- `severities` (string[], opcional): Severidades a filtrar (BLOCKER, CRITICAL, MAJOR, MINOR, INFO)
- `status` (string, opcional): Status das issues (OPEN, CONFIRMED, FALSE_POSITIVE, etc.)
- `limit` (number, opcional): Limite de issues (padrão: 100)

**Exemplo:**
```json
{
  "projectKey": "openclaw-panel",
  "pullRequest": "5",
  "severities": ["CRITICAL", "MAJOR"],
  "limit": 50
}
```

### `sonar_analyze_and_suggest`
Analisa issues e sugere soluções com base nas regras do SonarQube.

**Parâmetros:**
- `projectKey` (string, obrigatório): Chave do projeto
- `pullRequest` (string, opcional): Número da PR
- `autoFix` (boolean, opcional): Tentar aplicar correções automáticas (padrão: false)

**Exemplo:**
```json
{
  "projectKey": "openclaw-panel",
  "pullRequest": "5",
  "autoFix": false
}
```

### `sonar_quality_gate`
Verifica o status do Quality Gate de um projeto.

**Parâmetros:**
- `projectKey` (string, obrigatório): Chave do projeto
- `pullRequest` (string, opcional): Número da PR

**Exemplo:**
```json
{
  "projectKey": "openclaw-panel",
  "pullRequest": "5"
}
```

## Configuração

O skill usa as seguintes configurações do ambiente:

```bash
SONAR_HOST_URL=http://127.0.0.1:9000  # URL do SonarQube
SONAR_TOKEN=admin                      # Token de autenticação
```

## Uso

### Analisar uma PR específica:
```bash
node scripts/analyze.js --project=my-project --pr=5
```

### Gerar relatório de issues:
```bash
node scripts/report.js --project=my-project --format=markdown
```

### Verificar Quality Gate:
```bash
node scripts/quality-gate.js --project=my-project --pr=5
```

## Estrutura de Resposta

### sonar_get_issues
```json
{
  "total": 12,
  "issues": [
    {
      "key": "...",
      "severity": "MAJOR",
      "component": "apps/web/src/ui/App.tsx",
      "line": 346,
      "message": "Extract this nested ternary...",
      "rule": "typescript:S3358",
      "status": "OPEN",
      "solution": "Extract nested ternary into a separate function..."
    }
  ],
  "summary": {
    "BLOCKER": 0,
    "CRITICAL": 0,
    "MAJOR": 2,
    "MINOR": 10,
    "INFO": 0
  }
}
```

### sonar_analyze_and_suggest
```json
{
  "projectKey": "openclaw-panel",
  "analysis": {
    "totalIssues": 12,
    "fixableAutomatically": 8,
    "requiresManualFix": 4
  },
  "suggestions": [
    {
      "file": "apps/web/src/ui/App.tsx",
      "line": 346,
      "issue": "Nested ternary operation",
      "suggestion": "Extract into independent component",
      "codeExample": "...",
      "autoFixable": false
    }
  ],
  "nextSteps": [
    "Run lint:fix for auto-fixable issues",
    "Refactor nested ternaries in App.tsx",
    "Replace || with ?? operators"
  ]
}
```

## Soluções Automáticas Disponíveis

| Regra | Problema | Solução Automática |
|-------|----------|-------------------|
| S6606 | Use `\|\|` instead of `??` | ✅ Substituir por `??` |
| S3358 | Nested ternary | ❌ Requer refatoração manual |
| S6749 | Redundant fragment | ✅ Remover fragment |
| S6759 | Non-readonly props | ✅ Adicionar `readonly` |
| S3776 | Cognitive complexity | ❌ Requer extração de componentes |
| S6571 | `any` in union type | ✅ Remover redundância |

## Requisitos

- Node.js 18+
- Acesso ao SonarQube (localhost:9000)
- Token de autenticação configurado

## Integração com Workflows

Exemplo de uso em GitHub Actions:

```yaml
- name: Analyze with SonarQube Skill
  run: |
    npm install -g @felipeoff/sonarqube-analyzer
    sonarqube-analyzer \
      --project=my-project \
      --pr=${{ github.event.pull_request.number }} \
      --suggest-fixes
```
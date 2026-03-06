# Facebook Ads Manager Skill

Skill canonica para operar campanhas Meta Ads usando MCP tools.

Este pacote foi desenhado para:
- Cobrir 100% dos endpoints MCP disponiveis no servidor TypeScript.
- Evitar context overload com carregamento progressivo de referencias.
- Padronizar fluxos operacionais (planejamento, diagnostico, escala, audiencias).

## Estrutura

```text
facebook-ads-manager-skill/
  SKILL.md
  CHANGELOG.md
  references/
    tools-index.md
    safety-policy.md
    targeting-reference.md
    diagnostics-reference.md
    scaling-rules.md
    creative-frameworks.md
  workflows/
    01-plan-and-launch.md
    02-diagnose-and-optimize.md
    03-audience-crm-and-lookalike.md
    04-daily-operations.md
  checklists/
    preflight.md
    write-confirmation.md
    postflight.md
  examples/
    prompts.md
    response-templates.md
```

## Principios

1. Seguranca primeiro: criar objetos em `PAUSED` por padrao.
2. Nomes de tool exatos: sem aliases ou pseudo-tools.
3. Ler so o necessario: `SKILL.md` roteia; docs detalhadas ficam em `references/`.
4. Toda acao de escrita deve registrar contexto e plano de rollback.

## Uso recomendado

1. Leia `SKILL.md`.
2. Consulte `references/tools-index.md` para selecionar endpoints exatos.
3. Siga um workflow em `workflows/`.
4. Execute checklists em `checklists/`.

## Versao

Veja `CHANGELOG.md`.

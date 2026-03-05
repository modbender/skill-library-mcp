---
name: facebook-ads-manager
description: Orquestra planejamento, operacao e otimizacao de campanhas Meta Ads usando MCP tools com seguranca de escrita, cobertura completa de endpoints e carregamento progressivo de contexto.
metadata: {"openclaw":{"homepage":"https://github.com/williamneves/facebook-ads-manager-skill"},"version":"1.0.1","language":"pt-BR","compatibility":"opencode-openclaw"}
homepage: https://github.com/williamneves/facebook-ads-manager-skill
user-invocable: true
---

# Facebook Ads Manager

## Objetivo

Executar campanhas Meta Ads ponta a ponta com disciplina operacional:
- planejar,
- criar estruturas,
- diagnosticar performance,
- escalar com regras matematicas,
- operar audiencias e criativos,
- sempre com controle de risco.

## Como usar esta skill sem inflar contexto

1. Use este `SKILL.md` como roteador.
2. Carregue `{baseDir}/references/tools-index.md` para escolher tools exatas.
3. Carregue apenas a referencia adicional necessaria para a tarefa:
   - targeting -> `{baseDir}/references/targeting-reference.md`
   - diagnostico -> `{baseDir}/references/diagnostics-reference.md`
   - escala -> `{baseDir}/references/scaling-rules.md`
   - criativos -> `{baseDir}/references/creative-frameworks.md`
   - seguranca -> `{baseDir}/references/safety-policy.md`
4. Siga um workflow em `{baseDir}/workflows/`.
5. Execute checklists em `{baseDir}/checklists/` antes e depois de escrita.

## Regras nao negociaveis

- Criacoes devem usar status `PAUSED` por padrao.
- Nunca executar delete sem confirmacao explicita do usuario.
- Mudanca de budget agressiva e proibida sem validacao de risco.
- Nao inventar nome de tool: usar nomes exatos de `{baseDir}/references/tools-index.md`.
- Sempre tratar `act_id` no formato `act_<id>`.
- Em listas paginadas, seguir `paging.next` com `fetch_pagination_url`.

## Roteamento rapido por intencao

- Planejar conta e baseline -> `{baseDir}/workflows/01-plan-and-launch.md`
- Diagnosticar queda ou baixa entrega -> `{baseDir}/workflows/02-diagnose-and-optimize.md`
- Trabalhar CRM, custom e lookalike -> `{baseDir}/workflows/03-audience-crm-and-lookalike.md`
- Rotina diaria de operacao e escala -> `{baseDir}/workflows/04-daily-operations.md`

## Contrato de resposta

Para tarefas operacionais, responder com:
1. Objetivo e hipotese.
2. Plano de execucao com tools exatas.
3. Acoes feitas e IDs impactados.
4. Proximos passos e monitoramento.
5. Risco e rollback quando houver escrita.

## Anti-patterns

- Nao carregar todas as referencias de uma vez.
- Nao usar pseudo-tools (`update_x`, `delete_x`).
- Nao ativar campanha/adset/ad sem validacao minima.
- Nao otimizar por metrica unica ignorando funil.

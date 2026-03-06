---
name: memory-ops
description: "Consulta e persistência obrigatória da memória principal no
  PostgreSQL (Memory_openclaw + pgvector). Use quando for responder, delegar
  tarefas, consolidar contexto do usuário, registrar handoffs (ex.: Alfred,
  Prompt Improver), ou manter histórico operacional com auditoria."
---


# Memory Ops

## Protocolo obrigatório (sempre)
1. Consultar memória principal antes de responder ou delegar.
2. Responder/delegar com contexto recuperado.
3. Salvar contexto do prompt do usuário.
4. Salvar contexto de cada delegação enviada para agentes.
5. Registrar auditoria do ciclo (read/write status).

## Banco alvo
- Database: `Memory_openclaw`
- Extensão: `vector`
- Tabelas: usar `memories` + `memory_audit`.

## Regras de gravação
- Não salvar segredos sensíveis sem necessidade explícita.
- Priorizar fatos operacionais: objetivo, decisão, restrição, preferência, próximo passo.
- Sempre incluir metadados mínimos: `source`, `scope`, `agent`, `timestamp`, `kind`.

## SQL e esquema
- Criar/atualizar esquema em: `references/schema.sql`
- Queries de consulta em: `references/queries.sql`

## Auditoria obrigatória
- Registrar um evento em `memory_audit` por turno com:
  - `event_type`: `turn_cycle`
  - `read_ok`: true/false
  - `write_ok`: true/false
  - `details`: JSON com contagens e ids

## Handoff com agentes
Ao delegar para Alfred/Prompt Improver:
1. Salvar `kind=delegation_prompt` com prompt enviado.
2. Após retorno, salvar `kind=delegation_result` com resumo do output.
3. Só então consolidar resposta final ao usuário.

## Implementação de referência
- Script pronto: `scripts/memory_ops_template.sql`
- Se precisar adaptar dimensão de embedding, ajustar coluna `vector(1536)` conforme modelo.

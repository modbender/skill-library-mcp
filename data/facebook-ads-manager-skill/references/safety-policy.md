# Safety Policy

Politica de seguranca para operacoes write em Meta Ads.

## Regras obrigatorias

1. Criacao segura
- Criar campanha/adset/ad em `PAUSED` por padrao.
- Nao ativar imediatamente sem validar orcamento, tracking e criativo.

2. Confirmacao explicita
- Exigir confirmacao do usuario para:
  - `delete_audience`
  - `delete_object`
  - aumento agressivo de budget
  - alteracoes em massa

3. Controle de risco
- Fazer alteracoes incrementais e monitoradas.
- Sempre informar impacto esperado e plano de rollback.

4. Integridade de identificadores
- Ad account deve estar em formato `act_<id>`.
- Nao executar em IDs ambiguidos ou incompletos.

5. Transparencia operacional
- Antes de escrever: listar tools, parametros criticos e objetivo.
- Depois de escrever: devolver IDs alterados e estado final.

## Sequencia minima antes de escrita

1. Rodar `checklists/preflight.md`.
2. Obter baseline com insights/diagnostico.
3. Definir mudanca minima segura.
4. Registrar rollback.
5. Executar update/create/delete confirmado.

## Rollback padrao por objeto

- Campaign: `update_campaign` para restaurar budget/status anterior.
- Ad set: `update_adset` para restaurar budget/targeting/status.
- Ad: `update_ad` para status ou creative associada quando aplicavel.
- Audience: para deletes, rollback pode exigir recriacao manual.

# Workflow 03 - Audience CRM and Lookalike

Use para nutrir retargeting e expandir escala com audiencias quentes e similares.

## Objetivo

Operar ciclo de audiencias com segmentacao clara e baixa contaminacao.

## Passos

1. Ler estado atual de audiencias
- `list_custom_audiences`
- `list_lookalike_audiences`

2. Criar ou atualizar base CRM
- `create_custom_audience`
- `update_custom_audience_users`

3. Criar lookalike por objetivo
- `create_lookalike_audience`

4. Validar naming e higiene
- checar origem, janela e finalidade
- evitar sobreposicao excessiva entre pools

5. Aplicar em ad sets de teste
- `create_adset` (PAUSED) ou `update_adset`
- usar budgets controlados para aprendizagem

6. Higienizar ativos obsoletos (com confirmacao)
- `delete_audience`

## Saida esperada

- IDs das audiencias criadas/atualizadas.
- Segmentacao e hipotese de uso por estagio de funil.
- Plano de medicao de lift vs controle.

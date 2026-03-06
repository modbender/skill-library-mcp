# Workflow 02 - Diagnose and Optimize

Use quando ha queda de performance, custo alto, ou entrega fraca.

## Objetivo

Encontrar a causa raiz e aplicar a menor mudanca possivel com maior impacto.

## Passos

1. Ler funil por nivel
- `get_campaign_insights`
- `get_adset_insights`
- `get_ad_insights`

2. Inspecionar entidades com problema
- `get_campaign_by_id`
- `get_adset_by_id`
- `get_ad_by_id`

3. Verificar historico de mudancas
- `get_activities_by_adaccount`
- `get_activities_by_adset`

4. Classificar problema
- criativo (fadiga, CTR baixo)
- targeting (CPM alto, alcance ruim)
- estrutura (gasto concentrado)
- oferta/funil (CVR baixo)

5. Aplicar ajuste controlado
- `update_campaign`
- `update_adset`
- `update_ad`

6. Confirmar resultado inicial
- reler insights na mesma janela
- registrar risco e proximo checkpoint

## Saida esperada

- Diagnostico objetivo com evidencias.
- Acoes feitas, IDs impactados e rollback.
- Plano de monitoramento (janelas e metrica alvo).

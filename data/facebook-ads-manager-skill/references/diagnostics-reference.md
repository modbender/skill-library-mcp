# Diagnostics Reference

Framework operacional para identificar gargalos de performance.

## Tools principais

Insights por nivel:
- `get_adaccount_insights`
- `get_campaign_insights`
- `get_adset_insights`
- `get_ad_insights`

Leitura de entidades:
- `get_campaign_by_id`
- `get_adset_by_id`
- `get_ad_by_id`

Historico de alteracoes:
- `get_activities_by_adaccount`
- `get_activities_by_adset`

## Sequencia de diagnostico

1. Confirmar objetivo e janela de analise.
2. Ler conta/campanha/adset/ad (top-down).
3. Encontrar ponto de quebra do funil:
   - entrega (impressions/reach),
   - clique (CTR/CPC),
   - conversao (CPA/CVR),
   - monetizacao (ROAS).
4. Cruzar com atividades recentes para detectar causalidade.
5. Propor acao minima com hipotese clara.

## Sinais comuns

- CPM sobe e CTR cai -> fadiga criativa ou baixa relevancia.
- CPM estavel e CVR cai -> problema de oferta/landing/audiencia.
- Alcance baixo com budget alto -> restricao de targeting ou learning instavel.
- Gasto concentrado em poucos ads -> desequilibrio de entrega no adset.

## Acoes recomendadas

- Criativo: renovar angulo e hook quando sinais de fadiga aparecerem.
- Targeting: simplificar ou abrir gradualmente quando entrega trava.
- Estrutura: separar teste de escala para reduzir ruido de aprendizado.
- Budget: ajustar incrementalmente e acompanhar por ciclo completo.

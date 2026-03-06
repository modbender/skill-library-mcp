# Workflow 04 - Daily Operations

Use para rotina diaria de monitoramento, escala e manutencao.

## Objetivo

Manter crescimento com risco controlado e ritmo de iteracao constante.

## Rotina diaria

1. Ler painel de conta
- `get_adaccount_insights`
- `get_campaigns_by_adaccount`

2. Ler campanhas e ad sets priorizados
- `get_campaign_insights`
- `get_adsets_by_campaign`
- `get_adset_insights`

3. Ler ads mais relevantes
- `get_ads_by_campaign`
- `get_ad_insights`

4. Classificar por acao
- escalar
- manter
- corrigir
- pausar

5. Executar acoes pequenas
- `update_campaign`
- `update_adset`
- `update_ad`

6. Operar criativos quando necessario
- `list_ad_images`, `list_ad_videos`
- `get_ad_creatives_by_ad_id`
- `create_ad_creative`

7. Fechar dia com registro
- mudancas executadas
- impacto esperado
- checkpoint de revisao

## Paginacao

Quando resposta vier truncada, continuar leitura com:
- `fetch_pagination_url`

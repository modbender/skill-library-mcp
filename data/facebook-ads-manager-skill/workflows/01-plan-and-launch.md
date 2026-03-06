# Workflow 01 - Plan and Launch

Use quando o usuario quer sair de ideia para estrutura executavel.

## Objetivo

Construir campanha, ad sets e ads com risco controlado e rastreabilidade.

## Passos

1. Descobrir contexto da conta
- `list_ad_accounts`
- `get_details_of_ad_account`

2. Ler baseline de performance
- `get_adaccount_insights`
- `get_campaigns_by_adaccount`

3. Planejar targeting
- `search_interests`
- `search_interest_suggestions`
- `search_behaviors`
- `search_demographics`
- `search_geolocations`
- `validate_targeting`
- `get_reach_estimate`
- `get_delivery_estimate`
- `get_targeting_description`

4. Preparar criativos e assets
- `upload_ad_image` ou `upload_ad_video`
- `create_ad_creative`
- `get_ad_preview`

5. Criar estrutura em seguranca
- `create_campaign` com status `PAUSED`
- `create_adset` com status `PAUSED`
- `create_ad` com status `PAUSED`

6. Validar estado final
- `get_campaign_by_id`
- `get_adset_by_id`
- `get_ad_by_id`

## Saida esperada

- IDs da campaign, adset, ad e creative.
- Resumo do targeting criado.
- Plano de ativacao e metricas de monitoramento.

## Erros comuns

- Criar com status ativo sem validacao.
- Misturar muitos interesses no primeiro teste.
- Nao validar preview antes de publicar criativo.

# MCP Tools Index

Fonte canonica de nomes de endpoint para esta skill.

- Origem: `facebook-ads-mcp-server-ts/src/tools/*.ts`
- Cobertura esperada: 49 tools
- Regra: use nomes exatos, sem alias e sem pseudo-tools.

## Naming traps (evitar)

- Use `get_adaccount_insights` (nao `get_ad_account_insights`).
- Use `fetch_pagination_url` (nao `facebook_fetch_pagination_url`).
- Nao use placeholders como `update_x` ou `delete_x`.

## Account

Read:
- `list_ad_accounts`
- `get_details_of_ad_account`

## Activities

Read:
- `get_activities_by_adaccount`
- `get_activities_by_adset`

## Campaigns

Read:
- `get_campaign_by_id`
- `get_campaigns_by_adaccount`

Write:
- `create_campaign`
- `update_campaign`

## Ad Sets

Read:
- `get_adset_by_id`
- `get_adsets_by_ids`
- `get_adsets_by_adaccount`
- `get_adsets_by_campaign`

Write:
- `create_adset`
- `update_adset`

## Ads

Read:
- `get_ad_by_id`
- `get_ads_by_adaccount`
- `get_ads_by_campaign`
- `get_ads_by_adset`

Write:
- `create_ad`
- `update_ad`

## Creatives

Read:
- `get_ad_creative_by_id`
- `get_ad_creatives_by_ad_id`
- `get_ad_preview`

Write:
- `create_ad_creative`

## Insights

Read:
- `get_adaccount_insights`
- `get_campaign_insights`
- `get_adset_insights`
- `get_ad_insights`

## Targeting

Read:
- `validate_targeting`
- `get_reach_estimate`
- `get_delivery_estimate`
- `get_targeting_description`

## Search

Read:
- `search_interests`
- `search_interest_suggestions`
- `search_behaviors`
- `search_demographics`
- `search_geolocations`

## Audiences

Read:
- `list_custom_audiences`
- `list_lookalike_audiences`

Write:
- `create_custom_audience`
- `update_custom_audience_users`
- `create_lookalike_audience`
- `delete_audience`

## Media

Read:
- `list_ad_images`
- `list_ad_videos`

Write:
- `upload_ad_image`
- `upload_ad_video`

## Pagination

Read:
- `fetch_pagination_url`

## Delete (generic)

Write:
- `delete_object`

## Coverage check

- Total tools listadas: 49
- Objetivo: manter 49/49 alinhado com o servidor MCP.

## Manutencao rapida

Para verificar drift de endpoints:

```bash
cd facebook-ads-mcp-server-ts
rg -No 'server\.tool\(\s*"([^"]+)"' src/tools | sed -E 's/.*"([^"]+)"/\1/' | sort -u
```

# Targeting Reference

Guia curto para planejar e validar targeting sem inflar contexto.

## Tools principais

Pesquisa de opcoes:
- `search_interests`
- `search_interest_suggestions`
- `search_behaviors`
- `search_demographics`
- `search_geolocations`

Validacao e previsao:
- `validate_targeting`
- `get_reach_estimate`
- `get_delivery_estimate`
- `get_targeting_description`

## Fluxo recomendado

1. Descobrir segmentos candidatos via tools de search.
2. Montar `targeting_spec` enxuto com 1-3 hipoteses por vez.
3. Validar com `validate_targeting`.
4. Estimar tamanho com `get_reach_estimate`.
5. Projetar entrega/custo com `get_delivery_estimate`.
6. Gerar descricao legivel com `get_targeting_description` para auditoria.

## Heuristicas praticas

- Evitar empilhar interesses demais no mesmo ad set.
- Controlar overlap entre ad sets para reduzir canibalizacao.
- Manter coerencia entre criativo, promessa e publico.
- Testar geos separadamente quando houver diferenca de CPM/CVR.

## Alertas

- Targeting muito amplo pode degradar eficiencia em funis frios.
- Targeting muito restrito pode travar entrega e encarecer CPM.
- Sempre revalidar reach/delivery quando budget mudar materialmente.

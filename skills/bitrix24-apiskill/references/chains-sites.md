# Chains: sites

## 1) Site and page bootstrap

1. `landing.site.add`
2. `landing.landing.add`
3. `landing.block.getList`

## 2) Content update flow

1. `landing.landing.getList`
2. `landing.landing.update`
3. optional block-level card update methods

## 3) Controlled cleanup

1. `landing.landing.getList`
2. validate dependencies/publication state
3. `landing.landing.delete` or `landing.site.delete` with destructive confirmation

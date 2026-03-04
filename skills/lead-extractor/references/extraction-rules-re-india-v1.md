# Extraction Rules RE-India v1

Use these rules for WhatsApp broker-group style messages observed in real chat dumps.

## 1. Candidate Detection

Treat a message as a listing/lead candidate when at least one property signal and one transaction signal are present.

Property signals:
- `bhk`, `studio`, `shop`, `showroom`, `office`, `warehouse`, `pg`, `flat`, `carpet`

Transaction signals:
- `sale`, `outright`, `rent`, `lease`, `leave and licence`, `l & l`, `asking`

## 2. Phone Extraction

Accept these phone formats and normalize to `+91XXXXXXXXXX`:
- `+91 98205 82462`
- `98200 78845`
- `9773226679`

Rules:
- remove spaces, dashes, and punctuation
- if 10-digit and starts with `[6-9]`, prefix `+91`
- ignore obvious non-phone numeric tokens (`sqft`, `psf`, `cr`, `lakh`)

## 3. Multi-line Record Stitching

Many listings span multiple lines after the first timestamp line.

Keep collecting continuation lines into the same candidate while they contain supportive fields:
- area (`sqft`, `carpet`, `cpt`)
- price (`cr`, `lakh`, `k`, `psf`)
- location fragments (`near`, `off`, locality aliases)
- contact details

## 4. Deal-Type Classification

Map message to `deal_type`:
- `sale`: contains `sale`, `for sale`
- `outright`: contains `outright`
- `rent`: contains `rent`
- `lease`: contains `lease`, `leave and licence`, `l&l`, `l & l`
- fallback `unknown`

## 5. Asset-Class Classification

Map to `asset_class`:
- `commercial`: contains `office`, `showroom`, `shop`, `retail`, `commercial`
- `pg`: contains `pg`, `paying guest`
- `residential`: contains `bhk`, `flat`, `furnished`, `family`
- `mixed`: if both residential and commercial cues exist
- fallback `unknown`

## 6. Price Parsing Guards

Do not treat every numeric token as total budget.

Priority:
1. `psf` or `per sq ft` -> `price_basis=per_sqft`
2. `rent` / `lease` context -> `price_basis=monthly_rent` unless token explicitly marked as deposit
3. `deposit` context -> `price_basis=deposit`
4. otherwise -> `price_basis=total`

Examples:
- `60K psf` -> rate, not total deal value
- `3.5 Lakh rent` -> monthly rent
- `4.25 Cr` -> total sale value

## 7. Area Extraction

Extract `area_sqft` from tokens near:
- `sqft`, `sq ft`, `carpet`, `rera carpet`, `cpt`

Set `area_basis`:
- `carpet`, `rera_carpet`, `builtup`, fallback `unknown`

## 8. Low-Value / System Message Rejection

Reject candidate when message is clearly operational noise:
- group creation/add notices
- end-to-end encryption notice
- `<Media omitted>` with no supportive text

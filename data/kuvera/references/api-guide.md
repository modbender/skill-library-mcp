# Kuvera CLI API Guide

## Commands Reference

### `kuvera-cli market`
Shows a combined market overview with gold prices, USD/INR rate, and key mutual fund category returns.

### `kuvera-cli gold`
Returns current gold buy and sell prices in INR per gram, with GST breakdown.

### `kuvera-cli usd`
Returns the live USD/INR exchange rate from Kuvera's forex partner.

### `kuvera-cli categories`
Lists all 29 mutual fund categories with returns across time periods:
- 1 week, 1 month, 3 months, 6 months, 1 year, 3 years, 5 years, 10 years, since inception

### `kuvera-cli fund <code1,code2,...>`
Looks up detailed info for one or more mutual fund schemes by their Kuvera code.
Returns: name, ISIN, category, fund house, NAV, AUM, expense ratio, returns, fund manager.

Example codes: `LFAG-GR`, `KO178D-DP`, `PLPL56-GR`

### `kuvera-cli top <type>`
Shows top funds by activity. Types: `bought`, `sold`, `watched`.

### `kuvera-cli login <email> <password>`
Authenticates with Kuvera and stores a JWT token for accessing user-specific data.

### `kuvera-cli user`
Shows the logged-in user's profile and portfolio information.
Requires prior login.

## Error Handling

- If `kuvera-cli user` returns "Not logged in", run `kuvera-cli login` first.
- If login fails, verify email/password are correct for kuvera.in.
- Token expiry: re-run `kuvera-cli login` if authenticated commands fail.

# Auth Traps

## Bearer Token

- `Authorization: Bearer:token` (con dos puntos) = INCORRECTO, es `Bearer token` (espacio)
- Token con newline al final (copy-paste) = 401 misterioso
- Bearer en query param `?token=x` funciona en algunos APIs pero se loguea en access logs
- Token hardcodeado en código se commitea a git — siempre env var

## OAuth

- `state` parameter ignorado = vulnerable a CSRF — siempre validar
- Token refresh sin mutex = race condition, múltiples refreshes simultáneos
- Access token expirado + refresh token expirado = usuario debe re-login (no solo refresh)
- `offline_access` scope olvidado = no hay refresh token

## JWT

- Verificar solo firma sin validar `exp` = tokens eternos aceptados
- `exp` en segundos, no milliseconds — `Date.now()` / 1000
- `aud` claim ignorado = token para otro servicio aceptado
- Algorithm confusion: token dice `alg: none` y servidor acepta sin firma

## API Keys

- API key en URL se cachea por proxies/CDNs — expuesto en logs
- Ratelimit por API key + key compartida entre clientes = límite compartido
- Key rotation sin período de gracia = downtime
- API key sin expiración + leak = acceso permanente

## Session

- Session ID predecible = session hijacking
- Session no invalidada en logout = reutilizable
- Session timeout muy largo + shared computer = riesgo
- Cookies sin `Secure` flag enviadas en HTTP = interceptables

## Headers

- `X-API-Key` vs `Api-Key` vs `apikey` — cada API diferente, case-sensitive
- Auth header no propagado a redirects por defecto — 302 pierde auth
- Preflight CORS no incluye auth headers — CORS error confuso si backend espera auth en OPTIONS

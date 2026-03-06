# Resilience Traps

## Retry Logic

- Retry en POST/PUT sin idempotency key = duplicados
- Retry inmediato en 429 ignora `Retry-After` header = ban más largo
- Retry en 400 Bad Request = desperdicio, request es inválido
- Exponential backoff sin jitter = thundering herd, todos reintentan al mismo tiempo

## Timeouts

- Connect timeout muy alto = threads bloqueados esperando DNS/TCP
- Read timeout incluye tiempo de procesamiento del server — no solo red
- Sin timeout = request colgado para siempre si server no responde
- Timeout en cliente no cancela request en server — sigue procesando

## Circuit Breaker

- Threshold muy bajo = circuit abre por errores transitorios normales
- Half-open sin límite de requests = flood al server recovering
- Circuit por host, no por endpoint = un endpoint malo afecta todos
- Sin métricas de circuit state = debugging imposible

## Rate Limiting

- Rate limit client-side sin sincronización = exceder límite con múltiples instancias
- Contador local + distributed system = cada nodo tiene su propio contador
- Rate limit solo en 429 response = ya excediste el límite
- Backoff después de 429 muy corto = ban extendido

## Error Handling

- Catch genérico que silencia todos los errores = bugs invisibles
- Retry que loguea en cada intento = log flood en outage
- Error en fallback handler = crash, no graceful degradation
- Async error sin handler = unhandled rejection, proceso puede morir

## Connection Pooling

- Pool exhausted = requests encolados o rechazados
- Conexión stale en pool = primera request falla, siguiente OK
- Pool size muy grande = demasiadas conexiones al server
- Sin health check de conexiones = conexiones muertas en pool

# Webhook Traps

## Delivery

- Webhook timeout 5-30s — proceso largo = timeout = retry = duplicados
- Provider retry = mismo evento múltiples veces — handler DEBE ser idempotente
- Orden de entrega no garantizado — event B puede llegar antes que A
- IP del provider cambia — whitelist por IP se rompe

## Verification

- Signature con timestamp — replay attack si no verificas que timestamp es reciente
- HMAC comparison sin constant-time = timing attack posible
- Signature en header custom (`X-Hub-Signature`) no estándar — cada provider diferente
- Body modificado por middleware (parsing) antes de verificar = signature inválida

## Processing

- Response 200 antes de procesar = provider cree que OK pero proceso falla después
- Response 500 = provider reintenta = procesas dos veces si primer intento sí funcionó
- Webhook queue llena = nuevos eventos perdidos
- Async processing sin durabilidad = crash = evento perdido

## Payload

- Schema change sin aviso = parser falla en producción
- Campos nuevos ignorados si parser es strict
- Campos removed que tu código espera = null pointer / undefined
- Encoding issues — payload JSON con caracteres especiales mal encoded

## Development

- Localhost no es accesible para provider — necesitas tunnel (ngrok)
- Tunnel URL cambia cada sesión — reconfigurar webhook cada vez
- Provider no tiene retry manual — debes esperar al siguiente evento
- Logs de webhook en provider expiran rápido — debugging difícil

## Security

- Endpoint público sin verificación = cualquiera puede enviar eventos fake
- Secret compartido entre ambientes = staging puede afectar producción
- Webhook handler que hace calls externos = SSRF potencial
- Error message detallado en response = info leak al provider/attacker

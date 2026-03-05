# Integrações - Pastorini API

## Typebot

Conecta ao Typebot para fluxos de conversação automatizados.

### Configurar

```bash
POST /api/instances/:id/integrations/typebot
```

```json
{
  "enabled": true,
  "url": "https://typebot.seudominio.com",
  "typebot": "atendimento-vendas",
  "expire": 30,
  "keywordFinish": "#sair",
  "keywordRestart": "#reiniciar",
  "unknownMessage": "Não entendi. Digite #sair para atendente.",
  "stopBotFromMe": true,
  "debounceTime": 3000,
  "triggerType": "keyword",
  "triggerOperator": "contains",
  "triggerValue": "oi|olá|bom dia|boa tarde"
}
```

**Parâmetros:**
- `expire` — minutos para expirar sessão (0 = não expira)
- `triggerType` — `all`, `keyword` ou `none`
- `triggerOperator` — `contains`, `equals`, `startsWith`, `endsWith`, `regex`
- `debounceTime` — agrupa mensagens rápidas (ms)

### Obter Configuração

```bash
GET /api/instances/:id/integrations/typebot
```

## Chatwoot

Conecta ao Chatwoot para atendimento humano.

### Configurar

```bash
POST /api/instances/:id/integrations/chatwoot
```

```json
{
  "enabled": true,
  "url": "https://chatwoot.seudominio.com",
  "accountId": "1",
  "token": "seu_api_access_token",
  "nameInbox": "WhatsApp - Vendas",
  "autoCreateInbox": true,
  "webhookUrl": "https://api.seudominio.com",
  "signMsg": true,
  "signDelimiter": "\n\n",
  "reopenConversation": true,
  "conversationPending": false,
  "mergeBrazilContacts": true
}
```

**Parâmetros:**
- `signMsg` — assinar mensagens com nome do agente
- `reopenConversation` — reabrir ao receber nova mensagem
- `mergeBrazilContacts` — mesclar contatos com/sem 9º dígito

### Obter Configuração

```bash
GET /api/instances/:id/integrations/chatwoot
```

### Webhook Chatwoot

Endpoint que recebe mensagens do Chatwoot (configurado automaticamente):

```bash
POST /api/instances/:id/chatwoot/webhook
```

## Webhook Genérico

### Configurar

```bash
POST /api/instances/:id/webhook
```

```json
{
  "url": "https://seu-servidor.com/webhook",
  "enabled": true,
  "events": ["messages", "status", "message_reaction", "group_update"]
}
```

### Obter Configuração

```bash
GET /api/instances/:id/webhook
```

### Headers Recebidos

```
Content-Type: application/json
X-Instance-ID: minha-instancia
X-Event-Type: messages | message_status | message_reaction | ...
```

## WebSocket

Alternativa ao webhook com conexão persistente.

### Configurar

```bash
POST /api/instances/:id/websocket
```

```json
{
  "url": "wss://seu-servidor.com/ws",
  "enabled": true,
  "events": ["messages", "connection", "qr"]
}
```

### Obter Configuração

```bash
GET /api/instances/:id/websocket
```

# Mensagens Interativas - Pastorini API

## Botões (send-buttons)

Até 3 botões por mensagem. Funciona em Web, iOS e Android.

```bash
POST /api/instances/:id/send-buttons
```

### Tipos de Botões

```json
// Resposta rápida
{"type": "quick_reply", "displayText": "Sim", "id": "btn_sim"}

// URL
{"type": "cta_url", "displayText": "Visitar Site", "url": "https://google.com"}

// Ligação
{"type": "cta_call", "displayText": "Ligar", "phoneNumber": "+5511999999999"}

// Copiar código (PIX, cupom)
{"type": "cta_copy", "displayText": "📋 Copiar PIX", "copyCode": "00020126..."}
```

### Exemplo Completo

```json
{
  "jid": "5511999999999@s.whatsapp.net",
  "text": "Como posso ajudar?",
  "footer": "Atendimento 24h",
  "buttons": [
    {"type": "quick_reply", "displayText": "🛒 Comprar", "id": "comprar"},
    {"type": "quick_reply", "displayText": "🔧 Suporte", "id": "suporte"},
    {"type": "cta_url", "displayText": "🌐 Site", "url": "https://loja.com"}
  ]
}
```

## Lista (send-list)

Menu com seções organizadas. Ideal para muitas opções.

```bash
POST /api/instances/:id/send-list
```

```json
{
  "jid": "5511999999999@s.whatsapp.net",
  "title": "Menu Principal",
  "text": "Escolha uma opção:",
  "footer": "Delivery 24h",
  "buttonText": "Ver Opções",
  "sections": [
    {
      "title": "🍔 Lanches",
      "rows": [
        {"title": "X-Burger", "description": "R$ 25,00", "rowId": "xburger"},
        {"title": "X-Bacon", "description": "R$ 30,00", "rowId": "xbacon"}
      ]
    },
    {
      "title": "🥤 Bebidas",
      "rows": [
        {"title": "Refrigerante", "description": "R$ 6,00", "rowId": "refri"},
        {"title": "Suco", "description": "R$ 8,00", "rowId": "suco"}
      ]
    }
  ]
}
```

## Carrossel (send-carousel)

Cards deslizantes com imagem e botões. **Só funciona no celular!**

```bash
POST /api/instances/:id/send-carousel
```

```json
{
  "jid": "5511999999999@s.whatsapp.net",
  "title": "🛍️ Ofertas",
  "body": "Confira nossos produtos!",
  "footer": "Loja Virtual",
  "cards": [
    {
      "imageUrl": "https://exemplo.com/img1.jpg",
      "title": "📱 iPhone 15",
      "body": "256GB - Titânio",
      "footer": "R$ 8.999",
      "buttons": [
        {"id": "comprar_iphone", "title": "🛒 Comprar"},
        {"id": "info_iphone", "title": "📋 Detalhes"}
      ]
    },
    {
      "imageUrl": "https://exemplo.com/img2.jpg",
      "title": "💻 MacBook",
      "body": "M3 - 256GB SSD",
      "footer": "R$ 12.499",
      "buttons": [
        {"id": "comprar_mac", "title": "🛒 Comprar"}
      ]
    }
  ]
}
```

## Enquete (send-poll)

Votação interativa. Funciona em celular e desktop.

```bash
POST /api/instances/:id/send-poll
```

```json
{
  "jid": "5511999999999@s.whatsapp.net",
  "name": "Qual sua linguagem favorita?",
  "options": ["JavaScript", "Python", "TypeScript", "Go"],
  "selectableCount": 1
}
```

- `selectableCount: 1` = escolha única
- `selectableCount: 0` = múltipla escolha

## Produtos do Catálogo

### Múltiplos produtos (send-products)

```json
{
  "jid": "5511999999999@s.whatsapp.net",
  "productIds": ["produto_001", "produto_002"],
  "title": "Ofertas da Semana",
  "body": "Produtos em promoção!"
}
```

### Produto único (send-product)

```json
{
  "jid": "5511999999999@s.whatsapp.net",
  "productId": "produto_001",
  "body": "Olha esse produto!",
  "footer": "Frete grátis"
}
```

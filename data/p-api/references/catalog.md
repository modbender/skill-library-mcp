# Catálogo de Produtos - Pastorini API

Requer conta WhatsApp Business com catálogo configurado.

## Listar Produtos

```bash
GET /api/instances/:id/catalog?limit=100&cursor=abc123
```

Resposta:
```json
{
  "success": true,
  "productsCount": 15,
  "products": [
    {
      "id": "produto_001",
      "name": "Camiseta Básica",
      "description": "100% algodão",
      "price": 4990,
      "currency": "BRL",
      "imageUrl": "https://..."
    }
  ],
  "nextPageCursor": "abc123..."
}
```

**Nota:** Preço em centavos (4990 = R$ 49,90)

## Ver Catálogo de Outro Número

```bash
GET /api/instances/:id/catalog/:number
# Exemplo: GET /api/instances/minha-instancia/catalog/5511888888888
```

## Criar Produto

```bash
POST /api/instances/:id/catalog/product
```

```json
{
  "name": "Camiseta Premium",
  "description": "100% algodão, várias cores",
  "price": 7990,
  "currency": "BRL",
  "imageUrl": "https://exemplo.com/camiseta.jpg",
  "url": "https://loja.com/camiseta",
  "retailerId": "SKU-001",
  "isHidden": false
}
```

## Atualizar Produto

```bash
PUT /api/instances/:id/catalog/product/:productId
```

```json
{
  "price": 5990,
  "description": "Promoção! 25% OFF"
}
```

## Remover Produto

```bash
DELETE /api/instances/:id/catalog/product/:productId
```

## Coleções (Categorias)

### Listar Coleções

```bash
GET /api/instances/:id/catalog/collections
```

### Criar Coleção

```bash
POST /api/instances/:id/catalog/collection
```

```json
{
  "name": "Promoções de Verão",
  "productIds": ["produto_001", "produto_002", "produto_003"]
}
```

### Remover Coleção

```bash
DELETE /api/instances/:id/catalog/collection/:collectionId
```

Os produtos não são deletados, apenas removidos da coleção.

## Enviar Produtos

### Múltiplos Produtos

```bash
POST /api/instances/:id/send-products
```

```json
{
  "jid": "5511999999999@s.whatsapp.net",
  "productIds": ["produto_001", "produto_002"],
  "title": "Ofertas da Semana",
  "body": "Confira!",
  "footer": "Frete grátis"
}
```

### Produto Único

```bash
POST /api/instances/:id/send-product
```

```json
{
  "jid": "5511999999999@s.whatsapp.net",
  "productId": "produto_001",
  "body": "Olha esse produto!",
  "footer": "Frete grátis"
}
```

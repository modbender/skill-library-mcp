---
name: omie
description: "Omie ERP integration via API. Manage clients, products, orders, invoices (NF-e), financials (contas a receber/pagar), and stock. Use when users ask about ERP data, financials, orders, invoices, stock, or clients from Omie. Also handles webhooks for real-time events."
---

# Omie ERP Skill

Integração com o Omie ERP via API REST.

## Setup

Requer variáveis de ambiente:
```bash
export OMIE_APP_KEY="your_app_key_here"
export OMIE_APP_SECRET="your_app_secret_here"
```

## API Client

Use o script Python para todas as operações:

```bash
python3 skills/omie/scripts/omie_client.py <command> [args]
```

### Comandos disponíveis

#### Clientes
```bash
python3 scripts/omie_client.py clientes_listar [pagina] [por_pagina]
python3 scripts/omie_client.py clientes_buscar cnpj_cpf=00.000.000/0001-00
python3 scripts/omie_client.py clientes_buscar codigo=1234567
python3 scripts/omie_client.py clientes_detalhar codigo=1234567
```

#### Produtos
```bash
python3 scripts/omie_client.py produtos_listar [pagina] [por_pagina]
python3 scripts/omie_client.py produtos_detalhar codigo=1234567
```

#### Pedidos de Venda
```bash
python3 scripts/omie_client.py pedidos_listar [pagina] [por_pagina]
python3 scripts/omie_client.py pedidos_detalhar numero=1234
python3 scripts/omie_client.py pedidos_status numero=1234
```

#### Financeiro
```bash
python3 scripts/omie_client.py contas_receber [pagina] [por_pagina]
python3 scripts/omie_client.py contas_pagar [pagina] [por_pagina]
python3 scripts/omie_client.py resumo_financeiro
```

#### Notas Fiscais
```bash
python3 scripts/omie_client.py nfe_listar [pagina] [por_pagina]
python3 scripts/omie_client.py nfe_detalhar numero=1234
```

#### Estoque
```bash
python3 scripts/omie_client.py estoque_posicao [pagina] [por_pagina]
python3 scripts/omie_client.py estoque_produto codigo=1234567
```

## Webhook

O Omie pode enviar eventos para um endpoint HTTP. Configurar em:
Omie → Configurações → Integrações → Webhooks

Eventos suportados:
- `pedido.incluido` / `pedido.alterado`
- `nfe.emitida` / `nfe.cancelada`
- `financas.recebido` / `financas.pago`
- `cliente.incluido` / `cliente.alterado`

Para iniciar o receptor de webhooks:
```bash
python3 scripts/omie_webhook.py --port 8089
```

## Limites da API
- **Rate limit:** 3 requisições/segundo por app
- **Paginação:** máximo 500 registros por página
- **Timeout:** 30 segundos

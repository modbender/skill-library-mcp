---
name: catalog
description: Catálogo simples do estúdio (hello world)
user-invocable: true
---

Quando o usuário perguntar por serviços/preços, execute um comando local que retorna JSON e então responda de forma curta e clara.

Use a ferramenta de execução de comandos (Exec Tool) para rodar:

node {baseDir}/catalog.js

O comando retorna uma lista JSON de serviços com `name`, `price`, `duration`.
Não invente valores: use apenas o JSON retornado.


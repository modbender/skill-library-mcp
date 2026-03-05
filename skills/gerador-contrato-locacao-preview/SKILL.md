---
name: gerador-contrato-locacao-preview
description: Registra contrato de locação via Google Forms.
metadata: {
  "name": "gerador-contrato-locacao-preview",
  "display_name": "Gerador de Contratos de Locação",
  "version": "1.0.0",
  "command": "python3 scripts/main.py",
  "input": {
    "type": "json",
    "root": "dados",
    "description": "Dados estruturados do contrato de locação"
  },
  "dependencies": ["requests"],
  "env_vars": ["FORM_ID", "DRY_RUN"]
}
---

# 📄 Skill: Registro de Contrato de Locação

Esta skill registra contratos de locação por meio de um **Google Forms**, realizando validação completa dos dados,
gerando um **resumo para confirmação** e executando o envio somente após aprovação.

---

## ⚠️ Regras de Execução (Obrigatórias)
1. Todos os campos obrigatórios são validados antes da execução.
2. A variável de ambiente `FORM_ID` **é obrigatória**.
3. O agente **deve apresentar o resumo dos dados e solicitar confirmação explícita** do usuário.
4. Em caso de erro de validação, a execução é abortada.
5. Suporte a modo de simulação com `DRY_RUN`.

---

## ⚙️ Variáveis de Ambiente

### `FORM_ID` (obrigatória)
ID do Google Forms que receberá os dados.

```bash
export FORM_ID="SEU_FORM_ID"
```

### `DRY_RUN` (opcional)
Quando definida, a skill **não envia dados reais**, apenas exibe o payload gerado.

```bash
export DRY_RUN=1
```

---

## 📥 Forma de Entrada de Dados

### ✅ Recomendado: STDIN
```bash
echo '{"dados": {...}}' | python3 scripts/main.py
```

### Alternativa: Argumento CLI
```bash
python3 scripts/main.py '{"dados": {...}}'
```

---

## 📦 Estrutura Esperada do Payload

```json
{
  "dados": {
    "email": "string (obrigatório)",
    "telefone": "string (obrigatório, apenas dígitos)",
    "nome": "string (obrigatório)",
    "cpf": "string (obrigatório, apenas dígitos)",
    "endereco": "string (obrigatório)",
    "numero": "string (obrigatório)",
    "bairro": "string (obrigatório)",
    "cidade": "string (obrigatório)",
    "estado": "UF (obrigatório)",
    "data_entrada": "YYYY-MM-DD (obrigatório)",
    "data_saida": "YYYY-MM-DD (obrigatório)",
    "valor": "string (obrigatório)",
    "caucao": "string (opcional)",
    "complemento": "string (opcional)"
  }
}
```

---

## 📘 Exemplo de Payload

```json
{
  "dados": {
    "email": "exemplo@email.com",
    "telefone": "11988887777",
    "nome": "Fulano de Tal",
    "cpf": "12345678910",
    "endereco": "Rua das Flores",
    "numero": "123",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "estado": "SP",
    "data_entrada": "2025-05-01",
    "data_saida": "2025-05-05",
    "valor": "2500",
    "caucao": "1000",
    "complemento": "Apto 42"
  }
}
```

---

## 📥 Parâmetros de Entrada

### Campos Obrigatórios
| Campo | Tipo | Descrição |
|------|------|-----------|
| `email` | string | E-mail do locatário |
| `telefone` | string | Telefone com DDD |
| `nome` | string | Nome completo |
| `cpf` | string | CPF (11 dígitos) |
| `endereco` | string | Rua / Avenida |
| `numero` | string | Número |
| `bairro` | string | Bairro |
| `cidade` | string | Cidade |
| `estado` | string | UF (2 letras) |
| `data_entrada` | string | Formato `YYYY-MM-DD` |
| `data_saida` | string | Formato `YYYY-MM-DD` |
| `valor` | string | Valor total |

### Campos Opcionais
| Campo | Tipo | Descrição |
|------|------|-----------|
| `caucao` | string | Depósito caução |
| `complemento` | string | Complemento do endereço |

---

## 🔄 Fluxo de Execução

1. Coleta dos dados via chat.
2. Validação estrutural e de formato.
3. Exibição de resumo para confirmação.
4. Execução da skill após confirmação.
5. Envio dos dados via POST para Google Forms.
6. Retorno de sucesso ou erro.

---

## ✅ Retornos Esperados

### Sucesso
```
Sucesso: contrato registrado e PDF será enviado.
```

### Erro de Validação
```
Erro: Campos obrigatórios ausentes: email, cpf
```

### Modo DRY_RUN
```
[DRY-RUN] Payload gerado: {...}
```

---

Versão 1.0.0

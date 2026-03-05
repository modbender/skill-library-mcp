---
name: contrato-locacao-broa
description: Registra contrato no Google Forms.
metadata: {
  "name": "contrato-locacao-broa",
  "display_name": "Gerador de Contratos",
  "version": "1.1.0",
  "command": "python3 main.py",
  "dependencies": ["requests"]
}
---

# Skill: Registro de Contrato de Locação (Google Forms)

## 📝 Descrição
Esta skill automatiza o registro de contratos de locação imobiliária. Ela envia os dados coletados pelo agente para um Google Form, que por sua vez dispara um Google Apps Script responsável por:
1. Gerar um contrato em PDF baseado em um template do Google Docs.
2. Calcular automaticamente a **Permanência** (em dias) e o **Valor da Diária**.
3. Formatar valores monetários para o padrão brasileiro (R$).
4. Enviar o PDF assinado via e-mail para o locatário e administradores.

## 🛠 Parâmetros de Entrada
O agente deve extrair os seguintes dados da conversa. Todos são obrigatórios, exceto onde indicado.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `email` | string | E-mail do locatário (destino do PDF). | `exemplo@email.com` |
| `telefone` | string | Telefone com DDD (apenas números). | `16988035666` |
| `nome` | string | Nome completo do locatário. | `David Evaristo` |
| `cpf` | string | CPF (apenas números). | `40544335880` |
| `endereco` | string | Nome da rua/avenida. | `Rua Bichara Damha` |
| `numero` | string | Número do imóvel. | `360` |
| `bairro` | string | Bairro do imóvel. | `Sao Carlos 2` |
| `cidade` | string | Cidade. | `Sao Carlos` |
| `estado` | string | UF do estado (2 letras). | `SP` |
| `data_entrada` | string | Início da locação (Formato: **YYYY-MM-DD**). | `2026-02-10` |
| `data_saida` | string | Fim da locação (Formato: **YYYY-MM-DD**). | `2026-02-15` |
| `valor` | string | Valor total da estadia. | `2000` |
| `caucao` | string | Valor do depósito/caução (Opcional). | `200` |
| `complemento` | string | Apto, bloco, etc. (Opcional). | `Casa A` |

## 🤖 Instruções para a IA (System Prompt)
- **Formatação de Data:** Sempre converta datas relativas ("próximo domingo") ou em formato brasileiro ("10/02/26") para o padrão `YYYY-MM-DD`.
- **Validação:** Não execute a skill se o e-mail ou CPF estiverem ausentes.
- **Confirmação:** Antes de enviar, apresente um resumo: *"Confirmando: Contrato para David Evaristo, de 10/02 a 15/02, total R$ 2.000,00. Posso gerar?"*
- **Pós-execução:** Informe ao usuário que o contrato chegará no e-mail em instantes.

## ⚙️ Fluxo de Dados


1. O agente chama a função `fill_rental_form`.
2. A função realiza um `POST` para o endpoint `/formResponse` do Google.
3. O Google aciona o gatilho `onFormSubmit`.
4. O documento é gerado e o e-mail enviado.

---
name: openclaw-skill-debugger
description: "Identifica e resolve problemas comuns em AgentSkills do OpenClaw,
  incluindo: (1) Falhas de instalação via ClawHub, (2) Inconsistências de
  configuração (ex: paths absolutos), (3) Dependências ausentes ou mal
  documentadas, e (4) Erros de execução de scripts ou integração com APIs.
  Fornece um guia passo a passo para depurar e validar skills, garantindo sua
  correta operação em ambientes de quarentena ou produção. Use esta skill quando
  uma AgentSkill não se comporta como esperado ou você precisa auditar seu
  código."
---


# OpenClaw Skill Debugger

## Visão Geral

Esta skill foi projetada para auxiliar na depuração e análise de problemas em `AgentSkills` do OpenClaw. Ela fornece ferramentas e um fluxo de trabalho estruturado para identificar a causa raiz de falhas de instalação, erros de execução, problemas de dependência e outras inconsistências que podem impedir o funcionamento correto de uma skill.

## Workflow de Uso

Ao depurar uma skill, siga estas etapas:

1.  **Entender o Problema**: Comece coletando o máximo de informações possível sobre o erro: mensagens de erro, logs, passos para reproduzir o problema e o comportamento esperado da skill.
2.  **Verificação Inicial**: Use os scripts de verificação rápida e consulte os documentos de referência para identificar problemas comuns.
    *   **Caminhos Absolutos/Hardcoded**: Execute `scripts/check-hardcoded-paths.sh <caminho-da-skill>` para procurar paths que podem causar problemas de portabilidade.
    *   **Dependências**: Consulte `references/common-skill-issues.md` e execute `scripts/verify-dependencies.sh <caminho-da-skill>` (se implementado) para confirmar que todos os pré-requisitos estão satisfeitos e corretamente documentados.
    *   **Scripts Auxiliares Ausentes**: Verifique se todos os scripts referenciados no `SKILL.md` da skill alvo existem no seu diretório `scripts/`.
3.  **Análise Detalhada**: Se as verificações iniciais não resolverem, siga o `references/debug-workflow.md` para uma análise mais aprofundada, incluindo a revisão do código-fonte da skill, logs do OpenClaw e testes em ambiente isolado.
4.  **Correção e Validação**: Implemente as correções necessárias e teste a skill exaustivamente para garantir que o problema foi resolvido.

## Scripts

### `scripts/check-hardcoded-paths.sh`

Este script recebe o caminho para uma skill e varre seus arquivos em busca de padrões que indicam o uso de caminhos absolutos ou "hardcoded" (ex: `/home/usuario/`, `/var/`, `/etc/`).
*   **Uso:** `bash scripts/check-hardcoded-paths.sh <caminho-da-skill-a-depurar>`

### `scripts/verify-dependencies.sh` (TODO)

**(Ainda a ser implementado)** Este script verificará se as dependências listadas no `SKILL.md` da skill alvo estão instaladas no ambiente.

## Referências

### `references/common-skill-issues.md`

Este documento detalha problemas comuns encontrados no desenvolvimento e execução de skills do OpenClaw, como:
*   Caminhos absolutos em scripts.
*   Scripts auxiliares referenciados que não existem.
*   Declaração incorreta ou ausente de dependências.
*   Riscos e precauções ao usar `npx` para instalação (execução de código remoto).
*   Problemas de integração com telemetria (ex: falhas na emissão de logs OTLP como discutido no Issue #18794).

### `references/debug-workflow.md`

Este documento fornece um fluxo de trabalho estruturado para depurar skills, desde a reprodução do problema até a identificação da causa raiz e a aplicação da correção. Inclui etapas como:
*   Isolamento do problema.
*   Revisão de logs do sistema e da skill.
*   Uso de ambientes de quarentena.
*   Técnicas de inspeção de código.


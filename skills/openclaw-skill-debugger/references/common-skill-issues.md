# Problemas Comuns em OpenClaw AgentSkills

Este documento detalha os problemas mais frequentes encontrados no desenvolvimento e execução de AgentSkills do OpenClaw, juntamente com as causas prováveis e as abordagens de depuração.

## 1. Caminhos Absolutos (Hardcoded Paths)

### Descrição
O uso de caminhos de arquivo ou diretório absolutos (ex: `/home/usuario/meu-projeto/`, `C:\Users\...`) diretamente no código de uma skill torna-a não portátil. Quando a skill é movida para outro ambiente ou usuário, esses caminhos deixam de ser válidos, causando erros de "arquivo não encontrado" ou acesso negado.

### Causas Comuns
*   Desenvolvimento em um ambiente específico sem considerar a generalização.
*   Referência direta a arquivos de configuração ou recursos fora do diretório da skill.

### Depuração e Solução
*   **Use `scripts/check-hardcoded-paths.sh`**: Este script pode ajudar a identificar rapidamente padrões de caminhos absolutos.
*   **Caminhos Relativos**: Prefira caminhos relativos ao diretório da skill (ex: `./scripts/meu-script.sh`).
*   **Variáveis de Ambiente**: Utilize variáveis de ambiente como `$HOME`, `$OPENCLAW_WORKSPACE` ou crie parâmetros de configuração para a skill.
*   **`path.join` (em Node.js) / `os.path.join` (em Python)**: Ferramentas que constroem caminhos de forma segura e portátil.

## 2. Scripts Auxiliares Referenciados Ausentes

### Descrição
Uma skill pode referenciar scripts auxiliares (ex: em `SKILL.md` ou em outros scripts) que não são incluídos no pacote da skill. Isso leva a erros de "comando não encontrado" ou falha na execução de funcionalidades essenciais.

### Causas Comuns
*   Esquecimento de incluir todos os arquivos durante o empacotamento da skill.
*   Scripts desenvolvidos localmente e não versionados com o restante da skill.

### Depuração e Solução
*   **Revisão do `SKILL.md`**: Verifique todas as referências a scripts no `SKILL.md` e em outros arquivos de código.
*   **Estrutura de Diretórios**: Garanta que todos os scripts auxiliares estejam presentes no diretório `scripts/` da skill e sejam acessíveis pelos caminhos corretos.
*   **Validação do Empacotamento**: Use ferramentas de validação (como o `package_skill.py` da `skill-creator`) para verificar a integridade do pacote antes da publicação.

## 3. Dependências Ausentes ou Mal Documentadas

### Descrição
Uma skill pode depender de softwares externos (CLIs, bibliotecas, runtimes) que não estão instalados ou não são corretamente listados nos requisitos da skill. Isso causa erros de "comando não encontrado" ou falhas de importação/execução.

### Causas Comuns
*   Metadados do ClawHub incompletos (campo `requires` ausente ou incorreto).
*   `SKILL.md` da skill não lista claramente todos os pré-requisitos.
*   Diferenças entre o ambiente de desenvolvimento e o ambiente de execução.

### Depuração e Solução
*   **Documentação Clara**: O `SKILL.md` deve listar explicitamente todas as dependências (`Node.js`, `ripgrep`, `gh CLI`, etc.) e suas versões mínimas.
*   **Metadados do ClawHub**: Se aplicável, o arquivo de metadados da skill (ex: `skill.yaml`) deve incluir a seção `openclaw.requires.bins` para que o ClawHub possa verificar automaticamente.
*   **`scripts/verify-dependencies.sh` (TODO)**: Um script como este pode ser implementado para automatizar a verificação das dependências no runtime.

## 4. Riscos e Precauções com `npx` (Execução de Código Remoto)

### Descrição
O comando `npx` (muito usado para instalar skills do ClawHub) baixa e executa pacotes do registro `npm`. Embora seja conveniente, isso significa que código de terceiros está sendo executado no seu sistema, o que pode apresentar riscos de segurança se a skill for maliciosa ou tiver vulnerabilidades.

### Causas Comuns
*   Instalação direta de skills de fontes não confiáveis.
*   Vulnerabilidades em dependências de terceiros da skill.

### Depuração e Solução
*   **Ambiente Isolado**: **Sempre execute instalações de skills suspeitas ou desconhecidas em um ambiente isolado (VM, Docker Container, sandbox).** Isso contém quaisquer efeitos adversos.
*   **Revisão de Código**: Inspecione manualmente o código-fonte da skill antes de executá-la em um ambiente de produção.
*   **Ferramentas de Auditoria**: Utilize skills de auditoria (como a `clawhub-quarantine-installer`) para analisar o código da skill antes da promoção.

## 5. Problemas de Integração de Telemetria (Ex: Falhas na Emissão de Logs OTLP)

### Descrição
Problemas na integração de ferramentas de telemetria (como o OpenTelemetry) podem fazer com que logs, métricas ou traces não sejam emitidos ou processados corretamente, dificultando o monitoramento e a depuração do OpenClaw e suas skills.

### Causas Comuns
*   Configuração incorreta do exportador (endpoint, credenciais).
*   Problemas de conectividade de rede com o coletor de telemetria.
*   Bugs internos na forma como o OpenClaw integra e transporta os eventos para o exportador (como o Issue #18794).
*   Dependências de bibliotecas de telemetria ausentes ou desatualizadas.

### Depuração e Solução
*   **Verificar Configuração**: Revise `diagnostics.otel` nas configurações do OpenClaw (`openclaw config get diagnostics`).
*   **Conectividade de Rede**: Verifique se o coletor OTLP (ex: Docker `openclaw-otel-collector`) está em execução e acessível a partir do OpenClaw.
*   **Logs do OpenClaw**: Procure por mensagens de erro relacionadas a `diagnostics-otel` nos logs do gateway do OpenClaw.
*   **Atualização do OpenClaw**: Monitore o status de issues e PRs relevantes (ex: Issue #18794, PR #22478) e atualize o OpenClaw assim que as correções estiverem disponíveis.
*   **Logs do Coletor**: Verifique os logs do seu coletor OTLP (ex: `docker logs openclaw-otel-collector`) para ver se ele está recebendo algum dado ou reportando erros.

# Fluxo de Trabalho de Depuração para OpenClaw AgentSkills

Este documento descreve um fluxo de trabalho estruturado para depurar problemas em AgentSkills do OpenClaw. Seguir estas etapas ajudará a identificar a causa raiz de forma eficiente e aplicar as correções necessárias.

## 1. Entender e Reproduzir o Problema

Antes de tentar corrigir, é fundamental compreender o que está acontecendo.

*   **Coletar Informações**: Obtenha o máximo de detalhes possível:
    *   Qual a skill afetada?
    *   Qual o comportamento esperado?
    *   Qual o comportamento *observado* (o erro)?
    *   Mensagens de erro completas (incluindo stack traces, se houver).
    *   Quais foram os passos exatos que levaram ao problema (para reprodução)?
    *   Qualquer contexto adicional (configurações do ambiente, versões, etc.).
*   **Reprodução Controlada**: Tente reproduzir o problema consistentemente. Se não for reproduzível, o próximo passo é tentar isolar as condições em que ele ocorre.

## 2. Verificações Iniciais e Rápidas

Comece com as verificações mais comuns e de fácil execução.

*   **Revisar `SKILL.md` da Skill Alvo**: Verifique a seção de `Requisitos` e `Workflow de Uso`. Há alguma dependência ou passo que foi esquecido?
*   **Verificar Caminhos Absolutos**: Execute o script `scripts/check-hardcoded-paths.sh <caminho-da-skill-alvo>` para identificar se há caminhos absolutos que precisam ser corrigidos.
*   **Scripts Auxiliares**: Verifique se todos os scripts mencionados no `SKILL.md` da skill alvo (ex: em `scripts/` da própria skill) realmente existem e estão acessíveis.
*   **Dependências**: Confirme que todas as dependências listadas nos requisitos da skill (ex: `Node.js`, `ripgrep`, CLIs específicas) estão instaladas e no `PATH` do ambiente.
    *   **(TODO)** Se o `scripts/verify-dependencies.sh` for implementado, execute-o aqui.
*   **Configurações do OpenClaw**: Se o problema estiver relacionado a uma integração (ex: telemetria, APIs), verifique as configurações relevantes do OpenClaw (`openclaw config get <secao>`).

## 3. Análise Detalhada de Logs e Comportamento

Se as verificações iniciais não resolverem, é hora de aprofundar.

*   **Logs do Gateway do OpenClaw**: Acesse os logs do Gateway para procurar mensagens de erro, avisos ou informações que possam indicar o problema.
    *   Comando exemplo: `openclaw logs` (ou verifique o sistema de log do seu host).
*   **Logs da Skill (se aplicável)**: Algumas skills podem gerar seus próprios logs. Verifique-os.
*   **Execução em Modo Verbose/Debug**: Se a skill ou o OpenClaw suportarem, execute-os em um modo mais verboso para obter mais detalhes (ex: `openclaw agent --thinking verbose ...`).
*   **Isolamento em Ambiente de Quarentena (se aplicável)**: Se a skill for recém-instalada ou suspeita, use um ambiente isolado (VM, Docker) para testar. A skill `clawhub-quarantine-installer` pode ser útil aqui.
*   **Revisão do Código-Fonte**: Inspecione o código-fonte da skill alvo em busca de:
    *   Erros de lógica.
    *   Chamadas de API incorretas ou incompletas.
    *   Tratamento de erros deficiente.
    *   Interações inesperadas com o ambiente.
*   **Testes Unitários/Integração (se aplicável)**: Se a skill tiver testes, execute-os. Se não, considere escrever testes simples para as partes problemáticas.

## 4. Correção e Validação

Após identificar a causa raiz, aplique a correção e valide-a.

*   **Implementar a Correção**: Modifique o código da skill, as configurações ou o ambiente conforme necessário.
*   **Testar Exaustivamente**: Não apenas verifique se o problema original foi resolvido, mas também se nenhuma nova regressão foi introduzida.
    *   Repita os passos de reprodução do problema.
    *   Execute testes adicionais que cobrem a funcionalidade da skill.
*   **Documentar**: Se a correção for significativa (ex: altera requisitos, adiciona uma nova configuração), atualize o `SKILL.md` e outras documentações relevantes da skill alvo.
*   **Empacotar e Publicar (se for uma skill sua)**: Se você corrigiu uma skill que mantém, empacote-a e publique a nova versão no ClawHub. Certifique-se de que a descrição da versão e o changelog reflitam as mudanças.

---
description: "Provides access to the MCP_Server_Trigger (v0.1.0) MCP server. It offers 7 tool(s): {\"close_ssh_session\":\"\\nFecha uma sessão SSH ativa.\\n\\nArgs:\\n    session_id: O ID da sessão a ser fechada.\\n\",\"create_ssh_session\":\"\\nCria uma nova sessão SSH explicitamente.\\n\\nArgs:\\n    host: Endereço IP ou hostname do dispositivo.\\n    username: Usuário SSH.\\n    password: Senha SSH.\\n    session_id: Identificador único para a nova sessão.\\n    device_type: Tipo de dispositivo (ex: cisco_ios, linux). Default: cisco_ios.\\n    port: Porta SSH. Default: 22.\\n\",\"execute_ssh_command\":\"\\nExecuta um comando SSH em um dispositivo remoto.\\n\\nArgs:\\n    command: O comando a ser executado.\\n    session_id: ID único da sessão (se não existir, será criada com as credenciais fornecidas).\\n    host: Endereço IP ou hostname do dispositivo (obrigatório para nova sessão).\\n    username: Usuário SSH (obrigatório para nova sessão).\\n    password: Senha SSH (obrigatório para nova sessão).\\n    device_type: Tipo de dispositivo (ex: cisco_ios, linux, juniper_junos). Default: cisco_ios.\\n    port: Porta SSH. Default: 22.\\n    timeout: Timeout opcional para o comando.\\n\",\"health_check\":\"\\nVerifica a saúde do serviço API REST SSH.\\nRetorna o status atual do serviço.\\n\",\"list_active_sessions\":\"Lista todas as sessões SSH ativas em memória.\",\"list_history_commands\":\"\\nLista o histórico de comandos executados em uma sessão específica.\\n\\nArgs:\\n    session_id: O ID da sessão para consultar o histórico.\\n\",\"list_history_sessions\":\"\\nLista o histórico de todas as sessões registradas no banco de dados.\\nInclui sessões ativas e encerradas.\\n\"}"
name: restssh
---

# restssh

This skill provides access to the `MCP_Server_Trigger` MCP server.

## MCP Server Info

- **Server Name:** MCP_Server_Trigger
- **Server Version:** 0.1.0
- **Protocol Version:** 2025-06-18
- **Capabilities:** tools

## Available Tools

This skill provides the following tools:

- **health_check**:  Verifica a saúde do serviço API REST SSH. Retorna o status atual do serviço. 
- **create_ssh_session**:  Cria uma nova sessão SSH explicitamente.  Args:     host: Endereço IP ou hostname do dispositivo.     username: Usuário SSH.     password: Senha SSH.     session_id: Identificador único para a nova sessão.     device_type: Tipo de dispositivo (ex: cisco_ios, linux). Default: cisco_ios.     port: Porta SSH. Default: 22. 
- **execute_ssh_command**:  Executa um comando SSH em um dispositivo remoto.  Args:     command: O comando a ser executado.     session_id: ID único da sessão (se não existir, será criada com as credenciais fornecidas).     host: Endereço IP ou hostname do dispositivo (obrigatório para nova sessão).     username: Usuário SSH (obrigatório para nova sessão).     password: Senha SSH (obrigatório para nova sessão).     device_type: Tipo de dispositivo (ex: cisco_ios, linux, juniper_junos). Default: cisco_ios.     port: Porta SSH. Default: 22.     timeout: Timeout opcional para o comando. 
- **list_active_sessions**: Lista todas as sessões SSH ativas em memória.
- **list_history_sessions**:  Lista o histórico de todas as sessões registradas no banco de dados. Inclui sessões ativas e encerradas. 
- **list_history_commands**:  Lista o histórico de comandos executados em uma sessão específica.  Args:     session_id: O ID da sessão para consultar o histórico. 
- **close_ssh_session**:  Fecha uma sessão SSH ativa.  Args:     session_id: O ID da sessão a ser fechada. 

## Usage

This skill is automatically invoked when tools from this MCP server are required.

This skill requires `mcp2skill` to be installed globally (if not installed, you can install it from https://github.com/fenwei-dev/mcp2skill).
Use `mcp2skill --help` to see available commands.
Use `mcp2skill list-tools --server restssh` to list tools.
Use `mcp2skill call-tool --server restssh --tool <name> --args '<json>'` to call a tool.
Use `mcp2skill update-skill --skill <skill-dir>` to check for and apply updates to this skill (where <skill-dir> is the path to this skill's directory).
(Note: DO NOT use the `generate-skill` sub-command. It's not supposed to be used under a skill.)

For detailed documentation on each tool's parameters and usage, see [TOOLS.md](references/TOOLS.md).


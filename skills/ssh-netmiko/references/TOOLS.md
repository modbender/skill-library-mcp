# MCP Tools Reference

This document lists all available tools from the MCP server.

## Tools

### health_check


Verifica a saúde do serviço API REST SSH.
Retorna o status atual do serviço.


#### Parameters

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "additionalProperties": true,
  "properties": {},
  "type": "object"
}
```

### create_ssh_session


Cria uma nova sessão SSH explicitamente.

Args:
    host: Endereço IP ou hostname do dispositivo.
    username: Usuário SSH.
    password: Senha SSH.
    session_id: Identificador único para a nova sessão.
    device_type: Tipo de dispositivo (ex: cisco_ios, linux). Default: cisco_ios.
    port: Porta SSH. Default: 22.


#### Parameters

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "additionalProperties": true,
  "properties": {
    "device_type": {
      "default": "cisco_ios",
      "type": "string"
    },
    "host": {
      "type": "string"
    },
    "password": {
      "type": "string"
    },
    "port": {
      "default": 22,
      "type": "integer"
    },
    "session_id": {
      "type": "string"
    },
    "username": {
      "type": "string"
    }
  },
  "required": [
    "host",
    "username",
    "password",
    "session_id"
  ],
  "type": "object"
}
```

### execute_ssh_command


Executa um comando SSH em um dispositivo remoto.

Args:
    command: O comando a ser executado.
    session_id: ID único da sessão (se não existir, será criada com as credenciais fornecidas).
    host: Endereço IP ou hostname do dispositivo (obrigatório para nova sessão).
    username: Usuário SSH (obrigatório para nova sessão).
    password: Senha SSH (obrigatório para nova sessão).
    device_type: Tipo de dispositivo (ex: cisco_ios, linux, juniper_junos). Default: cisco_ios.
    port: Porta SSH. Default: 22.
    timeout: Timeout opcional para o comando.


#### Parameters

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "additionalProperties": true,
  "properties": {
    "command": {
      "type": "string"
    },
    "device_type": {
      "default": "cisco_ios",
      "type": "string"
    },
    "host": {
      "default": null,
      "type": [
        "string",
        "null"
      ]
    },
    "password": {
      "default": null,
      "type": [
        "string",
        "null"
      ]
    },
    "port": {
      "default": 22,
      "type": "integer"
    },
    "session_id": {
      "type": "string"
    },
    "timeout": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "username": {
      "default": null,
      "type": [
        "string",
        "null"
      ]
    }
  },
  "required": [
    "command",
    "session_id"
  ],
  "type": "object"
}
```

### list_active_sessions

Lista todas as sessões SSH ativas em memória.

#### Parameters

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "additionalProperties": true,
  "properties": {},
  "type": "object"
}
```

### list_history_sessions


Lista o histórico de todas as sessões registradas no banco de dados.
Inclui sessões ativas e encerradas.


#### Parameters

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "additionalProperties": true,
  "properties": {},
  "type": "object"
}
```

### list_history_commands


Lista o histórico de comandos executados em uma sessão específica.

Args:
    session_id: O ID da sessão para consultar o histórico.


#### Parameters

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "additionalProperties": true,
  "properties": {
    "session_id": {
      "type": "string"
    }
  },
  "required": [
    "session_id"
  ],
  "type": "object"
}
```

### close_ssh_session


Fecha uma sessão SSH ativa.

Args:
    session_id: O ID da sessão a ser fechada.


#### Parameters

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "additionalProperties": true,
  "properties": {
    "session_id": {
      "type": "string"
    }
  },
  "required": [
    "session_id"
  ],
  "type": "object"
}
```


# Grupos - Pastorini API

## Criar Grupo

```bash
POST /api/instances/:id/groups/create
```

```json
{
  "name": "Meu Grupo",
  "participants": [
    "5511999999999@s.whatsapp.net",
    "5511888888888@s.whatsapp.net"
  ]
}
```

## Listar Grupos

```bash
GET /api/instances/:id/groups
```

## Metadados do Grupo

```bash
GET /api/instances/:id/groups/:groupId/metadata
```

Retorna: nome, descrição, participantes, admins, etc.

## Código de Convite

```bash
GET /api/instances/:id/groups/:groupId/invite-code
```

## Gerenciar Participantes

```bash
POST /api/instances/:id/groups/:groupId/participants
```

### Adicionar

```json
{"action": "add", "participants": ["5511999999999@s.whatsapp.net"]}
```

### Remover

```json
{"action": "remove", "participants": ["5511999999999@s.whatsapp.net"]}
```

### Promover a Admin

```json
{"action": "promote", "participants": ["5511999999999@s.whatsapp.net"]}
```

### Rebaixar de Admin

```json
{"action": "demote", "participants": ["5511999999999@s.whatsapp.net"]}
```

## Configurações do Grupo

```bash
PUT /api/instances/:id/groups/:groupId/settings
```

```json
{
  "subject": "Novo Nome do Grupo",
  "description": "Descrição do grupo",
  "announce": true,
  "restrict": true
}
```

- `announce: true` = apenas admins enviam mensagens
- `restrict: true` = apenas admins editam info

## Sair do Grupo

```bash
POST /api/instances/:id/groups/:groupId/leave
```

## Formato do Group ID

O ID de grupo sempre termina em `@g.us`:
- Exemplo: `-1001234567890@g.us` ou `120363123456789012@g.us`

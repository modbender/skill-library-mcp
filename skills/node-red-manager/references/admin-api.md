# Node-RED Admin API Reference

## Authentication

The Admin API uses Bearer token authentication. The CLI automatically handles authentication using credentials from environment variables.

- **Login Endpoint**: `POST /auth/token`
- **Token Revocation**: `POST /auth/revoke`

## Flow Endpoints

### List Flows
- **Endpoint**: `GET /flows`
- **Description**: Get all active flows
- **CLI**: `scripts/nr list-flows`

### Get Flow
- **Endpoint**: `GET /flow/:id`
- **Description**: Get specific flow by ID
- **CLI**: `scripts/nr get-flow <flow-id>`

### Deploy Flows
- **Endpoint**: `POST /flows`
- **Description**: Deploy or update flows
- **Body**: `{"flows": [...]}` or array of flow objects
- **CLI**: `scripts/nr deploy --file <file>`

### Update Flow
- **Endpoint**: `PUT /flow/:id`
- **Description**: Update specific flow
- **CLI**: `scripts/nr update-flow <flow-id> --file <file>`

### Delete Flow
- **Endpoint**: `DELETE /flow/:id`
- **Description**: Delete specific flow
- **CLI**: `scripts/nr delete-flow <flow-id>`

### Get Flow State
- **Endpoint**: `GET /flows/state`
- **Description**: Get runtime state of flows
- **CLI**: `scripts/nr get-flow-state`

### Set Flow State
- **Endpoint**: `POST /flows/state`
- **Description**: Set runtime state of flows
- **CLI**: `scripts/nr set-flow-state --file <file>`

## Node Endpoints

### List Nodes
- **Endpoint**: `GET /nodes`
- **Description**: Get list of installed node modules
- **CLI**: `scripts/nr list-nodes`

### Install Node
- **Endpoint**: `POST /nodes`
- **Description**: Install a new node module
- **Body**: `{"module": "node-red-contrib-http-request"}`
- **CLI**: `scripts/nr install-node <module>`

### Get Node Info
- **Endpoint**: `GET /nodes/:module`
- **Description**: Get information about a node module
- **CLI**: `scripts/nr get-node <module>`

### Enable/Disable Node
- **Endpoint**: `PUT /nodes/:module`
- **Body**: `{"enabled": true|false}`
- **CLI**: `scripts/nr enable-node <module>` or `scripts/nr disable-node <module>`

### Remove Node
- **Endpoint**: `DELETE /nodes/:module`
- **Description**: Remove a node module
- **CLI**: `scripts/nr remove-node <module>`

## Settings Endpoints

### Get Settings
- **Endpoint**: `GET /settings`
- **Description**: Get runtime settings (httpNodeRoot, version, user info)
- **CLI**: `scripts/nr get-settings`

### Get Diagnostics
- **Endpoint**: `GET /diagnostics`
- **Description**: Get runtime diagnostics
- **CLI**: `scripts/nr get-diagnostics`

## Context Endpoints

### Get Context
- **Endpoint**: `GET /context/:store/:key`
- **Description**: Get context value from store
- **Stores**: `flow`, `global`, `memory`
- **CLI**: `scripts/nr get-context <store> <key>`

### Set Context
- **Endpoint**: `POST /context/:store/:key`
- **Body**: `{"value": <value>}`
- **Description**: Set context value in store
- **CLI**: `scripts/nr set-context <store> <key> <value>`

## Flow Design Best Practices

### Error Handling
- Use `catch` nodes for global error management
- Implement error handling in each flow section
- Log errors appropriately

### Context Usage
- Use `flow` context for flow-scoped state
- Use `global` context for shared state across flows
- Avoid using function variables for persistent state

### Organization
- Use subflows to encapsulate reusable logic
- Use link nodes instead of long wires (spaghetti flow)
- Group related nodes into tabs
- Add descriptive labels to nodes

### Performance
- Minimize use of `exec` nodes (RCE risk)
- Use `change` nodes for data transformation
- Leverage built-in nodes when possible
- Avoid blocking operations in function nodes

## Security Guidelines

### Authentication
- Always secure the editor (`/red`) with strong password
- Use `adminAuth` configuration in settings.js
- Consider OAuth for production deployments

### Dashboard Security
- Secure dashboard (`/ui`) with basic auth or OAuth
- Validate user inputs in dashboard nodes
- Use HTTPS in production

### Node Security
- Avoid using `exec` node unless strictly necessary (RCE risk)
- Validate and sanitize all user inputs
- Be cautious with HTTP Request nodes (SSRF risk)
- Review third-party node modules before installation

### Network Security
- Use firewall rules to restrict access
- Consider VPN or SSH tunneling for remote access
- Monitor for suspicious activity

## Error Codes

- **200**: Success
- **204**: Success (no content)
- **400**: Bad Request (invalid input)
- **401**: Unauthorized (authentication failed)
- **404**: Not Found (resource doesn't exist)
- **500**: Internal Server Error

## Rate Limiting

Node-RED may implement rate limiting on Admin API endpoints. If you encounter rate limit errors:
- Implement exponential backoff
- Reduce request frequency
- Use batch operations when possible

# OpenClaw Wiring

1. Build package:

```bash
npm --workspace @fub/crea-ddf-mcp run build
```

2. Register MCP server in your OpenClaw tool runtime with command:

```bash
node /ABSOLUTE/PATH/TO/packages/crea-ddf-mcp/dist/mcp-server.js
```

3. Export DDF credentials into the OpenClaw runtime environment.

4. Validate by calling tools:

- `ddf.search_properties`
- `ddf.get_property`
- `ddf.get_property_media`
- `ddf.get_metadata`

5. If media queries fail, set deployment-specific env vars:

- `DDF_MEDIA_ENTITY`
- `DDF_MEDIA_RECORD_KEY_FIELD`
- `DDF_MEDIA_ORDER_FIELD`

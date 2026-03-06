# Language-Specific Proxy Configuration

For detailed language-specific setup instructions, consult:
https://docs.speedscale.com/proxymock/getting-started/language-reference/

## Common Patterns

### Go
Go respects `http_proxy`/`https_proxy` by default via `net/http`.

```bash
proxymock record -- go run main.go
```

### Node.js
Node does NOT respect proxy env vars by default. Use a proxy agent or wrap with proxymock:

```bash
proxymock record -- node app.js
```

### Python
`requests` library respects proxy env vars. `urllib3` and `aiohttp` may need explicit config.

```bash
proxymock record -- python app.py
```

### Java
Set JVM proxy properties or use proxymock wrapping:

```bash
proxymock record -- java -Dhttp.proxyHost=localhost -Dhttp.proxyPort=4140 -jar app.jar
```

### cURL Testing
```bash
curl -k -x http://localhost:4140 https://api.example.com/endpoint
```

The `-k` flag trusts proxymock's TLS cert. The `-x` flag routes through the proxy.

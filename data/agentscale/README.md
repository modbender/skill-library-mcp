# agentscale

Deploy web apps and APIs to a public URL with a single command. No config, no Docker, no CI pipeline — just `agentscale deploy`.

Supports Node.js, Python, Go, and anything [Nixpacks](https://nixpacks.com) can detect.

## Quick start

```bash
npx agentscale register   # get an API key (saved to ~/.agentscale)
npx agentscale deploy     # package and deploy the current directory
```

Your app gets a public `.railway.app` URL on deploy.

## Commands

### `agentscale register`

Creates an API key and saves it to `~/.agentscale/config.json`. No account or payment needed.

### `agentscale deploy`

Packages the current directory and deploys it.

```bash
agentscale deploy              # auto-generates a service name
agentscale deploy --name myapp # deploy to a specific service
```

Your server must listen on the `$PORT` environment variable.

### `agentscale list`

Lists your services and their status.

```
  quick-fox-1234  [active]   (created 2/15/2026)
  my-api          [expires in 42m]  (created 2/15/2026)
```

## Free tier

- No signup or payment required.
- Free deploys expire after 1 hour.
- Limited to 1 service.

Add credits to remove the expiry and deploy permanently.

## Limits

- Upload: 100 MB compressed, 500 MB decompressed.
- Your project needs a standard structure (e.g. `package.json` with a start script, `requirements.txt`, or `go.mod`).

## License

MIT

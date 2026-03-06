# SSL Configuration by Server

## Nginx

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # Modern config (TLS 1.2+)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS (optional but recommended)
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

## Apache

```apache
<VirtualHost *:80>
    ServerName example.com
    Redirect permanent / https://example.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName example.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/example.com/cert.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem
    SSLCertificateChainFile /etc/letsencrypt/live/example.com/chain.pem

    # Modern config
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
</VirtualHost>
```

## Caddy

Caddy handles SSL automatically. Just use HTTPS in your address:

```caddyfile
example.com {
    reverse_proxy localhost:3000
}

# That's it - Caddy gets and renews certs automatically
```

For custom certs:
```caddyfile
example.com {
    tls /path/to/cert.pem /path/to/key.pem
    reverse_proxy localhost:3000
}
```

## Node.js / Express

```javascript
const https = require('https');
const fs = require('fs');
const express = require('express');

const app = express();

const options = {
  key: fs.readFileSync('/etc/letsencrypt/live/example.com/privkey.pem'),
  cert: fs.readFileSync('/etc/letsencrypt/live/example.com/fullchain.pem')
};

https.createServer(options, app).listen(443);

// Redirect HTTP to HTTPS
const http = require('http');
http.createServer((req, res) => {
  res.writeHead(301, { Location: `https://${req.headers.host}${req.url}` });
  res.end();
}).listen(80);
```

## Traefik

```yaml
# traefik.yml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web
```

```yaml
# docker-compose.yml labels
labels:
  - "traefik.http.routers.myapp.rule=Host(`example.com`)"
  - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
```

## HAProxy

```haproxy
frontend https_front
    bind *:443 ssl crt /etc/haproxy/certs/example.com.pem
    default_backend app_servers

frontend http_front
    bind *:80
    redirect scheme https code 301
```

Note: HAProxy expects cert + key in a single PEM file:
```bash
cat fullchain.pem privkey.pem > /etc/haproxy/certs/example.com.pem
```

# Server Configuration Examples

## Nginx Reverse Proxy (Basic)

```nginx
server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Nginx with SSL (Let's Encrypt)

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Caddy (Automatic SSL)

```caddyfile
example.com {
    reverse_proxy localhost:3000
}

# Multiple services
api.example.com {
    reverse_proxy localhost:8080
}

static.example.com {
    root * /var/www/static
    file_server
}
```

## PM2 Ecosystem File

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'myapp',
    script: './dist/index.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    env_development: {
      NODE_ENV: 'development',
      PORT: 3000
    }
  }]
};
```

## Systemd Service Unit

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/myapp
ExecStart=/usr/bin/node dist/index.js
Restart=on-failure
RestartSec=10
Environment=NODE_ENV=production
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
```

After creating: `systemctl daemon-reload && systemctl enable myapp && systemctl start myapp`

## Gunicorn (Python)

```bash
# Run directly
gunicorn -w 4 -b 0.0.0.0:8000 myapp:app

# With systemd
# ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 myapp:app
```

## Let's Encrypt Certificate

```bash
# Standalone (stops existing server)
certbot certonly --standalone -d example.com

# Webroot (server keeps running)
certbot certonly --webroot -w /var/www/html -d example.com

# Auto-renewal test
certbot renew --dry-run
```

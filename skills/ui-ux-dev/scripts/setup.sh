#!/bin/bash
# UI Designer Setup Script
# Usage: bash setup.sh <port> [serve_dir]

PORT="${1:-5174}"
SERVE_DIR="${2:-/var/www/ui-designer}"
HOST_IP=$(hostname -I | awk '{print $1}')

echo "=== UI Designer Setup ==="
echo "Port: $PORT"
echo "Serve directory: $SERVE_DIR"

# Create serve directory
sudo mkdir -p "$SERVE_DIR"
sudo chown "$(whoami):$(whoami)" "$SERVE_DIR"
chmod 755 "$SERVE_DIR"

# Create welcome page
cat > "$SERVE_DIR/index.html" << 'WELCOME'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UI Designer — Ready</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-gray-950 text-white min-h-screen flex items-center justify-center">
  <div class="text-center space-y-6 p-8">
    <div class="text-6xl">🎨</div>
    <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
      UI Designer
    </h1>
    <p class="text-gray-400 text-lg max-w-md mx-auto">
      Your AI-powered design studio is ready. Ask ClawBit to generate a page and it'll appear here.
    </p>
    <div class="flex items-center justify-center gap-2 text-sm text-gray-500">
      <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
      Server running
    </div>
  </div>
</body>
</html>
WELCOME

# Configure Nginx
NGINX_CONF="/etc/nginx/sites-available/ui-designer"
sudo tee "$NGINX_CONF" > /dev/null << NGINX
server {
    listen $PORT;
    server_name _;
    root $SERVE_DIR;
    index index.html;

    location / {
        try_files \$uri \$uri/ \$uri/index.html =404;
    }

    # Cache static assets
    location ~* \.(css|js|png|jpg|gif|svg|ico|woff2?)$ {
        expires 1h;
        add_header Cache-Control "public, immutable";
    }
}
NGINX

# Enable site
sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/ui-designer

# Test and reload nginx
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "=== Setup Complete ==="
echo "UI Designer is live at: http://${HOST_IP}:${PORT}/"
echo "Serve directory: $SERVE_DIR"
echo "Generate pages by asking ClawBit!"

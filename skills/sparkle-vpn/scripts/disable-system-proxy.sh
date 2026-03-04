#!/bin/bash
# Disable system proxy

echo "🔧 正在关闭系统代理..."

# Check if running in a desktop environment
if command -v gsettings &> /dev/null; then
    # GNOME/GTK based desktop
    gsettings set org.gnome.system.proxy mode 'none' 2>/dev/null || true
    echo "✅ GNOME 系统代理已关闭"
fi

# Unset environment variables
unset http_proxy
unset https_proxy
unset HTTP_PROXY
unset HTTPS_PROXY
unset no_proxy

# Remove proxy environment file
if [ -f ~/.config/sparkle/proxy.env ]; then
    rm ~/.config/sparkle/proxy.env
fi

echo ""

# Test connection (should show original IP)
IP=$(curl -s --max-time 5 https://ipinfo.io/ip 2>/dev/null || echo "unknown")
echo "🌐 当前出口 IP: $IP"

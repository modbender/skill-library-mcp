#\!/bin/bash
# 智能代理切换脚本

PROXY_SOCKS="127.0.0.1:10808"
PROXY_HTTP="127.0.0.1:10809"

# 检测是否需要代理 (访问外网域名)
NEED_PROXY=false

for arg in "$@"; do
    case "$arg" in
        *github.com*|*google.com*|*openai.com*|*anthropic.com*|*npmjs.com*|*pypi.org*|*docker.com*|*quay.io*)
            NEED_PROXY=true
            ;;
    esac
done

if [ "$NEED_PROXY" = true ]; then
    echo "🌐 检测到外网访问，启用代理..."
    export http_proxy="http://${PROXY_HTTP}"
    export https_proxy="http://${PROXY_HTTP}"
    export ALL_PROXY="socks5://${PROXY_SOCKS}"
fi

exec "$@"

#!/bin/bash
# HTTP Server Setup for Video Streaming
# Usage: setup_server.sh [start|stop|status|restart]

CBS_DIR="/root/.openclaw/workspace/cbs-live-local"
BBC_DIR="/root/.openclaw/workspace/bbc-news-live"
CBS_PORT=8093
BBC_PORT=8095

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

get_server_pid() {
    local port=$1
    lsof -t -i :$port 2>/dev/null
}

start_server() {
    local dir=$1
    local port=$2
    local name=$3
    
    # Check if already running
    pid=$(get_server_pid $port)
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}$name is already running on port $port (PID: $pid)${NC}"
        return 0
    fi
    
    # Check directory exists
    if [ ! -d "$dir" ]; then
        echo -e "${RED}Directory does not exist: $dir${NC}"
        return 1
    fi
    
    # Start server
    cd "$dir" && nohup python3 -m http.server $port --bind 0.0.0.0 > /dev/null 2>&1 &
    sleep 1
    
    # Verify started
    pid=$(get_server_pid $port)
    if [ -n "$pid" ]; then
        echo -e "${GREEN}✅ $name started on port $port (PID: $pid)${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to start $name${NC}"
        return 1
    fi
}

stop_server() {
    local port=$1
    local name=$2
    
    pid=$(get_server_pid $port)
    if [ -n "$pid" ]; then
        kill $pid 2>/dev/null
        sleep 1
        if [ -z "$(get_server_pid $port)" ]; then
            echo -e "${GREEN}✅ $name stopped (port $port)${NC}"
        else
            echo -e "${RED}❌ Failed to stop $name${NC}"
        fi
    else
        echo -e "${YELLOW}$name is not running (port $port)${NC}"
    fi
}

check_status() {
    local port=$1
    local name=$2
    
    pid=$(get_server_pid $port)
    if [ -n "$pid" ]; then
        echo -e "${GREEN}✅ $name: Running on port $port (PID: $pid)${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: Not running (port $port)${NC}"
        return 1
    fi
}

get_ip() {
    hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost"
}

show_urls() {
    ip=$(get_ip)
    echo ""
    echo "📺 Video Streaming URLs:"
    echo "======================="
    echo ""
    echo "🇺🇸 CBS Evening News:"
    echo "   Player: http://$ip:$CBS_PORT/"
    echo "   Video:  http://$ip:$CBS_PORT/cbs_latest.mp4"
    echo ""
    echo "🇬🇧 BBC News at Ten:"
    echo "   Player: http://$ip:$BBC_PORT/"
    echo "   Video:  http://$ip:$BBC_PORT/bbc_news_latest.mp4"
    echo ""
}

# Main command handling
case "${1:-status}" in
    start)
        echo "Starting video streaming servers..."
        start_server "$CBS_DIR" $CBS_PORT "CBS Evening News"
        start_server "$BBC_DIR" $BBC_PORT "BBC News at Ten"
        show_urls
        ;;
    stop)
        echo "Stopping video streaming servers..."
        stop_server $CBS_PORT "CBS Evening News"
        stop_server $BBC_PORT "BBC News at Ten"
        ;;
    restart)
        echo "Restarting video streaming servers..."
        stop_server $CBS_PORT "CBS Evening News"
        stop_server $BBC_PORT "BBC News at Ten"
        sleep 1
        start_server "$CBS_DIR" $CBS_PORT "CBS Evening News"
        start_server "$BBC_DIR" $BBC_PORT "BBC News at Ten"
        show_urls
        ;;
    status)
        echo "Video streaming server status:"
        echo "=============================="
        check_status $CBS_PORT "CBS Evening News"
        check_status $BBC_PORT "BBC News at Ten"
        show_urls
        ;;
    *)
        echo "Usage: $0 [start|stop|restart|status]"
        exit 1
        ;;
esac

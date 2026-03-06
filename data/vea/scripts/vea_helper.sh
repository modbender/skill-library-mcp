#!/bin/bash
# VEA Helper Script

VEA_DIR="$HOME/vea"
VEA_URL="http://localhost:8000"

case "$1" in
  status)
    curl -s "$VEA_URL/" | jq . 2>/dev/null || echo "VEA not running"
    ;;
  
  start)
    if curl -s "$VEA_URL/" > /dev/null 2>&1; then
      echo "VEA already running"
    else
      echo "Starting VEA..."
      cd "$VEA_DIR" && nohup ./.venv/bin/python -m src.app > /tmp/vea.log 2>&1 &
      sleep 5
      curl -s "$VEA_URL/" | jq . 2>/dev/null && echo "VEA started!" || echo "Failed to start, check /tmp/vea.log"
    fi
    ;;
  
  stop)
    pkill -f "src.app" && echo "VEA stopped" || echo "VEA was not running"
    ;;
  
  logs)
    tail -${2:-50} /tmp/vea.log
    ;;
  
  projects)
    echo "=== Videos (source) ==="
    ls -la "$VEA_DIR/data/videos/" 2>/dev/null || echo "No videos"
    echo ""
    echo "=== Indexed ==="
    ls -la "$VEA_DIR/data/indexing/" 2>/dev/null || echo "No indexed projects"
    echo ""
    echo "=== Outputs ==="
    ls -la "$VEA_DIR/data/outputs/" 2>/dev/null || echo "No outputs"
    ;;
  
  index)
    if [ -z "$2" ]; then
      echo "Usage: vea_helper.sh index <project_name>"
      exit 1
    fi
    curl -X POST "$VEA_URL/video-edit/v1/index" \
      -H "Content-Type: application/json" \
      -d "{\"blob_path\": \"data/videos/$2/\", \"start_fresh\": true}" | jq .
    ;;
  
  edit)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: vea_helper.sh edit <project_name> \"<prompt>\""
      exit 1
    fi
    curl -X POST "$VEA_URL/video-edit/v1/flexible_respond" \
      -H "Content-Type: application/json" \
      -d "{
        \"blob_path\": \"data/videos/$2/\",
        \"prompt\": \"$3\",
        \"video_response\": true,
        \"music\": true,
        \"narration\": false,
        \"aspect_ratio\": 0.5625,
        \"subtitles\": true
      }" | jq .
    ;;
  
  *)
    echo "VEA Helper Commands:"
    echo "  status   - Check if VEA is running"
    echo "  start    - Start VEA server"
    echo "  stop     - Stop VEA server"
    echo "  logs [n] - Show last n lines of logs (default 50)"
    echo "  projects - List all projects"
    echo "  index <name>        - Index a video project"
    echo "  edit <name> \"prompt\" - Generate edited video"
    ;;
esac

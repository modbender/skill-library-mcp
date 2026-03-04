#!/bin/bash
# Build with Public - Helper Script
# Simplify blog project management and publishing workflow

set -e

PROJECT_NAME="${1:-codewithriver}"
ACTION="${2:-init}"

show_help() {
    echo "Build with Public - Technical Blog Writing Assistant"
    echo ""
    echo "Usage:"
    echo "  ./bwp.sh <project-name> init       # Initialize new project"
    echo "  ./bwp.sh <project-name> start      # Start server"
    echo "  ./bwp.sh <project-name> stop       # Stop server"
    echo "  ./bwp.sh <project-name> status     # Check status"
    echo "  ./bwp.sh <project-name> commit     # Commit to Git"
    echo ""
    echo "Examples:"
    echo "  ./bwp.sh myblog init"
    echo "  ./bwp.sh myblog start"
}

init_project() {
    echo "🚀 Initializing Build with Public project: $PROJECT_NAME"
    
    # Create directory structure
    mkdir -p ~/$PROJECT_NAME/{articles,draft,images,logs,tweets}
    cd ~/$PROJECT_NAME
    
    # Initialize Git
    git init
    git config user.email "$(whoami)@example.com"
    git config user.name "$(whoami)"
    
    # Create .env
    cat > .env << EOF
# Build with Public - Configuration
PORT=12000
HOST=0.0.0.0
AUTH_USERNAME=user
AUTH_PASSWORD=openskill
CUSTOM_DOMAIN=localhost
EOF
    
    # Copy server.py template
    if [ -f "$(dirname $0)/templates/server.py.template" ]; then
        cp "$(dirname $0)/templates/server.py.template" server.py
        chmod +x server.py
    else
        echo "⚠️  server.py template not found, please create manually"
    fi
    
    # Create README
    cat > README.md << EOF
# $PROJECT_NAME - Build with Public

Technical blog writing project

## Directory Structure
- articles/ - Published articles
- draft/ - Writing outlines and drafts
- images/ - Images
- logs/ - Writing logs

## Start Server
python server.py

## Access URL
http://localhost:12000
EOF
    
    # Initial commit
    git add .
    git commit -m "[$(date +%Y-%m-%d)] init: Initialize Build with Public project"
    
    echo "✅ Project initialization complete!"
    echo ""
    echo "Next steps:"
    echo "  cd ~/$PROJECT_NAME"
    echo "  ./bwp.sh $PROJECT_NAME start"
}

start_server() {
    cd ~/$PROJECT_NAME
    
    if pgrep -f "server.py" > /dev/null; then
        echo "⚠️  Server is already running"
        return
    fi
    
    echo "🚀 Starting server..."
    nohup python server.py > logs/server.log 2>&1 &
    sleep 2
    
    echo "✅ Server started"
    echo "🔗 Access URL: http://localhost:12000"
    echo "🔐 Default password: openskill"
}

stop_server() {
    if pgrep -f "server.py" > /dev/null; then
        pkill -f "server.py"
        echo "✅ Server stopped"
    else
        echo "⚠️  Server is not running"
    fi
}

show_status() {
    cd ~/$PROJECT_NAME
    
    echo "📊 Project status: $PROJECT_NAME"
    echo ""
    
    # Git status
    echo "📝 Git status:"
    git log --oneline -3 2>/dev/null || echo "  No commits yet"
    echo ""
    
    # File statistics
    echo "📁 File statistics:"
    echo "  Articles: $(ls articles/*.md 2>/dev/null | wc -l) files"
    echo "  Drafts: $(ls draft/*.md 2>/dev/null | wc -l) files"
    echo ""
    
    # Server status
    if pgrep -f "server.py" > /dev/null; then
        echo "🟢 Server: Running"
        echo "   URL: http://localhost:12000"
    else
        echo "🔴 Server: Not running"
    fi
}

git_commit() {
    cd ~/$PROJECT_NAME
    
    echo "📝 Committing changes to Git..."
    git add -A
    
    # Only commit if there are changes
    if ! git diff --cached --quiet; then
        read -p "Commit message: " msg
        git commit -m "[$(date +%Y-%m-%d)] $msg"
        echo "✅ Commit successful"
    else
        echo "ℹ️  No changes to commit"
    fi
}

case "$ACTION" in
    init)
        init_project
        ;;
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    status)
        show_status
        ;;
    commit)
        git_commit
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown action: $ACTION"
        show_help
        exit 1
        ;;
esac

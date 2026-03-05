#!/bin/bash

# Check if ELEVENLABS_API_KEY is set
if [ -z "$ELEVENLABS_API_KEY" ]; then
  echo "Error: ELEVENLABS_API_KEY environment variable is not set." >&2
  exit 1
fi

# Define the port for the server
PORT=8124

# Check if a process is already running on the port
if lsof -i:$PORT > /dev/null; then
  echo "MCP server is already running on port $PORT."
  exit 0
fi

# Start the server in the background
echo "Starting ElevenLabs MCP Server on port $PORT..."
elevenlabs-mcp --port $PORT &> /tmp/elevenlabs_mcp_server.log &

# Give it a moment to start up
sleep 3

# Verify it's running
if lsof -i:$PORT > /dev/null; then
  echo "Server started successfully. Log file: /tmp/elevenlabs_mcp_server.log"
else
  echo "Error: Server failed to start. Check log for details: /tmp/elevenlabs_mcp_server.log" >&2
  exit 1
fi

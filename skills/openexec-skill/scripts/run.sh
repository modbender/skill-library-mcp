#!/bin/bash
set -e
echo "Starting OpenExec..."
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload

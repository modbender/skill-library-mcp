#!/bin/bash
# Refresh QMD index and embeddings
echo "🔄 Refreshing QMD index..."
qmd update
echo "🧠 Updating embeddings..."
qmd embed
echo "✅ Index refreshed!"
qmd status

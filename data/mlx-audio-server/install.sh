#!/bin/bash

set -ueo pipefail

brew update

# use brew to install deps if not exists
command -v ffmpeg || brew install ffmpeg
command -v jq || brew install jq

# install formula from tap:
# https://github.com/guoqiao/homebrew-tap/blob/main/Formula/mlx-audio-server.rb
brew install guoqiao/tap/mlx-audio-server || true

# (re)start brew service
brew services restart mlx-audio-server || true

sleep 3

# verify server/api is running
curl -Ss http://localhost:8899/v1/models | jq

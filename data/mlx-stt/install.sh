#!/bin/bash

command -v ffmpeg || brew install ffmpeg
command -v uv || brew install uv
uv tool install --force mlx-audio --prerelease=allow

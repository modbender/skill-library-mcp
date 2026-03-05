#!/bin/bash

# Install Doginals Skill Requirements
# This script checks for required dependencies and installs any missing components.

set -e

# Check for Node.js installation
if ! command -v node &> /dev/null
then
    echo "Node.js not found. Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "Node.js is already installed."
fi

# Check for Dogecoin Core installation
if [ ! -d "$HOME/.dogecoin" ]; then
    echo "Dogecoin Core not found. Installing Dogecoin Core..."
    wget https://github.com/dogecoin/dogecoin/releases/download/v1.14.6/dogecoin-1.14.6-x86_64-linux-gnu.tar.gz
    tar -xvf dogecoin-1.14.6-x86_64-linux-gnu.tar.gz
    sudo cp dogecoin-1.14.6/bin/* /usr/local/bin/
    mkdir -p $HOME/.dogecoin
    echo "rpcuser=yourrpcusername
rpcpassword=yourrpcpassword
rpcallowip=127.0.0.1
server=1
daemon=1
prune=550
" > $HOME/.dogecoin/dogecoin.conf
    echo "Dogecoin Core installed and configured."
else
    echo "Dogecoin Core is already installed."
fi

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Dependencies are already installed."
fi

# Final output
echo "Doginals skill setup complete. You can now use Doginals and Dunes commands!"
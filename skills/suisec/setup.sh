#!/bin/bash
# Check if sui client is installed
if ! command -v sui &> /dev/null
then
    echo "Sui client could not be found, please install it first."
    exit
fi
echo "Sui Secure Skill setup complete."

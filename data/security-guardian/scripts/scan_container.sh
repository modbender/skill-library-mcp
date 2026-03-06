#!/bin/bash
# Wrapper for Trivy container scanning

IMAGE_NAME=$1

if [ -z "$IMAGE_NAME" ]; then
    echo "Usage: $0 <image_name>"
    exit 1
fi

if ! command -v trivy &> /dev/null; then
    echo "Trivy not found. Please install it first: https://aquasecurity.github.io/trivy/"
    exit 1
fi

echo "Scanning image: $IMAGE_NAME..."
trivy image --severity HIGH,CRITICAL --quiet "$IMAGE_NAME"

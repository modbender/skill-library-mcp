#!/usr/bin/env bash
# detect_gpu.sh — Detect GPU accelerator type
# Outputs exactly one of: cuda, rocm, intel, cpu
set -euo pipefail

detect_gpu() {
    # 1. Check for NVIDIA GPU (CUDA)
    if command -v nvidia-smi &>/dev/null; then
        if nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 | grep -qi .; then
            echo "cuda"
            return 0
        fi
    fi

    # 2. Check for AMD GPU (ROCm)
    if command -v rocminfo &>/dev/null; then
        if rocminfo 2>/dev/null | grep -q "Name:.*gfx"; then
            echo "rocm"
            return 0
        fi
    elif [ -x /opt/rocm/bin/rocminfo ]; then
        if /opt/rocm/bin/rocminfo 2>/dev/null | grep -q "Name:.*gfx"; then
            echo "rocm"
            return 0
        fi
    fi
    # Also check for /dev/kfd (ROCm kernel driver)
    if [ -e /dev/kfd ] && lspci 2>/dev/null | grep -qi "amd.*radeon\|amd.*navi\|amd.*vega\|amd.*polaris"; then
        echo "rocm"
        return 0
    fi

    # 3. Check for Intel GPU (XPU)
    if command -v xpu-smi &>/dev/null; then
        echo "intel"
        return 0
    fi
    if command -v intel_gpu_top &>/dev/null; then
        echo "intel"
        return 0
    fi
    # Check for Intel discrete/integrated GPU via lspci
    if lspci 2>/dev/null | grep -qi "intel.*\(arc\|iris\|uhd\|graphics\)"; then
        # Only report intel if the compute runtime is available
        if [ -d /dev/dri ] && ls /dev/dri/renderD* &>/dev/null; then
            # Check if intel_extension_for_pytorch could work
            if dpkg -l 2>/dev/null | grep -qi "intel-level-zero" || \
               pacman -Q 2>/dev/null | grep -qi "level-zero" || \
               rpm -qa 2>/dev/null | grep -qi "level-zero"; then
                echo "intel"
                return 0
            fi
        fi
    fi

    # 4. Fallback: CPU only
    echo "cpu"
    return 0
}

# Run detection
GPU_TYPE=$(detect_gpu)
echo "$GPU_TYPE"

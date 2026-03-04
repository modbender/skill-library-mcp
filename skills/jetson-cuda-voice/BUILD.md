# Building whisper.cpp with CUDA on Jetson Xavier NX

Tested on: JetPack 5.1.4, CUDA 11.4, sm_72

## Prerequisites

```bash
sudo apt install cmake build-essential
# CUDA toolkit already included in JetPack
```

## Clone & Build

```bash
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp

mkdir build && cd build

# CRITICAL: sm_72 only — multi-arch compilation will OOM on 8GB Jetson
cmake .. \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=72 \
  -DCMAKE_BUILD_TYPE=Release

# -j4 is the sweet spot: -j6 OOMs, -j2 is too slow
make -j4 2>&1 | tee /tmp/whisper-build.log
```

> ⚠️ Build takes 30–45 minutes due to CUDA template compilation.
> Use `nohup make -j4 > /tmp/whisper-build.log 2>&1 &` to detach.
> First run takes ~17s for CUDA JIT — subsequent runs are ~2s.

## Download Model

```bash
mkdir -p ~/.local/share/whisper/models
cd whisper.cpp
bash models/download-ggml-model.sh base
cp models/ggml-base.bin ~/.local/share/whisper/models/
```

Available models (quality vs speed trade-off):
- `tiny` — fastest, lower accuracy
- `base` — good balance ✅ recommended for Jetson
- `small` — better accuracy, slower

## Install Binaries

```bash
cp build/bin/whisper-server ~/.local/bin/whisper-server-gpu
cp build/bin/whisper-cli    ~/.local/bin/whisper-cli-gpu
chmod +x ~/.local/bin/whisper-server-gpu ~/.local/bin/whisper-cli-gpu
```

## Test

```bash
# Start server
~/.local/bin/whisper-server-gpu \
  -m ~/.local/share/whisper/models/ggml-base.bin \
  --port 8181 -l auto &

# Test inference (record 3s first)
arecord -D hw:Array,0 -f S24_3LE -r 16000 -c 2 -d 3 /tmp/test.wav
curl -s http://127.0.0.1:8181/inference \
  -F "file=@/tmp/test.wav" \
  -F "language=auto" \
  -F "response_format=json"
```

## Backup

After successful build, back up the binaries — saves 45 min of recompilation:

```bash
mkdir -p ~/backups/whisper-cpp-gpu
cp ~/.local/bin/whisper-server-gpu ~/backups/whisper-cpp-gpu/
cp ~/.local/bin/whisper-cli-gpu    ~/backups/whisper-cpp-gpu/
```

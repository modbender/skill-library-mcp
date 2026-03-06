---
name: valtec-tts
description: Local Vietnamese text-to-speech via VITS2 (offline, no cloud). Supports 5 built-in speaker voices and zero-shot voice cloning from reference audio.
homepage: https://github.com/tronghieuit/valtec-tts
metadata:
  {
    "openclaw":
      {
        "emoji": "🇻🇳",
        "os": ["darwin", "linux", "win32"],
        "requires": { "env": ["VALTEC_TTS_DIR"] },
        "install":
          [
            {
              "id": "clone-repo",
              "kind": "shell",
              "cmd": "git clone https://github.com/tronghieuit/valtec-tts.git ~/.openclaw/tools/valtec-tts && cd ~/.openclaw/tools/valtec-tts && pip install -e .",
              "label": "Clone repo and install dependencies",
            },
          ],
      },
  }
---

# Valtec Vietnamese TTS

Local Vietnamese text-to-speech with zero-shot voice cloning, powered by VITS2.
Runs offline — no cloud API needed.

## Features

- 🇻🇳 High-quality Vietnamese speech synthesis
- 🎙️ Zero-shot voice cloning from ~5s reference audio
- 👥 5 built-in speaker voices (Northern/Southern, Male/Female)
- 🔒 Fully offline — no cloud API needed
- ⚡ GPU-accelerated (CUDA) or CPU inference

## Tính năng

- 🇻🇳 Tổng hợp giọng nói tiếng Việt chất lượng cao
- 🎙️ Nhân bản giọng nói zero-shot chỉ từ ~5s audio mẫu
- 👥 5 giọng nói có sẵn (Bắc/Nam, Nam/Nữ)
- 🔒 Hoạt động hoàn toàn offline — không cần cloud API
- ⚡ Tăng tốc bằng GPU (CUDA) hoặc chạy trên CPU

## Install / Cài đặt

### 1. Clone and install / Clone và cài đặt

```bash
git clone https://github.com/tronghieuit/valtec-tts.git ~/.openclaw/tools/valtec-tts
cd ~/.openclaw/tools/valtec-tts
pip install -e .
```

Các model sẽ tự động tải từ HuggingFace khi chạy lần đầu.

### 2. Configure OpenClaw / Cấu hình OpenClaw

Update `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "valtec-tts": {
        env: {
          VALTEC_TTS_DIR: "~/.openclaw/tools/valtec-tts",
        },
      },
    },
  },
}
```

## Usage / Cách sử dụng

### Multi-speaker TTS (giọng nói có sẵn)

```bash
{baseDir}/bin/valtec-tts.js --speaker NF -o output.wav "Xin chào, tôi là trợ lý AI của bạn."
```

Các giọng nói có sẵn:
- `NF` — Nữ miền Bắc (Northern Female)
- `SF` — Nữ miền Nam (Southern Female)
- `NM1` — Nam miền Bắc 1 (Northern Male 1)
- `SM` — Nam miền Nam (Southern Male)
- `NM2` — Nam miền Bắc 2 (Northern Male 2)

### Zero-shot voice cloning (Nhân bản giọng nói)

Chỉ cần cung cấp một đoạn audio mẫu (~5 giây), hệ thống sẽ tổng hợp giọng nói mới với giọng đó:

```bash
{baseDir}/bin/valtec-tts.js --zeroshot --reference voice_sample.wav -o output.wav "Xin chào, tôi là trợ lý AI."
```

### Options / Tuỳ chọn

| Flag | Mặc định | Mô tả |
|------|----------|-------|
| `--speaker` | `NF` | Tên giọng: NF, SF, NM1, SM, NM2 |
| `--zeroshot` | — | Bật chế độ nhân bản giọng nói |
| `--reference` | — | Đường dẫn file audio mẫu (3-10 giây) |
| `-o, --output` | `tts.wav` | Đường dẫn file WAV đầu ra |
| `--speed` | `1.0` | Tốc độ nói (0.5–2.0) |

## Notes / Ghi chú

- Lần chạy đầu tiên sẽ tải ~300MB model weights (lưu cache cục bộ).
- Khuyến nghị dùng GPU (CUDA) để tổng hợp giọng nói realtime. CPU vẫn hoạt động nhưng chậm hơn (~3–5x RTF).
- Audio mẫu cho nhân bản giọng nên dài 3–10 giây, giọng rõ ràng, ít tạp âm.
- Model hỗ trợ tiếng Việt có dấu, tự động chuyển đổi phoneme.

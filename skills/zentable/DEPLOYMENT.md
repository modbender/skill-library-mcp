# Deployment Guide

This project is designed to run with Docker Compose using **two containers**:

- `renderer` (main render program)
- `ocr-api` (unified OCR FastAPI)

## Recommended topology

- Keep renderer and OCR separated for easier maintenance.
- Connect them via internal Docker network.
- Expose only required ports.

## Quick start (OCR API)

```bash
docker compose up -d --build
curl http://127.0.0.1:8001/health
```

## Skill Hub deployment (two FastAPI containers)

For skill-oriented deployment (CSS render API + OCR API), use:

```bash
cd /var/www/html/zenTable/deploy/skill-fastapi
cp .env.example .env
docker compose up -d --build
```

Default ports:

- CSS API: `http://127.0.0.1:8002/health`
- OCR API: `http://127.0.0.1:8001/health`

## Environment variables

Use `.env` to control OCR backend without code changes:

```env
OCR_BACKEND=auto
OCR_LANG=ch
USE_ANGLE_CLS=true
OCR_CPU_THREADS=4
OCR_ENABLE_MKLDNN=false
OCR_IR_OPTIM=false
OCR_PORT=8000
```

## Backend modes

- `auto` (default): openvino -> onnx -> paddle
- `openvino`: force OpenVINO EP
- `onnx`: force CPU ONNXRuntime
- `paddle`: force PaddleOCR

## Health checks

- `GET /health`
- `POST /ocr`
- `POST /ocr/base64`

The API response schema is stable across backends:

```json
{
  "success": true,
  "rows": [{"text":"...","left":0,"top":0,"width":0,"height":0}],
  "elapsed_ms": 123,
  "error": null
}
```

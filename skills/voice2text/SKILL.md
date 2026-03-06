---
name: voice2text
description: "slug: voice2text title: Voice to Text description: Offline
  speech-to-text skill using Vosk local model. author: lxxtad license: MIT"
---

# voice2text

slug: voice2text
title: Voice to Text
description: Offline speech-to-text skill using Vosk local model.
author: lxxtad
license: MIT

**入口**: `main.py` implements `run(params)` – pass `{"audio":"path/to.wav"}` and get `{"text":"transcript"}`.

**依赖**: `vosk`, `pytest`.

**使用示例**:
```bash
clawhub install voice2text
clawhub run voice2text '{"audio":"sample.wav"}'
```
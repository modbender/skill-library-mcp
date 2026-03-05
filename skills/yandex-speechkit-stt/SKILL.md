---
name: yandex-speechkit-stt
description: Распознавание речи через Yandex SpeechKit API для голосовых сообщений в Telegram. Используй когда пользователь отправляет голосовые сообщения и хочет, чтобы они расшифровывались через Yandex SpeechKit.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["ffmpeg", "python3"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "packages": ["PyJWT", "cryptography", "requests"],
            },
          ],
      },
  }
---

# Yandex SpeechKit STT

Скилл для быстрого и качественного распознавания голосовых сообщений через Yandex SpeechKit.

## Настройка

### Переменные окружения

Создай `config.json` в папке скилла:

```json
{
  "id": "your-key-id",
  "service_account_id": "your-service-account-id",
  "folder_id": "your-folder-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n..."
}
```

## Использование

### Из командной строки

```bash
python scripts/yandex_stt.py voice_message.ogg
```

### Из кода

```python
import sys
sys.path.insert(0, 'scripts')
from yandex_stt import speech_to_text, get_token_iam

# Получить IAM токен
iam_token = get_token_iam(folder_id, service_account_id, private_key, key_id)

# Распознать речь
result = speech_to_text("voice.ogg", folder_id, iam_token)
print(result)
```

## Особенности

- Автоматически обрезает аудио до 28 секунд (лимит Yandex)
- IAM токен автоматически обновляется через service account
- Работает с OggOpus, WAV, MP3

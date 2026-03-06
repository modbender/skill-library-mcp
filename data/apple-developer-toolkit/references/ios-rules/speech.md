---
description: "Implementation rules for speech"
---
# Speech

SPEECH RECOGNITION:
- import Speech; SFSpeechRecognizer()
- Requires NSSpeechRecognitionUsageDescription + NSMicrophoneUsageDescription (add CONFIG_CHANGES)
- SFSpeechRecognizer.requestAuthorization() for permission
- On-device: SFSpeechRecognizer(locale:), set requiresOnDeviceRecognition = true
- Live: SFSpeechAudioBufferRecognitionRequest + AVAudioEngine
- File: SFSpeechURLRecognitionRequest(url:)

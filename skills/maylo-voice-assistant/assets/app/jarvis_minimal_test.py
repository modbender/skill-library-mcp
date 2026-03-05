#!/usr/bin/env python3
"""Minimal openWakeWord test for 'hey_jarvis'.

- Uses official openWakeWord API
- Just prints scores to stdout

Run:
  cd /Users/mlo/.openclaw/workspace/maylo-voice-assistant
  source venv/bin/activate
  python jarvis_minimal_test.py

Then say clearly: "Hey Jarvis" a few times.
"""

import time

import numpy as np
import sounddevice as sd

import openwakeword
from openwakeword.model import Model

# Ensure pretrained models are present
openwakeword.utils.download_models()

SAMPLE_RATE = 16000
BLOCK_SIZE = 1280  # 80 ms @16kHz (recommended in docs/examples)

model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

print("[openWakeWord] Minimal test running...")
print("Say clearly: 'Hey Jarvis' while watching the scores.")


def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)
    # indata: float32 [-1,1]
    audio_int16 = (indata[:, 0] * 32767).astype(np.int16)
    pred = model.predict(audio_int16)
    # pred is a dict of {model_name: score}
    for name, score in pred.items():
        if "jarvis" in name:
            # Print only jarvis-related scores
            print(f"{name}: {score:.3f}")
            if score > 0.5:
                print("*** DETECTED (score>0.5) ***")


with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=BLOCK_SIZE, callback=audio_callback):
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting.")

#!/usr/bin/env python3
import time
import numpy as np
import sounddevice as sd

SAMPLE_RATE=16000
BLOCK=1280
DEVICE=1  # External Microphone

print('Testing mic level... device=', DEVICE)

rms_hist=[]

def cb(indata, frames, time_info, status):
    if status:
        print('STATUS', status)
    x=indata[:,0]
    rms=float(np.sqrt(np.mean(np.square(x))))
    peak=float(np.max(np.abs(x)))
    rms_hist.append(rms)
    print(f"rms={rms:.4f} peak={peak:.4f}")

with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=BLOCK, dtype='float32', callback=cb, device=DEVICE):
    time.sleep(5)

print('done')

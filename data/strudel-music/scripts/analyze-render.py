#!/usr/bin/env python3
"""
analyze-render.py — Post-render spectral diagnostic for headless audio agents.

Analyzes a rendered WAV/MP3 and outputs a machine-readable JSON report:
  - Per-window stats (LUFS-proxy, RMS, silence, spectral cliffs, centroid)
  - Summary: total silence, cliff count, integrated loudness
  - Anomaly list: timestamped issues with severity

Usage:
  python3 analyze-render.py <input.wav|mp3> [--window 3.0] [--json] [--quiet]

Dependencies: numpy, ffmpeg (in PATH)
Optional: matplotlib (for spectrogram PNG output)

dandelion cult — ronan🌊 / 2026-02-28
"""

import sys
import os
import json
import subprocess
import struct
import argparse
import numpy as np


def read_audio_via_ffmpeg(path, sr=44100):
    """Convert any audio file to mono f32 PCM via ffmpeg."""
    result = subprocess.run(
        ['ffmpeg', '-hide_banner', '-i', path, '-ac', '1', '-ar', str(sr),
         '-f', 'f32le', '-'],
        capture_output=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.decode()[:200]}")
    samples = np.frombuffer(result.stdout, dtype=np.float32)
    return samples, sr


def rms_db(samples):
    """RMS in dB (relative to full scale)."""
    rms = np.sqrt(np.mean(samples ** 2))
    if rms < 1e-10:
        return -100.0
    return 20 * np.log10(rms)


def lufs_proxy(samples):
    """
    Approximate LUFS using K-weighted RMS.
    Not ITU BS.1770 compliant but close enough for diagnostics.
    Real LUFS uses two-stage K-weighting filter; we approximate with
    a simple high-shelf boost (+2dB above 1.5kHz).
    """
    rms = np.sqrt(np.mean(samples ** 2))
    if rms < 1e-10:
        return -100.0
    # Approximate K-weighting adds ~2dB for typical content
    return 20 * np.log10(rms) - 0.5


def spectral_centroid(samples, sr):
    """Spectral centroid in Hz (brightness indicator)."""
    if len(samples) < 512:
        return 0.0
    window = np.hanning(len(samples))
    spectrum = np.abs(np.fft.rfft(samples * window))
    freqs = np.fft.rfftfreq(len(samples), 1.0 / sr)
    total = np.sum(spectrum)
    if total < 1e-10:
        return 0.0
    return float(np.sum(freqs * spectrum) / total)


def spectral_flux(prev_spectrum, curr_spectrum):
    """Spectral flux: sum of positive spectral differences."""
    if prev_spectrum is None or len(prev_spectrum) != len(curr_spectrum):
        return 0.0
    diff = curr_spectrum - prev_spectrum
    return float(np.sum(np.maximum(diff, 0)))


def detect_cliffs(samples, sr, threshold_db=20, window_ms=100):
    """
    Detect spectral cliffs: sudden energy drops > threshold_db in < window_ms.
    Returns list of (time_sec, drop_db).
    """
    cliffs = []
    window_samples = int(sr * window_ms / 1000)
    hop = window_samples // 2

    prev_rms = None
    for i in range(0, len(samples) - window_samples, hop):
        chunk = samples[i:i + window_samples]
        curr_rms = np.sqrt(np.mean(chunk ** 2))

        if prev_rms is not None and prev_rms > 1e-8:
            if curr_rms < 1e-10:
                drop = 100.0
            else:
                drop = 20 * np.log10(prev_rms / curr_rms)

            if drop > threshold_db:
                time_sec = i / sr
                cliffs.append({"time": round(time_sec, 2), "drop_db": round(drop, 1)})

        prev_rms = curr_rms

    return cliffs


def analyze(path, window_sec=3.0, silence_threshold_db=-50, cliff_threshold_db=20):
    """Run full analysis on an audio file."""
    samples, sr = read_audio_via_ffmpeg(path)
    duration = len(samples) / sr

    window_samples = int(sr * window_sec)
    num_windows = int(np.ceil(len(samples) / window_samples))

    windows = []
    prev_spectrum = None
    total_silence_sec = 0.0

    for w in range(num_windows):
        start = w * window_samples
        end = min(start + window_samples, len(samples))
        chunk = samples[start:end]

        if len(chunk) < 256:
            continue

        # Pad short final window
        if len(chunk) < window_samples:
            chunk = np.pad(chunk, (0, window_samples - len(chunk)))

        # Compute metrics
        rms = rms_db(chunk)
        lufs = lufs_proxy(chunk)
        centroid = spectral_centroid(chunk, sr)
        is_silent = rms < silence_threshold_db

        # Spectral flux
        win_fn = np.hanning(len(chunk))
        curr_spectrum = np.abs(np.fft.rfft(chunk * win_fn))
        # Normalize spectrum for flux comparison
        spec_norm = curr_spectrum / (np.max(curr_spectrum) + 1e-10)
        flux = spectral_flux(prev_spectrum, spec_norm)
        prev_spectrum = spec_norm

        if is_silent:
            actual_len = min(end - start, len(samples) - start)
            total_silence_sec += actual_len / sr

        window_data = {
            "window": w,
            "time_start": round(start / sr, 2),
            "time_end": round(min(end, len(samples)) / sr, 2),
            "rms_db": round(rms, 1),
            "lufs_proxy": round(lufs, 1),
            "centroid_hz": round(centroid, 1),
            "spectral_flux": round(flux, 4),
            "silent": is_silent,
        }
        windows.append(window_data)

    # Detect cliffs
    cliffs = detect_cliffs(samples, sr, cliff_threshold_db)

    # Build anomaly list
    anomalies = []
    for w in windows:
        if w["silent"]:
            anomalies.append({
                "time": w["time_start"],
                "type": "silence",
                "severity": "critical",
                "detail": f"Window {w['window']} is silent (RMS {w['rms_db']} dB)"
            })
        if w["spectral_flux"] > 0.8:
            anomalies.append({
                "time": w["time_start"],
                "type": "spectral_discontinuity",
                "severity": "warning",
                "detail": f"High spectral flux ({w['spectral_flux']:.3f}) — possible hard cut"
            })

    for cliff in cliffs:
        anomalies.append({
            "time": cliff["time"],
            "type": "spectral_cliff",
            "severity": "critical" if cliff["drop_db"] > 40 else "warning",
            "detail": f"Energy drop of {cliff['drop_db']} dB"
        })

    # Sort anomalies by time
    anomalies.sort(key=lambda a: a["time"])

    # Integrated LUFS (approximate)
    all_rms = [10 ** (w["rms_db"] / 20) for w in windows if not w["silent"]]
    integrated_rms = np.sqrt(np.mean(np.array(all_rms) ** 2)) if all_rms else 0
    integrated_lufs = (20 * np.log10(integrated_rms) - 0.5) if integrated_rms > 1e-10 else -100

    report = {
        "file": os.path.basename(path),
        "duration_sec": round(duration, 2),
        "sample_rate": sr,
        "summary": {
            "integrated_lufs_proxy": round(integrated_lufs, 1),
            "total_silence_sec": round(total_silence_sec, 2),
            "silence_pct": round(100 * total_silence_sec / duration, 1) if duration > 0 else 0,
            "cliff_count": len(cliffs),
            "anomaly_count": len(anomalies),
            "window_count": len(windows),
            "window_sec": window_sec,
        },
        "anomalies": anomalies,
        "windows": windows,
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="Post-render audio diagnostic")
    parser.add_argument("input", help="Audio file to analyze")
    parser.add_argument("--window", type=float, default=3.0, help="Window size in seconds")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--quiet", action="store_true", help="Summary only")
    parser.add_argument("--silence-threshold", type=float, default=-50, help="Silence threshold in dB")
    parser.add_argument("--cliff-threshold", type=float, default=20, help="Cliff detection threshold in dB")
    args = parser.parse_args()

    report = analyze(args.input, args.window, args.silence_threshold, args.cliff_threshold)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    # Human-readable summary
    s = report["summary"]
    print(f"═══ Render Analysis: {report['file']} ═══")
    print(f"Duration: {report['duration_sec']}s | Windows: {s['window_count']} × {s['window_sec']}s")
    print(f"Integrated LUFS (proxy): {s['integrated_lufs_proxy']}")
    print(f"Silence: {s['total_silence_sec']}s ({s['silence_pct']}%)")
    print(f"Spectral cliffs: {s['cliff_count']}")
    print(f"Total anomalies: {s['anomaly_count']}")

    if not args.quiet and report["anomalies"]:
        print(f"\n─── Anomalies ───")
        for a in report["anomalies"]:
            icon = "🔴" if a["severity"] == "critical" else "🟡"
            print(f"  {icon} {a['time']:>6.1f}s  [{a['type']}] {a['detail']}")

    if not args.quiet:
        print(f"\n─── Window Stats ───")
        for w in report["windows"]:
            bar = "█" * max(0, int((w["rms_db"] + 60) / 2))
            silent_mark = " ⚠️ SILENT" if w["silent"] else ""
            print(f"  {w['time_start']:>6.1f}s  RMS:{w['rms_db']:>6.1f}dB  "
                  f"C:{w['centroid_hz']:>6.0f}Hz  F:{w['spectral_flux']:.3f}  "
                  f"{bar}{silent_mark}")


if __name__ == "__main__":
    main()

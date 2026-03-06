# Resemblyzer Voice Similarity Scoring Guide

## Quick Reference

**Similarity score interpretation:**

- **< 0.75** = Different speakers
- **0.75 - 0.84** = Likely same speaker
- **0.85+** = Excellent match (same speaker)

## How Resemblyzer Works

Resemblyzer computes speaker embeddings (d-vectors) using a deep neural network trained on speaker verification. It:

1. Extracts audio features from each sample
2. Computes a 256-dimensional embedding vector representing the speaker's voice
3. Calculates cosine similarity between the two embeddings

**Range:** 0.0 (completely different) to 1.0 (identical)

## Score Interpretation

### 0.00 - 0.50: Clearly Different Speakers
- **What it means:** The voices are very different
- **Use case:** Confirming speaker separation worked correctly
- **Example:** Male vs. female voice, different accents, different vocal qualities

### 0.50 - 0.74: Different Speakers (Possible Similarities)
- **What it means:** Some vocal similarities but likely different people
- **Use case:** May indicate same gender/age range but different speakers
- **Example:** Two male voices with similar pitch, two female voices with similar tone

### 0.75 - 0.84: Likely Same Speaker
- **What it means:** High probability of same speaker, acceptable match
- **Use case:** Speaker verification, voice authentication
- **Example:** Same person recorded at different times or with different microphones
- **Action:** Acceptable for most verification tasks, but not ideal for cloning

### 0.85 - 0.95: Excellent Match
- **What it means:** Very high confidence, same speaker
- **Use case:** High-quality voice cloning verification, speaker identification
- **Example:** Clean samples from the same speaker with consistent recording quality
- **Action:** Ideal threshold for voice cloning quality assessment

### 0.95 - 1.00: Near Identical
- **What it means:** Extremely similar or identical recordings
- **Use case:** Confirming duplicate audio, very high-quality clones
- **Example:** Same audio file, slight variations in processing
- **Note:** Scores this high are rare unless comparing very similar recordings

## Factors Affecting Scores

### Positive Factors (Increase Score)
- **Clean audio** - No background noise or music
- **Short, focused samples** - 5-30 seconds of clear speech
- **Consistent recording quality** - Same microphone, environment
- **Similar emotional tone** - Neutral speech vs. neutral speech
- **Same language** - Model performs best within same language

### Negative Factors (Decrease Score)
- **Background noise or music** - Interferes with voice features
- **Long, varied samples** - Introduces more variability
- **Different recording conditions** - Phone vs. studio mic
- **Different emotional states** - Shouting vs. whispering
- **Different languages** - May reduce similarity even for same speaker
- **Multiple speakers** - If not properly isolated

## Practical Thresholds

### Voice Authentication (Security)
- **Strict:** 0.85+ (low false positive rate)
- **Balanced:** 0.80+ (moderate security)
- **Lenient:** 0.75+ (higher false positives, fewer false negatives)

### Voice Cloning Quality Assessment
- **Excellent clone:** 0.85+ (publish-ready)
- **Good clone:** 0.80-0.84 (acceptable, may need refinement)
- **Poor clone:** < 0.80 (needs better sample or settings)

### Speaker Diarization Validation
- **Confirming separation worked:** < 0.75 between different speaker segments
- **Confirming speaker continuity:** 0.75+ across segments of same speaker

## Common Use Cases

### 1. Voice Clone Quality Check
```bash
compare_voices.py --audio1 original_sample.wav --audio2 cloned_output.wav --threshold 0.85
```

**Expected:**
- Good clone: 0.85+
- Poor clone: < 0.80

### 2. Speaker Verification
```bash
compare_voices.py --audio1 enrollment.wav --audio2 test.wav --threshold 0.75
```

**Expected:**
- Same speaker: 0.75+
- Different speaker: < 0.75

### 3. Validating Speaker Separation
```bash
compare_voices.py --audio1 speaker1.wav --audio2 speaker2.wav --threshold 0.75
```

**Expected:**
- Successful separation: < 0.75 (confirms different speakers)
- Failed separation: 0.75+ (may indicate mixed speakers)

## Troubleshooting Low Scores

### Same speaker scoring < 0.75?

**Possible causes:**
- **Different recording quality** - Check microphones, environment
- **Background noise** - Use Demucs to isolate vocals
- **Different emotional tone** - Compare similar speaking styles
- **Poor audio quality** - Use cleaner, shorter samples

**Solutions:**
1. Pre-process audio with Demucs `--two-stems vocals`
2. Trim to shorter, cleaner segments (5-30s)
3. Ensure 16kHz+ sample rate
4. Remove silence/padding from samples

### Different speakers scoring > 0.75?

**Possible causes:**
- **Similar vocal characteristics** - Same gender, age, accent
- **Mixed/contaminated samples** - Multiple speakers in one file
- **Very short samples** - Not enough data for distinction

**Solutions:**
1. Use longer samples (15-30s) for better distinction
2. Re-run speaker diarization to ensure clean separation
3. Manually verify samples contain only target speaker
4. Try different segments from each speaker

## Technical Notes

- **Model:** Resemblyzer uses a GE2E (Generalized End-to-End) loss-trained encoder
- **Embedding size:** 256-dimensional d-vector
- **Metric:** Cosine similarity (dot product of normalized vectors)
- **Processing:** Audio is converted to mel-spectrograms before embedding
- **Speed:** CPU-based inference (typically 1-3 seconds per comparison)

## Related Scripts

- **compare_voices.py** - Main comparison tool
- **diarize_and_slice_mps.py** - Extract per-speaker samples for comparison

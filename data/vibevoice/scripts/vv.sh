#!/usr/bin/env bash
# VibeVoice CLI - Local Spanish TTS
# Part of vibevoice skill for OpenClaw

set -e

VIBEVOICE_DIR="${VIBEVOICE_DIR:-$HOME/VibeVoice}"
VOICE="${VIBEVOICE_VOICE:-sp-Spk1_man}"
OUTPUT="/tmp/vibevoice_output.ogg"
SPEED="${VIBEVOICE_SPEED:-1.15}"
TEXT=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -v|--voice)
            VOICE="$2"
            shift 2
            ;;
        -f|--file)
            TEXT=$(cat "$2")
            shift 2
            ;;
        -s|--speed)
            SPEED="$2"
            shift 2
            ;;
        -h|--help)
            echo "VibeVoice CLI - Local Spanish TTS"
            echo ""
            echo "Usage: vv.sh \"text\" [-o output.ogg] [-v voice] [-s speed]"
            echo "       vv.sh -f file.txt [-o output.ogg]"
            echo ""
            echo "Options:"
            echo "  -o, --output   Output file (default: /tmp/vibevoice_output.ogg)"
            echo "  -v, --voice    Voice to use (default: sp-Spk1_man)"
            echo "  -s, --speed    Speech speed 0.5-2.0 (default: 1.15)"
            echo "  -f, --file     Read text from file"
            echo ""
            echo "Environment:"
            echo "  VIBEVOICE_DIR    VibeVoice install path (default: ~/VibeVoice)"
            echo "  VIBEVOICE_VOICE  Default voice"
            echo "  VIBEVOICE_SPEED  Default speed"
            echo ""
            echo "Available voices:"
            ls "$VIBEVOICE_DIR/demo/voices/streaming_model/"*.pt 2>/dev/null | xargs -n1 basename | sed 's/.pt$//' || echo "  (install VibeVoice first)"
            exit 0
            ;;
        *)
            TEXT="$1"
            shift
            ;;
    esac
done

if [ -z "$TEXT" ]; then
    echo "Error: No text provided" >&2
    echo "Usage: vv.sh \"text\" [-o output.ogg]" >&2
    exit 1
fi

if [ ! -d "$VIBEVOICE_DIR" ]; then
    echo "Error: VibeVoice not found at $VIBEVOICE_DIR" >&2
    echo "Install: git clone https://github.com/microsoft/VibeVoice.git ~/VibeVoice" >&2
    exit 1
fi

# Temp files
TEMP_TEXT=$(mktemp /tmp/vibevoice_text_XXXXXX.txt)
TEMP_WAV=$(mktemp /tmp/vibevoice_wav_XXXXXX.wav)
trap "rm -f '$TEMP_TEXT' '$TEMP_WAV'" EXIT

echo "$TEXT" > "$TEMP_TEXT"

# Generate audio
cd "$VIBEVOICE_DIR"
source venv/bin/activate

python3 << PYEOF
import torch
import sys
import warnings
warnings.filterwarnings("ignore")

text = open("$TEMP_TEXT").read().strip()
output_wav = "$TEMP_WAV"
voice = "$VOICE"

from vibevoice.modular.modeling_vibevoice_streaming_inference import VibeVoiceStreamingForConditionalGenerationInference
from vibevoice.processor.vibevoice_streaming_processor import VibeVoiceStreamingProcessor

model_path = "microsoft/VibeVoice-Realtime-0.5B"
processor = VibeVoiceStreamingProcessor.from_pretrained(model_path)

model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,
    device_map="cuda",
    attn_implementation="sdpa",
)
model.eval()
model.set_ddpm_inference_steps(num_steps=5)

voice_path = f"$VIBEVOICE_DIR/demo/voices/streaming_model/{voice}.pt"
all_prefilled_outputs = torch.load(voice_path, map_location="cuda", weights_only=False)

inputs = processor.process_input_with_cached_prompt(
    text=text,
    cached_prompt=all_prefilled_outputs,
    padding=True,
    return_tensors="pt",
    return_attention_mask=True,
)

for k, v in inputs.items():
    if torch.is_tensor(v):
        inputs[k] = v.to("cuda")

import copy
outputs = model.generate(
    **inputs,
    max_new_tokens=None,
    cfg_scale=1.5,
    tokenizer=processor.tokenizer,
    generation_config={'do_sample': False},
    verbose=False,
    all_prefilled_outputs=copy.deepcopy(all_prefilled_outputs),
)

processor.save_audio(outputs.speech_outputs[0], output_path=output_wav)

audio_samples = outputs.speech_outputs[0].shape[-1]
duration = audio_samples / 24000
print(f"Generated {duration:.1f}s of audio", file=sys.stderr)
PYEOF

# Convert to output format with speed adjustment
if [[ "$OUTPUT" == *.ogg ]]; then
    ffmpeg -y -i "$TEMP_WAV" -af "atempo=$SPEED" -c:a libopus -b:a 64k "$OUTPUT" 2>/dev/null
elif [[ "$OUTPUT" == *.mp3 ]]; then
    ffmpeg -y -i "$TEMP_WAV" -af "atempo=$SPEED" -c:a libmp3lame -b:a 128k "$OUTPUT" 2>/dev/null
else
    ffmpeg -y -i "$TEMP_WAV" -af "atempo=$SPEED" "$OUTPUT" 2>/dev/null
fi

echo "MEDIA: $OUTPUT"

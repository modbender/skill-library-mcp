---
name: qwenspeak
description: Text-to-speech generation via Qwen3-TTS over SSH. Preset voices, voice cloning, voice design. Use when the user wants to generate speech audio, clone voices, or work with TTS.
compatibility: Requires ssh and a running qwenspeak instance. QWENSPEAK_HOST and QWENSPEAK_PORT env vars must be set.
metadata:
  author: psyb0t
  homepage: https://github.com/psyb0t/docker-qwenspeak
---

# qwenspeak

YAML-driven text-to-speech over SSH using Qwen3-TTS models.

For installation and deployment, see [references/setup.md](references/setup.md).

## SSH Wrapper

Use `scripts/qwenspeak.sh` for all commands. It handles host, port, and host key acceptance via `QWENSPEAK_HOST` and `QWENSPEAK_PORT` env vars.

```bash
scripts/qwenspeak.sh <command> [args]
scripts/qwenspeak.sh <command> < input_file
scripts/qwenspeak.sh <command> > output_file
```

## TTS Generation

Submit YAML, get a job UUID back immediately, poll for progress. Jobs run sequentially — one at a time, the rest queue up.

```bash
# Get the YAML template
scripts/qwenspeak.sh "tts print-yaml" > job.yaml

# Submit job
scripts/qwenspeak.sh "tts" < job.yaml
# {"id": "550e8400-...", "status": "queued", "total_steps": 3, "total_generations": 7}

# Check progress
scripts/qwenspeak.sh "tts get-job 550e8400"

# Follow job log
scripts/qwenspeak.sh "tts get-job-log 550e8400 -f"

# Download result
scripts/qwenspeak.sh "get hello.wav" > hello.wav
```

## YAML Structure

Global settings + list of steps. Each step loads a model, runs all its generations, then unloads. Settings cascade: global > step > generation.

```yaml
steps:
  - mode: custom-voice
    model_size: 1.7b
    speaker: Ryan
    language: English
    generate:
      - text: "Hello world"
        output: hello.wav
      - text: "I cannot believe this!"
        speaker: Vivian
        instruct: "Speak angrily"
        output: angry.wav

  - mode: voice-design
    generate:
      - text: "Welcome to our store."
        instruct: "A warm, friendly young female voice with a cheerful tone"
        output: welcome.wav

  - mode: voice-clone
    model_size: 1.7b
    ref_audio: ref.wav
    ref_text: "Transcript of reference"
    generate:
      - text: "First line in cloned voice"
        output: clone1.wav
      - text: "Second line"
        output: clone2.wav
```

## Modes

**custom-voice** — Pick from 9 preset speakers. 1.7B supports emotion/style via `instruct`.

**voice-design** — Describe the voice in natural language via `instruct`. 1.7B only.

**voice-clone** — Clone from reference audio. Set `ref_audio` and `ref_text` at step level to reuse across generations. `x_vector_only: true` skips transcript.

### Emotion trick for cloned voices

Upload references with different emotions, use separate steps:

```bash
scripts/qwenspeak.sh "create-dir refs"
scripts/qwenspeak.sh "put refs/happy.wav" < me_happy.wav
scripts/qwenspeak.sh "put refs/angry.wav" < me_angry.wav
```

```yaml
steps:
  - mode: voice-clone
    ref_audio: refs/happy.wav
    ref_text: "transcript of happy ref"
    generate:
      - text: "Great news everyone!"
        output: happy1.wav

  - mode: voice-clone
    ref_audio: refs/angry.wav
    ref_text: "transcript of angry ref"
    generate:
      - text: "This is unacceptable"
        output: angry1.wav
```

## Job Management

```bash
scripts/qwenspeak.sh "tts list-jobs"              # list all
scripts/qwenspeak.sh "tts list-jobs --json"        # JSON output
scripts/qwenspeak.sh "tts get-job <id>"            # job details
scripts/qwenspeak.sh "tts get-job-log <id>"        # view log
scripts/qwenspeak.sh "tts get-job-log <id> -f"     # follow log
scripts/qwenspeak.sh "tts cancel-job <id>"         # cancel
```

Statuses: `queued` → `running` → `completed` | `failed` | `cancelled`

Completed jobs auto-cleaned after 1 day, all jobs after 1 week. UUID prefixes work (e.g. first 8 chars).

## File Operations

All paths relative to the work directory. Traversal blocked.

| Command                | Description                        |
| ---------------------- | ---------------------------------- |
| `put <path>`           | Upload file from stdin             |
| `get <path>`           | Download file to stdout            |
| `list-files [--json]`  | List directory                     |
| `remove-file <path>`   | Delete a file                      |
| `create-dir <path>`    | Create directory                   |
| `remove-dir <path>`    | Remove empty directory             |
| `move-file <src> <dst>`| Move or rename                     |
| `copy-file <src> <dst>`| Copy a file                        |
| `file-exists <path>`   | Check if file exists (true/false)  |
| `search-files <glob>`  | Glob search (`**` recursive)       |

## Speakers

| Speaker  | Gender | Language | Description                                    |
| -------- | ------ | -------- | ---------------------------------------------- |
| Vivian   | Female | Chinese  | Bright, slightly edgy young voice              |
| Serena   | Female | Chinese  | Warm, gentle young voice                       |
| Uncle_Fu | Male   | Chinese  | Seasoned, low mellow timbre                    |
| Dylan    | Male   | Chinese  | Youthful Beijing dialect, clear natural timbre |
| Eric     | Male   | Chinese  | Lively Chengdu/Sichuan dialect, slightly husky |
| Ryan     | Male   | English  | Dynamic with strong rhythmic drive             |
| Aiden    | Male   | English  | Sunny American, clear midrange                 |
| Ono_Anna | Female | Japanese | Playful, light nimble timbre                   |
| Sohee    | Female | Korean   | Warm with rich emotion                         |

## YAML Options

All settings cascade: global > step > generation.

| Field                | Default   | Description                                                         |
| -------------------- | --------- | ------------------------------------------------------------------- |
| `dtype`              | `float32` | float32, float16, bfloat16 (float16/bfloat16 GPU only)             |
| `flash_attn`         | `auto`    | FlashAttention-2: auto-detects, auto-switches float32→bfloat16     |
| `temperature`        | `0.9`     | Sampling temperature                                                |
| `top_k`              | `50`      | Top-k sampling                                                      |
| `top_p`              | `1.0`     | Top-p / nucleus sampling                                            |
| `repetition_penalty` | `1.05`    | Repetition penalty                                                  |
| `max_new_tokens`     | `2048`    | Max codec tokens to generate                                        |
| `no_sample`          | `false`   | Greedy decoding                                                     |
| `streaming`          | `false`   | Streaming mode (lower latency)                                      |
| `mode`               | required  | Step only: `custom-voice`, `voice-design`, or `voice-clone`         |
| `model_size`         | `1.7b`    | Step only: `1.7b` or `0.6b`                                        |
| `text`               | required  | Text to synthesize                                                  |
| `output`             | required  | Output file path                                                    |
| `speaker`            | `Vivian`  | custom-voice: speaker name                                          |
| `language`           | `Auto`    | Language for synthesis                                               |
| `instruct`           | -         | custom-voice: emotion/style; voice-design: voice description        |
| `ref_audio`          | -         | voice-clone: reference audio file path                              |
| `ref_text`           | -         | voice-clone: transcript of reference audio                          |
| `x_vector_only`      | `false`   | voice-clone: use speaker embedding only                             |

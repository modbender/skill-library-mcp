import argparse, subprocess, tempfile, os, sys, textwrap

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True, help='Input text file')
parser.add_argument('--voice', default='elevenlabs', help='Voice/provider stub')
parser.add_argument('--chunk', type=int, default=3500, help='Max chars per TTS call')
parser.add_argument('--out', default='briefing.mp3', help='Output mp3 path')
args = parser.parse_args()

def load_text(path):
    if path == '-':
        return sys.stdin.read()
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def chunk_text(text, size):
    words = text.split()
    chunks, buf = [], []
    for w in words:
        if sum(len(x)+1 for x in buf) + len(w) + 1 > size:
            chunks.append(" ".join(buf))
            buf = []
        buf.append(w)
    if buf:
        chunks.append(" ".join(buf))
    return chunks

def synthesize(text, idx):
    # TODO: wire your TTS provider here (ElevenLabs, etc.)
    # Placeholder: write to a dummy wav using say command (mac) or skip
    path = tempfile.mktemp(suffix=f"_{idx}.wav")
    # Replace this with real TTS call; here we just make a silent file
    subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "1", "-q:a", "9", "-acodec", "pcm_s16le", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return path

def main():
    text = load_text(args.input)
    chunks = chunk_text(text, args.chunk)
    wavs = []
    try:
        for i, ch in enumerate(chunks):
            print(f"Synth chunk {i+1}/{len(chunks)}")
            wavs.append(synthesize(ch, i))
        concat_list = tempfile.mktemp(suffix="_list.txt")
        with open(concat_list, 'w') as f:
            for w in wavs:
                f.write(f"file '{w}'\n")
        subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", args.out], check=True)
        print(f"Output: {args.out}")
    finally:
        for w in wavs:
            if os.path.exists(w):
                os.remove(w)

if __name__ == '__main__':
    main()

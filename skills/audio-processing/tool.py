import argparse
import json
import sys
import os
import time
import subprocess
import shutil
import re

# SECURITY: Validate file paths to prevent path traversal
def validate_file_path(file_path, must_exist=True):
    """Validate file path for security"""
    if not file_path:
        return None
    
    # Resolve to absolute path
    abs_path = os.path.abspath(file_path)
    
    # Check for path traversal attempts
    if '..' in file_path:
        # Allow .. only if it resolves to a safe location
        pass  # We'll check after resolution
    
    if must_exist and not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {abs_path}")
    
    # SECURITY: Ensure path doesn't escape workspace or common system dirs
    forbidden_prefixes = ['/etc/', '/proc/', '/sys/', '/root/']
    for prefix in forbidden_prefixes:
        if abs_path.startswith(prefix):
            raise ValueError(f"Access denied: cannot access {prefix} directories")
    
    return abs_path

# Lazy imports
def get_whisper(): import whisper; return whisper
def get_gtts(): from gtts import gTTS; return gTTS
def get_librosa(): import librosa; return librosa

def run_ffmpeg(args):
    """Run ffmpeg command and check for errors"""
    try:
        # Check if ffmpeg is in path
        if not shutil.which("ffmpeg"):
            return False, "ffmpeg not found in PATH"
            
        cmd = ["ffmpeg", "-y"] + args
        # ffmpeg logs info to stderr
        process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, process.stderr.decode()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()
    except FileNotFoundError as e:
        return False, f"File not found: {str(e)}"
    except Exception as e:
        return False, f"FFmpeg error: {str(e)}"

def transcribe(file_path, model_name="base"):
    try:
        # SECURITY: Validate file path
        safe_path = validate_file_path(file_path, must_exist=True)
        
        whisper = get_whisper()
        model = whisper.load_model(model_name)
        result = model.transcribe(safe_path)
        return {"text": result["text"], "segments": result.get("segments", [])}
    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

def tts(text, output_path=None):
    try:
        # SECURITY: Validate text input
        if not text or not isinstance(text, str):
            return {"error": "Text is required and must be a string"}
        
        if len(text) > 10000:
            return {"error": "Text too long (max 10000 characters)"}
        
        if not output_path:
            output_path = f"tts_{int(time.time())}.mp3"
        
        # SECURITY: Validate output path
        safe_output = validate_file_path(output_path, must_exist=False)
        if safe_output:
            output_path = safe_output
        
        gTTS = get_gtts()
        tts_obj = gTTS(text=text, lang='en')
        tts_obj.save(output_path)
        return {"file_path": output_path, "status": "created"}
    except Exception as e:
        return {"error": str(e)}

def extract_features(file_path):
    try:
        # SECURITY: Validate file path
        safe_path = validate_file_path(file_path, must_exist=True)
        
        librosa = get_librosa()
        y, sr = librosa.load(safe_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        rms = librosa.feature.rms(y=y)
        
        return {
            "duration": duration,
            "sample_rate": sr,
            "mfcc_mean": mfcc.mean(axis=1).tolist(),
            "rms_mean": float(rms.mean())  # Convert numpy to Python float
        }
    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

def vad_segments(file_path, aggressiveness=2):
    try:
        # SECURITY: Validate file path
        safe_path = validate_file_path(file_path, must_exist=True)
        
        # Use ffmpeg silencedetect filter
        # noise=-30dB, duration=0.5s (adjust based on aggressiveness)
        # aggressiveness 1-3 map to silence thresholds roughly
        db_threshold = -30 - (aggressiveness * 5) # e.g. -40dB for agg 2
        
        cmd = [
            "-i", safe_path,
            "-af", f"silencedetect=noise={db_threshold}dB:d=0.3",
            "-f", "null",
            "-"
        ]
        
        success, stderr = run_ffmpeg(cmd)
        if not success:
            return {"error": f"FFmpeg VAD failed: {stderr}"}
            
        # Parse stderr for silence_start and silence_end
        # [silencedetect @ 0x...] silence_start: 10.5
        # [silencedetect @ 0x...] silence_end: 12.0
        
        silence_starts = []
        silence_ends = []
        
        for line in stderr.split('\n'):
            if "silence_start" in line:
                match = re.search(r'silence_start: ([\d\.]+)', line)
                if match:
                    silence_starts.append(float(match.group(1)))
            elif "silence_end" in line:
                match = re.search(r'silence_end: ([\d\.]+)', line)
                if match:
                    silence_ends.append(float(match.group(1)))
                    
        # Get total duration to close the last segment
        duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)', stderr)
        total_duration = 0
        if duration_match:
            h, m, s = map(float, duration_match.groups())
            total_duration = h*3600 + m*60 + s
            
        # Convert silence segments to speech segments
        speech_segments = []
        current_time = 0.0
        
        # Zip starts and ends. 
        # Logic: Speech is from 0 to first_silence_start
        # Then from first_silence_end to second_silence_start...
        
        # If file starts with silence (silence_start is 0 or close to 0)
        if silence_starts and silence_starts[0] < 0.1:
            current_time = silence_ends.pop(0)
            silence_starts.pop(0)
            
        for i in range(len(silence_starts)):
            if silence_starts[i] > current_time:
                speech_segments.append({
                    "start": current_time,
                    "end": silence_starts[i]
                })
            
            if i < len(silence_ends):
                current_time = silence_ends[i]
                
        # Handle trailing speech
        if current_time < total_duration:
             speech_segments.append({
                "start": current_time,
                "end": total_duration
            })
            
        return {"segments": speech_segments}
        
    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

def transform(file_path, operations):
    try:
        # SECURITY: Validate file path
        safe_path = validate_file_path(file_path, must_exist=True)
        
        # Build ffmpeg command filter chain
        filters = []
        # SECURITY: Validate output path
        output_path = validate_file_path(file_path + ".processed.wav", must_exist=False)
        if not output_path:
            output_path = file_path + ".processed.wav"
        
        # Base command
        cmd = ["-i", safe_path]
        
        for op in operations:
            if not isinstance(op, dict) or "op" not in op:
                continue
                
            if op["op"] == "trim":
                # Use -ss and -t for trimming
                start = str(op.get("start", 0))
                cmd = ["-ss", start] + cmd
                if "end" in op:
                    duration = str(op["end"] - op.get("start", 0))
                    cmd += ["-t", duration]
            elif op["op"] == "resample":
                cmd += ["-ar", str(op["rate"])]
            elif op["op"] == "normalize":
                # Simple normalization using loudnorm filter
                filters.append("loudnorm")

        if filters:
            cmd += ["-af", ",".join(filters)]
            
        cmd.append(output_path)
        
        success, err = run_ffmpeg(cmd)
        if not success:
            return {"error": f"FFmpeg failed: {err}"}
            
        return {"file_path": output_path}
    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["transcribe", "tts", "extract_features", "vad_segments", "transform"])
    parser.add_argument("--file_path", help="Path to input audio file")
    parser.add_argument("--text", help="Text for TTS")
    parser.add_argument("--output_path", help="Output path for generated files")
    parser.add_argument("--model", default="base", help="Whisper model size")
    parser.add_argument("--ops", help="JSON string of operations for transform")
    
    args = parser.parse_args()
    
    result = {"error": "Unknown action"}
    
    if args.action == "transcribe":
        if not args.file_path:
            print(json.dumps({"error": "file_path required"}))
            sys.exit(1)
        result = transcribe(args.file_path, args.model)
        
    elif args.action == "tts":
        if not args.text:
            print(json.dumps({"error": "text required"}))
            sys.exit(1)
        result = tts(args.text, args.output_path)
        
    elif args.action == "extract_features":
        if not args.file_path:
            print(json.dumps({"error": "file_path required"}))
            sys.exit(1)
        result = extract_features(args.file_path)
        
    elif args.action == "vad_segments":
        if not args.file_path:
            print(json.dumps({"error": "file_path required"}))
            sys.exit(1)
        result = vad_segments(args.file_path)

    elif args.action == "transform":
        if not args.file_path:
            print(json.dumps({"error": "file_path required"}))
            sys.exit(1)
        ops = []
        if args.ops:
            try:
                ops = json.loads(args.ops)
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON for --ops"}))
                sys.exit(1)
        result = transform(args.file_path, ops)

    print(json.dumps(result, indent=2))

import re
import sys
import subprocess

def speak(text, voice="en-us", rate=100, pitch=0.5):
    command = ["espeak-ng", text, "-v", voice, "-a", str(rate), "-p", str(pitch)]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            print(f"Error: {stderr.decode()}")
        else:
            print(stdout.decode())
    except FileNotFoundError:
        print("Error: espeak-ng not found. Please ensure it is installed and in your PATH.")

if len(sys.argv) > 1:
    texts = re.sub(r'[^a-zA-Z0-9\s]', '',sys.argv[1])
    # print(texts)
else:
    texts = "Hello, world"

try:
    speak(texts)
    print("Success")
except:
    print("Failed")
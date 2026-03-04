#!/usr/bin/env python3
# Ollama Model Tuner Script
import ollama
import json
import sys

model = sys.argv[1] if len(sys.argv)>1 else 'llama3'
dataset_file = sys.argv[2]

with open(dataset_file) as f:
    data = [json.loads(line) for line in f]

for i, item in enumerate(data[:10]):  # Test 10 samples
    resp = ollama.chat(model=model, messages=[{'role':'user', 'content':item['prompt']}])
    print(f"Sample {i}: {resp['message']['content'][:100]}...")

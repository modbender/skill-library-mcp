#!/usr/bin/env python3
import json
import sys
import time
import requests
import argparse
import random
from pathlib import Path

def poll_and_download(host_url, prompt_id, output=None):
    history_url = f'{host_url}/history/{prompt_id}'
    print(f'Polling {history_url}')
    while True:
        time.sleep(5)
        hist_resp = requests.get(history_url)
        hist_resp.raise_for_status()
        history = hist_resp.json()
        if prompt_id in history and history[prompt_id]['outputs']:
            print('Job complete')
            break
    outputs = history[prompt_id]['outputs']['85']
    if 'images' not in outputs or not outputs['images']:
        raise ValueError('No images in output')
    img_info = outputs['images'][0]
    filename = img_info['filename']
    subfolder_path = img_info.get('subfolder', '')
    print(f'Image: {filename} in {subfolder_path or "root"}')
    view_url = f'{host_url}/view?filename={filename}&type=output&subfolder={subfolder_path}'
    img_resp = requests.get(view_url)
    img_resp.raise_for_status()
    out_path = output or f'./gen-{prompt_id}.jpg'
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(img_resp.content)
    print(f'Saved: {out_path}')
    return out_path

def main():
    parser = argparse.ArgumentParser(description='ComfyUI Flux2 Image Generator')
    prompt_group = parser.add_mutually_exclusive_group(required=False)
    prompt_group.add_argument('prompt', nargs='?', help='Image prompt string (default, ignored with --watch)')
    prompt_group.add_argument('--structured-prompt', help='Structured JSON prompt string (sent directly as positive prompt)')
    parser.add_argument('--seed', type=int, default=None, help='Fixed seed (random otherwise)')
    parser.add_argument('--steps', type=int, default=5, help='Sampling steps (1-50)')
    parser.add_argument('--output', default=None, help='Output JPG path')
    parser.add_argument('--host', default='localhost:8188', help='ComfyUI host:port')
    parser.add_argument('--submit-only', action='store_true', help='Submit and print prompt_id only')
    parser.add_argument('--watch', help='Watch prompt_id and download')
    args = parser.parse_args()

    effective_prompt = args.prompt or args.structured_prompt

    host_url = f'http://{args.host}'

    workflow_path = Path(__file__).parent.parent / 'workflows' / 'flux2.json'
    if not workflow_path.exists():
        raise FileNotFoundError(f'Missing workflow: {workflow_path}')

    if args.watch:
        poll_and_download(host_url, args.watch, args.output)
    elif effective_prompt is None:
        parser.error('Prompt required unless --watch')
    else:
        # Load/modify workflow
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        workflow['76']['inputs']['value'] = effective_prompt
        seed = args.seed or random.randrange(sys.maxsize)
        workflow['77:73']['inputs']['noise_seed'] = seed
        workflow['77:62']['inputs']['steps'] = args.steps

        # Submit
        url = f'{host_url}/prompt'
        resp = requests.post(url, json={'prompt': workflow})
        resp.raise_for_status()
        data = resp.json()
        prompt_id = data['prompt_id']
        print(f'Submitted: prompt_id={prompt_id} (seed={seed}, steps={args.steps})')

        if args.submit_only:
            return

        # Poll/download
        poll_and_download(host_url, prompt_id, args.output or f'./gen-{seed}.jpg')

if __name__ == '__main__':
    main()
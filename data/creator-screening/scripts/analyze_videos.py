#!/usr/bin/env python3
"""
Analyze creator videos via Memories.ai API.
Supports two modes:
  - transcript: Audio-only transcription (sync, fast ~2s/video)
  - mai: Full visual+audio AI analysis (async, ~30s/video, needs webhook)

Usage:
  python3 analyze_videos.py --mode transcript --videos_per_creator 5 --urls "url1,url2"
  python3 analyze_videos.py --mode mai --video_seconds 30 --urls "url1,url2"
"""
import argparse, json, urllib.request, sys, os, time

MAVI_KEY = os.environ.get('MEMORIES_API_KEY', '')
MAVI_BASE = 'https://mavi-backend.memories.ai/serve/api/v2'

def detect_platform(url):
    """Detect platform from URL."""
    if 'instagram.com' in url: return 'instagram'
    if 'tiktok.com' in url: return 'tiktok'
    if 'youtube.com' in url or 'youtu.be' in url: return 'youtube'
    return 'instagram'

def normalize_url(url):
    """Normalize Instagram URLs to /reel/ format."""
    if 'instagram.com' in url:
        url = url.replace('/p/', '/reel/')
        url = url.replace('/reels/', '/reel/')
    return url.strip()

def get_transcript(video_url):
    """Get audio transcript (sync, fast)."""
    platform = detect_platform(video_url)
    url = f'{MAVI_BASE}/{platform}/video/transcript'
    body = {'video_url': normalize_url(video_url), 'channel': 'rapid'}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', MAVI_KEY)
    req.add_header('Content-Type', 'application/json')
    
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        result = json.loads(resp.read())
        if result.get('code') == '0000':
            d = result.get('data', {})
            transcripts = d.get('transcripts', [])
            if transcripts:
                return {'text': transcripts[0].get('text', ''), 'success': True}
            # YouTube format
            content = d.get('content', [])
            if content:
                full = ' '.join(c.get('text', '') for c in content)
                return {'text': full, 'success': True}
        return {'text': '', 'success': False, 'error': result.get('msg')}
    except Exception as e:
        return {'text': '', 'success': False, 'error': str(e)}

def submit_mai(video_url):
    """Submit for full MAI visual+audio analysis (async)."""
    platform = detect_platform(video_url)
    url = f'{MAVI_BASE}/{platform}/video/mai/transcript'
    body = {'video_url': normalize_url(video_url)}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', MAVI_KEY)
    req.add_header('Content-Type', 'application/json')
    
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        result = json.loads(resp.read())
        if result.get('code') == '0000':
            return {'task_id': result['data']['task_id'], 'success': True}
        return {'task_id': None, 'success': False, 'error': result.get('msg')}
    except Exception as e:
        return {'task_id': None, 'success': False, 'error': str(e)}

def main():
    parser = argparse.ArgumentParser(description='Analyze creator videos')
    parser.add_argument('--mode', default='mai', choices=['transcript', 'mai'])
    parser.add_argument('--videos_per_creator', type=int, default=5)
    parser.add_argument('--video_seconds', type=int, default=30, help='Seconds to analyze (MAI mode)')
    parser.add_argument('--urls', required=True, help='Comma-separated video URLs')
    parser.add_argument('--output', default='-', help='Output file (- for stdout)')
    args = parser.parse_args()
    
    urls = [u.strip() for u in args.urls.split(',') if u.strip()]
    urls = urls[:args.videos_per_creator]
    
    results = []
    for url in urls:
        print(f"Analyzing: {url}", file=sys.stderr, flush=True)
        
        if args.mode == 'transcript':
            r = get_transcript(url)
            results.append({'url': url, 'mode': 'transcript', **r})
        else:
            r = submit_mai(url)
            results.append({'url': url, 'mode': 'mai', **r})
        
        time.sleep(1)  # Rate limiting
    
    output = json.dumps(results, indent=2, default=str)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w') as f:
            f.write(output)

if __name__ == '__main__':
    main()

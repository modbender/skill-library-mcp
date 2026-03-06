#!/usr/bin/env python3
"""Parse YouTube VTT/SRT caption files into clean plain text."""
import sys, re

if len(sys.argv) < 2:
    print("Usage: parse-vtt.py <file.vtt|file.srt>", file=sys.stderr)
    sys.exit(1)

lines = open(sys.argv[1], encoding='utf-8', errors='ignore').read().splitlines()

texts = []
for line in lines:
    l = line.strip()
    # Skip headers, timestamps, sequence numbers, blank lines
    if not l:
        continue
    if l.startswith('WEBVTT') or l.startswith('Kind:') or l.startswith('Language:'):
        continue
    if re.match(r'^\d+$', l):
        continue
    if re.match(r'[\d:,\. ]+-->', l):
        continue
    # Strip inline VTT word-timing tags like <00:00:01.200><c> and </c>
    l = re.sub(r'<\d+:\d+:\d+\.\d+>', '', l)
    l = re.sub(r'</?c>', '', l)
    l = re.sub(r'<[^>]+>', '', l)
    # HTML entities
    l = l.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ')
    l = l.strip()
    if not l:
        continue
    # Deduplicate adjacent identical lines (YouTube rolling caption style)
    if not texts or texts[-1] != l:
        texts.append(l)

# For rolling captions, each "frame" shows 1-2 lines. We want just the unique sentences.
# Join and print
print(' '.join(texts))

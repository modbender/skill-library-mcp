#!/usr/bin/env python3
"""
YouTube VTT Altyazı Temizleme Scripti
Kullanım: python3 clean_transcript.py <input.vtt> [output.txt]
"""

import re
import sys
import os

def clean_vtt(input_file, output_file=None):
    """VTT dosyasını temizler ve düz metin olarak kaydeder."""
    
    if not os.path.exists(input_file):
        print(f"Hata: Dosya bulunamadı: {input_file}")
        sys.exit(1)
    
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Header satırlarını atla
        if line.startswith('WEBVTT'):
            continue
        if line.startswith('Kind:'):
            continue
        if line.startswith('Language:'):
            continue
        
        # Zaman damgalı satırları atla
        if '-->' in line:
            continue
        
        # Boş satırları atla
        if not line:
            continue
        
        # HTML benzeri tag'leri temizle
        cleaned = re.sub(r'<[^>]+>', '', line).strip()
        
        if cleaned:
            clean_lines.append(cleaned)
    
    # Ardışık tekrarları kaldır
    unique = []
    prev = ""
    for line in clean_lines:
        if line != prev:
            unique.append(line)
            prev = line
    
    clean_text = '\n'.join(unique)
    
    # Output dosyası belirtilmemişse, input'tan çıkar
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + "_clean.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(clean_text)
    
    return len(clean_text), len(unique)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python3 clean_transcript.py <input.vtt> [output.txt]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    chars, lines = clean_vtt(input_file, output_file)
    print(f"Temizlendi!")
    print(f"  Karakter: {chars}")
    print(f"  Satır: {lines}")
    if output_file:
        print(f"  Çıktı: {output_file}")

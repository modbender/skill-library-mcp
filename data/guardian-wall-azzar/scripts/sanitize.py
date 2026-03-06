import sys
import re
import base64

def detect_homoglyphs(text):
    # Deteksi karakter yang mirip latin tapi bukan latin (Cyrillic, Greek, dll)
    # Ini sangat dasar, tapi efektif buat deteksi awal
    suspicious_chars = []
    for char in text:
        if ord(char) > 127 and ord(char) < 2000: # Range umum homoglyphs
            suspicious_chars.append(char)
    return list(set(suspicious_chars))

def detect_base64(text):
    b64_pattern = r'(?:[A-Za-z0-9+/]{4}){3,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?'
    matches = re.findall(b64_pattern, text)
    found_b64 = []
    for m in matches:
        try:
            decoded = base64.b64decode(m).decode('utf-8', errors='ignore').lower()
            if any(k in decoded for k in ["ignore", "system", "override", "assistant", "password", "forget"]):
                found_b64.append(f"Base64 containing sensitive words: {decoded[:30]}...")
        except:
            continue
    return found_b64

def sanitize_text(text):
    alerts = []
    
    # 1. Zero-width space detection
    if '\u200b' in text or '\u200c' in text or '\u200d' in text:
        alerts.append("Hidden Zero-Width Spaces detected (Bypass attempt)")
        text = text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')

    # 2. Homoglyph detection
    glyphs = detect_homoglyphs(text)
    if glyphs:
        alerts.append(f"Non-Latin homoglyphs detected: {''.join(glyphs)}")

    # 3. Remove non-printable characters
    clean_text = "".join(ch for ch in text if ch.isprintable() or ch in ['\n', '\r', '\t'])
    
    # 4. Advanced Patterns from Security Research
    injection_patterns = {
        "Direct Override": r"ignore (all )?previous instructions|forget everything|disregard prior",
        "Persona Modulation": r"you are now (a|an)|act as|adopt the persona|imagine you are",
        "System Mimicry": r"\[system message\]|### system|\[admin\]|assistant:|user:",
        "Visual Evasion": r"display:none|font-size:0|visibility:hidden|color:transparent",
        "Markdown/HTML Exfiltration": r"!\[.*\]\(https?://.*\)|<img.*src=.*https?://.*>",
        "Obfuscation": r"(?:[a-zA-Z] ){5,}|(?:[a-zA-Z]-){5,}", # Spaced or hyphenated text
    }
    
    for label, pattern in injection_patterns.items():
        if re.search(pattern, clean_text, re.IGNORECASE):
            alerts.append(label)
            
    # 5. Base64 Detection
    b64_alerts = detect_base64(clean_text)
    alerts.extend(b64_alerts)
    
    # 6. Normalization
    clean_text = re.sub(r' +', ' ', clean_text)
    
    return clean_text, alerts

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 sanitize.py <text>")
        sys.exit(1)
        
    input_text = sys.argv[1]
    cleaned, alerts = sanitize_text(input_text)
    
    print("--- CLEANED TEXT ---")
    print(cleaned)
    if alerts:
        print("\n--- WARNING: SECURITY RISKS DETECTED ---")
        for alert in alerts:
            print(f"ALERT: {alert}")

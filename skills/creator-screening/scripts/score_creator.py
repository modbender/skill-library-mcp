#!/usr/bin/env python3
"""
Score a creator against a screening framework.
Uses profile metrics + video transcripts to evaluate each framework dimension.

Usage:
  python3 score_creator.py --framework cac-crusher --profile profile.json --transcripts transcripts.json
"""
import argparse, json, sys

# Signals detected from transcript text
REJECT_SIGNALS = {
    'lip_sync': ['lip sync', 'lipsync', 'trending audio', 'trending sound'],
    'trend_dependent': ['tag your', 'mention your', 'comment and win', 'follow for'],
    'emotional_drama': ['surprise visit', 'wait for it', 'transformation', 'emotional'],
    'product_spam': ['comment goat', 'comment link', 'dm for', 'link in bio'],
    'devotional_political': ['bhajan', 'sermon', 'political', 'motivational speech'],
}

QUALITY_SIGNALS = {
    'structured': ['step 1', 'step 2', 'here\'s how', 'let me explain', 'in this video'],
    'educational': ['learn', 'course', 'training', 'tutorial', 'guide'],
    'professional': ['enterprise', 'business', 'strategy', 'advisor', 'expert'],
}

def detect_signals(text):
    """Detect quality and reject signals from transcript text."""
    text_lower = text.lower()
    
    found_reject = {}
    for signal, keywords in REJECT_SIGNALS.items():
        for kw in keywords:
            if kw in text_lower:
                found_reject[signal] = kw
                break
    
    found_quality = {}
    for signal, keywords in QUALITY_SIGNALS.items():
        for kw in keywords:
            if kw in text_lower:
                found_quality[signal] = kw
                break
    
    return found_reject, found_quality

def classify_category(profile, transcripts):
    """Classify creator into Talking Head or Skit/Couple."""
    bio = (profile.get('bio') or '').lower()
    captions = ' '.join(t.get('caption', '') for t in transcripts).lower()
    
    skit_signals = ['actor', 'couple', 'comedy', 'skit', 'drama', 'biwi', 'husband', 'wife']
    talking_head_signals = ['expert', 'advisor', 'coach', 'educator', 'ca ', 'mba', 'course', 'training', 'business']
    
    skit_score = sum(1 for s in skit_signals if s in bio or s in captions)
    th_score = sum(1 for s in talking_head_signals if s in bio or s in captions)
    
    return 'B (Skit/Couple)' if skit_score > th_score else 'A (Talking Head)'

def score_cac_crusher(profile, transcripts):
    """Score against CAC Crusher framework."""
    scores = {}
    red_flags = []
    
    # Combine all transcript text
    all_text = ' '.join(t.get('text', '') for t in transcripts if t.get('text'))
    reject_signals, quality_signals = detect_signals(all_text)
    
    category = classify_category(profile, transcripts)
    
    # 2.1 Look & Feel — scored via MAI visual analysis or inferred from metrics
    # Without MAI, we infer from engagement and follower quality
    followers = profile.get('followers', 0)
    verified = profile.get('verified', False)
    avg_views = profile.get('avgViews', 0)
    eng_rate = profile.get('engagementRate', 0)
    
    look_feel = 'PASS' if verified else 'FLAG'
    if avg_views < 1000 and followers > 50000:
        look_feel = 'FAIL'
        red_flags.append('Dead engagement — possible fake followers')
    scores['look_feel'] = look_feel
    
    # 2.2 Audio — inferred from transcript quality
    has_transcript = bool(all_text.strip())
    transcript_length = len(all_text)
    scores['audio'] = 'PASS' if has_transcript and transcript_length > 50 else 'FLAG'
    
    # 3.x Format-specific
    if 'Talking Head' in category:
        if quality_signals:
            scores['format'] = 'PASS'
        elif reject_signals:
            scores['format'] = 'FAIL'
            for sig, kw in reject_signals.items():
                red_flags.append(f'Talking Head reject: {sig} ("{kw}")')
        else:
            scores['format'] = 'FLAG'
    else:  # Skit
        if 'lip_sync' in reject_signals or 'trend_dependent' in reject_signals:
            scores['format'] = 'FAIL'
            red_flags.append(f'Skit reject: lip-sync/trend-dependent content')
        elif 'emotional_drama' in reject_signals:
            scores['format'] = 'FAIL'
            red_flags.append('Skit reject: exaggerated emotional drama')
        else:
            scores['format'] = 'FLAG'
    
    # 4. Positioning
    if quality_signals and not reject_signals:
        scores['positioning'] = 'PASS'
    elif reject_signals:
        scores['positioning'] = 'FAIL'
    else:
        scores['positioning'] = 'FLAG'
    
    # Final verdict
    fails = sum(1 for v in scores.values() if v == 'FAIL')
    flags = sum(1 for v in scores.values() if v == 'FLAG')
    
    if fails > 0:
        verdict = 'REJECTED'
    elif flags >= 2:
        verdict = 'CONDITIONAL'
    else:
        verdict = 'APPROVED'
    
    return {
        'username': profile.get('username', '?'),
        'category': category,
        'followers': followers,
        'verified': verified,
        'avgViews': avg_views,
        'engagementRate': eng_rate,
        'scores': scores,
        'redFlags': red_flags,
        'qualitySignals': list(quality_signals.keys()),
        'rejectSignals': list(reject_signals.keys()),
        'verdict': verdict,
    }

def main():
    parser = argparse.ArgumentParser(description='Score creator against framework')
    parser.add_argument('--framework', default='cac-crusher')
    parser.add_argument('--profile', required=True, help='Profile JSON file')
    parser.add_argument('--transcripts', required=True, help='Transcripts JSON file')
    parser.add_argument('--output', default='-')
    args = parser.parse_args()
    
    profile = json.load(open(args.profile))
    transcripts = json.load(open(args.transcripts))
    
    if args.framework == 'cac-crusher':
        result = score_cac_crusher(profile, transcripts)
    else:
        print(f"Framework {args.framework} not implemented", file=sys.stderr)
        sys.exit(1)
    
    output = json.dumps(result, indent=2, default=str)
    if args.output == '-':
        print(output)
    else:
        with open(args.output, 'w') as f:
            f.write(output)

if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
Analyze email tone
Usage: python3 tone_analyzer.py "email text"
"""
import sys
import re

def analyze_tone(text):
    """Detect tone indicators in email text"""
    
    # Formal indicators
    formal_words = ['pursuant', 'hereby', 'aforementioned', 'regarding', 
                   'sincerely', 'respectfully', 'cordially', 'distinguished',
                   'esteemed', 'honored', 'whereby', 'henceforth', 'therein',
                   'notwithstanding', 'endeavor', 'forthwith']
    
    # Casual indicators  
    casual_words = ['hey', 'gonna', 'wanna', 'yeah', 'yep', 'nope',
                   'btw', 'fyi', 'lol', 'omg', 'tbh', 'idk', 'imo',
                   'cool', 'awesome', 'great', 'super', 'totally',
                   'kinda', 'sorta', 'gotta']
    
    # Aggressive indicators
    aggressive_words = ['immediately', 'must', 'unacceptable', 'ridiculous',
                       'obviously', 'clearly', 'need to', 'have to',
                       'demand', 'require', 'insist', 'completely wrong',
                       'terrible', 'awful', 'incompetent', 'pathetic',
                       'useless', 'stupid', 'idiotic', 'failure']
    
    # Polite indicators
    polite_words = ['please', 'kindly', 'would you', 'could you',
                   'appreciate', 'thank', 'grateful', 'apologize',
                   'sorry', 'pardon', 'excuse', 'hope', 'wonderful',
                   'delighted', 'pleased', 'honored']
    
    # Urgent indicators
    urgent_words = ['urgent', 'asap', 'immediately', 'right away',
                   'time-sensitive', 'critical', 'emergency', 'deadline']
    
    # Friendly indicators
    friendly_words = ['hope you\'re well', 'hope this finds you',
                     'looking forward', 'excited', 'happy to',
                     'glad', 'wonderful', 'great to hear']
    
    text_lower = text.lower()
    
    formal_count = sum(1 for w in formal_words if w in text_lower)
    casual_count = sum(1 for w in casual_words if w in text_lower)
    aggressive_count = sum(1 for w in aggressive_words if w in text_lower)
    polite_count = sum(1 for w in polite_words if w in text_lower)
    urgent_count = sum(1 for w in urgent_words if w in text_lower)
    friendly_count = sum(1 for phrase in friendly_words if phrase in text_lower)
    
    # Exclamation marks
    exclamations = len(re.findall(r'!', text))
    
    # ALL CAPS detection
    caps_words = len(re.findall(r'\b[A-Z]{2,}\b', text))
    
    # Question marks (curiosity/engagement)
    questions = len(re.findall(r'\?', text))
    
    # Determine primary tone
    tones = []
    if formal_count >= 2:
        tones.append("FORMAL")
    if casual_count >= 2:
        tones.append("CASUAL")
    if aggressive_count >= 2 or caps_words >= 2:
        tones.append("AGGRESSIVE")
    if polite_count >= 2:
        tones.append("POLITE")
    if exclamations >= 3:
        tones.append("ENTHUSIASTIC")
    if urgent_count >= 1:
        tones.append("URGENT")
    if friendly_count >= 1:
        tones.append("FRIENDLY")
    
    if not tones:
        tones.append("NEUTRAL")
    
    # Warnings
    warnings = []
    if aggressive_count >= 2:
        warnings.append("Email may sound confrontational or aggressive")
    if caps_words >= 3:
        warnings.append("Excessive capitalization (appears like shouting)")
    if exclamations >= 4:
        warnings.append("Too many exclamation marks (unprofessional)")
    if casual_count >= 3 and formal_count == 0:
        warnings.append("Very casual tone - consider audience appropriateness")
    
    # Recommendations
    recommendations = []
    if aggressive_count > 0 and polite_count == 0:
        recommendations.append("Add polite language to soften tone")
    if formal_count > 3 and friendly_count == 0:
        recommendations.append("Consider adding a friendly opening or closing")
    if questions > 3:
        recommendations.append("Too many questions - consider consolidating")
    
    return {
        'primary_tone': tones[0],
        'all_tones': tones,
        'formal_score': formal_count,
        'casual_score': casual_count,
        'aggressive_score': aggressive_count,
        'polite_score': polite_count,
        'urgent_score': urgent_count,
        'friendly_score': friendly_count,
        'exclamations': exclamations,
        'caps_words': caps_words,
        'questions': questions,
        'warnings': warnings,
        'recommendations': recommendations
    }

def get_tone_description(tone):
    """Get description for a tone"""
    descriptions = {
        'FORMAL': 'Professional and ceremonial language',
        'CASUAL': 'Relaxed and conversational style',
        'AGGRESSIVE': 'Confrontational or demanding tone',
        'POLITE': 'Courteous and respectful language',
        'ENTHUSIASTIC': 'Excited and energetic tone',
        'URGENT': 'Time-sensitive and pressing',
        'FRIENDLY': 'Warm and approachable',
        'NEUTRAL': 'Balanced and straightforward'
    }
    return descriptions.get(tone, 'Unknown tone')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tone_analyzer.py 'text'")
        print("Example: python3 tone_analyzer.py 'Please let me know if you have any questions!'")
        sys.exit(1)
    
    result = analyze_tone(sys.argv[1])
    
    print(f"📊 PRIMARY TONE: {result['primary_tone']}")
    print(f"   {get_tone_description(result['primary_tone'])}")
    
    if len(result['all_tones']) > 1:
        print(f"\n🎯 OTHER TONES DETECTED: {', '.join(result['all_tones'][1:])}")
    
    print(f"\n📈 TONE METRICS:")
    print(f"   Formal: {result['formal_score']} | Casual: {result['casual_score']}")
    print(f"   Polite: {result['polite_score']} | Aggressive: {result['aggressive_score']}")
    print(f"   Urgent: {result['urgent_score']} | Friendly: {result['friendly_score']}")
    print(f"   Exclamations: {result['exclamations']} | ALL CAPS words: {result['caps_words']}")
    print(f"   Questions: {result['questions']}")
    
    if result['warnings']:
        print(f"\n⚠️  WARNINGS:")
        for warning in result['warnings']:
            print(f"   • {warning}")
    
    if result['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in result['recommendations']:
            print(f"   • {rec}")
    
    if not result['warnings'] and not result['recommendations']:
        print(f"\n✅ Tone appears appropriate")

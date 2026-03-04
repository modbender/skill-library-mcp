#!/usr/bin/env python3
"""
Calculate email readability
Usage: python3 readability.py "email text"
"""
import sys
import re

def count_syllables(word):
    """Simple syllable counter"""
    word = word.lower().strip('.,!?;:')
    
    # Special cases
    if len(word) <= 3:
        return 1
    
    vowels = 'aeiouy'
    syllable_count = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent 'e'
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    
    # Adjust for common patterns
    if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
        syllable_count += 1
    
    # Every word has at least one syllable
    if syllable_count == 0:
        syllable_count = 1
        
    return syllable_count

def flesch_reading_ease(text):
    """Calculate Flesch Reading Ease score"""
    # Remove email-specific elements
    text = re.sub(r'http[s]?://\S+', '', text)  # URLs
    text = re.sub(r'\S+@\S+', '', text)  # Email addresses
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences) if sentences else 1
    
    words = text.split()
    words = [w for w in words if w.strip() and not w.isdigit()]
    word_count = len(words) if words else 1
    
    syllable_count = sum(count_syllables(word) for word in words)
    
    # Flesch Reading Ease formula
    score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
    return round(score, 1)

def flesch_kincaid_grade(text):
    """Calculate Flesch-Kincaid Grade Level"""
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences) if sentences else 1
    
    words = text.split()
    words = [w for w in words if w.strip() and not w.isdigit()]
    word_count = len(words) if words else 1
    
    syllable_count = sum(count_syllables(word) for word in words)
    
    grade = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
    return round(grade, 1)

def analyze_readability(text):
    """Analyze email readability"""
    # Clean text
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    
    words = text.split()
    words = [w for w in words if w.strip() and not w.isdigit()]
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences) if sentences else 1
    
    paragraphs = text.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    paragraph_count = len(paragraphs) if paragraphs else 1
    
    # Calculate metrics
    avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
    avg_sentence_length = len(words) / sentence_count
    avg_paragraph_length = len(sentences) / paragraph_count
    
    flesch_score = flesch_reading_ease(text)
    fk_grade = flesch_kincaid_grade(text)
    
    # Interpret Flesch Reading Ease score
    if flesch_score >= 90:
        level = "Very Easy"
        grade = "5th grade"
        desc = "Easily understood by an average 11-year-old"
    elif flesch_score >= 80:
        level = "Easy"
        grade = "6th grade"
        desc = "Conversational English for consumers"
    elif flesch_score >= 70:
        level = "Fairly Easy"
        grade = "7th grade"
        desc = "Easily understood by 13-year-old students"
    elif flesch_score >= 60:
        level = "Standard"
        grade = "8-9th grade"
        desc = "Plain English, easily understood by most"
    elif flesch_score >= 50:
        level = "Fairly Difficult"
        grade = "10-12th grade"
        desc = "Fairly difficult to read"
    elif flesch_score >= 30:
        level = "Difficult"
        grade = "College level"
        desc = "Difficult to read, best for college students"
    else:
        level = "Very Difficult"
        grade = "Graduate level"
        desc = "Very difficult, best for university graduates"
    
    # Identify issues
    issues = []
    if avg_sentence_length > 25:
        issues.append("Sentences are too long (avg {:.1f} words)".format(avg_sentence_length))
    if avg_word_length > 6:
        issues.append("Words are too complex (avg {:.1f} chars)".format(avg_word_length))
    if flesch_score < 60:
        issues.append("Overall readability is low ({})".format(level))
    if len(words) > 200:
        issues.append("Email is too long ({} words)".format(len(words)))
    
    # Recommendations
    recommendations = []
    if avg_sentence_length > 20:
        recommendations.append("Break long sentences into shorter ones (aim for 15-20 words)")
    if avg_word_length > 5.5:
        recommendations.append("Use simpler words where possible")
    if flesch_score < 60:
        recommendations.append("Simplify language for better clarity")
    if len(words) > 150:
        recommendations.append("Consider splitting into multiple emails or using bullet points")
    
    return {
        'flesch_score': flesch_score,
        'fk_grade': fk_grade,
        'level': level,
        'grade': grade,
        'description': desc,
        'avg_word_length': round(avg_word_length, 1),
        'avg_sentence_length': round(avg_sentence_length, 1),
        'avg_paragraph_length': round(avg_paragraph_length, 1),
        'total_words': len(words),
        'total_sentences': sentence_count,
        'total_paragraphs': paragraph_count,
        'issues': issues,
        'recommendations': recommendations
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 readability.py 'text'")
        print("Example: python3 readability.py 'This is a simple test email.'")
        sys.exit(1)
    
    result = analyze_readability(sys.argv[1])
    
    print(f"📖 READABILITY ANALYSIS")
    print(f"=" * 50)
    
    print(f"\n📊 SCORES:")
    print(f"   Flesch Reading Ease: {result['flesch_score']}/100")
    print(f"   Flesch-Kincaid Grade: {result['fk_grade']}")
    print(f"   Reading Level: {result['level']} ({result['grade']})")
    print(f"   {result['description']}")
    
    print(f"\n📏 STATISTICS:")
    print(f"   Total Words: {result['total_words']}")
    print(f"   Total Sentences: {result['total_sentences']}")
    print(f"   Total Paragraphs: {result['total_paragraphs']}")
    print(f"   Avg Word Length: {result['avg_word_length']} characters")
    print(f"   Avg Sentence Length: {result['avg_sentence_length']} words")
    print(f"   Avg Paragraph Length: {result['avg_paragraph_length']} sentences")
    
    if result['issues']:
        print(f"\n⚠️  ISSUES DETECTED:")
        for issue in result['issues']:
            print(f"   • {issue}")
    
    if result['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in result['recommendations']:
            print(f"   • {rec}")
    
    if not result['issues']:
        print(f"\n✅ Readability is good!")
    
    # Exit code: 0 if no issues, 1 if issues found
    sys.exit(1 if result['issues'] else 0)

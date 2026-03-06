#!/usr/bin/env python3
"""
Distillation Engine for Tiered Memory

Three-stage compression:
  Raw conversation (500B) → Distilled fact (80B) → Core summary (20B)

Modes:
  - rule: Rule-based extraction (regex/heuristics, no LLM)
  - llm: LLM-powered extraction (requires LLM endpoint)

Usage:
  distiller.py --text "raw conversation" --mode rule
  distiller.py --text "raw conversation" --mode llm --llm-endpoint http://...
  distiller.py --file conversation.txt --mode rule --output distilled.json
"""

import argparse
import json
import re
import sys
from datetime import datetime

# ─── Rule-Based Distillation ───

def extract_people(text):
    """Extract people/entities mentioned (simple heuristics)."""
    people = set()
    
    # Patterns for names
    patterns = [
        r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # FirstName LastName
        r'\b([A-Z][a-z]+)(?:\'s| said| told| asked)\b',  # Name's, Name said
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        people.update(matches)
    
    # Filter common words
    stopwords = {'User', 'Agent', 'I', 'You', 'We', 'They', 'He', 'She', 'It', 'The', 'And'}
    people = {p for p in people if p not in stopwords and len(p) > 2}
    
    return sorted(list(people))


def extract_topics(text):
    """Extract topics/categories (keywords with frequency)."""
    # Remove common words
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
        'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'this',
        'that', 'these', 'those', 'what', 'which', 'who', 'when', 'where',
        'why', 'how', 'said', 'told', 'asked', 'like', 'just', 'know',
        'think', 'want', 'need', 'going', 'get', 'got', 'make', 'made'
    }
    
    # Tokenize and count
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    freq = {}
    for word in words:
        if word not in stopwords:
            freq[word] = freq.get(word, 0) + 1
    
    # Top 5 by frequency
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:5]]


def extract_emotion(text):
    """Detect emotional state changes (basic sentiment)."""
    # Simple emotion keywords
    emotions = {
        'happy': ['happy', 'excited', 'great', 'wonderful', 'love', 'glad', 'pleased', 'delighted'],
        'sad': ['sad', 'unhappy', 'disappointed', 'upset', 'miss', 'lonely', 'depressed'],
        'angry': ['angry', 'frustrated', 'annoyed', 'mad', 'furious', 'irritated'],
        'worried': ['worried', 'concerned', 'anxious', 'nervous', 'afraid', 'scared'],
        'relieved': ['relieved', 'better', 'recovered', 'calmer', 'phew'],
        'grateful': ['thanks', 'thank', 'grateful', 'appreciate', 'thankful'],
    }
    
    text_lower = text.lower()
    detected = []
    
    for emotion, keywords in emotions.items():
        if any(kw in text_lower for kw in keywords):
            detected.append(emotion)
    
    if not detected:
        return 'neutral'
    elif len(detected) == 1:
        return detected[0]
    else:
        # Detect transition (e.g., "worried → relieved")
        return f"{detected[0]} → {detected[-1]}"


def extract_actions(text):
    """Extract actions/verbs (what happened or needs to happen)."""
    # Action verbs pattern
    action_verbs = [
        'decided', 'created', 'built', 'deployed', 'fixed', 'solved', 'completed',
        'started', 'finished', 'implemented', 'designed', 'planned', 'scheduled',
        'contacted', 'called', 'emailed', 'messaged', 'sent', 'received',
        'bought', 'sold', 'ordered', 'delivered', 'shipped',
        'need', 'want', 'should', 'must', 'have to', 'going to',
        'will', 'plan to', 'intend to', 'hope to'
    ]
    
    text_lower = text.lower()
    actions = []
    
    for verb in action_verbs:
        if verb in text_lower:
            # Extract sentence containing the verb
            sentences = re.split(r'[.!?]', text)
            for sent in sentences:
                if verb in sent.lower():
                    # Clean and truncate
                    sent_clean = sent.strip()[:60]
                    if sent_clean and sent_clean not in actions:
                        actions.append(sent_clean)
                    break
    
    return actions[:3]  # Max 3 actions


def extract_outcome(text):
    """Determine outcome/resolution (positive/negative/pending)."""
    positive = ['success', 'worked', 'completed', 'done', 'finished', 'resolved', 'solved', 'great']
    negative = ['failed', 'broken', 'error', 'problem', 'issue', 'wrong', 'stuck']
    pending = ['working on', 'in progress', 'need to', 'will', 'plan to', 'waiting']
    
    text_lower = text.lower()
    
    has_pos = any(kw in text_lower for kw in positive)
    has_neg = any(kw in text_lower for kw in negative)
    has_pend = any(kw in text_lower for kw in pending)
    
    if has_pos and not has_neg:
        return 'positive'
    elif has_neg and not has_pos:
        return 'negative'
    elif has_pend:
        return 'pending'
    else:
        return 'ongoing'


def distill_rule_based(text, max_bytes=100):
    """
    Rule-based distillation: extract structured info from text.
    
    Returns:
        dict: {fact, emotion, people, topics, actions, outcome}
    """
    # Extract components
    people = extract_people(text)
    topics = extract_topics(text)
    emotion = extract_emotion(text)
    actions = extract_actions(text)
    outcome = extract_outcome(text)
    
    # Generate fact (core sentence)
    # Take first substantive sentence
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 20]
    fact = sentences[0][:80] if sentences else text[:80]
    
    result = {
        'fact': fact,
        'emotion': emotion,
        'people': people,
        'topics': topics,
        'actions': actions,
        'outcome': outcome
    }
    
    # Ensure it fits within max_bytes
    result_json = json.dumps(result)
    if len(result_json) > max_bytes:
        # Truncate actions and topics
        result['actions'] = result['actions'][:2]
        result['topics'] = result['topics'][:3]
        result['people'] = result['people'][:3]
        result_json = json.dumps(result)
        
        if len(result_json) > max_bytes:
            # Further truncate fact
            result['fact'] = result['fact'][:50]
    
    return result


def generate_core_summary(distilled, max_bytes=30):
    """
    Stage 2 → 3: Generate one-line core summary from distilled fact.
    
    Args:
        distilled (dict): Output from distill_rule_based
        max_bytes (int): Max length for core summary
    
    Returns:
        str: One-line core summary
    """
    fact = distilled.get('fact', '')
    people = distilled.get('people', [])
    outcome = distilled.get('outcome', '')
    
    # Template: [People] fact [outcome]
    parts = []
    
    if people:
        parts.append(people[0])
    
    # Shorten fact
    fact_words = fact.split()[:8]
    parts.append(' '.join(fact_words))
    
    if outcome and outcome != 'ongoing':
        parts.append(f"({outcome})")
    
    summary = ' '.join(parts)
    
    # Truncate to max_bytes
    if len(summary) > max_bytes:
        summary = summary[:max_bytes-3] + '...'
    
    return summary


# ─── LLM-Based Distillation ───

def distill_llm(text, llm_endpoint, max_bytes=100):
    """
    LLM-powered distillation (requires external LLM endpoint).
    
    Args:
        text (str): Raw conversation text
        llm_endpoint (str): HTTP endpoint for LLM (POST JSON)
        max_bytes (int): Target size for distilled output
    
    Returns:
        dict: {fact, emotion, people, topics, actions, outcome}
    """
    import urllib.request
    
    prompt = f"""Extract structured information from this conversation:

Conversation:
{text[:1000]}

Output as JSON with these fields:
- fact: One-sentence summary (max 80 chars)
- emotion: Emotional state or change (e.g., "worried → relieved")
- people: List of people mentioned (names only)
- topics: List of main topics/keywords (max 5)
- actions: Actions taken or needed (max 3, brief)
- outcome: positive|negative|pending|ongoing

Keep total JSON under {max_bytes} bytes. Be concise."""

    payload = {
        'prompt': prompt,
        'max_tokens': 200,
        'temperature': 0.3
    }
    
    try:
        req = urllib.request.Request(
            llm_endpoint,
            data=json.dumps(payload).encode(),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.load(resp)
            # Assuming response is {text: "...json..."}
            response_text = result.get('text', result.get('response', ''))
            
            # Parse JSON from response
            # Handle markdown code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            distilled = json.loads(response_text.strip())
            return distilled
    
    except Exception as e:
        print(f"LLM distillation failed: {e}", file=sys.stderr)
        print("Falling back to rule-based distillation", file=sys.stderr)
        return distill_rule_based(text, max_bytes)


# ─── CLI ───

def main():
    parser = argparse.ArgumentParser(
        description='Conversation distillation engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rule-based distillation
  distiller.py --text "Had a great talk about the garden project..." --mode rule

  # LLM distillation
  distiller.py --text "..." --mode llm --llm-endpoint http://localhost:8080/complete

  # From file
  distiller.py --file conversation.txt --mode rule --output distilled.json

  # Generate core summary
  distiller.py --text "..." --mode rule --core-summary
        """
    )
    
    parser.add_argument('--text', help='Raw conversation text')
    parser.add_argument('--file', help='Read text from file')
    parser.add_argument('--mode', choices=['rule', 'llm'], default='rule',
                        help='Distillation mode (default: rule)')
    parser.add_argument('--llm-endpoint', help='LLM HTTP endpoint (required for --mode llm)')
    parser.add_argument('--max-bytes', type=int, default=100,
                        help='Max distilled size in bytes (default: 100)')
    parser.add_argument('--core-summary', action='store_true',
                        help='Also generate core summary (stage 2→3)')
    parser.add_argument('--output', help='Write output to file (JSON)')
    
    args = parser.parse_args()
    
    # Get input text
    if args.file:
        with open(args.file) as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        parser.error('--text or --file required')
    
    # Validate LLM mode
    if args.mode == 'llm' and not args.llm_endpoint:
        parser.error('--llm-endpoint required for --mode llm')
    
    # Distill
    if args.mode == 'rule':
        distilled = distill_rule_based(text, args.max_bytes)
    else:
        distilled = distill_llm(text, args.llm_endpoint, args.max_bytes)
    
    # Add metadata
    result = {
        'distilled': distilled,
        'mode': args.mode,
        'timestamp': datetime.now().isoformat(),
        'original_size': len(text),
        'distilled_size': len(json.dumps(distilled)),
        'compression_ratio': round(len(text) / len(json.dumps(distilled)), 1)
    }
    
    # Generate core summary if requested
    if args.core_summary:
        core = generate_core_summary(distilled, max_bytes=30)
        result['core_summary'] = core
        result['core_size'] = len(core)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Written to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Parse WhatsApp chat export and extract messages by sender."""

import re
import json
import sys
import os
from collections import Counter, defaultdict

# WhatsApp export format: [DD/MM/YYYY, HH:MM:SS] Sender: Message
PATTERN = re.compile(
    r'\[(\d{2}/\d{2}/\d{4}),\s(\d{2}:\d{2}:\d{2})\]\s(.+?):\s(.*)'
)

def parse_chat(filepath, target_name):
    """Parse WhatsApp export and return structured data."""
    messages = []
    target_msgs = []
    other_msgs = []
    current_msg = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            match = PATTERN.match(line)
            if match:
                if current_msg:
                    messages.append(current_msg)
                    if current_msg['sender'] == target_name:
                        target_msgs.append(current_msg)
                    else:
                        other_msgs.append(current_msg)

                date, time, sender, text = match.groups()
                current_msg = {
                    'date': date,
                    'time': time,
                    'sender': sender,
                    'text': text,
                    'is_target': sender == target_name
                }
            elif current_msg:
                # Continuation of previous message
                current_msg['text'] += '\n' + line

    # Don't forget the last message
    if current_msg:
        messages.append(current_msg)
        if current_msg['sender'] == target_name:
            target_msgs.append(current_msg)
        else:
            other_msgs.append(current_msg)

    return messages, target_msgs, other_msgs


def analyze(target_msgs, target_name):
    """Analyze target's messages for patterns."""
    texts = [m['text'] for m in target_msgs if m['text']]

    # Filter out system messages and media
    text_msgs = [t for t in texts if not t.startswith('<') and 'omitido' not in t.lower()
                 and 'Sent image' not in t and 'Sent video' not in t
                 and 'Sent audio' not in t and 'Sent sticker' not in t]

    # Word frequency
    all_words = ' '.join(text_msgs).lower().split()
    word_freq = Counter(all_words).most_common(100)

    # Message length stats
    lengths = [len(t.split()) for t in text_msgs]
    avg_len = sum(lengths) / len(lengths) if lengths else 0

    # Emoji usage
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]+", flags=re.UNICODE
    )
    emojis = []
    for t in text_msgs:
        emojis.extend(emoji_pattern.findall(t))
    emoji_freq = Counter(emojis).most_common(20)

    # Laugh patterns
    laugh_pattern = re.compile(r'k{3,}|ha{2,}|hua+|ahu+|kkkk+', re.IGNORECASE)
    laugh_count = sum(1 for t in text_msgs if laugh_pattern.search(t))

    # Expressions / recurring phrases (2-4 word ngrams)
    bigrams = []
    for t in text_msgs:
        words = t.lower().split()
        for i in range(len(words) - 1):
            bigrams.append(f"{words[i]} {words[i+1]}")
    bigram_freq = Counter(bigrams).most_common(50)

    return {
        'target_name': target_name,
        'total_messages': len(target_msgs),
        'text_messages': len(text_msgs),
        'avg_words_per_msg': round(avg_len, 1),
        'top_words': word_freq,
        'top_emojis': emoji_freq,
        'laugh_ratio': round(laugh_count / len(text_msgs), 2) if text_msgs else 0,
        'top_bigrams': bigram_freq,
    }


def main():
    if len(sys.argv) < 4:
        print("Usage: parse_chat.py <chat_export.txt> <target_name> <output_dir>")
        print("  chat_export.txt  - WhatsApp exported chat file")
        print("  target_name      - Name of person to clone (as in chat)")
        print("  output_dir       - Directory to save output")
        sys.exit(1)

    filepath = sys.argv[1]
    target_name = sys.argv[2]
    output_dir = sys.argv[3]

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print(f"Parsing chat from: {filepath}")
    print(f"Target: {target_name}")

    messages, target_msgs, other_msgs = parse_chat(filepath, target_name)

    print(f"Total messages: {len(messages)}")
    print(f"Target messages: {len(target_msgs)}")
    print(f"Other messages: {len(other_msgs)}")

    # Analyze
    stats = analyze(target_msgs, target_name)
    print(f"Text messages (no media): {stats['text_messages']}")
    print(f"Avg words per message: {stats['avg_words_per_msg']}")
    print(f"Laugh ratio: {stats['laugh_ratio']}")

    # Save parsed data
    output = {
        'stats': stats,
        'target_messages': [{'date': m['date'], 'time': m['time'], 'text': m['text']}
                           for m in target_msgs if m['text']],
        'other_messages': [{'date': m['date'], 'time': m['time'], 'sender': m['sender'], 'text': m['text']}
                          for m in other_msgs if m['text']],
    }

    output_path = os.path.join(output_dir, 'parsed_messages.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Output saved to: {output_path}")

    # Also save target messages as plain text for easy reading
    txt_path = os.path.join(output_dir, 'target_messages.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        for m in target_msgs:
            if m['text']:
                f.write(f"[{m['date']}, {m['time']}] {m['text']}\n")

    print(f"Target messages text saved to: {txt_path}")


if __name__ == '__main__':
    main()

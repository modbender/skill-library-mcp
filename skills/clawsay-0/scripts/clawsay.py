#!/usr/bin/env python3
import sys
from termcolor import colored


LOBSTER = r"""
                             ,.---._
                   ,,,,     /       `,
                    \\\\   /    '\_  ;
                     |||| /\/``-.__\;'
                     ::::/\/_
     {{`-.__.-'(`(^^(^^^(^ 9 `.========='
    {{{{{{ { ( ( (  (   (-----:=
     {{.-'~~'-.(,(,,(,,,(__6_.'=========.
                     ::::\/\
                     |||| \/\  ,-'/,
                    ////   \ `` _/ ;
                   ''''     \  `  .'
jgs                           `---'
"""

def make_bubble(text):
    lines = text.splitlines()
    width = max(len(l) for l in lines)
    border = "-" * (width + 2)
    bubble = [f" {border}"]
    for i, line in enumerate(lines):
        padded = line.ljust(width)
        if len(lines) == 1:
            bubble.append(f"< {padded} >")
        elif i == 0:
            bubble.append(f"/ {padded} \\")
        elif i == len(lines) - 1:
            bubble.append(f"\\ {padded} /")
        else:
            bubble.append(f"| {padded} |")
    bubble.append(f" {border}")
    return "\n".join(bubble)

def make_lobstersay(text, lobster_color=None, message_color=None):
    bubble = make_bubble(text)
    lobster = LOBSTER
    if lobster_color:
        lobster = colored(lobster, lobster_color)
    if message_color:
        bubble = colored(bubble, message_color)
    return f"{bubble}\n{lobster}"

def main():
    if len(sys.argv) < 2:
        print("Usage: lobstersay <message>", file=sys.stderr)
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    print(make_lobstersay(message, lobster_color="red"))

if __name__ == "__main__":
    main()

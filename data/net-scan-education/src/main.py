#!/usr/bin/env python3
"""net-scan-education minimal demo"""

def safe_explain(prompt: str) -> str:
    # Very safe, non-operational response
    return "This is a non-operational, educational response. No scanning commands will be executed. You asked: \"" + prompt + "\""

def main():
    # simple demo harness
    prompt = input("Enter prompt: ")
    print(safe_explain(prompt))

if __name__ == "__main__":
    main()

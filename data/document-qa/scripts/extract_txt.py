
import sys
import os

def extract_text_from_txt(txt_path):
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        return f"Error extracting text from TXT: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        txt_file_path = sys.argv[1]
        if os.path.exists(txt_file_path):
            extracted_text = extract_text_from_txt(txt_file_path)
            print(extracted_text)
        else:
            print(f"Error: File not found at {txt_file_path}")
    else:
        print("Usage: python extract_txt.py <path_to_txt_file>")

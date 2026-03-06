
from docx import Document
import sys
import os

def extract_text_from_docx(docx_path):
    text = ""
    try:
        document = Document(docx_path)
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"Error extracting text from DOCX: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        docx_file_path = sys.argv[1]
        if os.path.exists(docx_file_path):
            extracted_text = extract_text_from_docx(docx_file_path)
            print(extracted_text)
        else:
            print(f"Error: File not found at {docx_file_path}")
    else:
        print("Usage: python extract_docx.py <path_to_docx_file>")

# NOTE: This script requires the python-docx library.
# If running in a new environment, you might need to install it:
# pip install python-docx

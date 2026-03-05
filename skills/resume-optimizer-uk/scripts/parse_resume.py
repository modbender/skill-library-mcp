#!/usr/bin/env python3
"""
Parse .docx resume and extract structured content.
"""
import sys
import json
from docx import Document

def parse_resume(docx_path):
    """Extract content from resume docx file."""
    doc = Document(docx_path)
    
    resume_data = {
        "filename": docx_path,
        "sections": [],
        "raw_text": ""
    }
    
    current_section = {"title": "Header", "content": []}
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # Detect section headers (usually short, all caps or title case)
        if len(text) < 50 and (text.isupper() or text in [
            "EXPERIENCE", "EDUCATION", "SKILLS", "SUMMARY", "PROFILE",
            "PROJECTS", "CERTIFICATIONS", "AWARDS", "LANGUAGES"
        ]):
            if current_section["content"]:
                resume_data["sections"].append(current_section)
            current_section = {"title": text, "content": []}
        else:
            current_section["content"].append(text)
            resume_data["raw_text"] += text + "\n"
    
    if current_section["content"]:
        resume_data["sections"].append(current_section)
    
    return resume_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_resume.py <input.docx> [--output output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = "parsed_resume.json"
    
    if "--output" in sys.argv:
        output_file = sys.argv[sys.argv.index("--output") + 1]
    
    data = parse_resume(input_file)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Parsed resume saved to {output_file}")

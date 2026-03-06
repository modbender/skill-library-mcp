#!/usr/bin/env python3
"""
OCR Text Recognition Script
Usage: python3 ocr.py <file_path> [--output <output_file>]
Supported: .pdf, .jpg, .jpeg, .png
"""

import sys
import os
import json
import argparse

def extract_images_from_pdf(pdf_path):
    """Extract images from PDF"""
    import fitz
    
    images = []
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_images = page.get_images()
        
        for img_index, img in enumerate(page_images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            output_path = f"/tmp/pdf_page{page_num+1}_img{img_index}.{image_ext}"
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            images.append(output_path)
    
    doc.close()
    return images


def ocr_file(file_path, output_path=None):
    """Perform OCR recognition on file"""
    from paddleocr import PaddleOCR
    
    # Initialize OCR
    ocr = PaddleOCR(lang='ch', use_angle_cls=True)
    
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        # PDF: extract images first, then recognize
        images = extract_images_from_pdf(file_path)
        all_texts = []
        
        for img_path in images:
            print(f"Recognizing: {img_path}")
            result = ocr.predict(img_path)
            if result:
                texts = result[0].get('rec_texts', [])
                all_texts.extend(texts)
        
        # Clean up temporary images
        for img_path in images:
            try:
                os.remove(img_path)
            except:
                pass
        
        final_texts = all_texts
    else:
        # Image: recognize directly
        print(f"Recognizing: {file_path}")
        result = ocr.predict(file_path)
        
        if result and len(result) > 0:
            final_texts = result[0].get('rec_texts', [])
        else:
            final_texts = []
    
    # Output results
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            for text in final_texts:
                f.write(text + '\n')
        print(f"Results saved to: {output_path}")
    else:
        print("\n=== OCR Recognition Results ===\n")
        for text in final_texts:
            print(text)
    
    return final_texts


def main():
    parser = argparse.ArgumentParser(description='OCR Text Recognition Tool')
    parser.add_argument('file', help='File to recognize (PDF or image)')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    try:
        ocr_file(args.file, args.output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

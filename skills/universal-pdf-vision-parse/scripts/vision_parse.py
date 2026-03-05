import os
import sys
import base64
import argparse
import fitz  # PyMuPDF
import dashscope
from dashscope import MultiModalConversation

def pdf_to_base64_images(pdf_path, dpi=300):
    """Render PDF pages to base64 images at high resolution."""
    print(f"📦 Rendering PDF: {pdf_path} (DPI: {dpi})...")
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        # Increase quality for better OCR results
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        img_data = pix.tobytes("png")
        base64_str = base64.b64encode(img_data).decode("utf-8")
        images.append(base64_str)
    doc.close()
    return images

def call_vision_api(base64_image, page_num, total_pages, api_key):
    """Use Qwen-VL-Max to 'see' and transcribe the French-Chinese notes."""
    print(f"  ⏳ Scanning Page {page_num}/{total_pages} (Multimodal Mode)...")
    dashscope.api_key = api_key
    
    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"data:image/png;base64,{base64_image}"},
                {"text": (
                    "You are a professional multilingual document digitizer and language expert. "
                    "Your task is to fully transcribe this image of language learning notes or document content into Markdown.\n\n"
                    "RULES:\n"
                    "1. TRANSCRIPTION: Capture all foreign language terms, their pronunciations (if present), and any translations/explanations.\n"
                    "2. FORMAT: Use bold for terms/keywords, and italics for meanings/examples.\n"
                    "3. TABLES: Use Markdown tables for vocabulary lists, conjugations, or comparative data.\n"
                    "4. QUALITY: Fix any minor OCR artifacts but stay true to the original text layout and logic.\n"
                    "5. OUTPUT: Raw Markdown content only."
                )}
            ]
        }
    ]
    
    try:
        response = MultiModalConversation.call(model='qwen-vl-max', messages=messages)
        if response.status_code == 200:
            return response.output.choices[0].message.content[0]['text']
        else:
            return f"\n\n> [Error on Page {page_num}: {response.message}]\n\n"
    except Exception as e:
        return f"\n\n> [Exception on Page {page_num}: {str(e)}]\n\n"

def main():
    parser = argparse.ArgumentParser(description="French PDF Vision Parser Skill (v0.1)")
    parser.add_argument("--pdf", required=True, help="Input PDF path")
    parser.add_argument("--out", required=True, help="Output Markdown path")
    parser.add_argument("--api-key", required=False, help="DashScope API Key")
    parser.add_argument("--max-pages", type=int, default=2, help="Max pages to process (default 2, -1 for all)")
    args = parser.parse_args()

    api_key = args.api_key or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ Error: API Key missing.")
        sys.exit(1)

    images = pdf_to_base64_images(args.pdf)
    total_available = len(images)
    
    # Determine how many pages to process
    if args.max_pages == -1:
        pages_to_process = total_available
    else:
        pages_to_process = min(args.max_pages, total_available)
        
    print(f"📄 PDF has {total_available} pages. Processing {pages_to_process} pages (Limit: {args.max_pages})...")
    
    full_md = f"# {os.path.basename(args.pdf).replace('.pdf', '')}\n\n"
    
    for i in range(pages_to_process):
        page_md = call_vision_api(images[i], i + 1, pages_to_process, api_key)
        full_md += page_md + "\n\n---\n\n"

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(full_md.strip())
    
    print(f"✅ Finished! Markdown saved to: {args.out}")

if __name__ == "__main__":
    main()

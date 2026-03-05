// Note: office-text-extractor has ESM compatibility issues
// Using a simpler approach for PPTX conversion

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

async function convertPptxToMd(filePath) {
  try {
    // Check if we have python3 and python-pptx available
    try {
      execSync('python3 --version', { stdio: 'pipe' });
    } catch (error) {
      throw new Error('Python3 is required for PPTX conversion');
    }
    
    // Create a simple Python script to extract text from PPTX
    const pythonScript = `
import sys
from pptx import Presentation

def extract_text_from_pptx(file_path):
    prs = Presentation(file_path)
    text_content = []
    
    for i, slide in enumerate(prs.slides):
        text_content.append(f"=== Slide {i+1} ===")
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                if shape.text.strip():
                    text_content.append(shape.text)
        text_content.append("")  # Empty line between slides
    
    return '\\n'.join(text_content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <pptx-file>")
        sys.exit(1)
    
    try:
        text = extract_text_from_pptx(sys.argv[1])
        print(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
`;
    
    // Write Python script to temporary file
    const tempScriptPath = '/tmp/extract_pptx.py';
    fs.writeFileSync(tempScriptPath, pythonScript);
    
    // Try to install python-pptx if not available
    try {
      execSync('python3 -c "import pptx"', { stdio: 'pipe' });
    } catch (error) {
      console.warn('python-pptx not installed. Trying to install...');
      try {
        execSync('pip3 install python-pptx', { stdio: 'pipe' });
      } catch (installError) {
        throw new Error('Failed to install python-pptx. Please install manually: pip3 install python-pptx');
      }
    }
    
    // Execute Python script
    const result = execSync(`python3 "${tempScriptPath}" "${filePath}"`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    // Clean up
    fs.unlinkSync(tempScriptPath);
    
    return result;
    
  } catch (error) {
    // Fallback: return basic error or try alternative method
    console.warn(`PPTX conversion warning: ${error.message}`);
    
    // Alternative: use unzip to extract XML and parse
    try {
      const tempDir = `/tmp/pptx_${Date.now()}`;
      execSync(`unzip -q "${filePath}" -d "${tempDir}"`, { stdio: 'pipe' });
      
      let text = '';
      // Look for slide files
      const slideFiles = fs.readdirSync(`${tempDir}/ppt/slides`).filter(f => f.endsWith('.xml'));
      
      for (const slideFile of slideFiles) {
        const slideNum = slideFile.match(/slide(\d+)\.xml/)?.[1] || 'unknown';
        text += `=== Slide ${slideNum} ===\\n`;
        
        const content = fs.readFileSync(`${tempDir}/ppt/slides/${slideFile}`, 'utf-8');
        // Simple XML text extraction (very basic)
        const textMatches = content.match(/<a:t>([^<]+)<\/a:t>/g) || [];
        for (const match of textMatches) {
          const extracted = match.replace(/<a:t>|<\/a:t>/g, '');
          if (extracted.trim()) {
            text += extracted + '\\n';
          }
        }
        text += '\\n';
      }
      
      // Clean up
      execSync(`rm -rf "${tempDir}"`, { stdio: 'pipe' });
      
      return text || 'No text could be extracted from the PPTX file.';
      
    } catch (fallbackError) {
      throw new Error(`Failed to convert PPTX: ${error.message}. Fallback also failed: ${fallbackError.message}`);
    }
  }
}

module.exports = convertPptxToMd;

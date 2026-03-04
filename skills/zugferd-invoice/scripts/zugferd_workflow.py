#!/usr/bin/env python3
"""
ZUGFeRD Invoice Workflow - Sauberer Anhang-Ansatz

Der Zeitnachweis wird NICHT als Seiten gemergt, sondern als Datei-Anhang
via --attachments eingebettet. Das ist der einzig valide Weg für ZUGFeRD-Factur-X.

Ablauf:
1. Identifiziere eRechnung (XML-Träger) via Validation
2. Extrahiere ZUGFeRD XML
3. Kombiniere: eRechnung-PDF + XML + Zeitnachweis als Attachment
4. Validiere Finale-PDF

Usage:
    python3 zugferd_workflow.py --invoice RE.pdf --attachment TIME.pdf --output final.pdf

Requirements:
    - Java 11+ (für MustangProject)
    - mustang.jar: ~/.openclaw/tools/mustang/mustang.jar
"""

import argparse
import subprocess
import sys
import os
import shutil
from pathlib import Path

MUSTANG_JAR = os.path.expanduser("~/.openclaw/tools/mustang/mustang.jar")
WORK_DIR = Path(__file__).parent.parent / "temp"

def run_mustang(args):
    """Execute mustang.jar with Java 21"""
    cmd = ["java", "-jar", MUSTANG_JAR] + args
    env = os.environ.copy()
    env["PATH"] = "/opt/homebrew/opt/openjdk@21/bin:" + env.get("PATH", "")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
    return result.stdout, result.stderr, result.returncode

def validate(pdf_path):
    """Validate PDF - returns dict with status"""
    stdout, stderr, _ = run_mustang(["--action", "validate", "--source", pdf_path, "--no-notices"])
    output = stdout + stderr
    
    return {
        "pdf_compliant": "isCompliant=true" in output,
        "pdf_flavour": "pdf-a/3" if "pdf-a/3" in output.lower() else "unknown",
        "has_xml": "XML:valid" in output or "attached" in output.lower(),
        "xml_valid": "<summary status=\"valid\"/>" in output,
        "raw": output
    }

def extract_xml(pdf_path, out_xml):
    """Extract ZUGFeRD XML from PDF"""
    _, _, rc = run_mustang([
        "--action", "extract",
        "--source", pdf_path,
        "--out", out_xml
    ])
    return rc == 0 and os.path.exists(out_xml)

def combine(invoice_pdf, xml_file, attachment_pdf, output):
    """
    Main: Combine invoice PDF + ZUGFeRD XML + attachment file
    
    This creates a valid ZUGFeRD/Factur-X PDF where:
    - The invoice is the primary PDF/A-3 document
    - The XML is embedded (ZUGFeRD data)
    - The attachment is embedded as file attachment (not merged pages)
    """
    _, stderr, rc = run_mustang([
        "--action", "combine",
        "--source", invoice_pdf,      # Base PDF/A-3
        "--source-xml", xml_file,     # ZUGFeRD XML
        "--out", output,
        "--format", "zf",             # ZUGFeRD
        "--version", "2",             # Version 2
        "--profile", "T",             # EXTENDED profile
        "--attachments", attachment_pdf,  # Additional file attachment
        "--no-additional-attachments"
    ])
    
    if rc != 0 and os.path.exists(output):
        # Sometimes output exists even with stderr warnings
        return True
    
    return rc == 0 and os.path.exists(output) and os.path.getsize(output) > 1000

def workflow(invoice_pdf, attachment_pdf, output_path):
    """Main workflow"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("ZUGFeRD Factur-X Workflow")
    print("=" * 60)
    
    # Step 1: Identify which file is the e-invoice
    print("\n[1/4] Identifying e-invoice...")
    
    print(f"  Checking: {Path(invoice_pdf).name}")
    v1 = validate(invoice_pdf)
    print(f"    PDF/A-3: {'✅' if v1['pdf_compliant'] else '❌'}, XML: {'✅' if v1['has_xml'] else '❌'}")
    
    print(f"  Checking: {Path(attachment_pdf).name}")
    v2 = validate(attachment_pdf)
    print(f"    PDF/A-3: {'✅' if v2['pdf_compliant'] else '❌'}, XML: {'✅' if v2['has_xml'] else '❌'}")
    
    # Determine which is invoice
    if v1['has_xml']:
        einvoice, z_anhang = invoice_pdf, attachment_pdf
        print(f"\n  → e-invoice: {Path(einvoice).name}")
    elif v2['has_xml']:
        einvoice, z_anhang = attachment_pdf, invoice_pdf
        print(f"\n  → e-invoice: {Path(einvoice).name}")
    else:
        print("\n  ❌ No ZUGFeRD XML found in either file")
        return False
    
    # Step 2: Extract XML
    print("\n[2/4] Extracting ZUGFeRD XML...")
    xml_temp = WORK_DIR / "extracted_zugferd.xml"
    if not extract_xml(einvoice, str(xml_temp)):
        print("  ❌ Failed to extract XML")
        return False
    print(f"  ✓ XML extracted: {xml_temp}")
    
    # Step 3: Combine with attachment
    print("\n[3/4] Combining PDF + XML + Attachment...")
    print(f"  Method: Attachment embedding (not page merge)")
    print(f"  Base PDF: {Path(einvoice).name}")
    print(f"  Attachment: {Path(z_anhang).name}")
    
    temp_out = WORK_DIR / "combined.pdf"
    if not combine(einvoice, str(xml_temp), z_anhang, str(temp_out)):
        print("  ❌ Combine failed")
        print(f"  Error details available in: {WORK_DIR}/")
        return False
    print(f"  ✓ Combined: {temp_out}")
    
    # Step 4: Validate
    print("\n[4/4] Validating output...")
    result = validate(str(temp_out))
    
    # Copy to final destination
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    shutil.copy(temp_out, output_path)
    
    # Results
    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Output:      {os.path.abspath(output_path)}")
    print(f"Size:        {os.path.getsize(output_path) / 1024:.1f} KB")
    print(f"PDF/A-3:     {'✅ COMPLIANT' if result['pdf_compliant'] else '⚠️ NON-COMPLIANT'}")
    print(f"Has XML:     {'✅' if result['has_xml'] else '❌'}")
    print(f"ZUGFeRD:     {'✅ VALID' if result['xml_valid'] else '⚠️ WARNINGS'}")
    print(f"Status:      {'✅ READY FOR EN16931' if result['xml_valid'] else '⚠️ REVIEW NEEDED'}")
    print("=" * 60)
    
    return result['xml_valid']

def main():
    parser = argparse.ArgumentParser(
        description="Create ZUGFeRD compliant PDF with file attachment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
    %(prog)s --invoice Rechnung.pdf --attachment Zeitnachweis.pdf \\
             --output Rechnung_mit_Anhang.pdf
        
Note:
    The attachment is embedded as a FILE attachment, not merged as pages.
    This preserves PDF/A-3 compliance and follows ZUGFeRD/Factur-X spec.
        """
    )
    parser.add_argument("--invoice", required=True, help="PDF containing ZUGFeRD XML")
    parser.add_argument("--attachment", required=True, help="Additional PDF to attach")
    parser.add_argument("--output", "-o", required=True, help="Output path")
    
    args = parser.parse_args()
    
    success = workflow(args.invoice, args.attachment, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
ZUGFeRD Invoice Workflow - Sichtbare Seiten + ZUGFeRD-konform

Workflow (basierend auf lokalem Macbook-Prozess von Heiko):
1. ZUGFeRD XML aus e-Rechnung extrahieren (mustangproject)
2. PDFs mit GhostScript mergen (sichtbare Seiten)
3. Merged PDF zu PDF/A-3 konvertieren (GhostScript)
4. XML wieder einbetten (mustangproject combine)
5. Validieren

Usage:
    python3 zugferd_pages_workflow.py \
        --invoice Rechnung.pdf \
        --attachment Zeitnachweis.pdf \
        --output Rechnung_mit_Anhang.pdf

Requirements:
    - Java 11+ (für MustangProject)
    - GhostScript (gs): brew install ghostscript
    - mustang.jar: ~/.openclaw/tools/mustang/mustang.jar
"""

import argparse
import subprocess
import sys
import os
import shutil
import tempfile
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

def run_ghostscript(args):
    """Execute GhostScript (gs)"""
    cmd = ["gs"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.stdout, result.stderr, result.returncode

def validate(pdf_path):
    """Validate PDF - returns dict with status"""
    stdout, stderr, _ = run_mustang(["--action", "validate", "--source", pdf_path, "--no-notices"])
    output = stdout + stderr
    
    return {
        "pdf_compliant": "isCompliant=true" in output,
        "pdf_flavour": "pdf-a/3" if "pdf-a/3" in output.lower() else ("pdf-a/1" if "pdf-a/1" in output.lower() else "unknown"),
        "has_xml": "XML:valid" in output or "attached" in output.lower(),
        "xml_valid": "<summary status=\"valid\"/>" in output,
        "raw": output
    }

def extract_xml(pdf_path, out_xml):
    """Extract ZUGFeRD XML from PDF"""
    _, stderr, rc = run_mustang([
        "--action", "extract",
        "--source", pdf_path,
        "--out", out_xml
    ])
    success = rc == 0 and os.path.exists(out_xml) and os.path.getsize(out_xml) > 100
    if not success and os.path.exists(out_xml):
        # Debug output
        print(f"    Debug: XML file exists but may be empty: {os.path.getsize(out_xml)} bytes")
        print(f"    stderr: {stderr[:500]}")
    return success

def merge_pdfs_ghostscript(pdf1, pdf2, output):
    """
    Step 2: Merge PDFs using GhostScript (sichtbare Seiten)
    """
    args = [
        "-dBATCH",
        "-dNOPAUSE",
        "-sDEVICE=pdfwrite",
        "-sOutputFile=" + output,
        "-dQUIET",
        pdf1,
        pdf2
    ]
    stdout, stderr, rc = run_ghostscript(args)
    
    if rc != 0:
        print(f"    GhostScript merge error: {stderr[:500]}")
        return False
    
    return os.path.exists(output) and os.path.getsize(output) > 1000

def convert_to_pdfa3(input_pdf, output_pdf):
    """
    Step 3: Convert merged PDF to PDF/A-3 using GhostScript
    """
    args = [
        "-dPDFA=3",
        "-dBATCH",
        "-dNOPAUSE",
        "-sDEVICE=pdfwrite",
        "-dPDFACompatibilityPolicy=1",
        "-sColorConversionStrategy=RGB",
        "-sOutputFile=" + output_pdf,
        "-dQUIET",
        input_pdf
    ]
    stdout, stderr, rc = run_ghostscript(args)
    
    if rc != 0:
        print(f"    GhostScript PDF/A-3 conversion error: {stderr[:500]}")
        return False
    
    return os.path.exists(output_pdf) and os.path.getsize(output_pdf) > 1000

def combine_with_xml(pdfa3_pdf, xml_file, output):
    """
    Step 4: Combine PDF/A-3 with ZUGFeRD XML (re-embed)
    """
    _, stderr, rc = run_mustang([
        "--action", "combine",
        "--source", pdfa3_pdf,
        "--source-xml", xml_file,
        "--out", output,
        "--format", "zf",
        "--version", "1",  # User specified version 1
        "--profile", "T",
        "--no-additional-attachments"
    ])
    
    if rc != 0:
        print(f"    MustangProject combine error: {stderr[:500]}")
    
    return os.path.exists(output) and os.path.getsize(output) > 1000

def workflow(invoice_pdf, attachment_pdf, output_path):
    """Main workflow with sichtbare Seiten"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("ZUGFeRD Workflow mit SICHTBAREN SEITEN")
    print("=" * 70)
    print(f"Rechnung:   {Path(invoice_pdf).name}")
    print(f"Anhang:     {Path(attachment_pdf).name}")
    print(f"Output:     {output_path}")
    print("=" * 70)
    
    # Step 1: Identify e-invoice and extract XML
    print("\n[1/5] Extrahiere ZUGFeRD XML...")
    
    # Test both files - the one with XML is the invoice
    xml_temp = WORK_DIR / "extracted_zugferd.xml"
    
    invoice_file = None
    for test_file in [invoice_pdf, attachment_pdf]:
        print(f"  Teste: {Path(test_file).name}")
        if extract_xml(test_file, str(xml_temp)):
            invoice_file = test_file
            print(f"  ✓ XML gefunden in: {Path(test_file).name}")
            break
    
    if not invoice_file:
        print("  ❌ Keine ZUGFeRD XML in beiden Dateien gefunden!")
        return False
    
    other_file = attachment_pdf if invoice_file == invoice_pdf else invoice_pdf
    
    # Step 2: Merge PDFs
    print("\n[2/5] Merge PDFs mit GhostScript...")
    merged_pdf = WORK_DIR / "merged.pdf"
    if not merge_pdfs_ghostscript(invoice_file, other_file, str(merged_pdf)):
        print("  ❌ Merge fehlgeschlagen!")
        return False
    print(f"  ✓ Gemerged: {merged_pdf} ({merged_pdf.stat().st_size / 1024:.1f} KB)")
    
    # Step 3: Convert to PDF/A-3
    print("\n[3/5] Konvertiere zu PDF/A-3...")
    pdfa3_pdf = WORK_DIR / "merged_pdfa3.pdf"
    if not convert_to_pdfa3(str(merged_pdf), str(pdfa3_pdf)):
        print("  ❌ PDF/A-3 Konvertierung fehlgeschlagen!")
        return False
    print(f"  ✓ PDF/A-3: {pdfa3_pdf} ({pdfa3_pdf.stat().st_size / 1024:.1f} KB)")
    
    # Validate intermediate PDF/A-3
    print("    Validiere PDF/A-3...")
    v_mid = validate(str(pdfa3_pdf))
    print(f"    PDF/A-3 kompliant: {'✅' if v_mid['pdf_compliant'] else '❌'} ({v_mid['pdf_flavour']})")
    
    # Step 4: Re-embed XML
    print("\n[4/5] Bette ZUGFeRD XML ein...")
    combined_pdf = WORK_DIR / "zugferd_combined.pdf"
    if not combine_with_xml(str(pdfa3_pdf), str(xml_temp), str(combined_pdf)):
        print("  ❌ XML Einbettung fehlgeschlagen!")
        return False
    print(f"  ✓ Kombiniert: {combined_pdf}")
    
    # Step 5: Validate final
    print("\n[5/5] Validiere finale ZUGFeRD PDF...")
    result = validate(str(combined_pdf))
    
    # Copy to final destination
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    shutil.copy(combined_pdf, output_path)
    
    # Results
    print("\n" + "=" * 70)
    print("ERGEBNIS")
    print("=" * 70)
    print(f"Output:          {os.path.abspath(output_path)}")
    print(f"Größe:           {os.path.getsize(output_path) / 1024:.1f} KB")
    print(f"Seiten:          ✅ Sichtbar gemerged")
    print(f"PDF/A-3:         {'✅ COMPLIANT' if result['pdf_compliant'] else '❌ FAILED'}")
    print(f"ZUGFeRD XML:     {'✅ Eingebettet' if result['has_xml'] else '❌ Fehlt'}")
    print(f"Validierung:     {'✅ VALID' if result['xml_valid'] else '⚠️ MIT WARNUNGEN'}")
    print(f"Status:          {'✅ ZUGFeRD-konform mit sichtbaren Seiten!' if result['xml_valid'] else '❌ Prüfung erforderlich'}")
    print("=" * 70)
    
    if result['xml_valid']:
        print("\n🎉 Erfolgreich! Mehrseitige ZUGFeRD-Rechnung erstellt.")
    else:
        print("\n⚠️ Achtung: Validierungswarnungen vorhanden.")
    
    return result['xml_valid']

def main():
    parser = argparse.ArgumentParser(
        description="ZUGFeRD Workflow mit sichtbaren Seiten (alle Tools)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflow:
  1. XML extrahieren (mustangproject)
  2. PDFs mergen (GhostScript) ← sichtbare Seiten!
  3. Zu PDF/A-3 konvertieren (GhostScript)
  4. XML einbetten (mustangproject combine)
  5. Validieren

Example:
    %(prog)s --invoice Rechnung.pdf --attachment Zeitnachweis.pdf \\
             --output Rechnung_komplett.pdf
        """
    )
    parser.add_argument("--invoice", "-i", required=True, 
                       help="PDF mit ZUGFeRD XML (Rechnung)")
    parser.add_argument("--attachment", "-a", required=True,
                       help="Zusätzliche PDF (Zeitnachweis)")
    parser.add_argument("--output", "-o", required=True,
                       help="Output Pfad")
    
    args = parser.parse_args()
    
    # Check dependencies
    missing = []
    if not os.path.exists(MUSTANG_JAR):
        missing.append(f"mustang.jar nicht gefunden: {MUSTANG_JAR}")
    
    gs_check = subprocess.run(["which", "gs"], capture_output=True)
    if gs_check.returncode != 0:
        missing.append("GhostScript (gs) nicht installiert: brew install ghostscript")
    
    if missing:
        print("❌ Fehlende Abhängigkeiten:")
        for m in missing:
            print(f"   - {m}")
        sys.exit(1)
    
    success = workflow(args.invoice, args.attachment, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

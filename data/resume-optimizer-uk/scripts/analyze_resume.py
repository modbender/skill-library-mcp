#!/usr/bin/env python3
"""
Five-dimension resume analysis against job description.
"""
import sys
import json
import re
from collections import Counter

def calculate_jd_match(resume_text, jd_text=None):
    """Calculate JD match score based on keyword overlap."""
    if not jd_text:
        return {"score": 50, "reason": "No JD provided", "missing_keywords": []}
    
    # Extract keywords (nouns and noun phrases) from JD
    jd_words = set(re.findall(r'\b[A-Za-z][a-z]+(?:\s+[A-Za-z][a-z]+){0,2}\b', jd_text.lower()))
    resume_words = set(re.findall(r'\b[A-Za-z][a-z]+(?:\s+[A-Za-z][a-z]+){0,2}\b', resume_text.lower()))
    
    # Filter for meaningful keywords (length > 3, not common words)
    common_words = {"and", "the", "for", "with", "from", "this", "that", "have", "will", "been"}
    jd_keywords = {w for w in jd_words if len(w) > 3 and w not in common_words}
    
    matched = jd_keywords & resume_words
    missing = jd_keywords - resume_words
    
    score = int((len(matched) / max(len(jd_keywords), 1)) * 100)
    
    return {
        "score": score,
        "matched_keywords": list(matched)[:20],
        "missing_keywords": list(missing)[:15],
        "recommendations": [f"Add keyword: {k}" for k in list(missing)[:5]]
    }

def calculate_quantification_score(resume_text):
    """Check for numbers, percentages, metrics."""
    patterns = [
        r'\d+%',  # Percentages
        r'\$[\d,]+',  # Dollar amounts
        r'£[\d,]+',  # Pound amounts
        r'\b\d{1,3}(?:,\d{3})+\b',  # Large numbers
        r'\b(?:increased|decreased|reduced|improved|grew|saved|generated)\s+(?:by\s+)?\d+',  # Action + number
    ]
    
    total_matches = sum(len(re.findall(p, resume_text, re.I)) for p in patterns)
    
    # Score based on number of quantified statements
    if total_matches >= 10:
        score = 95
    elif total_matches >= 5:
        score = 75
    elif total_matches >= 2:
        score = 55
    else:
        score = 35
    
    return {
        "score": score,
        "quantified_statements_found": total_matches,
        "recommendations": [
            "Add specific numbers to achievements (e.g., 'increased sales by 25%')",
            "Include scale metrics (team size, budget, users)"
        ] if score < 80 else []
    }

def calculate_structure_score(sections):
    """Evaluate resume structure and organization."""
    standard_sections = ["experience", "education", "skills"]
    section_names = [s["title"].lower() for s in sections]
    
    has_standard = sum(1 for std in standard_sections if any(std in name for name in section_names))
    
    # Check for contact info in header
    has_contact = any(
        "@" in s["content"][0] if s["content"] else False
        for s in sections if s["title"].lower() in ["header", "contact", "profile"]
    )
    
    score = min(100, (has_standard * 25) + (20 if has_contact else 0) + 30)  # Base 30 for attempt
    
    return {
        "score": score,
        "sections_found": section_names,
        "missing_standard": [s for s in standard_sections if not any(s in name for name in section_names)],
        "recommendations": [
            f"Add {s.title()} section" for s in standard_sections 
            if not any(s in name for name in section_names)
        ]
    }

def calculate_language_score(resume_text):
    """Check for strong action verbs and professional tone."""
    weak_verbs = ["responsible for", "helped with", "worked on", "assisted", "involved in"]
    strong_verbs = ["led", "managed", "implemented", "optimized", "increased", "reduced", 
                    "developed", "created", "launched", "negotiated", "streamlined"]
    
    weak_count = sum(resume_text.lower().count(v) for v in weak_verbs)
    strong_count = sum(resume_text.lower().count(v) for v in strong_verbs)
    
    total_verbs = weak_count + strong_count
    if total_verbs == 0:
        return {"score": 50, "weak_verbs": 0, "strong_verbs": 0, "recommendations": ["Add more action verbs"]}
    
    strong_ratio = strong_count / total_verbs
    score = int(50 + (strong_ratio * 50))
    
    return {
        "score": score,
        "weak_verbs_found": weak_count,
        "strong_verbs_found": strong_count,
        "recommendations": [
            f"Replace weak verbs: {', '.join([v for v in weak_verbs if v in resume_text.lower()][:3])}"
        ] if weak_count > 0 else ["Good use of strong action verbs!"]
    }

def calculate_ats_score(resume_text, sections):
    """Check ATS compatibility."""
    issues = []
    
    # Check for problematic characters
    if re.search(r'[^\x00-\x7F]', resume_text):  # Non-ASCII
        issues.append("Contains non-ASCII characters that may not parse")
    
    # Check section headers
    section_names = [s["title"].lower() for s in sections]
    non_standard = [s for s in section_names if s not in 
                   ["experience", "education", "skills", "summary", "contact", "header", 
                    "projects", "certifications", "awards", "languages", "profile"]]
    
    if len(non_standard) > 2:
        issues.append("Too many non-standard section headers")
    
    # Check for potential formatting issues
    if "table" in resume_text.lower():
        issues.append("May contain tables (ATS may not parse)")
    
    score = max(0, 100 - len(issues) * 15)
    
    return {
        "score": score,
        "issues": issues,
        "recommendations": [f"Fix: {i}" for i in issues] if issues else ["Good ATS compatibility!"]
    }

def analyze_resume(resume_data, jd_text=None):
    """Run complete five-dimension analysis."""
    resume_text = resume_data.get("raw_text", "")
    sections = resume_data.get("sections", [])
    
    report = {
        "dimensions": {
            "jd_match": calculate_jd_match(resume_text, jd_text),
            "quantification": calculate_quantification_score(resume_text),
            "structure": calculate_structure_score(sections),
            "language": calculate_language_score(resume_text),
            "ats_friendly": calculate_ats_score(resume_text, sections)
        },
        "overall_score": 0,
        "priority_fixes": []
    }
    
    # Calculate overall score
    scores = [v["score"] for v in report["dimensions"].values()]
    report["overall_score"] = int(sum(scores) / len(scores))
    
    # Collect priority fixes (from dimensions with score < 70)
    for dim_name, dim_data in report["dimensions"].items():
        if dim_data["score"] < 70:
            report["priority_fixes"].extend(dim_data.get("recommendations", [])[:2])
    
    return report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_resume.py <parsed_resume.json> [--jd jd.txt] [--output report.json]")
        sys.exit(1)
    
    resume_file = sys.argv[1]
    output_file = "analysis_report.json"
    jd_text = None
    
    if "--output" in sys.argv:
        output_file = sys.argv[sys.argv.index("--output") + 1]
    
    if "--jd" in sys.argv:
        with open(sys.argv[sys.argv.index("--jd") + 1], "r", encoding="utf-8") as f:
            jd_text = f.read()
    
    with open(resume_file, "r", encoding="utf-8") as f:
        resume_data = json.load(f)
    
    report = analyze_resume(resume_data, jd_text)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Analysis complete. Overall score: {report['overall_score']}/100")
    print(f"✓ Report saved to {output_file}")

#!/usr/bin/env python3
"""
heartbeat-scanner: Combined SHACL + Python Classification
Unified workflow:
1. SHACL validate structure (using embedded shapes)
2. Python check data quality
3. Python classify with v2.1 engine
4. Quirky output
"""

import sys
import random
from pathlib import Path
from typing import Tuple, Dict, Any
from pyshacl import validate
import rdflib

# Import embedded shapes
from shapes_embedded import SHAPES, EXAMPLES

# Import the quirky classification engine
from classify_v2_quirky import process_agent_profile


def load_profile_from_ttl(filepath: str) -> Dict[str, Any]:
    """Extract profile data from Turtle file."""
    data = rdflib.Graph()
    data.parse(filepath, format='turtle')
    
    # Query profile data
    query = """
    PREFIX m: <http://moltbook.org/mimicry/ontology#>
    SELECT ?agent ?name ?cv ?meta ?human ?score ?cls ?conf ?posts ?days
    WHERE {
        ?agent a m:AgentProfile ;
               m:agentName ?name ;
               m:hasCVScore ?cv ;
               m:hasMetaScore ?meta ;
               m:hasHumanContextScore ?human ;
               m:hasAgentScore ?score ;
               m:postCount ?posts ;
               m:daysSpan ?days .
        OPTIONAL { ?agent m:hasClassification ?cls }
        OPTIONAL { ?agent m:hasConfidence ?conf }
    }
    LIMIT 1
    """
    
    results = list(data.query(query))
    if not results:
        return None
    
    row = results[0]
    return {
        "agentId": str(row.agent).split("/")[-1] if row.agent else "unknown",
        "agentName": str(row.name),
        "cvScore": float(row.cv),
        "metaScore": float(row.meta),
        "humanContextScore": float(row.human),
        "agentScore": float(row.score),
        "postCount": int(row.posts),
        "daysSpan": float(row.days),
        "expectedClassification": row.cls.split("#")[-1] if row.cls else None,
        "expectedConfidence": float(row.conf) if row.conf else None,
    }


def shacl_validate(filepath: str, strict: bool = False) -> Tuple[bool, str]:
    """Run SHACL validation on profile using embedded shapes."""
    # Load ontology and shapes from embedded strings
    ontology = rdflib.Graph()
    ontology.parse(data=SHAPES['ontology'], format='turtle')
    
    shapes = rdflib.Graph()
    shapes.parse(data=SHAPES['agent_profile'], format='turtle')
    shapes.parse(data=SHAPES['classification'], format='turtle')
    
    if strict:
        shapes.parse(data=SHAPES['strict_validation'], format='turtle')
    
    # Load profile
    data = rdflib.Graph()
    data.parse(filepath, format='turtle')
    
    # Validate
    full = rdflib.Graph()
    full += ontology
    full += data
    
    try:
        conforms, _, report = validate(
            data_graph=full,
            shacl_graph=shapes,
            ont_graph=ontology,
            inference='rdfs',
            abort_on_first=False
        )
        return conforms, report
    except Exception as e:
        return False, str(e)


def scan_heartbeat(filepath: str, strict: bool = False) -> Dict[str, Any]:
    """
    Complete heartbeat scan: SHACL + Python classification
    """
    result = {
        "status": None,
        "shacl_valid": False,
        "profile_data": None,
        "classification": None,
        "message": None,
        "quirky_output": None
    }
    
    print("💓 Heartbeat Scanner v2.0")
    print("=" * 70)
    print(f"\n📄 Loading profile: {filepath}")
    
    # Step 1: SHACL Validation
    mode = "STRICT" if strict else "Standard"
    print(f"\n🔍 Step 1: SHACL Structural Validation ({mode})...")
    shacl_ok, shacl_report = shacl_validate(filepath, strict=strict)
    result["shacl_valid"] = shacl_ok
    
    if not shacl_ok:
        result["status"] = "INVALID_STRUCTURE"
        result["message"] = "SHACL validation failed. Profile structure is invalid."
        result["quirky_output"] = "❌ Oops! Your profile is malformed. Check required fields."
        print("❌ SHACL validation FAILED")
        print(f"\nErrors:\n{shacl_report[:500]}")
        return result
    
    print("✅ SHACL validation PASSED")
    
    # Step 2: Load Profile Data
    print("\n📊 Step 2: Extracting profile data...")
    profile_data = load_profile_from_ttl(filepath)
    
    if not profile_data:
        result["status"] = "PARSE_ERROR"
        result["message"] = "Could not parse profile data."
        result["quirky_output"] = "❌ Hmm, can't read your pulse. File corrupted?"
        print("❌ Failed to parse profile")
        return result
    
    result["profile_data"] = profile_data
    print(f"✅ Loaded: {profile_data['agentName']}")
    print(f"   Posts: {profile_data['postCount']}, Days: {profile_data['daysSpan']:.1f}")
    print(f"   CV: {profile_data['cvScore']:.2f}, Meta: {profile_data['metaScore']:.2f}, Human: {profile_data['humanContextScore']:.2f}")
    
    # Step 3: Python Classification
    print("\n🧠 Step 3: Running classification engine...")
    classification = process_agent_profile(profile_data)
    result["classification"] = classification
    
    # Build result
    result["status"] = classification.get("status", "UNKNOWN")
    result["message"] = classification.get("message", "")
    result["quirky_output"] = classification.get("message", "")
    
    if classification.get("status") == "INSUFFICIENT_DATA":
        print("⚠️  INSUFFICIENT DATA")
        print(f"   Need more posts/days")
    else:
        print(f"✅ Classification: {classification.get('classification', 'UNKNOWN')}")
        print(f"   Confidence: {classification.get('confidence', 0):.0%}")
    
    return result


def main():
    """CLI for heartbeat scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Heartbeat Scanner - Analyze agent posting patterns")
    parser.add_argument("profile", help="Path to Turtle profile file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--strict", "-s", action="store_true", help="Strict SHACL validation")
    
    args = parser.parse_args()
    
    if not Path(args.profile).exists():
        print(f"❌ File not found: {args.profile}")
        sys.exit(1)
    
    result = scan_heartbeat(args.profile, strict=args.strict)
    
    # Output
    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)
    
    if result["status"] == "INVALID_STRUCTURE":
        print("\n❌ STRUCTURAL VALIDATION FAILED")
        print("Your profile doesn't match the required schema.")
        print("\nCheck:")
        print("  - Required fields: agentId, agentName, platform")
        print("  - Data quality: postCount, daysSpan")
        print("  - Score ranges: 0.0-1.0")
        
    elif result["status"] == "INSUFFICIENT_DATA":
        print(f"\n⏳ {result['quirky_output']}")
        print(f"\n{result['classification'].get('recommendation', '')}")
        
    else:
        print(f"\n{result['quirky_output']}")
        
        if args.verbose and result["profile_data"]:
            print(f"\n📊 Technical Details:")
            print(f"   Score: {result['profile_data']['agentScore']:.3f}")
            print(f"   Data Quality: {result['classification'].get('data_quality', 'UNKNOWN')}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

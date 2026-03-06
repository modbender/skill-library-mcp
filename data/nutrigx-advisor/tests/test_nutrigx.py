"""
test_nutrigx.py — Automated test suite for NutriGx Advisor
Run with: pytest tests/test_nutrigx.py -v

Uses a FIXED synthetic patient (synthetic_patient.csv) with known genotypes
so that all assertions are deterministic and reproducible. This file is NOT
meant to showcase the skill — use examples/generate_patient.py for varied demos.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from parse_input import parse_genetic_file
from extract_genotypes import extract_snp_genotypes
from score_variants import compute_nutrient_risk_scores


SYNTHETIC = Path(__file__).parent / "synthetic_patient.csv"
PANEL     = Path(__file__).parent.parent / "data" / "snp_panel.json"


def load_panel():
    with open(PANEL) as f:
        return json.load(f)


# ── Parsing ────────────────────────────────────────────────────────────────────

def test_parse_23andme():
    table = parse_genetic_file(str(SYNTHETIC), fmt="23andme")
    assert len(table) >= 20
    assert "rs1801133" in table
    assert table["rs1801133"] in ("CT", "TC")


def test_all_panel_snps_present():
    panel = load_panel()
    table = parse_genetic_file(str(SYNTHETIC), fmt="23andme")
    calls = extract_snp_genotypes(table, panel)
    found = sum(1 for v in calls.values() if v["status"] == "found")
    assert found == len(panel), f"Expected all {len(panel)} SNPs found, got {found}"


# ── Extraction ─────────────────────────────────────────────────────────────────

def test_mthfr_heterozygous():
    """Fixed patient has MTHFR C677T = CT (1 risk allele)."""
    panel = load_panel()
    table = parse_genetic_file(str(SYNTHETIC), fmt="23andme")
    calls = extract_snp_genotypes(table, panel)
    mthfr = calls["rs1801133"]
    assert mthfr["status"] == "found"
    assert mthfr["risk_count"] == 1


def test_vdr_homozygous_risk():
    """Fixed patient has VDR TaqI = CC (2 risk alleles) → drives Elevated vitamin D score."""
    panel = load_panel()
    table = parse_genetic_file(str(SYNTHETIC), fmt="23andme")
    calls = extract_snp_genotypes(table, panel)
    vdr = calls["rs731236"]
    assert vdr["status"] == "found"
    assert vdr["risk_count"] == 2


def test_aldh2_ref_homozygous():
    """Fixed patient has ALDH2 = GG (0 risk alleles) → Low alcohol risk."""
    panel = load_panel()
    table = parse_genetic_file(str(SYNTHETIC), fmt="23andme")
    calls = extract_snp_genotypes(table, panel)
    aldh2 = calls["rs671"]
    assert aldh2["status"] == "found"
    assert aldh2["risk_count"] == 0


# ── Scoring ────────────────────────────────────────────────────────────────────

def test_scores_structure():
    panel = load_panel()
    table = parse_genetic_file(str(SYNTHETIC), fmt="23andme")
    calls = extract_snp_genotypes(table, panel)
    scores = compute_nutrient_risk_scores(calls, panel)
    assert "folate" in scores
    assert "vitamin_d" in scores
    assert "omega3" in scores
    assert "alcohol" in scores
    for domain, data in scores.items():
        if data["score"] is not None:
            assert 0.0 <= data["score"] <= 10.0
        assert data["category"] in ("Low", "Moderate", "Elevated", "Unknown")


def test_vitamin_d_elevated():
    """VDR TaqI hom risk → Vitamin D expected Elevated."""
    panel = load_panel()
    table = parse_genetic_file(str(SYNTHETIC), fmt="23andme")
    calls = extract_snp_genotypes(table, panel)
    scores = compute_nutrient_risk_scores(calls, panel)
    assert scores["vitamin_d"]["category"] == "Elevated"


def test_alcohol_low():
    """ALDH2 GG ref hom → Alcohol expected Low."""
    panel = load_panel()
    table = parse_genetic_file(str(SYNTHETIC), fmt="23andme")
    calls = extract_snp_genotypes(table, panel)
    scores = compute_nutrient_risk_scores(calls, panel)
    assert scores["alcohol"]["category"] == "Low"


def test_folate_not_low():
    """MTHFR C677T het → Folate should be Moderate or Elevated, not Low."""
    panel = load_panel()
    table = parse_genetic_file(str(SYNTHETIC), fmt="23andme")
    calls = extract_snp_genotypes(table, panel)
    scores = compute_nutrient_risk_scores(calls, panel)
    assert scores["folate"]["category"] in ("Moderate", "Elevated")

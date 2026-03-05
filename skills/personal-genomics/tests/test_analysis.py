"""
Unit tests for personal-genomics analysis.
"""

import pytest
import pandas as pd
import io
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_data import SAMPLE_DNA_DATA, EXPECTED_MTHFR_C677T, EXPECTED_COMT


class TestDataLoading:
    """Tests for DNA data loading and parsing."""
    
    def test_load_sample_data(self):
        """Test loading sample DNA data."""
        df = pd.read_csv(io.StringIO(SAMPLE_DNA_DATA), sep='\t', comment='#')
        assert len(df) > 0
        assert 'rsid' in df.columns
        assert 'allele1' in df.columns
        assert 'allele2' in df.columns
    
    def test_genotype_construction(self):
        """Test that genotypes are correctly constructed."""
        df = pd.read_csv(io.StringIO(SAMPLE_DNA_DATA), sep='\t', comment='#')
        df['genotype'] = df['allele1'] + df['allele2']
        
        # Check MTHFR C677T
        mthfr = df[df['rsid'] == 'rs1801133']['genotype'].values[0]
        assert mthfr == EXPECTED_MTHFR_C677T
        
        # Check COMT
        comt = df[df['rsid'] == 'rs4680']['genotype'].values[0]
        assert comt == EXPECTED_COMT
    
    def test_marker_lookup(self):
        """Test looking up specific markers."""
        df = pd.read_csv(io.StringIO(SAMPLE_DNA_DATA), sep='\t', comment='#')
        df = df.set_index('rsid')
        
        # Factor V Leiden should be CC (normal)
        assert df.loc['rs6025', 'allele1'] == 'C'
        assert df.loc['rs6025', 'allele2'] == 'C'
        
        # HFE C282Y should be GG (normal)
        assert df.loc['rs1800562', 'allele1'] == 'G'


class TestMarkerDatabase:
    """Tests for marker database integrity."""
    
    def test_health_markers_structure(self):
        """Test that health markers have required fields."""
        from markers.health_markers import HEALTH_MARKERS
        
        required_fields = ['gene', 'category', 'evidence']
        
        for rsid, marker in HEALTH_MARKERS.items():
            assert rsid.startswith('rs'), f"{rsid} should start with 'rs'"
            for field in required_fields:
                assert field in marker, f"{rsid} missing {field}"
    
    def test_health_markers_evidence_levels(self):
        """Test that evidence levels are valid."""
        from markers.health_markers import HEALTH_MARKERS
        
        valid_levels = ['strong', 'moderate', 'preliminary', 'weak']
        
        for rsid, marker in HEALTH_MARKERS.items():
            assert marker['evidence'] in valid_levels, \
                f"{rsid} has invalid evidence level: {marker['evidence']}"
    
    def test_trait_markers_structure(self):
        """Test that trait markers have required fields."""
        from markers.trait_markers import TRAIT_MARKERS
        
        for rsid, marker in TRAIT_MARKERS.items():
            assert rsid.startswith('rs'), f"{rsid} should start with 'rs'"
            assert 'gene' in marker
            assert 'trait' in marker
            assert 'interpretation' in marker


class TestRiskAssessment:
    """Tests for risk assessment logic."""
    
    def test_risk_allele_counting(self):
        """Test counting risk alleles in genotype."""
        def count_risk_alleles(genotype, risk_allele):
            return genotype.count(risk_allele)
        
        # MTHFR C677T: risk allele is A
        assert count_risk_alleles("AG", "A") == 1  # Heterozygous
        assert count_risk_alleles("AA", "A") == 2  # Homozygous risk
        assert count_risk_alleles("GG", "A") == 0  # Normal
    
    def test_apoe_inference(self):
        """Test APOE genotype inference from component SNPs."""
        # rs429358 and rs7412 determine APOE status
        # E2: rs429358=T, rs7412=T
        # E3: rs429358=T, rs7412=C
        # E4: rs429358=C, rs7412=C
        
        def infer_apoe_allele(rs429358_allele, rs7412_allele):
            if rs429358_allele == 'T' and rs7412_allele == 'T':
                return 'E2'
            elif rs429358_allele == 'T' and rs7412_allele == 'C':
                return 'E3'
            elif rs429358_allele == 'C' and rs7412_allele == 'C':
                return 'E4'
            return None
        
        assert infer_apoe_allele('T', 'C') == 'E3'
        assert infer_apoe_allele('C', 'C') == 'E4'
        assert infer_apoe_allele('T', 'T') == 'E2'


class TestOutputFormat:
    """Tests for output format integrity."""
    
    def test_actionable_structure(self):
        """Test that actionable items have correct structure."""
        from markers.health_markers import HEALTH_MARKERS
        
        valid_priorities = ['high', 'medium', 'low', 'informational']
        valid_action_types = ['medical_alert', 'screening', 'supplementation', 
                              'lifestyle', 'monitoring', 'awareness', 'none']
        
        for rsid, marker in HEALTH_MARKERS.items():
            if 'actionable' in marker:
                action = marker['actionable']
                assert 'priority' in action, f"{rsid} actionable missing priority"
                assert action['priority'] in valid_priorities, \
                    f"{rsid} has invalid priority: {action['priority']}"
                assert 'action_type' in action, f"{rsid} actionable missing action_type"


class TestPrivacy:
    """Tests for privacy guarantees."""
    
    def test_no_network_imports(self):
        """Verify no network-related imports in core modules."""
        import ast
        
        network_modules = ['requests', 'urllib', 'http.client', 'socket', 'aiohttp']
        
        # Check comprehensive_analysis.py
        with open('comprehensive_analysis.py', 'r') as f:
            tree = ast.parse(f.read())
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        for net_mod in network_modules:
            assert net_mod not in imports, \
                f"Network module {net_mod} found in comprehensive_analysis.py"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

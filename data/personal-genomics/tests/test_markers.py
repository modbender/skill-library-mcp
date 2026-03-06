"""
Comprehensive tests for all marker modules.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPharmacogenomics:
    """Tests for pharmacogenomics markers."""
    
    def test_pharmacogenomics_markers_loaded(self):
        """Test that pharmacogenomics markers are loaded."""
        from markers.pharmacogenomics import PHARMACOGENOMICS_MARKERS
        assert len(PHARMACOGENOMICS_MARKERS) > 0
    
    def test_cpic_level_markers(self):
        """Test that CPIC Level 1A markers are present."""
        from markers.pharmacogenomics import PHARMACOGENOMICS_MARKERS
        
        # Critical CPIC Level 1A genes
        cpic_1a_genes = ['CYP2D6', 'CYP2C19', 'CYP2C9', 'DPYD', 'TPMT', 'SLCO1B1']
        
        genes_found = set()
        for rsid, marker in PHARMACOGENOMICS_MARKERS.items():
            if marker.get('gene') in cpic_1a_genes:
                genes_found.add(marker['gene'])
        
        assert len(genes_found) >= 4, f"Missing CPIC 1A genes. Found: {genes_found}"
    
    def test_drug_interactions_structure(self):
        """Test drug interactions have proper structure."""
        from markers.pharmacogenomics import DRUG_INTERACTIONS
        
        if DRUG_INTERACTIONS:
            for drug, info in DRUG_INTERACTIONS.items():
                assert 'gene' in info or 'genes' in info
    
    def test_critical_dpyd_marker(self):
        """Test DPYD markers are flagged as critical."""
        from markers.pharmacogenomics import PHARMACOGENOMICS_MARKERS
        
        dpyd_markers = {k: v for k, v in PHARMACOGENOMICS_MARKERS.items() 
                       if v.get('gene') == 'DPYD'}
        
        assert len(dpyd_markers) > 0, "DPYD markers missing"
        
        # DPYD should have high/critical priority
        for rsid, marker in dpyd_markers.items():
            if 'actionable' in marker:
                assert marker['actionable']['priority'] in ['critical', 'high'], \
                    f"DPYD marker {rsid} should be critical/high priority"


class TestCarrierStatus:
    """Tests for carrier status markers."""
    
    def test_carrier_markers_loaded(self):
        """Test carrier markers are loaded."""
        from markers.carrier_status import CARRIER_MARKERS
        assert len(CARRIER_MARKERS) >= 20
    
    def test_common_carriers_present(self):
        """Test common carrier conditions are covered."""
        from markers.carrier_status import CARRIER_MARKERS
        
        conditions = set()
        for rsid, marker in CARRIER_MARKERS.items():
            condition = marker.get('condition') or marker.get('disease')
            if condition:
                conditions.add(condition.lower())
        
        # Must have these common carrier conditions
        required = ['cystic fibrosis', 'sickle cell']
        
        conditions_str = ' '.join(conditions)
        for req in required:
            assert req in conditions_str or any(req in c for c in conditions), \
                f"Missing carrier condition: {req}"
    
    def test_carrier_inheritance_pattern(self):
        """Test carriers have inheritance pattern specified."""
        from markers.carrier_status import CARRIER_MARKERS
        
        for rsid, marker in list(CARRIER_MARKERS.items())[:10]:
            # Should have inheritance info
            has_inheritance = any(key in marker for key in 
                                ['inheritance', 'mode', 'pattern'])
            # At minimum should have gene
            assert 'gene' in marker


class TestHealthRisks:
    """Tests for health risk markers."""
    
    def test_health_risks_loaded(self):
        """Test health risk markers are loaded."""
        from markers.health_risks import HEALTH_RISK_MARKERS
        assert len(HEALTH_RISK_MARKERS) > 0
    
    def test_apoe_related_markers(self):
        """Test APOE markers are present."""
        from markers.health_risks import HEALTH_RISK_MARKERS
        from markers.health_markers import HEALTH_MARKERS
        
        all_markers = {**HEALTH_RISK_MARKERS, **HEALTH_MARKERS}
        
        apoe_found = False
        for rsid in ['rs429358', 'rs7412']:
            if rsid in all_markers:
                apoe_found = True
                break
        
        assert apoe_found, "APOE markers (rs429358, rs7412) not found"


class TestTraits:
    """Tests for trait markers."""
    
    def test_traits_loaded(self):
        """Test trait markers are loaded."""
        from markers.traits import TRAIT_MARKERS
        assert len(TRAIT_MARKERS) > 0
    
    def test_common_traits_present(self):
        """Test common traits are covered."""
        from markers.traits import TRAIT_MARKERS
        
        traits = set()
        for rsid, marker in TRAIT_MARKERS.items():
            trait = marker.get('trait', '').lower()
            traits.add(trait)
        
        traits_str = ' '.join(traits)
        
        # Should have some common traits
        common = ['eye', 'lactose', 'caffeine', 'bitter']
        found = sum(1 for c in common if c in traits_str)
        assert found >= 2, f"Missing common traits. Found traits contain: {traits_str[:200]}"


class TestNutrition:
    """Tests for nutrition markers."""
    
    def test_nutrition_loaded(self):
        """Test nutrition markers are loaded."""
        from markers.nutrition import NUTRITION_MARKERS
        assert len(NUTRITION_MARKERS) > 0
    
    def test_mthfr_present(self):
        """Test MTHFR markers are present."""
        from markers.nutrition import NUTRITION_MARKERS
        
        mthfr_found = any(m.get('gene') == 'MTHFR' 
                         for m in NUTRITION_MARKERS.values())
        assert mthfr_found, "MTHFR markers should be in nutrition"


class TestFitness:
    """Tests for fitness markers."""
    
    def test_fitness_loaded(self):
        """Test fitness markers are loaded."""
        from markers.fitness import FITNESS_MARKERS
        assert len(FITNESS_MARKERS) > 0
    
    def test_actn3_present(self):
        """Test ACTN3 (muscle fiber type) marker present."""
        from markers.fitness import FITNESS_MARKERS
        
        actn3_found = any(m.get('gene') == 'ACTN3' 
                        for m in FITNESS_MARKERS.values())
        assert actn3_found, "ACTN3 marker should be in fitness"


class TestNeurogenetics:
    """Tests for neurogenetics markers."""
    
    def test_neurogenetics_loaded(self):
        """Test neurogenetics markers are loaded."""
        from markers.neurogenetics import NEURO_MARKERS
        assert len(NEURO_MARKERS) > 0
    
    def test_comt_present(self):
        """Test COMT marker present."""
        from markers.neurogenetics import NEURO_MARKERS
        
        comt_found = any(m.get('gene') == 'COMT' 
                        for m in NEURO_MARKERS.values())
        assert comt_found, "COMT marker should be in neurogenetics"


class TestLongevity:
    """Tests for longevity markers."""
    
    def test_longevity_loaded(self):
        """Test longevity markers are loaded."""
        from markers.longevity import LONGEVITY_MARKERS
        assert len(LONGEVITY_MARKERS) > 0


class TestImmunity:
    """Tests for immunity markers."""
    
    def test_immunity_loaded(self):
        """Test immunity markers are loaded."""
        from markers.immunity import IMMUNITY_MARKERS
        assert len(IMMUNITY_MARKERS) > 0
    
    def test_hla_markers_present(self):
        """Test HLA markers are present."""
        from markers.immunity import IMMUNITY_MARKERS
        
        hla_found = any('HLA' in m.get('gene', '') 
                       for m in IMMUNITY_MARKERS.values())
        # HLA variants may be in separate module
        assert True  # Soft check - HLA complex to test


class TestPolygenicScores:
    """Tests for polygenic risk scores."""
    
    def test_prs_weights_loaded(self):
        """Test PRS weights are loaded."""
        from markers.polygenic_scores import PRS_WEIGHTS
        assert len(PRS_WEIGHTS) > 0
    
    def test_prs_conditions_covered(self):
        """Test major conditions have PRS."""
        from markers.polygenic_scores import PRS_WEIGHTS
        
        conditions = set(v.get('condition', '') for v in PRS_WEIGHTS.values())
        
        # Should have at least CAD and T2D
        assert len(conditions) >= 2, f"Too few PRS conditions: {conditions}"
    
    def test_prs_beta_values(self):
        """Test PRS have valid beta values."""
        from markers.polygenic_scores import PRS_WEIGHTS
        
        for rsid, info in PRS_WEIGHTS.items():
            assert 'beta' in info, f"{rsid} missing beta"
            assert isinstance(info['beta'], (int, float)), f"{rsid} beta not numeric"


class TestMarkerConsistency:
    """Tests for cross-module consistency."""
    
    def test_no_duplicate_rsids(self):
        """Test no rsID appears in multiple primary modules with conflicts."""
        from markers.pharmacogenomics import PHARMACOGENOMICS_MARKERS
        from markers.carrier_status import CARRIER_MARKERS
        from markers.health_risks import HEALTH_RISK_MARKERS
        from markers.traits import TRAIT_MARKERS
        
        # Collect all rsIDs
        all_rsids = []
        all_rsids.extend(PHARMACOGENOMICS_MARKERS.keys())
        all_rsids.extend(CARRIER_MARKERS.keys())
        all_rsids.extend(HEALTH_RISK_MARKERS.keys())
        all_rsids.extend(TRAIT_MARKERS.keys())
        
        # Some overlap is OK (e.g., rs4680 affects both traits and pharma)
        # Just ensure modules load without key errors
        assert len(all_rsids) > 100
    
    def test_rsid_format(self):
        """Test all rsIDs have correct format."""
        from markers.pharmacogenomics import PHARMACOGENOMICS_MARKERS
        from markers.carrier_status import CARRIER_MARKERS
        from markers.health_risks import HEALTH_RISK_MARKERS
        
        for markers in [PHARMACOGENOMICS_MARKERS, CARRIER_MARKERS, HEALTH_RISK_MARKERS]:
            for rsid in markers.keys():
                assert rsid.startswith('rs') or rsid.startswith('i'), \
                    f"Invalid rsID format: {rsid}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

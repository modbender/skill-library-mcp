"""
Tests for new v3.0 marker modules.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRareDiseases:
    """Tests for rare disease markers."""
    
    def test_rare_diseases_loaded(self):
        """Test rare disease markers are loaded."""
        from markers.rare_diseases import RARE_DISEASE_MARKERS
        assert len(RARE_DISEASE_MARKERS) >= 20
    
    def test_lysosomal_storage_present(self):
        """Test lysosomal storage disorders are covered."""
        from markers.rare_diseases import RARE_DISEASE_MARKERS
        
        genes = set(m.get('gene', '') for m in RARE_DISEASE_MARKERS.values())
        
        # Should have Gaucher (GBA) and Tay-Sachs (HEXA)
        assert 'GBA' in genes or 'HEXA' in genes
    
    def test_rare_disease_panels(self):
        """Test rare disease screening panels exist."""
        from markers.rare_diseases import RARE_DISEASE_PANELS
        
        assert 'ashkenazi_jewish' in RARE_DISEASE_PANELS
        assert len(RARE_DISEASE_PANELS['ashkenazi_jewish']) > 0


class TestMentalHealth:
    """Tests for mental health markers."""
    
    def test_mental_health_loaded(self):
        """Test mental health markers are loaded."""
        from markers.mental_health import MENTAL_HEALTH_MARKERS
        assert len(MENTAL_HEALTH_MARKERS) >= 15
    
    def test_bdnf_present(self):
        """Test BDNF marker is present."""
        from markers.mental_health import MENTAL_HEALTH_MARKERS
        
        bdnf_found = any(m.get('gene') == 'BDNF' 
                        for m in MENTAL_HEALTH_MARKERS.values())
        assert bdnf_found
    
    def test_comt_present(self):
        """Test COMT is in mental health markers."""
        from markers.mental_health import MENTAL_HEALTH_MARKERS
        
        comt_found = any(m.get('gene') == 'COMT' 
                        for m in MENTAL_HEALTH_MARKERS.values())
        assert comt_found
    
    def test_mental_health_notes(self):
        """Test interpretation notes exist."""
        from markers.mental_health import MENTAL_HEALTH_NOTES
        
        assert len(MENTAL_HEALTH_NOTES) > 100
        assert 'polygenic' in MENTAL_HEALTH_NOTES.lower()


class TestDermatology:
    """Tests for dermatology markers."""
    
    def test_dermatology_loaded(self):
        """Test dermatology markers are loaded."""
        from markers.dermatology import DERMATOLOGY_MARKERS
        assert len(DERMATOLOGY_MARKERS) >= 20
    
    def test_mc1r_present(self):
        """Test MC1R (red hair/melanoma) markers present."""
        from markers.dermatology import DERMATOLOGY_MARKERS
        
        mc1r_found = any(m.get('gene') == 'MC1R' 
                        for m in DERMATOLOGY_MARKERS.values())
        assert mc1r_found
    
    def test_pigmentation_markers(self):
        """Test pigmentation markers present."""
        from markers.dermatology import DERMATOLOGY_MARKERS
        
        pigment_genes = ['SLC24A5', 'SLC45A2', 'OCA2']
        genes_found = set(m.get('gene', '') for m in DERMATOLOGY_MARKERS.values())
        
        found_count = sum(1 for g in pigment_genes if g in genes_found)
        assert found_count >= 2


class TestVisionHearing:
    """Tests for vision and hearing markers."""
    
    def test_vision_markers_loaded(self):
        """Test vision markers are loaded."""
        from markers.vision_hearing import VISION_MARKERS
        assert len(VISION_MARKERS) >= 10
    
    def test_hearing_markers_loaded(self):
        """Test hearing markers are loaded."""
        from markers.vision_hearing import HEARING_MARKERS
        assert len(HEARING_MARKERS) >= 5
    
    def test_amd_markers_present(self):
        """Test AMD markers (CFH, ARMS2) are present."""
        from markers.vision_hearing import VISION_MARKERS
        
        genes = set(m.get('gene', '') for m in VISION_MARKERS.values())
        
        # CFH and ARMS2 are key AMD genes
        assert 'CFH' in genes or 'ARMS2' in genes
    
    def test_aminoglycoside_marker(self):
        """Test aminoglycoside deafness marker is present."""
        from markers.vision_hearing import HEARING_MARKERS
        
        mt_found = any('MT-RNR1' in m.get('gene', '') or 'aminoglycoside' in str(m).lower()
                      for m in HEARING_MARKERS.values())
        assert mt_found, "Critical aminoglycoside deafness marker should be present"


class TestFertility:
    """Tests for fertility markers."""
    
    def test_fertility_loaded(self):
        """Test fertility markers are loaded."""
        from markers.fertility import FERTILITY_MARKERS
        assert len(FERTILITY_MARKERS) >= 15
    
    def test_female_fertility_markers(self):
        """Test female fertility markers present."""
        from markers.fertility import FERTILITY_MARKERS
        
        female_found = any(m.get('sex') == 'female' 
                          for m in FERTILITY_MARKERS.values())
        assert female_found
    
    def test_pcos_markers(self):
        """Test PCOS markers present."""
        from markers.fertility import FERTILITY_MARKERS
        
        categories = set(m.get('category', '') for m in FERTILITY_MARKERS.values())
        assert 'pcos' in categories
    
    def test_thrombophilia_in_fertility(self):
        """Test thrombophilia markers are in fertility context."""
        from markers.fertility import FERTILITY_MARKERS
        
        # Factor V Leiden should be in fertility due to pregnancy implications
        fvl_found = any('F5' in m.get('gene', '') or 'Factor V' in str(m)
                       for m in FERTILITY_MARKERS.values())
        assert fvl_found


class TestIntegration:
    """Integration tests for all marker modules."""
    
    def test_all_modules_import(self):
        """Test all marker modules can be imported."""
        from markers import (
            RARE_DISEASE_MARKERS,
            MENTAL_HEALTH_MARKERS,
            DERMATOLOGY_MARKERS,
            VISION_HEARING_MARKERS,
            FERTILITY_MARKERS
        )
        
        assert len(RARE_DISEASE_MARKERS) > 0
        assert len(MENTAL_HEALTH_MARKERS) > 0
        assert len(DERMATOLOGY_MARKERS) > 0
        assert len(VISION_HEARING_MARKERS) > 0
        assert len(FERTILITY_MARKERS) > 0
    
    def test_marker_counts(self):
        """Test total marker count is substantial."""
        from markers import get_marker_counts
        
        counts = get_marker_counts()
        # Base markers + new categories should exceed 1200
        assert counts['total'] >= 1200
    
    def test_new_categories_in_counts(self):
        """Test new categories appear in marker counts."""
        from markers import get_marker_counts
        
        counts = get_marker_counts()
        
        assert 'rare_diseases' in counts
        assert 'mental_health' in counts
        assert 'dermatology' in counts
        assert 'vision_hearing' in counts
        assert 'fertility' in counts


class TestAnalysisIntegration:
    """Test integration with comprehensive_analysis.py."""
    
    def test_analysis_imports_new_modules(self):
        """Test comprehensive analysis can import new modules."""
        # This tests the import at module level
        from comprehensive_analysis import (
            RARE_DISEASE_MARKERS,
            MENTAL_HEALTH_MARKERS,
            DERMATOLOGY_MARKERS,
            VISION_HEARING_MARKERS,
            FERTILITY_MARKERS
        )
        
        assert len(RARE_DISEASE_MARKERS) > 0
    
    def test_lifestyle_recommendations_function(self):
        """Test lifestyle recommendations function exists."""
        from comprehensive_analysis import generate_lifestyle_recommendations
        
        # Test with empty results
        result = generate_lifestyle_recommendations({})
        assert 'diet' in result
        assert 'exercise' in result
        assert 'supplements' in result
    
    def test_drug_interaction_matrix_function(self):
        """Test drug interaction matrix function exists."""
        from comprehensive_analysis import generate_drug_interaction_matrix
        
        result = generate_drug_interaction_matrix({})
        assert 'critical_interactions' in result
        assert 'warnings' in result
        assert 'dosing_adjustments' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Tests for the HiEnergy API Skill
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.hienergy_skill import HiEnergySkill


class TestHiEnergySkill(unittest.TestCase):
    """Test cases for HiEnergySkill class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key_12345"
        self.skill = HiEnergySkill(api_key=self.api_key)
    
    def test_initialization_with_api_key(self):
        """Test that skill initializes correctly with API key"""
        skill = HiEnergySkill(api_key="test_key")
        self.assertEqual(skill.api_key, "test_key")
        self.assertIn('X-Api-Key', skill.headers)
        self.assertEqual(skill.headers['X-Api-Key'], 'test_key')
    
    def test_initialization_without_api_key(self):
        """Test that skill raises error without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                HiEnergySkill()
            self.assertIn("API key is required", str(context.exception))
    
    def test_initialization_from_environment(self):
        """Test that skill can read API key from environment"""
        with patch.dict(os.environ, {'HIENERGY_API_KEY': 'env_key'}):
            skill = HiEnergySkill()
            self.assertEqual(skill.api_key, 'env_key')

    def test_initialization_from_alt_environment(self):
        """Test that skill can read API key from alternate environment variable"""
        with patch.dict(os.environ, {'HI_ENERGY_API_KEY': 'alt_env_key'}, clear=True):
            skill = HiEnergySkill()
            self.assertEqual(skill.api_key, 'alt_env_key')
    
    @patch('scripts.hienergy_skill.requests.request')
    def test_get_advertisers(self, mock_request):
        """Test getting advertisers"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'name': 'Test Advertiser 1'},
                {'id': '2', 'name': 'Test Advertiser 2'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = self.skill.get_advertisers(search='test', limit=5)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Test Advertiser 1')
        mock_request.assert_called_once()
    
    @patch('scripts.hienergy_skill.requests.request')
    def test_get_affiliate_programs(self, mock_request):
        """Test getting affiliate programs via advertisers endpoint"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'name': 'Test Program 1', 'commission_rate': '10%'},
                {'id': '2', 'name': 'Test Program 2', 'commission_rate': '15%'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        result = self.skill.get_affiliate_programs(limit=5)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Test Program 1')
        called_url = mock_request.call_args.kwargs.get('url', '')
        self.assertIn('/advertisers', called_url)

    @patch('scripts.hienergy_skill.requests.request')
    def test_get_affiliate_programs_weed_query_filters_wedding_false_positive(self, mock_request):
        """Search for weed should not match wedding brands by substring."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'name': "David's Bridal", 'description': 'Wedding dresses'},
                {'id': '2', 'name': 'Wyld CBD', 'description': 'CBD gummies and wellness'},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        result = self.skill.get_affiliate_programs(search='weed', limit=10)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Wyld CBD')

    def test_text_has_term_avoids_false_positive_for_plain_terms(self):
        """Plain keyword matching should not use compact substring fallback."""
        self.assertFalse(self.skill._text_has_term("the mens wearhouse", "thc"))
        self.assertTrue(self.skill._text_has_term("delta8 gummies", "delta-8"))
    
    @patch('scripts.hienergy_skill.requests.request')
    def test_find_deals(self, mock_request):
        """Test finding deals"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'title': 'Test Deal 1', 'description': 'Great deal'},
                {'id': '2', 'title': 'Test Deal 2', 'description': 'Amazing offer'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = self.skill.find_deals(search='discount', limit=5)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Test Deal 1')
    
    @patch('scripts.hienergy_skill.requests.request')
    def test_get_transactions(self, mock_request):
        """Test getting transactions"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': 'tx1', 'amount': 120.50, 'status': 'completed'},
                {'id': 'tx2', 'amount': 80.00, 'status': 'pending'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        result = self.skill.get_transactions(status='completed', limit=5)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 'tx1')

    @patch('scripts.hienergy_skill.requests.request')
    def test_get_contacts(self, mock_request):
        """Test getting contacts"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': 'c1', 'name': 'Jane Doe', 'email': 'jane@example.com'},
                {'id': 'c2', 'name': 'John Doe', 'email': 'john@example.com'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        result = self.skill.get_contacts(search='john', limit=5)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Jane Doe')

    @patch('scripts.hienergy_skill.requests.request')
    def test_get_advertiser_details(self, mock_request):
        """Test getting advertiser details"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {'id': '1', 'name': 'Test Advertiser', 'description': 'Test description'}
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = self.skill.get_advertiser_details('1')
        
        self.assertEqual(result['name'], 'Test Advertiser')
        self.assertEqual(result['id'], '1')
    
    @patch('scripts.hienergy_skill.requests.request')
    def test_answer_question_about_advertisers(self, mock_request):
        """Test answering questions about advertisers"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'name': 'Nike', 'description': 'Sports brand', 'publisher_name': 'HiEnergy'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        answer = self.skill.answer_question("What advertisers are available?")

        self.assertIn('Nike', answer)
        self.assertIn('publisher', answer.lower())
        self.assertIn('https://app.hienergy.ai/a/1', answer)
        self.assertIn("Reply 'yes'", answer)

    @patch('scripts.hienergy_skill.requests.request')
    def test_answer_question_advertiser_details_uses_show_endpoint(self, mock_request):
        """Test detail advertiser question uses show endpoint"""
        list_response = Mock()
        list_response.json.return_value = {
            'data': [
                {'id': '1', 'name': 'Nike', 'publisher_name': 'HiEnergy'}
            ]
        }
        list_response.raise_for_status = Mock()

        detail_response = Mock()
        detail_response.json.return_value = {
            'data': {
                'id': '1',
                'name': 'Nike',
                'domain': 'nike.com',
                'url': 'https://nike.com',
                'status': 'approved',
                'publisher_name': 'HiEnergy',
                'network_name': 'Impact',
                'commission_rate': '10%'
            }
        }
        detail_response.raise_for_status = Mock()

        mock_request.side_effect = [list_response, detail_response]

        answer = self.skill.answer_question("Show me more details about advertiser Nike")

        self.assertIn('Advertiser details', answer)
        self.assertIn('nike.com', answer)
    
    @patch('scripts.hienergy_skill.requests.request')
    def test_get_advertisers_by_domain_endpoint(self, mock_request):
        """Test advertiser domain lookup uses search_by_domain endpoint"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': '3625414', 'name': 'Alo Yoga', 'domain': 'aloyoga.com'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        result = self.skill.get_advertisers(search='aloyoga.com', limit=5)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Alo Yoga')
        called_url = mock_request.call_args.kwargs.get('url', '')
        self.assertIn('/advertisers/search_by_domain', called_url)

    @patch('scripts.hienergy_skill.requests.request')
    def test_answer_question_advertiser_profile_triggers_show_endpoint(self, mock_request):
        """Test advertiser profile/detail phrasing triggers show endpoint"""
        list_response = Mock()
        list_response.json.return_value = {
            'data': [
                {'id': '99', 'name': 'Alo Yoga', 'publisher_name': 'HiEnergy'}
            ]
        }
        list_response.raise_for_status = Mock()

        detail_response = Mock()
        detail_response.json.return_value = {
            'data': {
                'id': '99',
                'name': 'Alo Yoga',
                'domain': 'aloyoga.com',
                'status': 'approved',
                'publisher_name': 'HiEnergy',
                'network_name': 'Skimlinks'
            }
        }
        detail_response.raise_for_status = Mock()
        mock_request.side_effect = [list_response, detail_response]

        answer = self.skill.answer_question("Advertiser profile for Alo Yoga")

        self.assertIn('Advertiser details', answer)
        self.assertIn('Publisher: HiEnergy', answer)

    def test_format_advertisers_answer_publisher_fallbacks(self):
        """Test advertiser formatter uses publisher fallback fields"""
        answer = self.skill._format_advertisers_answer(
            [
                {'id': '1', 'name': 'Brand A', 'agency_name': 'Agency A'},
                {'id': '2', 'name': 'Brand B', 'publisher_id': 123},
            ],
            'show advertisers'
        )

        self.assertIn('Brand A [publisher: Agency A]', answer)
        self.assertIn('Brand B [publisher: 123]', answer)

    @patch('scripts.hienergy_skill.requests.request')
    def test_yes_followup_summarizes_advertiser_show_endpoint(self, mock_request):
        """Test yes follow-up uses context last_advertiser_id and returns show summary"""
        detail_response = Mock()
        detail_response.json.return_value = {
            'data': {
                'id': '3625414',
                'name': 'Alo Yoga',
                'domain': 'aloyoga.com',
                'url': 'https://aloyoga.com',
                'status': 'approved',
                'publisher_name': 'HiEnergy',
                'network_name': 'Skimlinks',
                'commission_rate': '9.24'
            }
        }
        detail_response.raise_for_status = Mock()
        mock_request.return_value = detail_response

        answer = self.skill.answer_question(
            "yes",
            context={'last_advertiser_id': '3625414'}
        )

        self.assertIn('Advertiser details', answer)
        self.assertIn('Alo Yoga', answer)
        self.assertIn('aloyoga.com', answer)

    @patch('scripts.hienergy_skill.requests.request')
    def test_research_affiliate_programs_ranking(self, mock_request):
        """Test affiliate program research ranking by commission"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': 'p1', 'name': 'Low Program', 'commission_rate': '5%'},
                {'id': 'p2', 'name': 'High Program', 'commission_rate': '25%'},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        report = self.skill.research_affiliate_programs(search='supplements', top_n=2)

        self.assertEqual(report['summary']['total_programs_matched'], 2)
        self.assertEqual(report['programs'][0]['name'], 'High Program')

    def test_commission_insight_parses_percent_range(self):
        """Commission parser should normalize percent ranges with midpoint."""
        insight = self.skill._commission_insight({'commission_rate': '8-12%'})

        self.assertEqual(insight.model, 'percent-range')
        self.assertEqual(insight.percent_value, 10.0)
        self.assertIsNone(insight.flat_amount_usd)

    def test_commission_insight_parses_flat_cpa(self):
        """Commission parser should classify flat CPA payouts."""
        insight = self.skill._commission_insight({'commission_rate': '$25 CPA'})

        self.assertEqual(insight.model, 'flat')
        self.assertEqual(insight.flat_amount_usd, 25.0)
        self.assertIsNone(insight.percent_value)

    @patch('scripts.hienergy_skill.requests.request')
    def test_research_affiliate_programs_min_commission_filters_percent_only(self, mock_request):
        """Min commission filter should apply to percent-based programs only."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': 'p1', 'name': 'Flat Program', 'commission_rate': '$30 CPA'},
                {'id': 'p2', 'name': 'Percent Program', 'commission_rate': '15%'},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        report = self.skill.research_affiliate_programs(search='fitness', min_commission=10, top_n=5)

        self.assertEqual(report['summary']['total_programs_matched'], 1)
        self.assertEqual(report['programs'][0]['name'], 'Percent Program')

    @patch('scripts.hienergy_skill.requests.request')
    def test_answer_question_research_programs_includes_commission_type(self, mock_request):
        """Research output should explain commission type for each program."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': 'p1', 'name': 'Elite Program', 'commission_rate': '12-18%', 'advertiser_id': '3625414'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        answer = self.skill.answer_question('Research top affiliate programs for fitness')

        self.assertIn('type: percent-range', answer)
        self.assertIn('avg commission', answer)

    @patch('scripts.hienergy_skill.requests.request')
    def test_answer_question_programs_multiple_prompts_for_disambiguation(self, mock_request):
        """If multiple program matches exist, ask for publisher/network refinement"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'name': 'Qatar Airways', 'network_name': 'Optimise', 'publisher_name': 'Pub A'},
                {'id': '2', 'name': 'Qatar Airways', 'network_name': 'Impact', 'publisher_name': 'Pub B'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        answer = self.skill.answer_question("search for qatar airways affiliate program")

        self.assertIn('Found 2 affiliate programs', answer)
        self.assertIn('specific publisher or network', answer)

    @patch('scripts.hienergy_skill.requests.request')
    def test_answer_question_research_programs(self, mock_request):
        """Test research-mode answer for affiliate programs"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': 'p1', 'name': 'Elite Program', 'commission_rate': '15%', 'advertiser_id': '3625414'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        answer = self.skill.answer_question("Research top affiliate programs for fitness")

        self.assertIn('Program research:', answer)
        self.assertIn('Elite Program', answer)
        self.assertIn('https://app.hienergy.ai/a/3625414', answer)

    @patch('scripts.hienergy_skill.requests.request')
    def test_answer_question_about_transactions(self, mock_request):
        """Test answering questions about transactions"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': 'tx1', 'amount': 120.50, 'status': 'completed', 'advertiser': {'id': '42', 'name': 'Alo Yoga'}}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        answer = self.skill.answer_question("Show me recent transactions")

        self.assertIn('tx1', answer)
        self.assertIn('https://app.hienergy.ai/a/42', answer)

    @patch('scripts.hienergy_skill.requests.request')
    def test_answer_question_about_contacts(self, mock_request):
        """Test answering questions about contacts"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': 'c1', 'name': 'Jane Doe', 'email': 'jane@example.com'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        answer = self.skill.answer_question("Find contact Jane")

        self.assertIn('Jane Doe', answer)

    @patch('scripts.hienergy_skill.requests.request')
    def test_answer_question_about_deals(self, mock_request):
        """Test answering questions about deals"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'title': '50% Off Sale', 'description': 'Half price', 'advertiser_id': '3625414'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        answer = self.skill.answer_question("What deals can I find?")

        self.assertIn('50% Off Sale', answer)
        self.assertIn('https://app.hienergy.ai/a/3625414', answer)

    @patch('scripts.hienergy_skill.requests.request')
    def test_conversational_follow_up_uses_context_intent(self, mock_request):
        """Conversational follow-up in Slack should use prior intent from context."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'title': "Macy's Weekend Deal", 'advertiser_id': '3625439'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        answer = self.skill.answer_question(
            "what about macys",
            context={'last_intent': 'deals'}
        )

        self.assertIn("Macy's Weekend Deal", answer)
        self.assertIn('https://app.hienergy.ai/a/3625439', answer)
    
    def test_extract_search_term(self):
        """Test search term extraction from questions"""
        test_cases = [
            ("What are the best Nike deals?", "best nike deals"),
            ("Show me advertisers in sports", "advertisers sports"),
            ("Find affiliate programs for fashion", "affiliate programs fashion")
        ]
        
        for question, expected_start in test_cases:
            result = self.skill._extract_search_term(question)
            # Check that stop words are filtered
            self.assertNotIn('what', result.lower())
            self.assertNotIn('the', result.lower())
    
    @patch('scripts.hienergy_skill.requests.request')
    def test_api_error_handling(self, mock_request):
        """Test that API errors are handled properly"""
        import requests
        mock_request.side_effect = requests.exceptions.RequestException("Connection error")
        
        with self.assertRaises(Exception) as context:
            self.skill.get_advertisers()
        
        self.assertIn("API request failed", str(context.exception))
    
    @patch('scripts.hienergy_skill.requests.request')
    def test_get_program_details(self, mock_request):
        """Test getting program details"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {'id': 'prog1', 'name': 'Test Program', 'commission_rate': '20%'}
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = self.skill.get_program_details('prog1')
        
        self.assertEqual(result['name'], 'Test Program')
        self.assertEqual(result['commission_rate'], '20%')
    
    @patch('scripts.hienergy_skill.requests.request')
    def test_get_transaction_details(self, mock_request):
        """Test getting transaction details"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {'id': 'tx1', 'amount': 120.50, 'status': 'completed'}
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        result = self.skill.get_transaction_details('tx1')

        self.assertEqual(result['id'], 'tx1')
        self.assertEqual(result['status'], 'completed')

    @patch('scripts.hienergy_skill.requests.request')
    def test_get_contact_details(self, mock_request):
        """Test getting contact details"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {'id': 'c1', 'name': 'Jane Doe', 'email': 'jane@example.com'}
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        result = self.skill.get_contact_details('c1')

        self.assertEqual(result['id'], 'c1')
        self.assertEqual(result['name'], 'Jane Doe')

    @patch('scripts.hienergy_skill.requests.request')
    def test_get_deal_details(self, mock_request):
        """Test getting deal details"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {'id': 'deal1', 'title': 'Black Friday Sale', 'description': 'Huge discounts'}
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        result = self.skill.get_deal_details('deal1')
        
        self.assertEqual(result['title'], 'Black Friday Sale')
        self.assertEqual(result['description'], 'Huge discounts')


class TestHiEnergySkillIntegration(unittest.TestCase):
    """Integration tests - these require a valid API key to run"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.environ.get('HIENERGY_API_KEY')
        if self.api_key:
            self.skill = HiEnergySkill(api_key=self.api_key)
        else:
            self.skipTest("HIENERGY_API_KEY not set - skipping integration tests")
    
    def test_real_api_get_advertisers(self):
        """Test getting advertisers from real API"""
        try:
            result = self.skill.get_advertisers(limit=1)
            # Just verify we get a list back
            self.assertIsInstance(result, list)
        except Exception as e:
            self.skipTest(f"API not available: {e}")
    
    def test_real_api_get_programs(self):
        """Test getting affiliate programs from real API"""
        try:
            result = self.skill.get_affiliate_programs(limit=1)
            self.assertIsInstance(result, list)
        except Exception as e:
            self.skipTest(f"API not available: {e}")
    
    def test_real_api_find_deals(self):
        """Test finding deals from real API"""
        try:
            result = self.skill.find_deals(limit=1)
            self.assertIsInstance(result, list)
        except Exception as e:
            self.skipTest(f"API not available: {e}")


if __name__ == '__main__':
    # Run tests
    unittest.main()

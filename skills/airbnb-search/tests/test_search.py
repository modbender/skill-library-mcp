"""Tests for airbnb_search.search module."""

import pytest
from airbnb_search.search import parse_listings, search_airbnb


# Sample API response structure for testing parsing
MOCK_API_RESPONSE = {
    'data': {
        'dora': {
            'exploreV3': {
                'metadata': {
                    'geography': {
                        'city': 'Steamboat Springs',
                        'fullAddress': 'Steamboat Springs, Colorado, United States'
                    },
                    'paginationMetadata': {
                        'totalCount': 100,
                        'hasNextPage': True
                    }
                },
                'sections': [
                    {
                        '__typename': 'DoraExploreV3ListingsSection',
                        'items': [
                            {
                                'listing': {
                                    'id': '12345',
                                    'name': 'Cozy Mountain Cabin',
                                    'bedrooms': 2,
                                    'bathrooms': 1.5,
                                    'beds': 3,
                                    'avgRating': 4.95,
                                    'reviewsCount': 42,
                                    'roomType': 'Entire cabin',
                                    'propertyType': 'Cabin',
                                    'personCapacity': 4,
                                    'isSuperhost': True,
                                    'city': 'Steamboat Springs',
                                    'lat': 40.4850,
                                    'lng': -106.8317
                                },
                                'pricingQuote': {
                                    'canInstantBook': True,
                                    'structuredStayDisplayPrice': {
                                        'primaryLine': {
                                            'price': '$450 total',
                                            'qualifier': 'before taxes'
                                        }
                                    }
                                }
                            },
                            {
                                'listing': {
                                    'id': '67890',
                                    'name': 'Ski-in/Ski-out Condo',
                                    'bedrooms': 3,
                                    'bathrooms': 2,
                                    'beds': 4,
                                    'avgRating': 4.88,
                                    'reviewsCount': 156,
                                    'roomType': 'Entire condo',
                                    'propertyType': 'Condominium',
                                    'personCapacity': 6,
                                    'isSuperhost': False,
                                    'city': None,  # Test fallback to geography.city
                                    'lat': 40.4571,
                                    'lng': -106.8045
                                },
                                'pricingQuote': {
                                    'canInstantBook': False,
                                    'structuredStayDisplayPrice': {
                                        'primaryLine': {
                                            'discountedPrice': '$380 total',
                                            'originalPrice': '$420 total',
                                            'qualifier': 'before taxes'
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        '__typename': 'DoraExploreV3MapMarkerSection',
                        'items': []  # Should be ignored
                    }
                ]
            }
        }
    }
}


class TestParseListings:
    """Tests for parse_listings function."""

    def test_parse_basic_structure(self):
        """Test that parse_listings returns expected structure."""
        result = parse_listings(MOCK_API_RESPONSE)
        
        assert 'listings' in result
        assert 'total_count' in result
        assert 'has_next_page' in result
        assert 'location' in result

    def test_parse_listing_count(self):
        """Test that correct number of listings are parsed."""
        result = parse_listings(MOCK_API_RESPONSE)
        
        assert len(result['listings']) == 2

    def test_parse_metadata(self):
        """Test metadata parsing."""
        result = parse_listings(MOCK_API_RESPONSE)
        
        assert result['total_count'] == 100
        assert result['has_next_page'] is True
        assert result['location'] == 'Steamboat Springs, Colorado, United States'

    def test_parse_listing_details(self):
        """Test that listing details are correctly parsed."""
        result = parse_listings(MOCK_API_RESPONSE)
        listing = result['listings'][0]
        
        assert listing['id'] == '12345'
        assert listing['name'] == 'Cozy Mountain Cabin'
        assert listing['bedrooms'] == 2
        assert listing['bathrooms'] == 1.5
        assert listing['beds'] == 3
        assert listing['rating'] == 4.95
        assert listing['reviews_count'] == 42
        assert listing['is_superhost'] is True
        assert listing['url'] == 'https://airbnb.com/rooms/12345'

    def test_parse_pricing(self):
        """Test price parsing."""
        result = parse_listings(MOCK_API_RESPONSE)
        listing = result['listings'][0]
        
        assert listing['total_price'] == '$450 total'
        assert listing['total_price_num'] == 450
        assert listing['price_qualifier'] == 'before taxes'

    def test_parse_discounted_price(self):
        """Test that discounted prices are preferred over regular prices."""
        result = parse_listings(MOCK_API_RESPONSE)
        listing = result['listings'][1]
        
        assert listing['total_price'] == '$380 total'
        assert listing['original_price'] == '$420 total'
        assert listing['total_price_num'] == 380

    def test_parse_city_fallback(self):
        """Test that city falls back to geography when listing.city is None."""
        result = parse_listings(MOCK_API_RESPONSE)
        listing = result['listings'][1]
        
        assert listing['city'] == 'Steamboat Springs'

    def test_parse_empty_response(self):
        """Test handling of empty response."""
        result = parse_listings({})
        
        assert result['listings'] == []
        assert result['total_count'] is None
        assert result['has_next_page'] is None

    def test_ignores_non_listing_sections(self):
        """Test that non-listing sections are ignored."""
        result = parse_listings(MOCK_API_RESPONSE)
        
        # Should only have 2 listings, not items from MapMarkerSection
        assert len(result['listings']) == 2


@pytest.mark.integration
class TestSearchAirbnb:
    """Integration tests for search_airbnb function.
    
    These tests make real API calls and may fail if the Airbnb API changes.
    Run with: pytest -m integration
    """

    def test_search_returns_dict(self):
        """Test that search returns a dictionary."""
        result = search_airbnb('New York, NY', items_per_page=5)
        
        assert isinstance(result, dict)
        assert 'data' in result

    def test_search_with_dates(self):
        """Test search with check-in/check-out dates."""
        result = search_airbnb(
            'Denver, CO',
            checkin='2026-03-15',
            checkout='2026-03-17',
            items_per_page=5
        )
        
        assert isinstance(result, dict)
        assert 'data' in result

    def test_search_with_filters(self):
        """Test search with price and bedroom filters."""
        result = search_airbnb(
            'Austin, TX',
            min_price=100,
            max_price=500,
            min_bedrooms=2,
            items_per_page=5
        )
        
        assert isinstance(result, dict)


@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests."""

    def test_full_search_flow(self):
        """Test complete search and parse flow."""
        raw = search_airbnb('Seattle, WA', items_per_page=10)
        result = parse_listings(raw)
        
        assert 'listings' in result
        assert isinstance(result['listings'], list)
        # Should get some results for Seattle
        assert len(result['listings']) > 0

    def test_listing_has_required_fields(self):
        """Test that parsed listings have all required fields."""
        raw = search_airbnb('Portland, OR', items_per_page=5)
        result = parse_listings(raw)
        
        if result['listings']:  # Only test if we got results
            listing = result['listings'][0]
            required_fields = ['id', 'name', 'url', 'bedrooms', 'total_price']
            for field in required_fields:
                assert field in listing, f"Missing field: {field}"

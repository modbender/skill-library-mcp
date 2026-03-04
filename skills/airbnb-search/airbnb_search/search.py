"""Core search functionality for Airbnb."""

import json
import requests
from typing import Optional, Dict, Any

API_KEY = 'd306zoyjsyarp7ifhu67rjxn52tv0t20'
API_URL = 'https://www.airbnb.com/api/v3/ExploreSearch'


def search_airbnb(
    query: str,
    checkin: Optional[str] = None,
    checkout: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_bedrooms: Optional[int] = None,
    items_per_page: int = 50,
    currency: str = 'USD'
) -> Dict[str, Any]:
    """
    Search Airbnb and return raw API results.
    
    Args:
        query: Search location (e.g., "Steamboat Springs, CO")
        checkin: Check-in date (YYYY-MM-DD)
        checkout: Check-out date (YYYY-MM-DD)
        min_price: Minimum price filter
        max_price: Maximum price filter
        min_bedrooms: Minimum bedrooms filter
        items_per_page: Number of results (max 50)
        currency: Currency code (default: USD)
    
    Returns:
        Raw API response as dict
    """
    headers = {'x-airbnb-api-key': API_KEY}
    
    request_params = {
        'metadataOnly': False,
        'version': '1.7.9',
        'itemsPerGrid': items_per_page,
        'tabId': 'home_tab',
        'refinementPaths': ['/homes'],
        'source': 'structured_search_input_header',
        'searchType': 'filter_change',
        'query': query,
        'cdnCacheSafe': False,
        'simpleSearchTreatment': 'simple_search_only',
    }
    
    if checkin:
        request_params['checkin'] = checkin
    if checkout:
        request_params['checkout'] = checkout
    if min_price:
        request_params['priceMin'] = min_price
    if max_price:
        request_params['priceMax'] = max_price
    if min_bedrooms:
        request_params['minBedrooms'] = min_bedrooms
    
    variables = {'request': request_params}
    extensions = {
        'persistedQuery': {
            'version': 1,
            'sha256Hash': '13aa9971e70fbf5ab888f2a851c765ea098d8ae68c81e1f4ce06e2046d91b6ea'
        }
    }
    
    var_str = json.dumps(variables, separators=(',', ':'))
    ext_str = json.dumps(extensions, separators=(',', ':'))
    
    full_url = f'{API_URL}?operationName=ExploreSearch&locale=en&currency={currency}&variables={var_str}&extensions={ext_str}'
    
    response = requests.get(full_url, headers=headers)
    response.raise_for_status()
    return response.json()


def parse_listings(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse raw API response into clean listing data.
    
    Args:
        data: Raw API response from search_airbnb()
    
    Returns:
        Dict with 'listings', 'total_count', 'has_next_page', and 'location'
    """
    listings = []
    
    ev3 = data.get('data', {}).get('dora', {}).get('exploreV3', {})
    metadata = ev3.get('metadata', {})
    geography = metadata.get('geography', {})
    pagination = metadata.get('paginationMetadata', {})
    
    for section in ev3.get('sections', []):
        if section.get('__typename') != 'DoraExploreV3ListingsSection':
            continue
            
        for item in section.get('items', []):
            listing = item.get('listing', {})
            pricing = item.get('pricingQuote', {})
            
            price_struct = pricing.get('structuredStayDisplayPrice', {})
            primary = price_struct.get('primaryLine', {})
            
            total_price = primary.get('discountedPrice') or primary.get('price', '')
            original_price = primary.get('originalPrice', '')
            qualifier = primary.get('qualifier', '')
            
            price_num = None
            if total_price:
                try:
                    price_num = int(''.join(c for c in total_price if c.isdigit()))
                except ValueError:
                    pass
            
            listings.append({
                'id': listing.get('id'),
                'name': listing.get('name'),
                'url': f"https://airbnb.com/rooms/{listing.get('id')}",
                'bedrooms': listing.get('bedrooms'),
                'bathrooms': listing.get('bathrooms'),
                'beds': listing.get('beds'),
                'rating': listing.get('avgRating'),
                'reviews_count': listing.get('reviewsCount'),
                'room_type': listing.get('roomType'),
                'property_type': listing.get('propertyType'),
                'person_capacity': listing.get('personCapacity'),
                'is_superhost': listing.get('isSuperhost'),
                'city': listing.get('city') or geography.get('city'),
                'lat': listing.get('lat'),
                'lng': listing.get('lng'),
                'total_price': total_price,
                'total_price_num': price_num,
                'original_price': original_price,
                'price_qualifier': qualifier,
                'can_instant_book': pricing.get('canInstantBook'),
            })
    
    return {
        'listings': listings,
        'total_count': pagination.get('totalCount'),
        'has_next_page': pagination.get('hasNextPage'),
        'location': geography.get('fullAddress'),
    }

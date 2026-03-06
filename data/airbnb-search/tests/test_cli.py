"""Tests for airbnb_search.cli module."""

import json
import pytest
from unittest.mock import patch
from airbnb_search.cli import main


class TestCLI:
    """Tests for CLI functionality."""

    def test_cli_help(self, capsys):
        """Test that --help works."""
        with pytest.raises(SystemExit) as exc_info:
            main(['--help'])
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert 'airbnb' in captured.out.lower() or 'search' in captured.out.lower()

    def test_cli_requires_query(self, capsys):
        """Test that CLI requires a query argument."""
        with pytest.raises(SystemExit) as exc_info:
            main([])
        
        # Should exit with error code
        assert exc_info.value.code != 0

    @patch('airbnb_search.cli.search_airbnb')
    @patch('airbnb_search.cli.parse_listings')
    def test_cli_json_output(self, mock_parse, mock_search, capsys):
        """Test JSON output format."""
        mock_search.return_value = {'data': {}}
        mock_parse.return_value = {
            'listings': [
                {'id': '123', 'name': 'Test', 'total_price': '$100', 'total_price_num': 100}
            ],
            'total_count': 1,
            'has_next_page': False,
            'location': 'Test City'
        }
        
        main(['Test City', '--json'])
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert 'listings' in output
        assert len(output['listings']) == 1

    @patch('airbnb_search.cli.search_airbnb')
    @patch('airbnb_search.cli.parse_listings')
    def test_cli_default_output(self, mock_parse, mock_search, capsys):
        """Test default (human-readable) output."""
        mock_search.return_value = {'data': {}}
        mock_parse.return_value = {
            'listings': [
                {
                    'id': '123',
                    'name': 'Cozy Cabin',
                    'total_price': '$200 total',
                    'total_price_num': 200,
                    'original_price': None,
                    'price_qualifier': 'before taxes',
                    'bedrooms': 2,
                    'bathrooms': 1,
                    'rating': 4.9,
                    'reviews_count': 50,
                    'is_superhost': True,
                    'url': 'https://airbnb.com/rooms/123'
                }
            ],
            'total_count': 1,
            'has_next_page': False,
            'location': 'Test City'
        }
        
        main(['Test City'])
        
        captured = capsys.readouterr()
        assert 'Cozy Cabin' in captured.out
        assert '$200' in captured.out

    @patch('airbnb_search.cli.search_airbnb')
    @patch('airbnb_search.cli.parse_listings')
    def test_cli_limit_option(self, mock_parse, mock_search):
        """Test --limit option is passed correctly."""
        mock_search.return_value = {'data': {}}
        mock_parse.return_value = {
            'listings': [],
            'total_count': 0,
            'has_next_page': False,
            'location': None
        }
        
        main(['Test', '--limit', '10'])
        
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs.get('items_per_page') == 10

    @patch('airbnb_search.cli.search_airbnb')
    @patch('airbnb_search.cli.parse_listings')
    def test_cli_date_options(self, mock_parse, mock_search):
        """Test --checkin and --checkout options."""
        mock_search.return_value = {'data': {}}
        mock_parse.return_value = {
            'listings': [],
            'total_count': 0,
            'has_next_page': False,
            'location': None
        }
        
        main(['Test', '--checkin', '2026-03-01', '--checkout', '2026-03-05'])
        
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs.get('checkin') == '2026-03-01'
        assert call_kwargs.get('checkout') == '2026-03-05'

    @patch('airbnb_search.cli.search_airbnb')
    @patch('airbnb_search.cli.parse_listings')
    def test_cli_price_filters(self, mock_parse, mock_search):
        """Test --min-price and --max-price options."""
        mock_search.return_value = {'data': {}}
        mock_parse.return_value = {
            'listings': [],
            'total_count': 0,
            'has_next_page': False,
            'location': None
        }
        
        main(['Test', '--min-price', '100', '--max-price', '500'])
        
        mock_search.assert_called_once()
        call_kwargs = mock_search.call_args[1]
        assert call_kwargs.get('min_price') == 100
        assert call_kwargs.get('max_price') == 500

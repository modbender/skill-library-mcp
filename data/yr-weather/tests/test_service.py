#!/usr/bin/env python3
"""
Tests for yr_service.py - mocks urllib.
"""

import unittest
import unittest.mock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts.yr_service import get_location_forecast

class TestYrService(unittest.TestCase):
    @unittest.mock.patch('urllib.request.urlopen')
    def test_get_location_forecast(self, mock_urlopen):
        mock_response = unittest.mock.MagicMock()
        mock_response.read.return_value = b'{"type":"Feature","properties":{}}'
        mock_response.__enter__.return_value = mock_response  # Fix context manager

        data = get_location_forecast(-33.9288, 18.4174)
        expected_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=-33.9288&lon=18.4174"
        self.assertIn(expected_url, mock_urlopen.call_args[0][0].get_full_url())

    @unittest.mock.patch('urllib.request.urlopen')
    def test_with_altitude(self, mock_urlopen):
        mock_response = unittest.mock.MagicMock()
        mock_response.read.return_value = b'{}'
        mock_response.__enter__.return_value = mock_response

        get_location_forecast(-33.9288, 18.4174, "100")
        expected_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=-33.9288&lon=18.4174&altitude=100"
        self.assertIn(expected_url, mock_urlopen.call_args[0][0].get_full_url())

if __name__ == '__main__':
    unittest.main()

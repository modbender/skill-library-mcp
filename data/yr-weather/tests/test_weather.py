#!/usr/bin/env python3
import unittest
import unittest.mock
import sys
import io
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts.weather import format_weather
from scripts.utils import get_emoji
from scripts.tests.data.sample_cape_town import sample_data  # Assume loaded

class TestWeather(unittest.TestCase):
    def test_get_emoji(self):
        self.assertEqual(get_emoji("partlycloudy_night"), "⛅")
        self.assertEqual(get_emoji("unknown"), "🌡️")

    @unittest.mock.patch('scripts.weather.get_location_forecast')
    def test_format_weather(self, mock_service):
        sample = {
            "properties": {
                "meta": {"updated_at": "2026-02-22T04:00:00Z"},
                "timeseries": [
                    {
                        "time": "2026-02-22T04:00:00Z",
                        "data": {
                            "instant": {
                                "details": {
                                    "air_temperature": 18.5,
                                    "wind_speed": 3.2,
                                    "relative_humidity": 75
                                }
                            },
                            "next_1_hours": {
                                "summary": {"symbol_code": "partlycloudy_night"}
                            }
                        }
                    }
                ]
            }
        }
        mock_service.return_value = sample

        f = io.StringIO()
        sys.stdout = f
        format_weather(sample)
        output = f.getvalue()
        self.assertIn("Weather Forecast", output)
        self.assertIn("18.5°C", output)
        sys.stdout = sys.__stdout__

if __name__ == '__main__':
    unittest.main()

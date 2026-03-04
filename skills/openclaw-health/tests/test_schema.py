import os
import sys
import unittest
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from connectors import whoop as whoop_mod
from connectors import oura as oura_mod
from connectors import withings as withings_mod
from core.normalize import normalize


class TestNormalization(unittest.TestCase):
    def test_normalized_schema_keys(self):
        today = datetime.now().strftime("%Y-%m-%d")
        sources = {
            "whoop": whoop_mod.fetch(today),
            "oura": oura_mod.fetch(today),
            "withings": withings_mod.fetch(today),
        }
        norm = normalize(today, sources)
        self.assertIn("date", norm)
        self.assertIn("sources", norm)
        self.assertIn("metrics", norm)
        m = norm["metrics"]
        # Required top-level fields exist
        for key in [
            "sleep",
            "readiness",
            "activity",
            "resting_hr",
            "hrv_rmssd",
            "respiratory_rate",
            "spo2",
            "weight_kg",
            "body_fat_percent",
        ]:
            self.assertIn(key, m)
        # Nested checks
        self.assertIn("total_seconds", m["sleep"])  # may be None but key exists
        self.assertIn("score", m["sleep"])  # may be None but key exists


if __name__ == "__main__":
    unittest.main()


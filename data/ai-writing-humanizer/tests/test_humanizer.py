import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from humanize import humanize_text

class TestHumanizer(unittest.TestCase):
    def test_hedging_removed(self):
        text = 'At the end of the day, this works.'
        self.assertEqual(humanize_text(text), 'this works.')

    def test_stock_transition(self):
        text = 'Firstly, we check this; secondly, we move on.'
        cleaned = humanize_text(text)
        # Expect 'we check this; we move on.' without 'firstly' and 'secondly'
        self.assertNotIn('Firstly', cleaned)
        self.assertNotIn('secondly', cleaned.lower())

    def test_passive_removed(self):
        text = 'The task was completed successfully.'
        cleaned = humanize_text(text)
        self.assertNotIn('was', cleaned)

    def test_em_dash_replaced(self):
        text = 'This is cool — really cool.'
        cleaned = humanize_text(text)
        self.assertNotIn('—', cleaned)
        # expect comma replacement
        self.assertIn(',', cleaned)

if __name__ == '__main__':
    unittest.main()

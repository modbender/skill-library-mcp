import unittest
# Import the solution function. 
# In the sandbox, the user's submission is saved as 'solution.py'
from solution import solve

class TestSolution(unittest.TestCase):
    """
    The Buyer's hidden test suite.
    """
    
    def test_basic_case(self):
        """Test the happy path."""
        input_data = [1, 2, 3]
        expected = 6
        self.assertEqual(solve(input_data), expected)

    def test_edge_case(self):
        """Test edge cases (empty, negative, etc)."""
        self.assertEqual(solve([]), 0)

    def test_performance(self):
        """Optional: Test for efficiency."""
        large_input = list(range(1000))
        # assert execution time < X
        solve(large_input)

if __name__ == '__main__':
    unittest.main()

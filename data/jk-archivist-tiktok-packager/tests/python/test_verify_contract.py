import unittest

from src.python.verify_slides import EXPECTED_FILES, EXPECTED_SIZE


class VerifyContractTests(unittest.TestCase):
    def test_expected_files_and_size_contract(self):
        self.assertEqual(len(EXPECTED_FILES), 6)
        self.assertEqual(EXPECTED_FILES[0], "slide_01.png")
        self.assertEqual(EXPECTED_FILES[-1], "slide_06.png")
        self.assertEqual(EXPECTED_SIZE, (1024, 1536))


if __name__ == "__main__":
    unittest.main()

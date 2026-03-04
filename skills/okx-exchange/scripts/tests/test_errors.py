"""Unit tests for errors.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from errors import (
    OKXBaseError, NetworkError, APIError, BusinessError, ArbHedgeFailedError,
    OKXErrorCode,
)


class TestOKXErrorCode(unittest.TestCase):
    def test_known_codes(self):
        self.assertEqual(OKXErrorCode.INVALID_KEY, 50111)
        self.assertEqual(OKXErrorCode.WRONG_ENV, 50101)

    def test_membership(self):
        self.assertIn(50111, OKXErrorCode.__members__.values())


class TestNetworkError(unittest.TestCase):
    def test_is_base(self):
        e = NetworkError("timeout")
        self.assertIsInstance(e, OKXBaseError)

    def test_message(self):
        self.assertEqual(str(NetworkError("timeout")), "timeout")


class TestAPIError(unittest.TestCase):
    def test_defaults(self):
        e = APIError("bad request")
        self.assertEqual(e.code, "")
        self.assertEqual(e.status, 0)

    def test_with_code_and_status(self):
        e = APIError("not found", code="404", status=404)
        self.assertEqual(e.code, "404")
        self.assertEqual(e.status, 404)

    def test_is_base(self):
        self.assertIsInstance(APIError("x"), OKXBaseError)


class TestBusinessError(unittest.TestCase):
    def test_is_base(self):
        self.assertIsInstance(BusinessError("x"), OKXBaseError)

    def test_code(self):
        e = BusinessError("insufficient margin", code="51020")
        self.assertEqual(e.code, "51020")


class TestArbHedgeFailedError(unittest.TestCase):
    def test_is_business(self):
        e = ArbHedgeFailedError("swap-short", "order failed")
        self.assertIsInstance(e, BusinessError)

    def test_leg_in_message(self):
        e = ArbHedgeFailedError("swap-short", "order failed")
        self.assertIn("swap-short", str(e))

    def test_raise_catch(self):
        with self.assertRaises(ArbHedgeFailedError):
            raise ArbHedgeFailedError("swap-short", "fail")

        with self.assertRaises(BusinessError):
            raise ArbHedgeFailedError("swap-short", "fail")


if __name__ == "__main__":
    unittest.main()

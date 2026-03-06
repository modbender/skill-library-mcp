"""OKX Exchange Skill — Unified error hierarchy"""
from enum import IntEnum


class OKXErrorCode(IntEnum):
    """Common OKX V5 API error codes"""
    INVALID_KEY = 50111
    WRONG_ENV = 50101
    EMPTY_KEY = 50103
    INVALID_SIGN = 50113
    TIMESTAMP_EXPIRED = 50114
    RATE_LIMIT = 50011
    INSUFFICIENT_FUNDS = 51008
    ORDER_NOT_FOUND = 51503


class OKXBaseError(Exception):
    """Base class for all OKX Skill errors"""


class NetworkError(OKXBaseError):
    """Connection-level errors: SSL, timeout, connection refused"""


class APIError(OKXBaseError):
    """HTTP-level or OKX code != 0 errors"""
    def __init__(self, message: str, code: str = "", status: int = 0):
        super().__init__(message)
        self.code = code
        self.status = status


class BusinessError(OKXBaseError):
    """Business-logic violations: insufficient funds, order not found, etc."""
    def __init__(self, message: str, code: str = ""):
        super().__init__(message)
        self.code = code


class ArbHedgeFailedError(BusinessError):
    """Arbitrage hedge leg failed to execute"""
    def __init__(self, leg: str, message: str):
        super().__init__(f"Hedge failed on {leg} leg: {message}", code="ARB_HEDGE_FAIL")
        self.leg = leg

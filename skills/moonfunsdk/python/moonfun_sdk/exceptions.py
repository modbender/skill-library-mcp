"""
Custom exceptions for MoonfunSDK
"""


class MoonfunSDKError(Exception):
    """Base exception for all SDK errors"""
    pass


class AuthenticationError(MoonfunSDKError):
    """Authentication failed (signature or timestamp invalid)"""
    pass


class InvalidSignatureError(AuthenticationError):
    """Signature verification failed"""
    pass


class ExpiredTimestampError(AuthenticationError):
    """Request timestamp expired"""
    pass


class InsufficientBalanceError(MoonfunSDKError):
    """Wallet balance too low"""
    pass


class RateLimitError(MoonfunSDKError):
    """API rate limit exceeded"""
    pass


class NetworkError(MoonfunSDKError):
    """Network connection error"""
    pass


class RPCConnectionError(NetworkError):
    """BSC RPC connection failed"""
    pass


class APIConnectionError(NetworkError):
    """API connection failed"""
    pass


class PlatformError(MoonfunSDKError):
    """MoonnFun platform API error"""
    pass


class LoginError(PlatformError):
    """Platform login failed"""
    pass


class UploadError(PlatformError):
    """Image upload failed"""
    pass


class MetadataCreationError(PlatformError):
    """Token metadata creation failed"""
    pass


class BlockchainError(MoonfunSDKError):
    """Blockchain interaction error"""
    pass


class TransactionFailedError(BlockchainError):
    """Transaction execution failed"""
    pass


class InsufficientGasError(BlockchainError):
    """Insufficient gas for transaction"""
    pass


class ContractError(BlockchainError):
    """Smart contract execution error"""
    pass

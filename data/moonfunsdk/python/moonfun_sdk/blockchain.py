"""
Blockchain Client
Handles Web3 interactions with BSC smart contracts
"""
from web3 import Web3
from typing import Optional
from .auth import AuthManager
from .constants import (
    ROUTER_ADDRESS,
    ROUTER_ABI,
    ERC20_ABI,
    WBNB_ADDRESS,
    CREATE_FEE_BNB,
    CHAIN_ID
)
from .exceptions import (
    RPCConnectionError,
    TransactionFailedError,
    InsufficientGasError,
    ContractError
)


class BlockchainClient:
    """
    Client for BSC blockchain interactions
    
    Features:
        - Token creation via smart contract
        - Balance queries
        - Transaction management
    """
    
    def __init__(self, rpc_url: str, auth_manager: AuthManager):
        """
        Initialize blockchain client
        
        Args:
            rpc_url: BSC RPC endpoint URL
            auth_manager: Authentication manager instance
        
        Raises:
            RPCConnectionError: If unable to connect to RPC
        """
        self.rpc_url = rpc_url
        self.auth = auth_manager
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            raise RPCConnectionError(f"Unable to connect to RPC: {rpc_url}")
        
        # Initialize router contract
        self.router = self.w3.eth.contract(
            address=Web3.to_checksum_address(ROUTER_ADDRESS),
            abi=ROUTER_ABI
        )
    
    def create_token(
        self,
        token_id: int,
        name: str,
        symbol: str,
        salt: int,
        gas_multiplier: float = 1.2
    ) -> str:
        """
        Call contract createToken function
        
        Args:
            token_id: Token ID from platform metadata
            name: Token name
            symbol: Token symbol
            salt: Salt value from platform metadata
            gas_multiplier: Gas price multiplier (default 1.2 = 20% extra)
        
        Returns:
            Transaction hash (0x...)
        
        Raises:
            InsufficientGasError: Not enough BNB for gas
            TransactionFailedError: Transaction reverted
            ContractError: Contract execution error
        """
        try:
            # Get current nonce
            nonce = self.w3.eth.get_transaction_count(self.auth.address)
            
            # Get gas price
            gas_price = int(self.w3.eth.gas_price * gas_multiplier)
            
            # Estimate gas
            try:
                gas_estimate = self.router.functions.createToken(
                    token_id, name, symbol, salt
                ).estimate_gas({
                    'from': self.auth.address,
                    'value': self.w3.to_wei(CREATE_FEE_BNB, 'ether')
                })
                gas_limit = int(gas_estimate * 1.2)  # 20% buffer
            except Exception as e:
                # Gas estimation failed, use default
                gas_limit = 500000
            
            # Build transaction
            tx = self.router.functions.createToken(
                token_id, name, symbol, salt
            ).build_transaction({
                'from': self.auth.address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'value': self.w3.to_wei(CREATE_FEE_BNB, 'ether'),
                'chainId': CHAIN_ID
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(
                tx,
                self.auth.private_key
            )
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] != 1:
                raise TransactionFailedError(
                    f"Transaction failed - Status: {receipt['status']}, "
                    f"TxHash: {tx_hash.hex()}"
                )
            
            return tx_hash.hex()
        
        except ValueError as e:
            error_msg = str(e)
            if "insufficient funds" in error_msg.lower():
                raise InsufficientGasError(
                    f"Insufficient BNB - Need at least {CREATE_FEE_BNB} BNB + gas fees"
                )
            raise ContractError(f"Contract error: {error_msg}")
        
        except Exception as e:
            if isinstance(e, (TransactionFailedError, InsufficientGasError, ContractError)):
                raise
            raise ContractError(f"Unexpected blockchain error: {str(e)}")
    
    def get_balance(self, address: Optional[str] = None) -> float:
        """
        Get BNB balance
        
        Args:
            address: Address to query (defaults to SDK wallet)
        
        Returns:
            Balance in BNB
        """
        addr = address or self.auth.address
        balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(addr))
        return float(self.w3.from_wei(balance_wei, 'ether'))
    
    def get_token_balance(self, token_address: str, address: Optional[str] = None) -> int:
        """
        Get token balance
        
        Args:
            token_address: Token contract address
            address: Address to query (defaults to SDK wallet)
        
        Returns:
            Balance in wei (raw units)
        """
        addr = address or self.auth.address
        
        token_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        
        return token_contract.functions.balanceOf(
            Web3.to_checksum_address(addr)
        ).call()

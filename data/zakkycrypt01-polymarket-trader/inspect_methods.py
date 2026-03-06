
import inspect
from py_clob_client.client import ClobClient

# This script inspects the function signatures to see what arguments they accept.
print("--- Inspecting ClobClient method signatures ---")

try:
    # Print the signature for the singular 'get_market' method
    print("\nSignature for ClobClient.get_market:")
    print(inspect.signature(ClobClient.get_market))
except Exception as e:
    print(f"Could not inspect get_market: {e}")

try:
    # Print the signature for the plural 'get_markets' method
    print("\nSignature for ClobClient.get_markets:")
    print(inspect.signature(ClobClient.get_markets))
except Exception as e:
    print(f"Could not inspect get_markets: {e}")

print("\n-------------------------------------------")

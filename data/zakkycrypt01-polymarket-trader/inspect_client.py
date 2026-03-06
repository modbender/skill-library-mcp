
from py_clob_client.client import ClobClient

# A simple script to inspect the available methods on the ClobClient object.
# This will help us find the correct function name to use instead of 'get_market_by_slug'.

print("--- Inspecting ClobClient class ---")
# We print the directory of the class itself, which lists all its methods.
print(dir(ClobClient))
print("---------------------------------")

"""
Example 1: Create a sandbox and execute Python code

This example demonstrates:
1. Creating a new Lybic sandbox
2. Executing Python code in the sandbox
3. Capturing and displaying output
4. Cleaning up the sandbox
"""

import asyncio
import base64
from lybic import LybicClient


async def main():
    # Initialize the Lybic client (reads credentials from environment variables)
    async with LybicClient() as client:
        print("Creating sandbox...")
        
        # Create a new linux sandbox
        sandbox = await client.sandbox.create(
            name="python-example",
            shape="beijing-2c-4g-cpu-linux",
            maxLifeSeconds=1800  # 30 minutes
        )
        
        print(f"✓ Sandbox created: {sandbox.id}")
        
        # Execute Python code
        code = """
print("Hello from Lybic sandbox!")
import sys
print(f"Python version: {sys.version}")

# Do some calculation
result = sum(range(1, 101))
print(f"Sum of 1 to 100: {result}")
"""
        
        print("Executing Python code...")
        result = await client.sandbox.execute_process(
            sandbox.id,
            executable="python3",
            stdinBase64=base64.b64encode(code.encode()).decode()
        )
        
        # Decode and print output
        stdout = base64.b64decode(result.stdoutBase64 or '').decode()
        stderr = base64.b64decode(result.stderrBase64 or '').decode()
        
        print(f"\n{'='*60}")
        print("STDOUT:")
        print(f"{'='*60}")
        print(stdout)
        
        if stderr:
            print(f"\n{'='*60}")
            print("STDERR:")
            print(f"{'='*60}")
            print(stderr)
        
        print(f"\nExit code: {result.exitCode}")
        
        # Cleanup
        print(f"\nDeleting sandbox {sandbox.id}...")
        await client.sandbox.delete(sandbox.id)
        print("✓ Sandbox deleted")


if __name__ == '__main__':
    asyncio.run(main())

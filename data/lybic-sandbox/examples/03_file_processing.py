"""
Example 3: Download and Process File

This example demonstrates:
1. Downloading a file from URL into sandbox
2. Processing the file with Python
3. Executing commands in a working directory
"""

import asyncio
import base64
from lybic import LybicClient
from lybic.dto import FileCopyItem, HttpGetLocation, SandboxFileLocation


async def main():
    sandbox_id = input("Enter your sandbox ID (e.g., SBX-xxxx): ").strip()
    
    async with LybicClient() as client:
        print(f"Working with sandbox {sandbox_id}")
        
        # Download a sample CSV file
        print("\n📥 Downloading file into sandbox...")
        file_url = "https://raw.githubusercontent.com/plotly/datasets/master/iris.csv"
        
        try:
            await client.sandbox.copy_files(
                sandbox_id,
                files=[
                    FileCopyItem(
                        id="iris-dataset",
                        src=HttpGetLocation(url=file_url),
                        dest=SandboxFileLocation(path="/tmp/iris.csv")
                    )
                ]
            )
            print("✓ File downloaded to /tmp/iris.csv")
        except Exception as e:
            print(f"❌ Error downloading file: {e}")
            return
        
        # List files to verify
        print("\n📂 Listing files in /tmp...")
        result = await client.sandbox.execute_process(
            sandbox_id,
            executable="ls",
            args=["-lh", "/tmp/iris.csv"],
            workingDirectory="/tmp"
        )
        print(base64.b64decode(result.stdoutBase64 or '').decode())
        
        # Process the file with Python
        print("\n🐍 Processing file with Python...")
        code = """
import csv

# Read and analyze the CSV
with open('/tmp/iris.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = list(reader)
    
print(f"Total rows: {len(data)}")
print(f"Columns: {list(data[0].keys())}")
print(f"\\nFirst 3 rows:")
for i, row in enumerate(data[:3], 1):
    print(f"{i}. {row}")

# Count species
species_count = {}
for row in data:
    species = row.get('species', row.get('Name', 'Unknown'))
    species_count[species] = species_count.get(species, 0) + 1

print(f"\\nSpecies distribution:")
for species, count in species_count.items():
    print(f"  {species}: {count}")
"""
        
        result = await client.sandbox.execute_process(
            sandbox_id,
            executable="python3",
            stdinBase64=base64.b64encode(code.encode()).decode(),
            workingDirectory="/tmp"
        )
        
        output = base64.b64decode(result.stdoutBase64 or '').decode()
        print(f"\n{'='*60}")
        print("Output:")
        print(f"{'='*60}")
        print(output)
        
        if result.exitCode == 0:
            print("\n✅ File processed successfully!")
        else:
            print(f"\n❌ Process failed with exit code: {result.exitCode}")
            stderr = base64.b64decode(result.stderrBase64 or '').decode()
            if stderr:
                print(f"Error: {stderr}")


if __name__ == '__main__':
    asyncio.run(main())

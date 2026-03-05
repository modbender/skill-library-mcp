"""
Example 6: HTTP Port Mapping

This example demonstrates:
1. Creating an HTTP port mapping
2. Running a web server in sandbox
3. Accessing the server from outside
4. Cleaning up the mapping
"""

import asyncio
from lybic import LybicClient


async def main():
    sandbox_id = input("Enter your sandbox ID (e.g., SBX-xxxx): ").strip()
    
    async with LybicClient() as client:
        print(f"Working with sandbox {sandbox_id}")
        
        # Verify sandbox
        try:
            sandbox_info = await client.sandbox.get(sandbox_id)
            print(f"✓ Connected to: {sandbox_info.name}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Start a simple HTTP server in the sandbox
        print("\n🚀 Starting Python HTTP server on port 8000...")
        
        # Create a simple HTML file
        html_code = f"""
cat > /tmp/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Lybic Sandbox Server</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{ color: #2c3e50; }}
        .info {{ 
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="info">
        <h1>🎉 Hello from Lybic Sandbox!</h1>
        <p>This page is served from a Python HTTP server running inside a Lybic cloud sandbox.</p>
        <p><strong>Sandbox ID:</strong> {sandbox_id}</p>
        <p>You can access this server from anywhere on the internet thanks to Lybic's HTTP port mapping feature!</p>
    </div>
</body>
</html>
EOF
"""
        
        # Create the HTML file
        result = await client.sandbox.execute_process(
            sandbox_id,
            executable="sh",
            args=["-c", html_code]
        )
        
        if result.exitCode == 0:
            print("✓ HTML file created")
        else:
            print("⚠️ Could not create HTML file")
        
        # Note: For a production server, you would use long-running task support
        # This is a simplified example showing the HTTP mapping creation
        
        # Create HTTP port mapping
        print("\n🔗 Creating HTTP port mapping for port 8000...")
        try:
            mapping = await client.sandbox.create_http_port_mapping(
                sandbox_id=sandbox_id,
                target_endpoint="127.0.0.1:8000"
            )
            
            print(f"\n{'='*60}")
            print("Port Mapping Created!")
            print(f"{'='*60}")
            print(f"Public URL: https://{mapping.domain}")
            print(f"Gateway ID: {mapping.gatewayId}")
            print(f"Created At: {mapping.createdAt}")
            print(f"\n💡 To use this mapping:")
            print(f"   1. Start your server at 127.0.0.1:8000 in the sandbox")
            print(f"   2. Access it via: https://{mapping.domain}")
            print(f"\n📝 Example server start command:")
            print(f"   cd /tmp && python3 -m http.server 8000")
        except Exception as e:
            print(f"❌ Error creating mapping: {e}")
            return
        
        # List all mappings
        print("\n📋 All HTTP port mappings:")
        try:
            mappings = await client.sandbox.list_http_port_mappings(sandbox_id)
            for i, m in enumerate(mappings, 1):
                print(f"\n{i}. https://{m.domain}")
                print(f"   Target: {m.targetEndpoint}")
                print(f"   Token: {m.accessToken[:20]}...")
        except Exception as e:
            print(f"⚠️ Could not list mappings: {e}")
        
        # Ask if user wants to delete the mapping
        print("\n" + "="*60)
        delete = input("\nDelete this mapping? (y/n): ").strip().lower()
        
        if delete == 'y':
            print(f"\n🗑️  Deleting mapping for 127.0.0.1:8000...")
            try:
                await client.sandbox.delete_http_port_mapping(
                    sandbox_id=sandbox_id,
                    target_endpoint="127.0.0.1:8000"
                )
                print("✓ Mapping deleted")
            except Exception as e:
                print(f"❌ Error deleting mapping: {e}")
        else:
            print("\n💡 Mapping kept active. You can delete it later or it will be")
            print("   automatically removed when the sandbox is deleted.")


if __name__ == '__main__':
    asyncio.run(main())

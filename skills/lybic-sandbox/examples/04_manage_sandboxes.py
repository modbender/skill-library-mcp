"""
Example 4: List and Manage Sandboxes

This example demonstrates:
1. Listing all sandboxes in your organization
2. Getting detailed information about sandboxes
3. Creating projects
4. Organizing sandboxes by project
"""

import asyncio
from lybic import LybicClient


async def main():
    async with LybicClient() as client:
        # Get organization stats
        print("📊 Organization Statistics:")
        print("="*60)
        try:
            stats = await client.stats.get()
            print(f"Total Sandboxes: {stats.sandboxes}")
            print(f"Total Projects: {stats.projects}")
            print(f"MCP Servers: {stats.mcpServers}")
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return
        
        # List all projects
        print("\n📁 Projects:")
        print("="*60)
        projects = await client.project.list()
        for project in projects:
            default_marker = " [DEFAULT]" if project.defaultProject else ""
            print(f"  • {project.name}{default_marker}")
            print(f"    ID: {project.id}")
            print(f"    Created: {project.createdAt}")
            print()
        
        # List all sandboxes
        print("\n🖥️  Sandboxes:")
        print("="*60)
        sandboxes = await client.sandbox.list()
        
        if not sandboxes:
            print("No sandboxes found.")
        else:
            for i, sandbox in enumerate(sandboxes, 1):
                print(f"\n{i}. {sandbox.name or 'Unnamed'}")
                print(f"   ID: {sandbox.id}")
                print(f"   Shape: {sandbox.shape}")
                print(f"   Status: {sandbox.status}")
                print(f"   Created: {sandbox.createdAt}")
                
                # Get detailed info
                try:
                    details = await client.sandbox.get(sandbox.id)
                    print(f"   Project: {details.projectId}")
                    print(f"   Max Life: {details.maxLifeSeconds}s")
                except Exception as e:
                    print(f"   ⚠️ Could not get details: {e}")
        
        print(f"\n{'='*60}")
        print(f"Total: {len(sandboxes)} sandbox(es)")
        
        # Option to create a new project
        print("\n" + "="*60)
        create_project = input("\nWould you like to create a new project? (y/n): ").strip().lower()
        
        if create_project == 'y':
            project_name = input("Enter project name: ").strip()
            if project_name:
                print(f"\nCreating project '{project_name}'...")
                try:
                    new_project = await client.project.create(name=project_name)
                    print(f"✓ Project created!")
                    print(f"  ID: {new_project.id}")
                    print(f"  Name: {new_project.name}")
                except Exception as e:
                    print(f"❌ Error creating project: {e}")


if __name__ == '__main__':
    asyncio.run(main())

#!/usr/bin/env python3
"""
Auto Context Manager - Main Module
AI-powered automatic project context management with adaptive learning
"""

import json
import os
from datetime import datetime
from pathlib import Path

PROJECTS_FILE = Path.home() / ".auto-context/projects.json"

class AutoContextManager:
    """Automatic context manager with adaptive learning"""

    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".auto-context"
        self.projects_file = self.data_dir / "projects.json"

        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "vectordb").mkdir(exist_ok=True)

        # Initialize projects if needed
        self._init_projects()

    def _init_projects(self):
        """Initialize projects database"""
        if not self.projects_file.exists():
            # Load default projects template
            default_projects = {
                "projects": {
                    "default": {
                        "name": "Default / General",
                        "description": "General messages and default context",
                        "keywords": ["hello", "help", "status", "general"],
                        "created_at": datetime.now().isoformat(),
                        "last_active": datetime.now().isoformat()
                    }
                },
                "current_project": "default"
            }

            # Save to data directory
            with open(self.projects_file, 'w') as f:
                json.dump(default_projects, f, indent=2)

    def load_projects(self):
        """Load projects database"""
        with open(self.projects_file, 'r') as f:
            return json.load(f)

    def save_projects(self, projects):
        """Save projects database"""
        with open(self.projects_file, 'w') as f:
            json.dump(projects, f, indent=2)

    def detect_project(self, message):
        """Detect project from message"""
        projects = self.load_projects()
        message_lower = message.lower()

        # Score each project
        scores = {}
        for proj_id, proj_data in projects["projects"].items():
            keywords = proj_data.get("keywords", [])
            score = sum(1 for kw in keywords if kw.lower() in message_lower)

            if score > 0:
                scores[proj_id] = score

        # Return best match
        if scores:
            best = max(scores, key=scores.get)
            confidence = scores[best] / len(projects["projects"][best]["keywords"])
            return (best, confidence)

        return ("default", 0.0)

    def switch_project(self, project_id):
        """Switch to different project"""
        projects = self.load_projects()

        if project_id not in projects["projects"]:
            return f"Error: Project '{project_id}' not found"

        old_project = projects.get("current_project", "default")
        projects["current_project"] = project_id
        projects["projects"][project_id]["last_active"] = datetime.now().isoformat()

        self.save_projects(projects)

        return f"Switched from '{old_project}' to '{project_id}'"

    def get_current_project(self):
        """Get current active project"""
        projects = self.load_projects()
        return projects.get("current_project", "default")

    def create_project(self, project_id, name, keywords, description=""):
        """Create new project"""
        projects = self.load_projects()

        if project_id in projects["projects"]:
            raise ValueError(f"Project '{project_id}' already exists")

        projects["projects"][project_id] = {
            "name": name,
            "description": description,
            "keywords": keywords,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }

        self.save_projects(projects)

        return f"Created project '{project_id}'"

    def list_projects(self):
        """List all projects"""
        projects = self.load_projects()
        current = projects.get("current_project", "default")

        output = []
        output.append("Available Projects:")
        output.append("=" * 50)

        for proj_id, proj_data in projects["projects"].items():
            marker = "* " if proj_id == current else "  "
            output.append(f"{marker}{proj_id}")
            output.append(f"   Name: {proj_data['name']}")
            output.append(f"   Keywords: {', '.join(proj_data.get('keywords', [])[:3])}...")
            output.append("")

        return "\n".join(output)

if __name__ == "__main__":
    # Test
    print("Auto Context Manager - Generic Version")
    print("=" * 50)

    acm = AutoContextManager()

    # Test project creation
    print("Creating test project...")
    acm.create_project(
        project_id="test-project",
        name="Test Project",
        keywords=["test", "example", "demo"],
        description="A test project"
    )

    # Test detection
    print("\nTesting project detection...")
    messages = [
        "Hello, how are you?",
        "This is a test message",
        "Show me demo examples"
    ]

    for msg in messages:
        proj, conf = acm.detect_project(msg)
        print(f"'{msg}' → {proj} (conf: {conf:.2f})")

    # List projects
    print("\n" + acm.list_projects())

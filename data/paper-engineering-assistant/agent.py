import os
import json
from pathlib import Path

class PaperEngineer:
    def __init__(self, base_path="./PaperProject"):
        self.base_path = Path(base_path)
        self.structs_path = self.base_path / "structs.json"
        self.summaries_path = self.base_path / "summaries.json"
        self.body_dir = self.base_path / "document_body"
        self.references_dir = self.base_path / "references"
        self.processed_refs_dir = self.base_path / "processed_references"

    def ensure_dirs(self):
        """Ensure necessary directories exist"""
        self.body_dir.mkdir(parents=True, exist_ok=True)
        self.references_dir.mkdir(parents=True, exist_ok=True)
        self.processed_refs_dir.mkdir(parents=True, exist_ok=True)
        return f"Project directories initialized at: {self.base_path.absolute()}"

    def get_project_structure(self):
        """Return the current project structure for context"""
        structure = {
            "project_root": str(self.base_path.absolute()),
            "framework_file": str(self.structs_path) if self.structs_path.exists() else None,
            "summary_file": str(self.summaries_path) if self.summaries_path.exists() else None,
            "body_dir": str(self.body_dir) if self.body_dir.exists() else None,
            "references_count": len(list(self.references_dir.glob("*"))) if self.references_dir.exists() else 0
        }
        return structure

    def update_summary_from_body(self, section_id: str, new_content: str):
        """
        Update the summary layer when a body layer file is modified.
        This is a simplified example; actual implementation would require more sophisticated content analysis.
        """
        if not self.summaries_path.exists():
            return "Summary layer file does not exist. Please initialize the project first."

        with open(self.summaries_path, 'r', encoding='utf-8') as f:
            summaries = json.load(f)

        # TODO: Implement logic to find the corresponding section_id
        # and update its section_summary with a generated summary
        # This would involve a content summarization function
        
        # Placeholder update logic
        for item in summaries:
            if item.get("section_id") == section_id:
                # In practice, you would generate a summary from new_content
                item["section_summary"] = f"Updated summary for {section_id}"
                break

        with open(self.summaries_path, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=2)
        
        return f"Attempted to update summary layer for node: {section_id}"

# Async functions for OpenClaw Gateway
async def sync_on_body_change(section_id: str, new_content: str, project_path: str = "./PaperProject"):
    engineer = PaperEngineer(project_path)
    result = engineer.update_summary_from_body(section_id, new_content)
    return result

async def initialize_project(project_path: str = "./PaperProject"):
    engineer = PaperEngineer(project_path)
    result = engineer.ensure_dirs()
    structure = engineer.get_project_structure()
    return f"{result}\nCurrent structure: {json.dumps(structure, indent=2)}"

async def get_project_status(project_path: str = "./PaperProject"):
    engineer = PaperEngineer(project_path)
    structure = engineer.get_project_structure()
    return json.dumps(structure, indent=2)
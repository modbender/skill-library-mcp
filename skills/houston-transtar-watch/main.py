import os
import subprocess

# Bypass the faulty internal imports for now to see if the UI loads
try:
    from openclaw.skills import BaseSkill
except ImportError:
    # Creating a dummy class so the script doesn't crash the loader
    class BaseSkill:
        def __init__(self):
            self.name = "RunExternalScript"

class RunExternalScript(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "RunExternalScript"
        self.description = "Executes external script"

    async def perform(self, *args, **kwargs):
        # Use an absolute path to your scripts folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Adjust the number of ".." based on your folder depth
        script_path = os.path.join(current_dir, "..", "..", "scripts", "your_script.py")
        
        process = subprocess.run(["python", script_path], capture_output=True, text=True)
        return process.stdout

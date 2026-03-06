import os
import sys
from datetime import datetime
from typing import Optional

# Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler import run_crawl_task, get_default_date_str

# Try to import analysis function from main.py
try:
    from main import process_downloaded_files
except ImportError:
    def process_downloaded_files(*args, **kwargs):
        print("Warning: Analysis function could not be imported from main.py")

def log_callback(msg):
    """Standard logging callback."""
    print(f"[YindengSkill] {msg}")

class YindengSkill:
    """
    Standard Skill for CoPAW to crawl Yindeng announcements and results.
    """
    
    def run(self, date: Optional[str] = None, source: str = "all", analyze: bool = False) -> str:
        """
        Execute the crawling task.

        Args:
            date: Start date in 'YYYY-MM-DD' format. If not provided, defaults to auto-calculation (1-3 days ago).
            source: Source to crawl. Options: 'result', 'announcement', 'all'. Default is 'all'.
            analyze: Whether to perform LLM analysis on the downloaded documents. Default is False.
            
        Returns:
            A summary string of the execution result.
        """
        try:
            # Determine date
            if date:
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                    start_date_str = date
                except ValueError:
                    return f"Error: Invalid date format '{date}'. Please use YYYY-MM-DD."
            else:
                start_date_str = get_default_date_str()
            
            # Determine tasks
            tasks = []
            if source == "all":
                tasks = ["announcement", "result"]
            elif source in ["announcement", "result"]:
                tasks = [source]
            else:
                return f"Error: Invalid source '{source}'. Must be 'result', 'announcement', or 'all'."

            results = []
            total_added = 0
            
            for task_name in tasks:
                log_callback(f"Starting task: {task_name} from {start_date_str}")
                pdf_dir, excel_path, added, no_update = run_crawl_task(task_name, start_date_str=start_date_str, log_cb=log_callback)
                
                if added is not None:
                    total_added += added
                
                task_result = f"Task '{task_name}': "
                if no_update:
                    task_result += "No new updates."
                else:
                    task_result += f"Added {added} records."
                
                if analyze and pdf_dir and excel_path:
                    log_callback(f"Analyzing {task_name}...")
                    process_downloaded_files(pdf_dir, excel_path, log_callback)
                    task_result += " Analysis completed."
                
                results.append(task_result)

            final_summary = "\n".join(results)
            return f"Execution completed.\n{final_summary}\nTotal new records: {total_added}"

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error executing skill: {str(e)}"

# Expose a standalone function for Agent integration
def run_yindeng_crawler(date: Optional[str] = None, source: str = "all", analyze: bool = False) -> str:
    """
    Crawl Yindeng (银登网) announcements and results.
    
    Args:
        date: Start date (YYYY-MM-DD). Defaults to auto (1-3 days ago).
        source: 'result', 'announcement', or 'all'.
        analyze: Enable LLM analysis of PDFs.
    """
    skill = YindengSkill()
    return skill.run(date, source, analyze)

if __name__ == "__main__":
    # Test run
    print(run_yindeng_crawler(source="result", analyze=False))

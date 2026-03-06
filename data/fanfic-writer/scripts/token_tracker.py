"""
Token Tracker - Track token consumption for novel writing process
Records every step's token usage and generates reports
"""
import json
from datetime import datetime
from pathlib import Path

class TokenTracker:
    """Track and report token consumption for novel writing"""
    
    def __init__(self, book_dir):
        self.book_dir = Path(book_dir)
        self.report_file = self.book_dir / "token-report.json"
        self.report = self._load_report()
    
    def _load_report(self):
        """Load existing report or create new one"""
        if self.report_file.exists():
            with open(self.report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Initialize new report
        config_file = self.book_dir / "0-book-config.json"
        book_title = "Unknown"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                book_title = config.get("title", "Unknown")
        
        return {
            "book_title": book_title,
            "book_dir": str(self.book_dir),
            "created_at": datetime.now().isoformat(),
            "total_tokens": {
                "prompt": 0,
                "completion": 0,
                "total": 0
            },
            "total_cost_usd": 0.0,
            "by_phase": {},
            "by_chapter": {},
            "steps": []
        }
    
    def _save_report(self):
        """Save report to file"""
        self.report["updated_at"] = datetime.now().isoformat()
        with open(self.report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
    
    def record_step(self, phase, step_name, prompt_tokens, completion_tokens, 
                    chapter_num=None, notes=None):
        """
        Record token usage for a step
        
        Args:
            phase: One of [outline, worldbuilding, chapter_writing, quality_check, merge]
            step_name: Description of the step
            prompt_tokens: Input tokens
            completion_tokens: Output tokens
            chapter_num: If applicable, which chapter
            notes: Additional notes
        """
        step_record = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "step_name": step_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "chapter_num": chapter_num,
            "notes": notes
        }
        
        # Add to steps list
        self.report["steps"].append(step_record)
        
        # Update total
        self.report["total_tokens"]["prompt"] += prompt_tokens
        self.report["total_tokens"]["completion"] += completion_tokens
        self.report["total_tokens"]["total"] += prompt_tokens + completion_tokens
        
        # Update by_phase
        if phase not in self.report["by_phase"]:
            self.report["by_phase"][phase] = {
                "prompt": 0,
                "completion": 0,
                "total": 0,
                "steps": 0
            }
        self.report["by_phase"][phase]["prompt"] += prompt_tokens
        self.report["by_phase"][phase]["completion"] += completion_tokens
        self.report["by_phase"][phase]["total"] += prompt_tokens + completion_tokens
        self.report["by_phase"][phase]["steps"] += 1
        
        # Update by_chapter if applicable
        if chapter_num is not None:
            ch_key = f"chapter_{chapter_num}"
            if ch_key not in self.report["by_chapter"]:
                self.report["by_chapter"][ch_key] = {
                    "prompt": 0,
                    "completion": 0,
                    "total": 0,
                    "steps": 0
                }
            self.report["by_chapter"][ch_key]["prompt"] += prompt_tokens
            self.report["by_chapter"][ch_key]["completion"] += completion_tokens
            self.report["by_chapter"][ch_key]["total"] += prompt_tokens + completion_tokens
            self.report["by_chapter"][ch_key]["steps"] += 1
        
        # Estimate cost (approximate rates)
        step_cost = self._estimate_cost(prompt_tokens, completion_tokens)
        self.report["total_cost_usd"] += step_cost
        step_record["estimated_cost_usd"] = step_cost
        
        self._save_report()
        return step_record
    
    def _estimate_cost(self, prompt_tokens, completion_tokens):
        """Estimate cost in USD (approximate rates for Claude/GPT-4 class models)"""
        # Approximate: $3 per 1M input tokens, $15 per 1M output tokens
        prompt_cost = (prompt_tokens / 1000000) * 3.0
        completion_cost = (completion_tokens / 1000000) * 15.0
        return round(prompt_cost + completion_cost, 4)
    
    def get_report(self):
        """Get current report"""
        return self.report
    
    def print_summary(self):
        """Print human-readable summary"""
        print("=" * 60)
        print(f"《{self.report['book_title']}》Token消耗报告")
        print("=" * 60)
        print(f"总Token数: {self.report['total_tokens']['total']:,}")
        print(f"  - 输入: {self.report['total_tokens']['prompt']:,}")
        print(f"  - 输出: {self.report['total_tokens']['completion']:,}")
        print(f"预估成本: ${self.report['total_cost_usd']:.2f} USD")
        print()
        
        print("分阶段统计:")
        print("-" * 40)
        for phase, stats in self.report["by_phase"].items():
            print(f"  {phase}: {stats['total']:,} tokens ({stats['steps']} 步)")
        
        if self.report["by_chapter"]:
            print()
            print("按章节统计 (Top 5):")
            print("-" * 40)
            sorted_chapters = sorted(
                self.report["by_chapter"].items(),
                key=lambda x: x[1]['total'],
                reverse=True
            )[:5]
            for ch_key, stats in sorted_chapters:
                print(f"  {ch_key}: {stats['total']:,} tokens")
        
        print("=" * 60)

def create_tracker(book_dir):
    """Factory function to create tracker"""
    return TokenTracker(book_dir)

def record_tokens(book_dir, phase, step_name, prompt_tokens, completion_tokens,
                  chapter_num=None, notes=None):
    """Quick record function"""
    tracker = TokenTracker(book_dir)
    return tracker.record_step(phase, step_name, prompt_tokens, completion_tokens,
                               chapter_num, notes)

def get_report_for_book(book_dir):
    """Get report for a specific book"""
    tracker = TokenTracker(book_dir)
    return tracker.get_report()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: token_tracker.py <book_dir> [summary]")
        print("  book_dir: Path to book directory")
        print("  summary: Print summary report")
        sys.exit(1)
    
    book_dir = sys.argv[1]
    tracker = TokenTracker(book_dir)
    
    if len(sys.argv) > 2 and sys.argv[2] == "summary":
        tracker.print_summary()
    else:
        # Example: Record a step
        tracker.record_step(
            phase="chapter_writing",
            step_name="Generate detailed outline for Chapter 1",
            prompt_tokens=3500,
            completion_tokens=2800,
            chapter_num=1,
            notes="First attempt"
        )
        print("Token usage recorded.")

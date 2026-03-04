#!/usr/bin/env python3
"""
Self-Reflection Module
Provides periodic self-reflection capabilities for overkill-memory-system

Reflection Areas:
- What went well
- What could improve
- Lessons learned
- Next steps
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class SelfReflector:
    """Handles periodic self-reflection for the memory system"""
    
    def __init__(self, reflections_path: str = "~/.openclaw/memory/reflections"):
        self.reflections_path = Path(reflections_path).expanduser()
        self.reflections_path.mkdir(parents=True, exist_ok=True)
        
    def _get_date_filename(self, date: datetime = None) -> Path:
        """Get filename for a specific date"""
        if date is None:
            date = datetime.now()
        return self.reflections_path / f"{date.strftime('%Y-%m-%d')}.json"
    
    def _load_day_reflections(self, date: datetime = None) -> List[Dict]:
        """Load reflections for a specific day"""
        filepath = self._get_date_filename(date)
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get('reflections', [])
        return []
    
    def _save_reflections(self, date: datetime, reflections: List[Dict]):
        """Save reflections for a specific day"""
        filepath = self._get_date_filename(date)
        data = {
            'date': date.strftime('%Y-%m-%d'),
            'reflections': reflections
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def reflect_task(self, task: str, outcome: str, notes: str = "") -> Dict:
        """
        Reflect on a completed task
        
        Args:
            task: Description of the task
            outcome: Outcome of the task (success, partial, failure)
            notes: Additional notes/lessons
        
        Returns:
            The created reflection entry
        """
        reflection = {
            'type': 'task',
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'outcome': outcome,
            'notes': notes,
            'what_went_well': self._extract_well(outcome, notes),
            'what_could_improve': self._extract_improve(outcome, notes),
            'lessons': self._extract_lessons(notes)
        }
        
        # Load today's reflections and add new one
        today = datetime.now()
        reflections = self._load_day_reflections(today)
        reflections.append(reflection)
        self._save_reflections(today, reflections)
        
        return reflection
    
    def _extract_well(self, outcome: str, notes: str) -> str:
        """Extract what went well from outcome and notes"""
        if outcome.lower() in ['success', 'good', 'positive']:
            return "Task completed successfully"
        elif outcome.lower() in ['partial', 'mixed']:
            return "Some aspects completed well"
        return "Completed despite challenges"
    
    def _extract_improve(self, outcome: str, notes: str) -> str:
        """Extract areas for improvement"""
        if outcome.lower() == 'failure':
            return "Need to analyze root cause"
        elif outcome.lower() == 'partial':
            return "Could improve on incomplete aspects"
        return "Room for optimization"
    
    def _extract_lessons(self, notes: str) -> str:
        """Extract lessons from notes"""
        if notes:
            return notes[:200]  # Truncate long notes
        return "Continue iterating and improving"
    
    def daily_review(self) -> Dict:
        """
        Perform daily self-assessment
        
        Returns:
            Summary of the day's reflections and focus areas
        """
        today = datetime.now()
        reflections = self._load_day_reflections(today)
        
        # Filter task reflections
        task_reflections = [r for r in reflections if r.get('type') == 'task']
        
        # Calculate success rate
        success_count = sum(1 for r in task_reflections 
                          if r.get('outcome', '').lower() in ['success', 'good'])
        total_tasks = len(task_reflections)
        
        review = {
            'type': 'daily_review',
            'date': today.strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'total_reflections': len(reflections),
            'tasks_completed': total_tasks,
            'success_rate': f"{success_count}/{total_tasks}" if total_tasks > 0 else "N/A",
            'focus_tomorrow': self._suggest_focus(reflections),
            'summary': self._generate_summary(reflections)
        }
        
        # Save daily review
        reflections.append(review)
        self._save_reflections(today, reflections)
        
        return review
    
    def _suggest_focus(self, reflections: List[Dict]) -> str:
        """Suggest focus areas based on recent reflections"""
        if not reflections:
            return "Continue current tasks"
        
        # Look for patterns in what could improve
        improvements = [r.get('what_could_improve', '') for r in reflections 
                      if r.get('type') == 'task']
        
        if improvements:
            return improvements[-1]  # Focus on most recent area
        
        return "Maintain momentum"
    
    def _generate_summary(self, reflections: List[Dict]) -> str:
        """Generate a summary of the day's reflections"""
        if not reflections:
            return "No reflections recorded today"
        
        task_count = len([r for r in reflections if r.get('type') == 'task'])
        review_count = len([r for r in reflections if r.get('type') == 'daily_review'])
        
        parts = []
        if task_count > 0:
            parts.append(f"{task_count} task(s) reflected on")
        if review_count > 0:
            parts.append("1 daily review completed")
        
        return "; ".join(parts) if parts else "Quiet day of reflection"
    
    def weekly_review(self) -> Dict:
        """
        Perform weekly reflection
        
        Returns:
            Summary of the week's progress and insights
        """
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        # Collect all reflections from the week
        all_reflections = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_reflections = self._load_day_reflections(day)
            all_reflections.extend(day_reflections)
        
        # Analyze the week
        task_reflections = [r for r in all_reflections if r.get('type') == 'task']
        daily_reviews = [r for r in all_reflections if r.get('type') == 'daily_review']
        
        # Success stats
        success_count = sum(1 for r in task_reflections 
                          if r.get('outcome', '').lower() in ['success', 'good'])
        total_tasks = len(task_reflections)
        
        review = {
            'type': 'weekly_review',
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': today.strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'total_reflections': len(all_reflections),
            'tasks_completed': total_tasks,
            'daily_reviews': len(daily_reviews),
            'success_rate': f"{success_count}/{total_tasks}" if total_tasks > 0 else "N/A",
            'achievements': self._extract_achievements(task_reflections),
            'challenges': self._extract_challenges(task_reflections),
            'insights': self._extract_insights(all_reflections)
        }
        
        # Save weekly review
        reflections = self._load_day_reflections(today)
        reflections.append(review)
        self._save_reflections(today, reflections)
        
        return review
    
    def _extract_achievements(self, task_reflections: List[Dict]) -> List[str]:
        """Extract achievements from task reflections"""
        achievements = []
        for r in task_reflections:
            if r.get('outcome', '').lower() in ['success', 'good']:
                achievements.append(r.get('task', 'Task completed'))
        return achievements[:5]  # Limit to top 5
    
    def _extract_challenges(self, task_reflections: List[Dict]) -> List[str]:
        """Extract challenges from task reflections"""
        challenges = []
        for r in task_reflections:
            if r.get('outcome', '').lower() in ['partial', 'failure']:
                challenges.append(r.get('task', 'Task had issues'))
        return challenges[:5]
    
    def _extract_insights(self, all_reflections: List[Dict]) -> List[str]:
        """Extract key insights from all reflections"""
        insights = []
        for r in all_reflections:
            if r.get('lessons') and r['lessons'] not in insights:
                insights.append(r['lessons'])
        return insights[:5]
    
    def get_reflections(self, days: int = 7) -> List[Dict]:
        """
        Get reflections from the last N days
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of reflection entries
        """
        today = datetime.now()
        all_reflections = []
        
        for i in range(days):
            day = today - timedelta(days=i)
            day_reflections = self._load_day_reflections(day)
            all_reflections.extend(day_reflections)
        
        # Sort by timestamp (newest first)
        all_reflections.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return all_reflections


# CLI helper functions
def cli_reflect_task(task: str, outcome: str, notes: str = "") -> Dict:
    """CLI wrapper for reflect_task"""
    reflector = SelfReflector()
    return reflector.reflect_task(task, outcome, notes)


def cli_daily_review() -> Dict:
    """CLI wrapper for daily_review"""
    reflector = SelfReflector()
    return reflector.daily_review()


def cli_weekly_review() -> Dict:
    """CLI wrapper for weekly_review"""
    reflector = SelfReflector()
    return reflector.weekly_review()


def cli_list_reflections(days: int = 7) -> List[Dict]:
    """CLI wrapper for get_reflections"""
    reflector = SelfReflector()
    return reflector.get_reflections(days)


if __name__ == "__main__":
    # Test functionality
    reflector = SelfReflector()
    
    # Demo: Add a test reflection
    print("Self-Reflection Module")
    print("=" * 40)
    
    # Test task reflection
    result = reflector.reflect_task(
        task="Implemented self-reflection feature",
        outcome="success",
        notes="Used the framework from SELF_REFLECTION_INTEGRATION.md"
    )
    print(f"Task Reflection: {json.dumps(result, indent=2)}")
    
    # Get recent reflections
    recent = reflector.get_reflections(7)
    print(f"\nRecent Reflections: {len(recent)}")

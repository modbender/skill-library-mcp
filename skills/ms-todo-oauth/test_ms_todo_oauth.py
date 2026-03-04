#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for ms-todo-oauth.py
Tests all commands and features to ensure they work properly
"""

import subprocess
import time
import json
import sys
from datetime import datetime, timedelta

# ANSI colors for better output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class TestRunner:
    def __init__(self, script_path="scripts/ms-todo-oauth.py"):
        self.script_path = script_path
        self.test_list_name = f"🧪 Test List {datetime.now().strftime('%H:%M:%S')}"
        self.passed = 0
        self.failed = 0
        self.test_results = []
        
    def run_command(self, *args):
        """Run a ms-todo-oauth.py command and return output"""
        cmd = ["uv", "run", self.script_path] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def test(self, name, *args, expect_success=True, check_output=None):
        """Run a test case"""
        print(f"\n{BLUE}Testing:{RESET} {name}")
        print(f"  Command: ms-todo-oauth.py {' '.join(args)}")
        
        returncode, stdout, stderr = self.run_command(*args)
        
        # Check return code
        success = (returncode == 0) if expect_success else (returncode != 0)
        
        # Check output if specified
        if success and check_output:
            if isinstance(check_output, str):
                success = check_output in stdout
            elif callable(check_output):
                success = check_output(stdout)
        
        # Record result
        if success:
            print(f"  {GREEN}✓ PASSED{RESET}")
            self.passed += 1
            self.test_results.append(("PASS", name))
        else:
            print(f"  {RED}✗ FAILED{RESET}")
            print(f"  Return code: {returncode}")
            if stdout:
                print(f"  Output: {stdout[:200]}")
            if stderr:
                print(f"  Error: {stderr[:200]}")
            self.failed += 1
            self.test_results.append(("FAIL", name))
        
        time.sleep(0.5)  # Small delay between tests
        return success
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n" + "="*70)
        print(f"{YELLOW}ms-todo-oauth comprehensive test suite{RESET}")
        print("="*70)
        
        # Test 1: List all task lists
        self.test(
            "List all task lists",
            "lists",
            check_output=lambda x: "Task Lists" in x or "No task lists" in x
        )
        
        # Test 2: Create a test list
        self.test(
            "Create a new task list",
            "create-list",
            self.test_list_name,
            check_output=f"✓ List created: {self.test_list_name}"
        )
        
        # Test 3: Add simple task
        self.test(
            "Add simple task",
            "add",
            "-l", self.test_list_name,
            "Simple test task",
            check_output="✓ Task added"
        )
        
        # Test 4: Add task with high priority
        self.test(
            "Add high priority task",
            "add",
            "-l", self.test_list_name,
            "High priority task",
            "-p", "high",
            check_output="✓ Task added"
        )
        
        # Test 5: Add task with due date (tomorrow)
        self.test(
            "Add task with due date (1 day)",
            "add",
            "-l", self.test_list_name,
            "Task due tomorrow",
            "-d", "1",
            check_output="✓ Task added"
        )
        
        # Test 6: Add task with specific date
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.test(
            "Add task with specific due date",
            "add",
            "-l", self.test_list_name,
            "Task due next week",
            "-d", future_date,
            check_output="✓ Task added"
        )
        
        # Test 7: Add task with reminder (3 hours)
        self.test(
            "Add task with reminder",
            "add",
            "-l", self.test_list_name,
            "Task with reminder",
            "-r", "3h",
            check_output="✓ Task added"
        )
        
        # Test 8: Add task with description
        self.test(
            "Add task with description",
            "add",
            "-l", self.test_list_name,
            "Task with notes",
            "-D", "This is a detailed description of the task",
            check_output="✓ Task added"
        )
        
        # Test 9: Add task with tags/categories
        self.test(
            "Add task with tags",
            "add",
            "-l", self.test_list_name,
            "Task with tags",
            "-t", "work,important,urgent",
            check_output="✓ Task added"
        )
        
        # Test 10: Add daily recurring task
        self.test(
            "Add daily recurring task",
            "add",
            "-l", self.test_list_name,
            "Daily recurring task",
            "-R", "daily",
            check_output="✓ Task added"
        )
        
        # Test 11: Add weekly recurring task
        self.test(
            "Add weekly recurring task",
            "add",
            "-l", self.test_list_name,
            "Weekly recurring task",
            "-R", "weekly",
            check_output="✓ Task added"
        )
        
        # Test 12: Add weekdays recurring task
        self.test(
            "Add weekdays recurring task",
            "add",
            "-l", self.test_list_name,
            "Weekday recurring task",
            "-R", "weekdays",
            check_output="✓ Task added"
        )
        
        # Test 13: Add task with all options combined
        self.test(
            "Add task with all options",
            "add",
            "-l", self.test_list_name,
            "Complete featured task",
            "-p", "high",
            "-d", "3",
            "-D", "Task with all features enabled",
            "-t", "test,comprehensive",
            check_output="✓ Task added"
        )
        
        # Test 14: List tasks in the test list
        self.test(
            "List tasks in test list",
            "tasks",
            self.test_list_name,
            check_output=lambda x: "Tasks in list" in x and self.test_list_name in x
        )
        
        # Test 15: List tasks including completed
        self.test(
            "List all tasks including completed",
            "tasks",
            self.test_list_name,
            "-a",
            check_output="Tasks in list"
        )
        
        # Test 16: View task details
        self.test(
            "View task details",
            "detail",
            "-l", self.test_list_name,
            "Simple test task",
            check_output="Task Details"
        )
        
        # Test 17: Search for tasks
        self.test(
            "Search for tasks",
            "search",
            "test task",
            check_output=lambda x: "Search results" in x or "Tasks found" in x or "Simple test task" in x
        )
        
        # Test 18: Complete a task
        self.test(
            "Complete a task",
            "complete",
            "-l", self.test_list_name,
            "Simple test task",
            check_output="✓ Task completed"
        )
        
        # Test 19: View statistics
        self.test(
            "View statistics",
            "stats",
            check_output="Task Statistics"
        )
        
        # Test 20: View pending tasks
        self.test(
            "View pending tasks",
            "pending",
            check_output=lambda x: "incomplete task" in x.lower() or "pending" in x.lower()
        )
        
        # Test 21: View pending tasks grouped
        self.test(
            "View pending tasks grouped by list",
            "pending",
            "-g",
            check_output=self.test_list_name
        )
        
        # Test 22: View today's tasks
        self.test(
            "View today's tasks",
            "today",
            check_output=lambda x: "due today" in x.lower() or "no tasks" in x.lower()
        )
        
        # Test 23: View overdue tasks
        self.test(
            "View overdue tasks",
            "overdue",
            check_output=lambda x: "overdue" in x.lower() or "no overdue" in x.lower()
        )
        
        # Test 24: Export tasks to JSON
        export_file = f"test_export_{int(time.time())}.json"
        if self.test(
            "Export tasks to JSON",
            "export",
            "-o", export_file,
            check_output=f"✓ Tasks exported to: {export_file}"
        ):
            # Verify the export file exists and is valid JSON
            try:
                import os
                if os.path.exists(export_file):
                    with open(export_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print(f"  {GREEN}✓ Export file is valid JSON{RESET}")
                    os.remove(export_file)  # Clean up
            except Exception as e:
                print(f"  {RED}✗ Export file validation failed: {e}{RESET}")
        
        # Test 25: Delete a task
        self.test(
            "Delete a task",
            "delete",
            "-l", self.test_list_name,
            "Task with tags",
            "-y",  # Skip confirmation
            check_output="✓ Task deleted"
        )
        
        # Test 26: Try to delete non-existent task
        self.test(
            "Attempt to delete non-existent task",
            "delete",
            "-l", self.test_list_name,
            "This task does not exist",
            "-y",
            expect_success=False,
            check_output="Task not found"
        )
        
        # Test 27: Delete the test list
        self.test(
            "Delete test list",
            "delete-list",
            self.test_list_name,
            "-y",  # Skip confirmation
            check_output="✓ List deleted"
        )
        
        # Test 28: Verify list was deleted
        returncode, stdout, stderr = self.run_command("lists")
        if self.test_list_name not in stdout:
            print(f"\n{BLUE}Testing:{RESET} Verify list deletion")
            print(f"  {GREEN}✓ PASSED{RESET} - Test list no longer exists")
            self.passed += 1
            self.test_results.append(("PASS", "Verify list deletion"))
        else:
            print(f"\n{BLUE}Testing:{RESET} Verify list deletion")
            print(f"  {RED}✗ FAILED{RESET} - Test list still exists")
            self.failed += 1
            self.test_results.append(("FAIL", "Verify list deletion"))
        
        # Test 29: Verbose mode
        self.test(
            "Verbose mode with lists",
            "-v",
            "lists",
            check_output="ID:"
        )
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print(f"{YELLOW}TEST SUMMARY{RESET}")
        print("="*70)
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"Pass rate: {pass_rate:.1f}%")
        
        if self.failed > 0:
            print(f"\n{RED}Failed tests:{RESET}")
            for status, name in self.test_results:
                if status == "FAIL":
                    print(f"  ✗ {name}")
        
        print("\n" + "="*70)
        
        if self.failed == 0:
            print(f"{GREEN}🎉 ALL TESTS PASSED! 🎉{RESET}")
        else:
            print(f"{YELLOW}⚠️  Some tests failed. Please review the output above.{RESET}")
        
        print("="*70 + "\n")

def main():
    """Main function"""
    print(f"\n{BLUE}Starting comprehensive test suite...{RESET}\n")
    
    # Check if authenticated
    runner = TestRunner()
    returncode, stdout, stderr = runner.run_command("lists")
    
    if returncode != 0 and "Not logged in" in (stdout + stderr):
        print(f"{RED}ERROR: Not authenticated!{RESET}")
        print("\nPlease authenticate first:")
        print("  1. uv run scripts/ms-todo-oauth.py login get")
        print("  2. uv run scripts/ms-todo-oauth.py login verify <code>")
        sys.exit(1)
    
    # Run all tests
    runner.run_all_tests()
    
    sys.exit(0 if runner.failed == 0 else 1)

if __name__ == "__main__":
    main()

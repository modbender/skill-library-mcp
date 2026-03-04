MS-TODO-OAUTH TEST SUITE
=======================

This package contains comprehensive testing tools for ms-todo-oauth.py to verify
all functionality works correctly after fixes or updates.

FILES INCLUDED:
---------------
1. test_ms_todo_sync.py         - Automated test script (29 tests)
2. MANUAL_TEST_CHECKLIST.txt    - Manual testing checklist
3. TEST_README.txt              - This file


OPTION 1: AUTOMATED TESTING (RECOMMENDED)
==========================================

Prerequisites:
--------------
1. You must be authenticated (logged in) before running tests
2. The script will create and delete a test list automatically
3. Requires Python 3.7+ and the same dependencies as ms-todo-oauth.py

How to Run:
-----------
1. Navigate to your project directory:
   cd ~/clawd/skills/ms-todo-oauth

2. Make the test script executable:
   chmod +x test_ms_todo_sync.py

3. Run the automated tests:
   python3 test_ms_todo_sync.py

   OR if using uv:
   uv run test_ms_todo_sync.py

What It Tests:
--------------
The automated script runs 29 comprehensive tests covering:

✓ List Management (3 tests)
  - List all task lists
  - Create new list
  - Delete list

✓ Basic Task Operations (6 tests)
  - Add simple task
  - List tasks
  - View task details
  - Search tasks
  - Complete task
  - Delete task

✓ Tasks with Options (7 tests)
  - High/low priority tasks
  - Tasks with due dates (relative and absolute)
  - Tasks with reminders
  - Tasks with descriptions
  - Tasks with tags/categories
  - Combined options

✓ Recurring Tasks (4 tests)
  - Daily recurring
  - Weekly recurring
  - Weekdays recurring
  - Custom intervals

✓ Task Views (5 tests)
  - Today's tasks
  - Overdue tasks
  - Pending tasks
  - Grouped views
  - Statistics

✓ Data Management (2 tests)
  - Export to JSON
  - JSON validation

✓ Error Handling (2 tests)
  - Non-existent tasks
  - Non-existent lists

Expected Output:
----------------
The script will show:
- Progress for each test
- ✓ PASSED in green for successful tests
- ✗ FAILED in red for failed tests
- Final summary with pass rate

Example:
========================================================================
Testing: Add simple task
  Command: ms-todo-oauth.py add -l 🧪 Test List 14:23:45 Simple test task
  ✓ PASSED

Testing: Add high priority task
  Command: ms-todo-oauth.py add -l 🧪 Test List 14:23:45 High priority task -p high
  ✓ PASSED
...
========================================================================
TEST SUMMARY
========================================================================

Total tests: 29
Passed: 29
Failed: 0
Pass rate: 100.0%

========================================================================
🎉 ALL TESTS PASSED! 🎉
========================================================================


OPTION 2: MANUAL TESTING
=========================

If you prefer to test manually or want to test specific features:

1. Open MANUAL_TEST_CHECKLIST.txt
2. Follow the commands listed for each test category
3. Check off each test as you complete it
4. Note any failures or unexpected behavior

Manual testing is recommended when:
- You want to verify specific functionality
- You want to test edge cases not covered by automation
- You're debugging a specific issue
- You want to understand how each command works


TROUBLESHOOTING
===============

Test fails with "Not logged in":
---------------------------------
You need to authenticate first:
  uv run scripts/ms-todo-oauth.py login get
  uv run scripts/ms-todo-oauth.py login verify <code>

Test fails with "Module not found":
------------------------------------
Ensure all dependencies are installed:
  uv sync

Tests timeout or hang:
----------------------
- Check your internet connection
- Verify you can access Microsoft Graph API
- Try running with debug mode: --debug flag

Some tests fail but others pass:
---------------------------------
This is normal during development. Check which tests failed and review:
1. The specific error messages
2. Whether it's a script bug or API issue
3. The MANUAL_TEST_CHECKLIST for that specific feature


INTERPRETING RESULTS
====================

100% Pass Rate:
- All functionality working correctly
- Safe to use in production
- All features tested and verified

90-99% Pass Rate:
- Most functionality working
- Review failed tests
- May be acceptable depending on features you use

Below 90%:
- Significant issues present
- Review all failed tests carefully
- Do not use in production until fixed


CONTINUOUS TESTING
==================

Run this test suite:
- After every code change
- Before committing changes
- After pulling updates
- When switching between environments
- When you notice unexpected behavior


CONTRIBUTING TEST CASES
========================

If you find a bug that isn't caught by these tests:
1. Document the steps to reproduce
2. Add it to MANUAL_TEST_CHECKLIST.txt
3. Consider contributing it to the automated test suite


SUPPORT
=======

If tests fail unexpectedly:
1. Check that ms-todo-oauth.py has all the fixes applied
2. Verify you're authenticated
3. Check your internet connection
4. Review the error messages carefully
5. Run individual commands manually to isolate the issue


CLEANUP
=======

The automated test script:
- Creates a test list with timestamp (e.g., "🧪 Test List 14:23:45")
- Deletes the test list after tests complete
- Cleans up export files

If tests crash or are interrupted:
- You may have leftover test lists in your account
- Delete them manually: uv run scripts/ms-todo-oauth.py delete-list "<list_name>" -y

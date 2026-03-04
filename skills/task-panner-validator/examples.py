"""
Example Usage of Task Planner and Validator
Demonstrates how to use the task planning system
"""

from task_planner import TaskPlanner, TaskStatus, StepStatus


def example_executor(action: str, parameters: dict):
    """
    Example executor function that simulates step execution
    
    In a real implementation, this would:
    - Make API calls
    - Execute shell commands
    - Perform file operations
    - etc.
    """
    print(f"Executing: {action}")
    print(f"Parameters: {parameters}")
    
    # Simulate different actions
    if action == "fetch_data":
        return {"status": "success", "data": [1, 2, 3, 4, 5]}
    elif action == "process_data":
        return {"status": "success", "processed": True}
    elif action == "save_results":
        return {"status": "success", "file": "results.json"}
    else:
        return {"status": "success", "message": "Action completed"}


def example_1_basic_usage():
    """Example 1: Basic task planning and execution"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60 + "\n")
    
    # Create planner
    planner = TaskPlanner(auto_approve=False)
    
    # Define steps
    steps = [
        {
            "description": "Fetch user data from API",
            "action": "fetch_data",
            "parameters": {"endpoint": "/api/users", "method": "GET"},
            "expected_output": "List of user objects",
            "safety_check": True,
            "rollback_possible": True
        },
        {
            "description": "Process and validate data",
            "action": "process_data",
            "parameters": {"validation_rules": ["email", "age"]},
            "expected_output": "Validated user data",
            "safety_check": True,
            "rollback_possible": True
        },
        {
            "description": "Save results to database",
            "action": "save_results",
            "parameters": {"database": "users_db", "table": "validated_users"},
            "expected_output": "Success confirmation",
            "safety_check": True,
            "rollback_possible": True
        }
    ]
    
    # Create plan
    plan = planner.create_plan(
        title="User Data Processing Pipeline",
        description="Fetch, validate, and save user data",
        steps=steps
    )
    
    print(f"Created plan: {plan.task_id}")
    print(f"Status: {plan.status.value}")
    print(f"Total steps: {len(plan.steps)}\n")
    
    # Validate plan
    is_valid, warnings = planner.validate_plan(plan)
    print(f"Plan validation: {'✅ VALID' if is_valid else '❌ INVALID'}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    print()
    
    # Approve plan
    if planner.approve_plan(plan, approved_by="admin"):
        print(f"✅ Plan approved by: {plan.approved_by}\n")
    
    # Execute plan (dry run)
    print("Executing plan (DRY RUN)...")
    success, results = planner.execute_plan(plan, example_executor, dry_run=True)
    
    print(f"\nExecution completed: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Show summary
    summary = planner.get_execution_summary(plan)
    print(f"\nExecution Summary:")
    print(f"  Total Steps: {summary['total_steps']}")
    print(f"  Completed: {summary['completed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Progress: {summary['progress_percentage']:.1f}%")


def example_2_dangerous_operations():
    """Example 2: Handling dangerous operations"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Safety Validation - Dangerous Operations")
    print("="*60 + "\n")
    
    planner = TaskPlanner(auto_approve=False)
    
    # Define steps with dangerous operations
    steps = [
        {
            "description": "Create backup of data",
            "action": "backup_data",
            "parameters": {"source": "/data", "destination": "/backup"},
            "expected_output": "Backup file created",
            "safety_check": True,
            "rollback_possible": True
        },
        {
            "description": "Delete old files",
            "action": "delete_files",
            "parameters": {"path": "/data/old", "pattern": "*.tmp"},
            "expected_output": "Files deleted",
            "safety_check": True,
            "rollback_possible": False  # Deletion cannot be rolled back!
        },
        {
            "description": "Clean up backup",
            "action": "remove_backup",
            "parameters": {"path": "/backup/old"},
            "expected_output": "Backup cleaned",
            "safety_check": True,
            "rollback_possible": False
        }
    ]
    
    plan = planner.create_plan(
        title="Data Cleanup Task",
        description="Backup and clean old data files",
        steps=steps
    )
    
    print(f"Created plan: {plan.task_id}\n")
    
    # Validate plan - should show warnings
    is_valid, warnings = planner.validate_plan(plan)
    print(f"Plan validation: {'✅ VALID' if is_valid else '❌ INVALID'}")
    print(f"\nSafety warnings detected: {len(warnings)}")
    for warning in warnings:
        print(f"  {warning}")
    
    print("\n⚠️ Note: Dangerous operations detected - manual review required!")


def example_3_save_and_load():
    """Example 3: Saving and loading plans"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Save and Load Plans")
    print("="*60 + "\n")
    
    planner = TaskPlanner(auto_approve=False)
    
    # Create a simple plan
    steps = [
        {
            "description": "Initialize system",
            "action": "init_system",
            "parameters": {"config": "default"},
            "expected_output": "System initialized"
        },
        {
            "description": "Run health check",
            "action": "health_check",
            "parameters": {"endpoints": ["api", "db", "cache"]},
            "expected_output": "All systems healthy"
        }
    ]
    
    plan = planner.create_plan(
        title="System Health Check",
        description="Initialize and verify system health",
        steps=steps
    )
    
    # Save plan
    filepath = "/home/claude/health_check_plan.json"
    planner.save_plan(plan, filepath)
    print(f"✅ Plan saved to: {filepath}\n")
    
    # Load plan
    loaded_plan = planner.load_plan(filepath)
    print(f"✅ Plan loaded: {loaded_plan.task_id}")
    print(f"Title: {loaded_plan.title}")
    print(f"Steps: {len(loaded_plan.steps)}")
    print(f"Integrity verified: {loaded_plan.verify_integrity()}")


def example_4_auto_approve():
    """Example 4: Auto-approve mode for automation"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Auto-Approve Mode")
    print("="*60 + "\n")
    
    # Create planner with auto-approve enabled
    planner = TaskPlanner(auto_approve=True)
    
    steps = [
        {
            "description": "Generate report",
            "action": "generate_report",
            "parameters": {"format": "pdf", "include_charts": True},
            "expected_output": "Report generated"
        },
        {
            "description": "Send email notification",
            "action": "send_email",
            "parameters": {"to": "team@example.com", "subject": "Report Ready"},
            "expected_output": "Email sent"
        }
    ]
    
    plan = planner.create_plan(
        title="Automated Report Generation",
        description="Generate and send weekly report",
        steps=steps
    )
    
    print(f"Created plan: {plan.task_id}")
    print(f"Auto-approve enabled: {planner.auto_approve}\n")
    
    # Execute directly - will auto-approve
    print("Executing plan with auto-approve...")
    success, results = planner.execute_plan(plan, example_executor, dry_run=True)
    
    print(f"\nPlan status: {plan.status.value}")
    print(f"Execution: {'✅ SUCCESS' if success else '❌ FAILED'}")


def example_5_error_handling():
    """Example 5: Error handling and stop-on-error"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Error Handling")
    print("="*60 + "\n")
    
    planner = TaskPlanner(auto_approve=True)
    
    def failing_executor(action: str, parameters: dict):
        """Executor that fails on specific actions"""
        print(f"Executing: {action}")
        
        if action == "failing_step":
            raise Exception("Simulated failure!")
        
        return {"status": "success"}
    
    steps = [
        {
            "description": "Step 1 - Success",
            "action": "step_1",
            "parameters": {},
            "expected_output": "Success"
        },
        {
            "description": "Step 2 - Will Fail",
            "action": "failing_step",
            "parameters": {},
            "expected_output": "Should fail"
        },
        {
            "description": "Step 3 - Won't Execute",
            "action": "step_3",
            "parameters": {},
            "expected_output": "Won't reach here"
        }
    ]
    
    plan = planner.create_plan(
        title="Error Handling Demo",
        description="Demonstrate error handling",
        steps=steps
    )
    
    print("Executing plan with stop_on_error=True...")
    success, results = planner.execute_plan(
        plan, 
        failing_executor, 
        dry_run=False,
        stop_on_error=True
    )
    
    print(f"\nExecution: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print("\nStep Results:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} Step {result['order']}: {result.get('error', 'Success')}")
    
    summary = planner.get_execution_summary(plan)
    print(f"\nFinal Status: {summary['status']}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("TASK PLANNER AND VALIDATOR - EXAMPLES")
    print("="*60)
    
    example_1_basic_usage()
    example_2_dangerous_operations()
    example_3_save_and_load()
    example_4_auto_approve()
    example_5_error_handling()
    
    print("\n" + "="*60)
    print("ALL EXAMPLES COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

"""
Simple tests to verify Task Planner functionality
Run with: python test_basic.py
"""

from task_planner import TaskPlanner, TaskStatus, StepStatus


def simple_executor(action: str, parameters: dict):
    """Simple executor for testing"""
    return {"status": "success", "action": action, "params": parameters}


def test_plan_creation():
    """Test basic plan creation"""
    print("Testing plan creation...")
    
    planner = TaskPlanner()
    steps = [
        {
            "description": "Step 1",
            "action": "action_1",
            "parameters": {"key": "value"},
            "expected_output": "Output 1"
        }
    ]
    
    plan = planner.create_plan("Test Plan", "Test Description", steps)
    
    assert plan.title == "Test Plan"
    assert len(plan.steps) == 1
    assert plan.status == TaskStatus.PENDING
    assert plan.checksum is not None
    
    print("✅ Plan creation test passed")


def test_plan_validation():
    """Test plan validation"""
    print("Testing plan validation...")
    
    planner = TaskPlanner()
    steps = [
        {
            "description": "Safe step",
            "action": "read_data",
            "parameters": {"file": "data.txt"},
            "expected_output": "Data read"
        }
    ]
    
    plan = planner.create_plan("Validation Test", "Test", steps)
    is_valid, warnings = planner.validate_plan(plan)
    
    assert is_valid == True
    
    print("✅ Plan validation test passed")


def test_dangerous_operations():
    """Test detection of dangerous operations"""
    print("Testing dangerous operation detection...")
    
    planner = TaskPlanner()
    steps = [
        {
            "description": "Dangerous step",
            "action": "delete_all_files",
            "parameters": {"path": "/important"},
            "expected_output": "Files deleted",
            "safety_check": False
        }
    ]
    
    plan = planner.create_plan("Danger Test", "Test", steps)
    is_valid, warnings = planner.validate_plan(plan)
    
    assert len(warnings) > 0
    assert any("dangerous" in w.lower() for w in warnings)
    
    print("✅ Dangerous operation detection test passed")


def test_plan_execution():
    """Test plan execution"""
    print("Testing plan execution...")
    
    planner = TaskPlanner(auto_approve=True)
    steps = [
        {
            "description": "Execute step",
            "action": "process_data",
            "parameters": {"data": [1, 2, 3]},
            "expected_output": "Processed"
        }
    ]
    
    plan = planner.create_plan("Execution Test", "Test", steps)
    success, results = planner.execute_plan(plan, simple_executor, dry_run=True)
    
    assert success == True
    assert len(results) == 1
    assert plan.status == TaskStatus.COMPLETED
    
    print("✅ Plan execution test passed")


def test_checksum_integrity():
    """Test checksum verification"""
    print("Testing checksum integrity...")
    
    planner = TaskPlanner()
    steps = [
        {
            "description": "Test step",
            "action": "test",
            "parameters": {},
            "expected_output": "Test"
        }
    ]
    
    plan = planner.create_plan("Checksum Test", "Test", steps)
    original_checksum = plan.checksum
    
    # Verify integrity
    assert plan.verify_integrity() == True
    
    # Modify plan
    plan.title = "Modified Title"
    
    # Checksum should still match because we're not recalculating
    assert plan.checksum == original_checksum
    
    # But if we recalculate, it should be different
    new_checksum = plan.calculate_checksum()
    assert new_checksum != original_checksum
    
    print("✅ Checksum integrity test passed")


def test_save_and_load():
    """Test saving and loading plans"""
    print("Testing save and load...")
    
    planner = TaskPlanner()
    steps = [
        {
            "description": "Save test step",
            "action": "save_test",
            "parameters": {"test": True},
            "expected_output": "Saved"
        }
    ]
    
    plan = planner.create_plan("Save Test", "Test saving", steps)
    
    # Save plan
    filepath = "/home/claude/test_plan.json"
    planner.save_plan(plan, filepath)
    
    # Load plan
    loaded_plan = planner.load_plan(filepath)
    
    assert loaded_plan.task_id == plan.task_id
    assert loaded_plan.title == plan.title
    assert len(loaded_plan.steps) == len(plan.steps)
    
    print("✅ Save and load test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("RUNNING BASIC TESTS")
    print("="*60 + "\n")
    
    try:
        test_plan_creation()
        test_plan_validation()
        test_dangerous_operations()
        test_plan_execution()
        test_checksum_integrity()
        test_save_and_load()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")


if __name__ == "__main__":
    run_all_tests()

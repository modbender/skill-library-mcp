#!/usr/bin/env python3
"""
Apple Notes Extraction System - Test Suite
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path
import time

class SystemTester:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.root_dir = self.script_dir.parent
        self.test_output_dir = self.root_dir / "output" / "test"
        self.passed = 0
        self.failed = 0
        
    def print_test(self, name, success, details=""):
        """Print test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
        if details:
            print(f"      {details}")
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_environment(self):
        """Test basic environment requirements"""
        print("\n🔍 Testing Environment...")
        
        # Test Python version
        version = sys.version_info
        python_ok = version.major == 3 and version.minor >= 8
        self.print_test(
            "Python version >= 3.8",
            python_ok,
            f"Found Python {version.major}.{version.minor}.{version.micro}"
        )
        
        # Test osascript availability
        try:
            result = subprocess.run(["osascript", "-e", "return true"], 
                                  capture_output=True, timeout=5)
            osascript_ok = result.returncode == 0
        except:
            osascript_ok = False
        
        self.print_test("osascript availability", osascript_ok)
        
        # Test macOS version
        try:
            result = subprocess.run(["sw_vers", "-productVersion"], 
                                  capture_output=True, text=True)
            macos_version = result.stdout.strip()
            macos_ok = result.returncode == 0
        except:
            macos_ok = False
            macos_version = "Unknown"
        
        self.print_test("macOS system", macos_ok, f"Version: {macos_version}")
        
        return python_ok and osascript_ok and macos_ok
    
    def test_notes_access(self):
        """Test Apple Notes application access"""
        print("\n🔍 Testing Apple Notes Access...")
        
        # Test if Notes app responds
        try:
            result = subprocess.run([
                "osascript", "-e", 
                'tell application "Notes" to get name'
            ], capture_output=True, text=True, timeout=10)
            
            notes_accessible = (result.returncode == 0 and "Notes" in result.stdout)
            
        except subprocess.TimeoutExpired:
            notes_accessible = False
            
        self.print_test("Notes app accessibility", notes_accessible)
        
        # Test getting notes count
        if notes_accessible:
            try:
                result = subprocess.run([
                    "osascript", "-e",
                    'tell application "Notes" to count every note'
                ], capture_output=True, text=True, timeout=15)
                
                notes_count_ok = result.returncode == 0
                count = result.stdout.strip() if notes_count_ok else "Error"
                
            except subprocess.TimeoutExpired:
                notes_count_ok = False
                count = "Timeout"
            
            self.print_test("Notes count retrieval", notes_count_ok, f"Found {count} notes")
        
        return notes_accessible
    
    def test_simple_extraction(self):
        """Test simple AppleScript extraction method"""
        print("\n🔍 Testing Simple Extraction...")
        
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Run simple extraction
            extract_script = self.script_dir / "extract-notes.py"
            result = subprocess.run([
                sys.executable, str(extract_script),
                "--method", "simple",
                "--output-dir", str(self.test_output_dir)
            ], capture_output=True, text=True, timeout=60)
            
            extraction_ok = result.returncode == 0
            
            # Check if output files were created
            json_dir = self.test_output_dir / "json"
            json_files = list(json_dir.glob("notes_simple_*.json")) if json_dir.exists() else []
            
            if extraction_ok and json_files:
                # Verify JSON content
                try:
                    with open(json_files[0]) as f:
                        data = json.load(f)
                    
                    json_valid = isinstance(data, list)
                    note_count = len(data) if json_valid else 0
                    
                except:
                    json_valid = False
                    note_count = 0
                
                self.print_test("Simple extraction execution", True, f"Extracted {note_count} notes")
                self.print_test("JSON output validation", json_valid)
                
            else:
                self.print_test("Simple extraction execution", False, result.stderr[:100])
                json_valid = False
            
        except subprocess.TimeoutExpired:
            extraction_ok = False
            json_valid = False
            self.print_test("Simple extraction execution", False, "Timeout after 60 seconds")
        
        return extraction_ok and json_valid
    
    def test_configuration(self):
        """Test configuration loading and validation"""
        print("\n🔍 Testing Configuration...")
        
        # Test extractor configuration
        config_file = self.root_dir / "configs" / "extractor.json"
        config_exists = config_file.exists()
        self.print_test("Extractor config exists", config_exists)
        
        if config_exists:
            try:
                with open(config_file) as f:
                    config = json.load(f)
                
                config_valid = (
                    "methods" in config and
                    "output" in config and
                    "privacy" in config
                )
                
            except:
                config_valid = False
            
            self.print_test("Extractor config validation", config_valid)
        else:
            config_valid = False
        
        # Test monitor configuration
        monitor_config = self.root_dir / "configs" / "monitor.json"
        monitor_exists = monitor_config.exists()
        self.print_test("Monitor config exists", monitor_exists)
        
        return config_exists and config_valid
    
    def test_workflow_integration(self):
        """Test workflow integration capabilities"""
        print("\n🔍 Testing Workflow Integration...")
        
        # Test workflow integrator script
        workflow_script = self.script_dir / "workflow-integrator.py"
        workflow_exists = workflow_script.exists()
        self.print_test("Workflow integrator exists", workflow_exists)
        
        if workflow_exists:
            try:
                # Test dry run mode
                result = subprocess.run([
                    sys.executable, str(workflow_script),
                    "--dry-run"
                ], capture_output=True, text=True, timeout=30)
                
                dry_run_ok = result.returncode == 0 or "No notes data available" in result.stdout
                
            except subprocess.TimeoutExpired:
                dry_run_ok = False
            
            self.print_test("Workflow dry run", dry_run_ok)
        
        return workflow_exists
    
    def test_monitor_functionality(self):
        """Test monitoring system"""
        print("\n🔍 Testing Monitor System...")
        
        monitor_script = self.script_dir / "monitor-notes.py"
        monitor_exists = monitor_script.exists()
        self.print_test("Monitor script exists", monitor_exists)
        
        if monitor_exists:
            try:
                # Test single check mode
                result = subprocess.run([
                    sys.executable, str(monitor_script),
                    "--check-once",
                    "--config", str(self.root_dir / "configs" / "monitor.json")
                ], capture_output=True, text=True, timeout=30)
                
                check_ok = result.returncode == 0
                
            except subprocess.TimeoutExpired:
                check_ok = False
            
            self.print_test("Monitor check functionality", check_ok)
        
        return monitor_exists
    
    def cleanup_test_files(self):
        """Clean up test output files"""
        try:
            if self.test_output_dir.exists():
                import shutil
                shutil.rmtree(self.test_output_dir)
            return True
        except:
            return False
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print("🧪 Apple Notes Extraction System - Test Suite")
        print("==============================================")
        
        # Run tests in order
        env_ok = self.test_environment()
        
        if env_ok:
            notes_ok = self.test_notes_access()
            config_ok = self.test_configuration()
            
            if notes_ok:
                extraction_ok = self.test_simple_extraction()
            else:
                extraction_ok = False
                print("⚠️ Skipping extraction test due to Notes access issues")
            
            workflow_ok = self.test_workflow_integration()
            monitor_ok = self.test_monitor_functionality()
        else:
            print("⚠️ Skipping remaining tests due to environment issues")
            notes_ok = extraction_ok = config_ok = workflow_ok = monitor_ok = False
        
        # Cleanup
        cleanup_ok = self.cleanup_test_files()
        
        # Summary
        print("\n📊 Test Summary")
        print("================")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        
        if cleanup_ok:
            print("🧹 Test cleanup completed")
        
        # Overall assessment
        if env_ok and notes_ok and extraction_ok:
            print("\n🎉 System is ready for use!")
            return True
        elif env_ok and config_ok:
            print("\n⚠️ System partially functional - check Notes app permissions")
            return False
        else:
            print("\n❌ System needs setup - run scripts/setup.sh")
            return False

def main():
    tester = SystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
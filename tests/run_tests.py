#!/usr/bin/env python3
"""
Test Runner for FinalRound Multi-Agent Interview System
Runs all test suites and provides comprehensive reporting.
"""

import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_core_logic import run_core_logic_tests


def print_banner():
    """Print test banner."""
    print("🚀 FinalRound Test Suite")
    print("="*60)
    print("Multi-Agent Interview System - Phase 1 Testing")
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


def run_system_health_check():
    """Run basic system health check."""
    print("\n🔍 System Health Check")
    print("-" * 30)
    
    health_checks = []
    
    # Check if required directories exist
    required_dirs = ['core', 'agents', 'data', 'tests']
    for dir_name in required_dirs:
        exists = os.path.exists(dir_name)
        status = "✅" if exists else "❌"
        print(f"{status} {dir_name}/ directory")
        health_checks.append(exists)
    
    # Check if key files exist
    required_files = [
        'core/document_parser.py',
        'core/session_manager.py', 
        'agents/orchestrator_agent.py',
        'agents/interviewer_agent.py',
        'sample_job_description.txt',
        'sample_resume.txt'
    ]
    
    for file_name in required_files:
        exists = os.path.exists(file_name)
        status = "✅" if exists else "❌"
        print(f"{status} {file_name}")
        health_checks.append(exists)
    
    # Check test fixtures
    test_fixtures = [
        'tests/fixtures/sample_job_description.txt',
        'tests/fixtures/sample_resume.txt'
    ]
    
    for fixture in test_fixtures:
        exists = os.path.exists(fixture)
        status = "✅" if exists else "❌"
        print(f"{status} {fixture}")
        health_checks.append(exists)
    
    all_healthy = all(health_checks)
    if all_healthy:
        print("✅ System health check passed")
    else:
        print("❌ System health check failed - some required files missing")
    
    return all_healthy


def run_import_tests():
    """Test if all modules can be imported."""
    print("\n📦 Import Tests")
    print("-" * 20)
    
    import_tests = []
    
    modules_to_test = [
        ('core.document_parser', 'DocumentParser'),
        ('core.session_manager', 'SessionManager'),
        ('agents.orchestrator_agent', 'OrchestratorAgent'),
        ('agents.interviewer_agent', 'InterviewerAgent'),
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
            import_tests.append(True)
        except Exception as e:
            print(f"❌ {module_name}.{class_name} - {str(e)}")
            import_tests.append(False)
    
    all_imports_ok = all(import_tests)
    if all_imports_ok:
        print("✅ All imports successful")
    else:
        print("❌ Some import failures detected")
    
    return all_imports_ok


def run_all_tests():
    """Run all test suites."""
    print_banner()
    
    # Track overall results
    test_results = {
        "health_check": False,
        "imports": False,
        "core_logic": False
    }
    
    start_time = time.time()
    
    # Run health check
    test_results["health_check"] = run_system_health_check()
    
    # Run import tests
    test_results["imports"] = run_import_tests()
    
    # Run core logic tests
    if test_results["health_check"] and test_results["imports"]:
        try:
            test_results["core_logic"] = run_core_logic_tests()
        except Exception as e:
            print(f"\n❌ Core logic tests failed with error: {str(e)}")
            test_results["core_logic"] = False
    else:
        print("\n⚠️  Skipping core logic tests due to health check or import failures")
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Print final summary
    print("\n" + "="*60)
    print("📊 FINAL TEST SUMMARY")
    print("="*60)
    
    total_suites = len(test_results)
    passed_suites = sum(test_results.values())
    
    print(f"🏁 Test Duration: {duration:.2f} seconds")
    print(f"📋 Test Suites: {passed_suites}/{total_suites} passed")
    print()
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print()
    
    if passed_suites == total_suites:
        print("🎉 ALL TEST SUITES PASSED!")
        print("✅ FinalRound Phase 1 is ready for production use")
        print("🚀 System is fully functional and tested")
    else:
        print("❌ SOME TEST SUITES FAILED")
        print("🔧 Please address the failures before using the system")
    
    print("="*60)
    
    return passed_suites == total_suites


def main():
    """Main test runner entry point."""
    try:
        success = run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Test run interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Test runner failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
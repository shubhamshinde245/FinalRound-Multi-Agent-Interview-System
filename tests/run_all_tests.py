#!/usr/bin/env python3
"""
Complete Test Runner for FinalRound Multi-Agent Interview System
Runs all available test suites and provides comprehensive reporting.
"""

import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_banner():
    """Print test banner."""
    print("🚀 FinalRound Complete Test Suite")
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


def run_simplified_tests():
    """Run simplified core tests."""
    print("\n🧪 Running Simplified Core Tests...")
    try:
        from test_simplified import run_simplified_tests
        return run_simplified_tests()
    except Exception as e:
        print(f"❌ Simplified tests failed: {str(e)}")
        return False


def run_integration_demo():
    """Run a quick integration demo."""
    print("\n🔗 Integration Demo")
    print("-" * 20)
    
    try:
        from core.document_parser import DocumentParser
        from core.session_manager import SessionManager
        import tempfile
        import shutil
        
        # Create temporary session
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Parse documents
            parser = DocumentParser()
            job_desc = parser.parse_job_description("tests/fixtures/sample_job_description.txt")
            resume = parser.parse_resume("tests/fixtures/sample_resume.txt")
            
            # Create session
            session_mgr = SessionManager(temp_dir)
            session_id = session_mgr.create_session(resume.name, job_desc.title)
            
            # Simulate interview interaction
            session_mgr.add_question("Tell me about your Python experience.", "technical")
            session_mgr.add_response("I have 5 years of Python development experience.")
            session_mgr.update_scores({"technical_knowledge": 8})
            
            # Verify integration
            summary = session_mgr.get_session_summary()
            
            print(f"✅ Created interview session for {resume.name}")
            print(f"✅ Position: {job_desc.title} at {job_desc.company}")
            print(f"✅ Questions asked: {summary['questions_asked']}")
            print(f"✅ Session ID: {summary['session_id']}")
            
            return True
            
        finally:
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"❌ Integration demo failed: {str(e)}")
        return False


def main():
    """Main test runner."""
    print_banner()
    
    start_time = time.time()
    
    # Track results
    test_results = {
        "health_check": False,
        "core_tests": False,
        "integration_demo": False
    }
    
    # Run tests
    test_results["health_check"] = run_system_health_check()
    
    if test_results["health_check"]:
        test_results["core_tests"] = run_simplified_tests()
        test_results["integration_demo"] = run_integration_demo()
    else:
        print("\n⚠️  Skipping core tests due to health check failures")
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Print final summary
    print("\n" + "="*60)
    print("📊 COMPLETE TEST SUMMARY")
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
        print()
        print("📝 What was tested:")
        print("   • Document parsing (job descriptions, resumes)")
        print("   • Session management (create, save, load)")
        print("   • Agent system (initialization, coordination)")
        print("   • Core interview flow integration")
        print()
        print("🎯 Ready for Phase 2 development!")
    else:
        print("❌ SOME TEST SUITES FAILED")
        print("🔧 Please address the failures before using the system")
    
    print("="*60)
    
    return passed_suites == total_suites


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Core Logic Tests for FinalRound Multi-Agent Interview System
Tests the main functionality without extensive edge cases.
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.document_parser import DocumentParser
from core.session_manager import SessionManager
from agents.orchestrator_agent import OrchestratorAgent
from agents.interviewer_agent import InterviewerAgent


class TestDocumentParsing:
    """Test core document parsing logic."""
    
    def test_job_description_parsing(self):
        """Test basic job description parsing."""
        parser = DocumentParser()
        job_desc = parser.parse_job_description("tests/fixtures/sample_job_description.txt")
        
        # Verify basic parsing
        assert job_desc.title == "Senior Backend Engineer"
        assert job_desc.company == "TechCorp Industries"
        assert len(job_desc.requirements) > 0
        assert len(job_desc.responsibilities) > 0
        
        print("✅ Job description parsing works")
        return True
    
    def test_resume_parsing(self):
        """Test basic resume parsing."""
        parser = DocumentParser()
        resume = parser.parse_resume("tests/fixtures/sample_resume.txt")
        
        # Verify basic parsing
        assert resume.name == "Jane Smith"
        assert "Engineer" in resume.title
        assert len(resume.skills) > 0
        
        print("✅ Resume parsing works")
        return True
    
    def test_skill_matching(self):
        """Test skill matching between job and resume."""
        parser = DocumentParser()
        job_desc = parser.parse_job_description("tests/fixtures/sample_job_description.txt")
        resume = parser.parse_resume("tests/fixtures/sample_resume.txt")
        
        matching = parser.get_matching_skills(job_desc, resume)
        
        # Verify matching structure
        assert "match_percentage" in matching
        assert "matching_skills" in matching
        assert "missing_skills" in matching
        assert isinstance(matching["match_percentage"], (int, float))
        
        print("✅ Skill matching works")
        return True


class TestSessionManagement:
    """Test core session management logic."""
    
    def setup_temp_session_dir(self):
        """Create temporary session directory."""
        self.temp_dir = tempfile.mkdtemp()
        return self.temp_dir
    
    def cleanup_temp_session_dir(self):
        """Clean up temporary session directory."""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)
    
    def test_session_creation(self):
        """Test basic session creation."""
        session_dir = self.setup_temp_session_dir()
        session_mgr = SessionManager(session_dir)
        
        session_id = session_mgr.create_session("Test Candidate", "Test Position")
        
        # Verify session creation
        assert session_id.startswith("interview_")
        assert session_mgr.current_session is not None
        assert session_mgr.current_session.candidate_name == "Test Candidate"
        
        self.cleanup_temp_session_dir()
        print("✅ Session creation works")
        return True
    
    def test_session_persistence(self):
        """Test session save and load."""
        session_dir = self.setup_temp_session_dir()
        session_mgr = SessionManager(session_dir)
        
        # Create and populate session
        session_id = session_mgr.create_session("Persist Test", "Test Job")
        session_mgr.add_question("Test question?", "technical")
        session_mgr.add_response("Test response")
        session_mgr.save_session()
        
        # Load session in new manager
        new_session_mgr = SessionManager(session_dir)
        loaded = new_session_mgr.load_session(session_id)
        
        # Verify loading
        assert loaded is True
        assert new_session_mgr.current_session.candidate_name == "Persist Test"
        assert len(new_session_mgr.current_session.questions_asked) == 1
        assert len(new_session_mgr.current_session.responses) == 1
        
        self.cleanup_temp_session_dir()
        print("✅ Session persistence works")
        return True
    
    def test_report_generation(self):
        """Test transcript and evaluation generation."""
        session_dir = self.setup_temp_session_dir()
        
        # Create a proper session manager with data directory structure
        data_dir = f"{session_dir}/data"
        os.makedirs(f"{data_dir}/sessions", exist_ok=True)
        os.makedirs(f"{data_dir}/transcripts", exist_ok=True)
        os.makedirs(f"{data_dir}/evaluations", exist_ok=True)
        
        session_mgr = SessionManager(f"{data_dir}/sessions")
        session_id = session_mgr.create_session("Report Test", "Test Position")
        
        # Add interview data
        session_mgr.add_question("How are you?", "behavioral")
        session_mgr.add_response("I am good")
        session_mgr.update_scores({"technical_knowledge": 8, "overall": 7})
        
        # End session to generate reports
        session_mgr.end_session()
        
        # Check if files exist
        transcript_file = f"{data_dir}/transcripts/{session_id}_transcript.json"
        evaluation_file = f"{data_dir}/evaluations/{session_id}_evaluation.json"
        
        assert os.path.exists(transcript_file)
        assert os.path.exists(evaluation_file)
        
        # Verify content structure
        with open(transcript_file, 'r') as f:
            transcript = json.load(f)
            assert "conversation" in transcript
            assert len(transcript["conversation"]) > 0
        
        with open(evaluation_file, 'r') as f:
            evaluation = json.load(f)
            assert "scores" in evaluation
            assert evaluation["scores"]["overall"] == 7
        
        self.cleanup_temp_session_dir()
        print("✅ Report generation works")
        return True


class TestAgentCoordination:
    """Test core agent coordination logic."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator agent setup."""
        session_dir = tempfile.mkdtemp()
        session_mgr = SessionManager(session_dir)
        
        orchestrator = OrchestratorAgent(session_mgr)
        
        # Verify initialization
        assert orchestrator is not None
        assert orchestrator.shared_state is not None
        assert orchestrator.llm is not None
        
        shutil.rmtree(session_dir)
        print("✅ Orchestrator initialization works")
        return True
    
    def test_interviewer_initialization(self):
        """Test interviewer agent setup."""
        session_dir = tempfile.mkdtemp()
        session_mgr = SessionManager(session_dir)
        
        shared_state = {"test": "data"}
        interviewer = InterviewerAgent(session_mgr, shared_state)
        
        # Verify initialization
        assert interviewer is not None
        assert interviewer.shared_state == shared_state
        assert interviewer.llm is not None
        
        shutil.rmtree(session_dir)
        print("✅ Interviewer initialization works")
        return True
    
    def test_shared_state_management(self):
        """Test shared state between agents."""
        session_dir = tempfile.mkdtemp()
        session_mgr = SessionManager(session_dir)
        
        orchestrator = OrchestratorAgent(session_mgr)
        
        # Test state updates
        orchestrator.shared_state["test_key"] = "test_value"
        shared_state = orchestrator.get_shared_state()
        
        assert shared_state["test_key"] == "test_value"
        
        # Test with interviewer
        interviewer = InterviewerAgent(session_mgr, shared_state)
        assert interviewer.shared_state["test_key"] == "test_value"
        
        shutil.rmtree(session_dir)
        print("✅ Shared state management works")
        return True


class TestInterviewFlow:
    """Test core interview flow logic."""
    
    def test_question_generation(self):
        """Test basic question generation."""
        session_dir = tempfile.mkdtemp()
        session_mgr = SessionManager(session_dir)
        session_mgr.create_session("Flow Test", "Test Position")
        
        interviewer = InterviewerAgent(session_mgr)
        
        # Test opening question
        opening_question = interviewer.start_interview()
        
        assert len(opening_question) > 10
        assert "?" in opening_question
        
        shutil.rmtree(session_dir)
        print("✅ Question generation works")
        return True
    
    def test_document_analysis_flow(self):
        """Test document analysis integration."""
        session_dir = tempfile.mkdtemp()
        session_mgr = SessionManager(session_dir)
        
        orchestrator = OrchestratorAgent(session_mgr)
        
        # Test document initialization (without API call)
        parser = DocumentParser()
        job_desc = parser.parse_job_description("tests/fixtures/sample_job_description.txt")
        resume = parser.parse_resume("tests/fixtures/sample_resume.txt")
        
        # Update shared state manually
        orchestrator.shared_state["job_description"] = job_desc
        orchestrator.shared_state["resume"] = resume
        
        # Verify data is available
        shared_state = orchestrator.get_shared_state()
        assert "job_description" in shared_state
        assert "resume" in shared_state
        assert shared_state["job_description"].title == "Senior Backend Engineer"
        
        shutil.rmtree(session_dir)
        print("✅ Document analysis flow works")
        return True


def run_core_logic_tests():
    """Run all core logic tests."""
    print("🧪 Running FinalRound Core Logic Tests")
    print("="*50)
    
    test_classes = [
        TestDocumentParsing(),
        TestSessionManagement(),
        TestAgentCoordination(),
        TestInterviewFlow()
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__class__.__name__}")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                result = getattr(test_class, test_method)()
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ {test_method} failed: {str(e)}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ALL CORE LOGIC TESTS PASSED!")
        print("✅ Phase 1 core functionality is working correctly")
        return True
    else:
        print(f"❌ {total_tests - passed_tests} tests failed")
        return False


if __name__ == "__main__":
    success = run_core_logic_tests()
    sys.exit(0 if success else 1)
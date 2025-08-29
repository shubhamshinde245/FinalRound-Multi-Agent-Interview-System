#!/usr/bin/env python3
"""
Test script for streaming question generation functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.session_manager import SessionManager
from agents.interviewer_agent import InterviewerAgent
from core.document_parser import DocumentParser


def test_streaming_question_generation():
    """Test the streaming question generation functionality."""
    print("🧪 Testing Streaming Question Generation")
    print("=" * 50)
    
    try:
        # Initialize components
        print("1. Initializing session manager...")
        session_manager = SessionManager()
        
        print("2. Parsing sample documents...")
        parser = DocumentParser()
        job_desc = parser.parse_job_description("sample_job_description.txt")
        resume = parser.parse_resume("sample_resume.txt")
        
        print("3. Setting up shared state...")
        shared_state = {
            "job_description": job_desc,
            "resume": resume,
            "next_topic": "Python development"
        }
        
        print("4. Initializing InterviewerAgent...")
        interviewer = InterviewerAgent(session_manager, shared_state)
        
        print("5. Testing streaming question generation...")
        print("\n--- STREAMING OUTPUT ---")
        
        def stream_callback(chunk):
            print(chunk, end="", flush=True)
        
        # Test different question types
        question_types = ["technical", "behavioral", "situational", "system_design"]
        
        for i, q_type in enumerate(question_types, 1):
            print(f"\n\n{i}. Testing {q_type} question:")
            print("Interviewer: ", end="")
            
            question = interviewer.generate_streaming_question(
                question_type=q_type,
                topic="Python and system design",
                context="Candidate has 5 years experience with Python",
                callback=stream_callback
            )
            
            print(f"\n\nComplete question length: {len(question)} characters")
            print("--- END ---\n")
        
        print("✅ Streaming test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_regular_vs_streaming():
    """Compare regular vs streaming question generation."""
    print("\n🔍 Comparing Regular vs Streaming")
    print("=" * 50)
    
    try:
        session_manager = SessionManager()
        parser = DocumentParser()
        job_desc = parser.parse_job_description("sample_job_description.txt")
        resume = parser.parse_resume("sample_resume.txt")
        
        shared_state = {
            "job_description": job_desc,
            "resume": resume,
            "next_topic": "AWS and cloud architecture"
        }
        
        interviewer = InterviewerAgent(session_manager, shared_state)
        
        print("\n1. Regular question generation:")
        regular_question = interviewer.generate_next_question("I have experience with microservices")
        print(f"Question: {regular_question}")
        
        print("\n2. Streaming question generation:")
        print("Streaming: ", end="")
        
        def callback(chunk):
            print(chunk, end="", flush=True)
        
        streaming_question = interviewer.generate_streaming_question(
            question_type="technical",
            topic="AWS and microservices",
            context="Candidate mentioned microservices experience",
            callback=callback
        )
        
        print(f"\n\nRegular length: {len(regular_question)} chars")
        print(f"Streaming length: {len(streaming_question)} chars")
        print("✅ Comparison completed!")
        
    except Exception as e:
        print(f"❌ Comparison failed: {str(e)}")


if __name__ == "__main__":
    print("🚀 FinalRound Streaming Test Suite")
    print("Testing real-time question generation with OpenAI streaming")
    print()
    
    # Test streaming functionality
    success = test_streaming_question_generation()
    
    if success:
        # Test comparison
        test_regular_vs_streaming()
        
        print("\n🎉 All streaming tests completed!")
        print("You can now run 'python main.py' to experience streaming in the CLI")
    else:
        print("\n❌ Streaming tests failed. Check your OpenAI API key and connection.")
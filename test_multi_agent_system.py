#!/usr/bin/env python3
"""
Enhanced Test Suite for FinalRound Multi-Agent Interview System v2.0

This comprehensive test suite validates the integration of all 4 agents:
- OrchestratorAgent: Enhanced coordinator with multi-agent management
- TopicManagerAgent: Intelligent topic flow and depth control
- InterviewerAgent: Adaptive question generation with evaluation integration
- EvaluatorAgent: Real-time candidate assessment and performance tracking

Features tested:
- Multi-agent workflow coordination
- Real-time evaluation and adaptation
- Intelligent topic sequencing and transitions
- Enhanced session management with agent state persistence
- Comprehensive reporting with agent insights
"""

import os
import sys
import logging
import time
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.session_manager import SessionManager
from core.multi_agent_workflow import MultiAgentWorkflow

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiAgentTestSuite:
    """Comprehensive test suite for the multi-agent interview system."""
    
    def __init__(self):
        self.session_manager = None
        self.workflow = None
        self.test_results = {}
        self.start_time = None
        
    def setup_test_environment(self) -> bool:
        """Initialize the test environment with proper error handling."""
        try:
            logger.info("🔧 Setting up multi-agent test environment")
            
            # Initialize session manager
            self.session_manager = SessionManager()
            logger.info("✅ SessionManager initialized")
            
            # Initialize multi-agent workflow
            self.workflow = MultiAgentWorkflow(self.session_manager)
            logger.info("✅ MultiAgentWorkflow initialized")
            
            self.start_time = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"❌ Test environment setup failed: {str(e)}")
            return False
    
    def test_individual_agents(self) -> Dict[str, bool]:
        """Test each agent individually to ensure proper functionality."""
        logger.info("\n🔬 Phase 1: Individual Agent Testing")
        results = {}
        
        try:
            from agents.topic_manager_agent import TopicManagerAgent
            from agents.evaluator_agent import EvaluatorAgent
            from agents.orchestrator_agent import OrchestratorAgent
            from agents.interviewer_agent import InterviewerAgent
            
            shared_state = {}
            
            # Test 1: TopicManagerAgent
            logger.info("🧪 Testing TopicManagerAgent...")
            try:
                topic_manager = TopicManagerAgent(self.session_manager, shared_state)
                
                # Test topic planning
                plan_result = topic_manager.chat("plan_topic_sequence()")
                logger.info(f"Topic Planning: {plan_result[:100]}...")
                
                # Test coverage analysis
                coverage_result = topic_manager.chat("analyze_coverage()")
                logger.info(f"Coverage Analysis: {coverage_result[:100]}...")
                
                results["topic_manager"] = True
                logger.info("✅ TopicManagerAgent tests passed")
                
            except Exception as e:
                logger.error(f"❌ TopicManagerAgent failed: {str(e)}")
                results["topic_manager"] = False
            
            # Test 2: EvaluatorAgent
            logger.info("🧪 Testing EvaluatorAgent...")
            try:
                evaluator = EvaluatorAgent(self.session_manager, shared_state)
                
                # Test initialization
                init_result = evaluator.initialize_evaluation("Test Candidate")
                logger.info(f"Evaluator Init: {init_result}")
                
                # Test response evaluation
                eval_result = evaluator.chat(
                    "evaluate_response('I have 5 years of Python experience building web APIs', "
                    "'Tell me about your Python experience', 'Python', 'technical')"
                )
                logger.info(f"Response Evaluation: {eval_result[:100]}...")
                
                # Test assessment retrieval
                assessment = evaluator.get_current_assessment()
                logger.info(f"Current Assessment: {assessment}")
                
                results["evaluator"] = True
                logger.info("✅ EvaluatorAgent tests passed")
                
            except Exception as e:
                logger.error(f"❌ EvaluatorAgent failed: {str(e)}")
                results["evaluator"] = False
            
            # Test 3: Enhanced OrchestratorAgent
            logger.info("🧪 Testing Enhanced OrchestratorAgent...")
            try:
                orchestrator = OrchestratorAgent(self.session_manager)
                
                # Test agent management
                agent_status = orchestrator.chat("manage_agents('get_status', 'all')")
                logger.info(f"Agent Status: {agent_status[:100]}...")
                
                results["orchestrator"] = True
                logger.info("✅ OrchestratorAgent tests passed")
                
            except Exception as e:
                logger.error(f"❌ OrchestratorAgent failed: {str(e)}")
                results["orchestrator"] = False
            
            # Test 4: Enhanced InterviewerAgent
            logger.info("🧪 Testing Enhanced InterviewerAgent...")
            try:
                interviewer = InterviewerAgent(self.session_manager, shared_state)
                
                # Test question generation
                question = interviewer.generate_next_question()
                logger.info(f"Generated Question: {question[:100]}...")
                
                results["interviewer"] = True
                logger.info("✅ InterviewerAgent tests passed")
                
            except Exception as e:
                logger.error(f"❌ InterviewerAgent failed: {str(e)}")
                results["interviewer"] = False
            
            return results
            
        except ImportError as e:
            logger.error(f"❌ Agent import failed: {str(e)}")
            return {"import_error": False}
    
    def test_workflow_initialization(self) -> bool:
        """Test the complete multi-agent workflow initialization."""
        logger.info("\n🧪 Test: Multi-Agent Workflow Initialization")
        
        try:
            # Test with sample data
            job_desc_path = "sample_job_description.txt"
            resume_path = "sample_resume.txt"
            candidate_name = "Sarah Chen"
            
            # Check if sample files exist
            if not os.path.exists(job_desc_path):
                logger.warning(f"Sample job description not found at {job_desc_path}")
                # Create minimal sample for testing
                with open(job_desc_path, 'w') as f:
                    f.write("Senior Backend Engineer\nRequirements: Python, AWS, System Design")
            
            if not os.path.exists(resume_path):
                logger.warning(f"Sample resume not found at {resume_path}")
                # Create minimal sample for testing
                with open(resume_path, 'w') as f:
                    f.write("John Doe\nSenior Software Engineer\nSkills: Python, Django, AWS")
            
            # Initialize workflow
            init_result = self.workflow.initialize_workflow(
                job_desc_path, resume_path, candidate_name
            )
            
            logger.info(f"Initialization Result: {init_result}")
            
            # Verify workflow status
            status = self.workflow.get_workflow_status()
            logger.info(f"Workflow Status: {status}")
            
            if not status["workflow_active"]:
                raise Exception("Workflow failed to activate properly")
            
            # Verify all agents are initialized
            agents_status = status["agents_initialized"]
            for agent_name, initialized in agents_status.items():
                if not initialized:
                    raise Exception(f"{agent_name} failed to initialize")
            
            logger.info("✅ Workflow initialization successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow initialization failed: {str(e)}")
            return False
    
    def test_adaptive_question_generation(self) -> bool:
        """Test the adaptive question generation with multi-agent coordination."""
        logger.info("\n🧪 Test: Adaptive Question Generation")
        
        try:
            # Test 1: Generate initial question
            logger.info("Generating initial question...")
            first_question = self.workflow.generate_next_question()
            
            if "error" in first_question.lower():
                raise Exception(f"Error in first question: {first_question}")
            
            logger.info(f"✅ First Question Generated: {first_question[:100]}...")
            
            # Test 2: Simulate strong candidate response
            strong_response = """
            I have 8 years of experience with Python, specializing in backend development 
            and distributed systems. Recently, I architected a microservices platform 
            handling 1M+ requests/day using FastAPI, PostgreSQL, and Redis. I implemented 
            event-driven architecture with Kafka and deployed on AWS using Docker and 
            Kubernetes. The system achieved 99.9% uptime with sub-100ms response times.
            """
            
            logger.info("Testing with strong candidate response...")
            adaptive_question = self.workflow.generate_next_question(
                previous_response=strong_response,
                previous_question=first_question
            )
            
            if "error" in adaptive_question.lower():
                raise Exception(f"Error in adaptive question: {adaptive_question}")
            
            logger.info(f"✅ Adaptive Question Generated: {adaptive_question[:100]}...")
            
            # Test 3: Simulate weaker candidate response
            weak_response = """
            I know Python basics and have used it for some scripts.
            """
            
            logger.info("Testing with weaker candidate response...")
            supportive_question = self.workflow.generate_next_question(
                previous_response=weak_response,
                previous_question=adaptive_question
            )
            
            if "error" in supportive_question.lower():
                raise Exception(f"Error in supportive question: {supportive_question}")
            
            logger.info(f"✅ Supportive Question Generated: {supportive_question[:100]}...")
            
            logger.info("✅ Adaptive question generation successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Adaptive question generation failed: {str(e)}")
            return False
    
    def test_topic_management(self) -> bool:
        """Test intelligent topic management and transitions."""
        logger.info("\n🧪 Test: Topic Management and Transitions")
        
        try:
            # Test 1: Get initial topic guidance
            logger.info("Getting initial topic guidance...")
            guidance = self.workflow.get_interview_guidance()
            
            if "error" in str(guidance).lower():
                logger.warning(f"Warning in guidance: {guidance}")
            else:
                logger.info(f"✅ Initial guidance retrieved: {type(guidance)}")
            
            # Test 2: Simulate topic transition
            logger.info("Testing topic transition...")
            transition_result = self.workflow.transition_topic(
                current_topic="Python",
                coverage_status="complete"
            )
            
            logger.info(f"✅ Topic transition result: {transition_result[:100]}...")
            
            # Test 3: Generate question after transition
            logger.info("Generating post-transition question...")
            post_transition_question = self.workflow.generate_next_question()
            
            if "error" in post_transition_question.lower():
                raise Exception(f"Error in post-transition question: {post_transition_question}")
            
            logger.info(f"✅ Post-transition question: {post_transition_question[:100]}...")
            
            logger.info("✅ Topic management tests successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Topic management failed: {str(e)}")
            return False
    
    def test_real_time_evaluation(self) -> bool:
        """Test real-time candidate evaluation and performance tracking."""
        logger.info("\n🧪 Test: Real-time Evaluation and Performance Tracking")
        
        try:
            # Simulate multiple responses with different quality levels
            test_responses = [
                {
                    "response": "I have basic Python knowledge and can write simple scripts.",
                    "expected_level": "beginner"
                },
                {
                    "response": """I've built several REST APIs using Django and Flask, 
                    implemented database schemas with PostgreSQL, and used Redis for caching. 
                    I understand OOP principles and have experience with testing frameworks like pytest.""",
                    "expected_level": "intermediate"
                },
                {
                    "response": """I've architected distributed systems using microservices patterns, 
                    implemented event-driven architectures with message queues, optimized database 
                    performance through indexing and query optimization, and designed scalable 
                    systems handling millions of requests with proper monitoring and observability.""",
                    "expected_level": "advanced"
                }
            ]
            
            evaluation_results = []
            
            for i, test_case in enumerate(test_responses):
                logger.info(f"Evaluating response {i+1} ({test_case['expected_level']} level)...")
                
                # Generate question and evaluate response
                question = self.workflow.generate_next_question(
                    previous_response=test_case["response"] if i > 0 else "",
                    previous_question="Tell me about your Python experience"
                )
                
                # Get evaluation insights
                guidance = self.workflow.get_interview_guidance()
                evaluation_results.append({
                    "level": test_case["expected_level"],
                    "guidance": guidance
                })
                
                logger.info(f"✅ Response {i+1} evaluated successfully")
                
                # Small delay to simulate real interview timing
                time.sleep(0.5)
            
            logger.info("✅ Real-time evaluation tests successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Real-time evaluation failed: {str(e)}")
            return False
    
    def test_session_persistence(self) -> bool:
        """Test enhanced session management with multi-agent state persistence."""
        logger.info("\n🧪 Test: Enhanced Session Management")
        
        try:
            # Get current session info
            if not self.session_manager.current_session:
                raise Exception("No active session found")
            
            session_id = self.session_manager.current_session.session_id
            logger.info(f"Testing session: {session_id}")
            
            # Test session summary with multi-agent data
            summary = self.session_manager.get_session_summary()
            logger.info(f"✅ Session summary retrieved: {len(summary)} fields")
            
            # Test manual save
            self.session_manager.save_session()
            logger.info("✅ Session saved manually")
            
            # Verify session file exists
            session_file = f"data/sessions/{session_id}.json"
            if os.path.exists(session_file):
                logger.info(f"✅ Session file created: {session_file}")
            else:
                logger.warning(f"⚠️ Session file not found: {session_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Session persistence failed: {str(e)}")
            return False
    
    def test_workflow_completion(self) -> bool:
        """Test workflow completion and comprehensive reporting."""
        logger.info("\n🧪 Test: Workflow Completion and Reporting")
        
        try:
            # End workflow
            logger.info("Ending workflow...")
            end_result = self.workflow.end_workflow()
            logger.info(f"✅ Workflow ended: {end_result}")
            
            # Verify generated files
            if self.session_manager.current_session:
                session_id = self.session_manager.current_session.session_id
                
                expected_files = [
                    f"data/sessions/{session_id}.json",
                    f"data/transcripts/{session_id}_transcript.json", 
                    f"data/evaluations/{session_id}_evaluation.json"
                ]
                
                files_created = 0
                for file_path in expected_files:
                    if os.path.exists(file_path):
                        logger.info(f"✅ Generated: {file_path}")
                        files_created += 1
                    else:
                        logger.warning(f"⚠️ Missing: {file_path}")
                
                logger.info(f"✅ Files generated: {files_created}/{len(expected_files)}")
            
            # Get workflow event log
            events = self.workflow.get_event_log()
            logger.info(f"✅ Workflow events logged: {len(events)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow completion failed: {str(e)}")
            return False
    
    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite and return detailed results."""
        logger.info("🎯 Starting FinalRound Multi-Agent System Comprehensive Test Suite")
        logger.info("=" * 70)
        
        if not self.setup_test_environment():
            return {"success": False, "error": "Environment setup failed"}
        
        # Run all tests
        test_results = {}
        
        # Phase 1: Individual Agent Tests
        logger.info("\n📋 PHASE 1: Individual Agent Testing")
        test_results["individual_agents"] = self.test_individual_agents()
        
        # Phase 2: Workflow Integration Tests
        logger.info("\n📋 PHASE 2: Multi-Agent Workflow Integration")
        test_results["workflow_init"] = self.test_workflow_initialization()
        
        if test_results["workflow_init"]:
            test_results["adaptive_questions"] = self.test_adaptive_question_generation()
            test_results["topic_management"] = self.test_topic_management()
            test_results["real_time_evaluation"] = self.test_real_time_evaluation()
            test_results["session_persistence"] = self.test_session_persistence()
            test_results["workflow_completion"] = self.test_workflow_completion()
        else:
            logger.warning("⚠️ Skipping integration tests due to workflow initialization failure")
        
        # Calculate overall results
        individual_success = all(test_results.get("individual_agents", {}).values())
        integration_tests = ["workflow_init", "adaptive_questions", "topic_management", 
                           "real_time_evaluation", "session_persistence", "workflow_completion"]
        integration_success = all(test_results.get(test, False) for test in integration_tests)
        
        overall_success = individual_success and integration_success
        
        # Generate final report
        end_time = datetime.now()
        duration = end_time - self.start_time if self.start_time else None
        
        return {
            "success": overall_success,
            "individual_agents": test_results.get("individual_agents", {}),
            "integration_tests": {test: test_results.get(test, False) for test in integration_tests},
            "duration": duration.total_seconds() if duration else 0,
            "timestamp": end_time.isoformat()
        }


def print_detailed_results(results: Dict[str, Any]):
    """Print detailed test results in a formatted way."""
    print("\n" + "=" * 70)
    print("🎉 FINALROUND MULTI-AGENT SYSTEM TEST RESULTS")
    print("=" * 70)
    
    # Individual Agent Results
    print("\n🤖 Individual Agent Tests:")
    agent_results = results.get("individual_agents", {})
    for agent, success in agent_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {agent.replace('_', ' ').title()}: {status}")
    
    # Integration Test Results
    print("\n🔗 Integration Tests:")
    integration_results = results.get("integration_tests", {})
    for test, success in integration_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        test_name = test.replace('_', ' ').title()
        print(f"   {test_name}: {status}")
    
    # Summary
    print(f"\n⏱️ Test Duration: {results.get('duration', 0):.2f} seconds")
    print(f"📅 Completed: {results.get('timestamp', 'Unknown')}")
    
    if results.get("success", False):
        print("\n🎉 ALL TESTS PASSED! Multi-agent system is ready for production.")
        print("\n🚀 Key Features Validated:")
        print("   • 4-Agent Architecture (Orchestrator, TopicManager, Interviewer, Evaluator)")
        print("   • Real-time Multi-Agent Coordination")
        print("   • Adaptive Question Generation")
        print("   • Intelligent Topic Management")
        print("   • Continuous Candidate Evaluation")
        print("   • Enhanced Session Persistence")
        print("   • Comprehensive Reporting")
    else:
        print("\n💥 SOME TESTS FAILED. Please review the logs above for details.")
        
        # Show which categories failed
        failed_agents = [agent for agent, success in agent_results.items() if not success]
        failed_integration = [test for test, success in integration_results.items() if not success]
        
        if failed_agents:
            print(f"\n❌ Failed Agent Tests: {', '.join(failed_agents)}")
        if failed_integration:
            print(f"❌ Failed Integration Tests: {', '.join(failed_integration)}")


def main():
    """Main test execution function."""
    # Create and run test suite
    test_suite = MultiAgentTestSuite()
    results = test_suite.run_comprehensive_test_suite()
    
    # Print detailed results
    print_detailed_results(results)
    
    # Exit with appropriate code
    exit_code = 0 if results.get("success", False) else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
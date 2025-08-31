import os
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
import logging

from core.session_manager import SessionManager
from agents.orchestrator_agent import OrchestratorAgent
from agents.interviewer_agent import InterviewerAgent
from agents.topic_manager_agent import TopicManagerAgent
from agents.evaluator_agent import EvaluatorAgent


load_dotenv()


class MultiAgentWorkflow:
    """
    Coordinates the interaction between all agents in the FinalRound interview system.
    
    Workflow pattern:
    1. OrchestratorAgent initializes the interview and sub-agents
    2. TopicManagerAgent plans the interview topic flow
    3. InterviewerAgent generates questions based on topic guidance
    4. EvaluatorAgent evaluates responses and provides feedback
    5. All agents coordinate through shared state and event-driven communication
    """
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.shared_state: Dict[str, Any] = {}
        
        # Initialize agents
        self.orchestrator = OrchestratorAgent(session_manager)
        self.interviewer: Optional[InterviewerAgent] = None
        self.topic_manager: Optional[TopicManagerAgent] = None
        self.evaluator: Optional[EvaluatorAgent] = None
        
        # Workflow state
        self.workflow_active = False
        self.current_phase = "initialization"
        self.event_log: List[Dict] = []
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
    def initialize_workflow(self, job_desc_path: str, resume_path: str, candidate_name: str = None) -> str:
        """Initialize the multi-agent workflow with document analysis and agent setup."""
        try:
            self.logger.info(f"Initializing multi-agent workflow for candidate: {candidate_name}")
            
            # Phase 1: Initialize orchestrator and analyze documents
            init_result = self.orchestrator.initialize_interview(job_desc_path, resume_path, candidate_name)
            self._log_event("orchestrator_init", {"result": init_result})
            
            # Phase 2: Get shared state from orchestrator
            self.shared_state = self.orchestrator.get_shared_state()
            
            # Phase 3: Initialize sub-agents with shared state
            self.interviewer = InterviewerAgent(self.session_manager, self.shared_state)
            self.topic_manager = TopicManagerAgent(self.session_manager, self.shared_state)
            self.evaluator = EvaluatorAgent(self.session_manager, self.shared_state)
            
            # Update orchestrator with agent references
            self.orchestrator.topic_manager = self.topic_manager
            self.orchestrator.evaluator = self.evaluator
            
            # Phase 4: Initialize topic management and evaluation
            topic_init = self.topic_manager.initialize_topic_management()
            eval_init = self.evaluator.initialize_evaluation(candidate_name)
            
            self._log_event("agents_initialized", {
                "topic_manager": topic_init,
                "evaluator": eval_init
            })
            
            # Phase 5: Set workflow as active
            self.workflow_active = True
            self.current_phase = "ready"
            
            return f"Multi-agent workflow initialized successfully.\n{init_result}\nTopic Manager: {topic_init}\nEvaluator: {eval_init}"
            
        except Exception as e:
            self.logger.error(f"Error initializing workflow: {str(e)}")
            return f"Error initializing multi-agent workflow: {str(e)}"
    
    def generate_next_question(self, previous_response: str = "", previous_question: str = "") -> str:
        """Generate the next interview question through multi-agent coordination."""
        try:
            if not self.workflow_active:
                return "Workflow not initialized. Please initialize first."
            
            self.logger.info("Generating next question through multi-agent coordination")
            
            # Step 1: If there's a previous response, evaluate it first
            if previous_response and previous_question:
                evaluation_result = self._evaluate_response(previous_response, previous_question)
                self._log_event("response_evaluated", {"result": evaluation_result})
            
            # Step 2: Get topic guidance from TopicManagerAgent
            topic_guidance = self._get_topic_guidance()
            self._log_event("topic_guidance_received", topic_guidance)
            
            # Step 3: Update shared state with guidance
            self._update_shared_state_from_guidance(topic_guidance)
            
            # Step 4: Generate question using InterviewerAgent with multi-agent context
            question = self._generate_contextual_question(previous_response)
            self._log_event("question_generated", {"question": question})
            
            return question
            
        except Exception as e:
            self.logger.error(f"Error generating next question: {str(e)}")
            return f"Error generating question: {str(e)}"
    
    def _evaluate_response(self, response: str, question: str) -> str:
        """Coordinate response evaluation through multi-agent system."""
        try:
            # Use orchestrator's multi-agent coordination for response evaluation
            current_topic = self.shared_state.get("next_topic", "")
            
            evaluation_result = self.orchestrator.chat(
                f"coordinate_multi_agents('response_evaluation', '', '{response}', '{question}')"
            )
            
            # Update shared state with evaluation insights
            if self.evaluator:
                assessment = self.evaluator.get_current_assessment()
                self.shared_state.update({
                    "performance_level": "high" if assessment.get("overall_score", 0) >= 7 else "medium" if assessment.get("overall_score", 0) >= 5 else "low",
                    "strong_areas": assessment.get("strengths", []),
                    "weak_areas": assessment.get("improvement_areas", []),
                    "evaluation_insights": assessment
                })
            
            return evaluation_result
            
        except Exception as e:
            self.logger.error(f"Error evaluating response: {str(e)}")
            return f"Error in response evaluation: {str(e)}"
    
    def _get_topic_guidance(self) -> Dict[str, Any]:
        """Get topic guidance from TopicManagerAgent."""
        try:
            if not self.topic_manager:
                return {"error": "TopicManager not initialized"}
            
            # Get comprehensive topic guidance
            guidance = self.topic_manager.get_topic_guidance({})
            
            # Check if topic transition is needed
            coverage_analysis = self.topic_manager.chat("analyze_coverage()")
            
            # Get time management insights
            time_status = self.topic_manager.chat("manage_time_allocation('check_time')")
            
            return {
                "topic_guidance": guidance,
                "coverage_analysis": coverage_analysis,
                "time_status": time_status,
                "transition_recommendation": guidance.get("transition_recommendation", "continue")
            }
            
        except Exception as e:
            self.logger.error(f"Error getting topic guidance: {str(e)}")
            return {"error": f"Topic guidance error: {str(e)}"}
    
    def _update_shared_state_from_guidance(self, guidance: Dict[str, Any]):
        """Update shared state based on topic guidance and evaluation insights."""
        try:
            topic_info = guidance.get("topic_guidance", {})
            
            # Update topic-related state
            if "current_topic" in topic_info:
                self.shared_state["next_topic"] = topic_info["current_topic"]
            if "suggested_depth" in topic_info:
                self.shared_state["suggested_depth"] = topic_info["suggested_depth"]
            if "topic_category" in topic_info:
                self.shared_state["topic_category"] = topic_info["topic_category"]
            
            # Update transition flags
            if guidance.get("transition_recommendation") == "transition":
                self.shared_state["transition_needed"] = True
            
            # Sync shared state across all agents
            if self.interviewer:
                self.interviewer.shared_state = self.shared_state
            if self.topic_manager:
                self.topic_manager.shared_state = self.shared_state
            if self.evaluator:
                self.evaluator.shared_state = self.shared_state
            
            self.orchestrator.shared_state = self.shared_state
            
        except Exception as e:
            self.logger.error(f"Error updating shared state: {str(e)}")
    
    def _generate_contextual_question(self, previous_response: str = "") -> str:
        """Generate a contextual question using InterviewerAgent with multi-agent coordination."""
        try:
            if not self.interviewer:
                return "InterviewerAgent not initialized"
            
            # Use enhanced question generation with previous response context
            question = self.interviewer.generate_next_question(
                context=self.shared_state.get("interview_context", ""),
                previous_response=previous_response
            )
            
            # Update topic manager with question timing
            if self.topic_manager:
                current_topic = self.shared_state.get("next_topic", "")
                self.topic_manager.chat(f"manage_time_allocation('start_topic', '{current_topic}')")
            
            return question
            
        except Exception as e:
            self.logger.error(f"Error generating contextual question: {str(e)}")
            return f"Error generating contextual question: {str(e)}"
    
    def transition_topic(self, current_topic: str, coverage_status: str = "partial") -> str:
        """Coordinate topic transition across all agents."""
        try:
            if not self.workflow_active:
                return "Workflow not active"
            
            self.logger.info(f"Transitioning from topic: {current_topic}")
            
            # Use orchestrator's multi-agent coordination for topic transition
            transition_result = self.orchestrator.chat(
                f"coordinate_multi_agents('topic_transition', 'current_topic: {current_topic}, status: {coverage_status}')"
            )
            
            # Update shared state and sync across agents
            self._sync_agents_state()
            
            self._log_event("topic_transition", {
                "from_topic": current_topic,
                "result": transition_result
            })
            
            return transition_result
            
        except Exception as e:
            self.logger.error(f"Error in topic transition: {str(e)}")
            return f"Error transitioning topic: {str(e)}"
    
    def get_interview_guidance(self) -> Dict[str, Any]:
        """Get comprehensive interview guidance from all agents."""
        try:
            if not self.workflow_active:
                return {"error": "Workflow not active"}
            
            # Get guidance from orchestrator's multi-agent coordination
            guidance_result = self.orchestrator.chat(
                "coordinate_multi_agents('interview_guidance')"
            )
            
            # Get individual agent status
            agent_status = {}
            
            if self.topic_manager:
                topic_guidance = self.topic_manager.get_topic_guidance({})
                agent_status["topic_manager"] = topic_guidance
            
            if self.evaluator:
                evaluation_summary = self.evaluator.get_current_assessment()
                agent_status["evaluator"] = evaluation_summary
            
            # Get session summary
            session_summary = self.session_manager.get_session_summary()
            
            return {
                "workflow_status": "active",
                "current_phase": self.current_phase,
                "orchestrator_guidance": guidance_result,
                "agent_status": agent_status,
                "session_summary": session_summary,
                "shared_state": self.shared_state
            }
            
        except Exception as e:
            self.logger.error(f"Error getting interview guidance: {str(e)}")
            return {"error": f"Guidance error: {str(e)}"}
    
    def _sync_agents_state(self):
        """Synchronize shared state across all agents."""
        try:
            agents = [self.orchestrator, self.interviewer, self.topic_manager, self.evaluator]
            
            for agent in agents:
                if agent and hasattr(agent, 'shared_state'):
                    agent.shared_state = self.shared_state.copy()
            
        except Exception as e:
            self.logger.error(f"Error syncing agent state: {str(e)}")
    
    def end_workflow(self) -> str:
        """End the multi-agent workflow and generate final reports."""
        try:
            self.logger.info("Ending multi-agent workflow")
            
            # Generate final evaluation using EvaluatorAgent
            if self.evaluator:
                final_assessment = self.evaluator.get_current_assessment()
                self.session_manager.update_scores({
                    "overall": final_assessment.get("overall_score", 0),
                    "technical_knowledge": final_assessment.get("dimension_scores", {}).get("technical_knowledge", 0),
                    "communication_skills": final_assessment.get("dimension_scores", {}).get("communication_skills", 0),
                    "problem_solving": final_assessment.get("dimension_scores", {}).get("problem_solving", 0)
                })
            
            # Get final topic coverage from TopicManagerAgent
            if self.topic_manager:
                coverage_analysis = self.topic_manager.chat("analyze_coverage()")
                self.session_manager.update_topic_progression({
                    "final_coverage": coverage_analysis,
                    "completed_at": datetime.now().isoformat()
                })
            
            # End session and generate reports
            self.session_manager.end_session()
            
            # Mark workflow as inactive
            self.workflow_active = False
            self.current_phase = "completed"
            
            self._log_event("workflow_ended", {
                "final_assessment": final_assessment if 'final_assessment' in locals() else None,
                "coverage_analysis": coverage_analysis if 'coverage_analysis' in locals() else None
            })
            
            return "Multi-agent workflow completed successfully. Final reports generated."
            
        except Exception as e:
            self.logger.error(f"Error ending workflow: {str(e)}")
            return f"Error ending workflow: {str(e)}"
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log workflow events for debugging and analysis."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.event_log.append(event)
        self.logger.info(f"Workflow event: {event_type}")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status and agent health."""
        return {
            "workflow_active": self.workflow_active,
            "current_phase": self.current_phase,
            "agents_initialized": {
                "orchestrator": self.orchestrator is not None,
                "interviewer": self.interviewer is not None,
                "topic_manager": self.topic_manager is not None,
                "evaluator": self.evaluator is not None
            },
            "shared_state_size": len(self.shared_state),
            "event_log_size": len(self.event_log),
            "session_active": self.session_manager.current_session is not None and self.session_manager.current_session.is_active
        }
    
    def get_event_log(self) -> List[Dict]:
        """Get the workflow event log for debugging."""
        return self.event_log.copy()
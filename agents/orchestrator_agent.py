import os
from typing import Dict, List, Optional, Any
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.core.base.llms.types import ChatMessage
from dotenv import load_dotenv

from core.session_manager import SessionManager
from core.document_parser import DocumentParser, ParsedJobDescription, ParsedResume
from agents.topic_manager_agent import TopicManagerAgent
from agents.evaluator_agent import EvaluatorAgent


load_dotenv()


class OrchestratorAgent:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.document_parser = DocumentParser()
        self.llm = OpenAI(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7
        )
        
        # Initialize sub-agents
        self.topic_manager: Optional[TopicManagerAgent] = None
        self.evaluator: Optional[EvaluatorAgent] = None
        
        self.shared_state = {
            "job_description": None,
            "resume": None,
            "skill_matching": None,
            "interview_context": "",
            "current_focus_areas": [],
            "completed_topics": [],
            "next_topic": ""
        }
        
        self.agent = self._create_agent()
    
    def initialize_agents(self):
        """Initialize the sub-agents after orchestrator is ready."""
        if not self.topic_manager:
            self.topic_manager = TopicManagerAgent(self.session_manager, self.shared_state)
        if not self.evaluator:
            self.evaluator = EvaluatorAgent(self.session_manager, self.shared_state)
    
    def _create_agent(self) -> ReActAgent:
        tools = [
            self._create_session_tool(),
            self._create_document_analysis_tool(),
            self._create_state_management_tool(),
            self._create_coordination_tool(),
            self._create_agent_management_tool(),
            self._create_multi_agent_coordination_tool()
        ]
        
        system_prompt = """
        You are the Orchestrator Agent for a multi-agent interview system. Your role is to:
        
        1. Coordinate the overall interview process across multiple agents
        2. Manage shared state between all agents (TopicManager, Interviewer, Evaluator)
        3. Parse and analyze job descriptions and resumes
        4. Initialize and coordinate sub-agents
        5. Monitor interview progress and agent performance
        
        Key responsibilities:
        - Initialize interview sessions and sub-agents
        - Analyze job requirements and candidate qualifications
        - Coordinate with TopicManagerAgent for optimal topic flow
        - Coordinate with InterviewerAgent for contextual question generation
        - Coordinate with EvaluatorAgent for real-time assessment
        - Maintain interview state and progress tracking across all agents
        - Make high-level decisions about interview direction
        
        Agent coordination:
        - TopicManagerAgent: Manages topic sequence, depth, and transitions
        - InterviewerAgent: Generates questions and manages conversation flow
        - EvaluatorAgent: Evaluates responses and provides performance insights
        
        Always maintain professional tone and ensure comprehensive coverage of job requirements.
        """
        
        return ReActAgent.from_tools(
            tools=tools,
            llm=self.llm,
            system_prompt=system_prompt,
            verbose=True
        )
    
    def _create_session_tool(self) -> FunctionTool:
        def manage_session(action: str, **kwargs) -> str:
            """
            Manage interview session lifecycle.
            
            Args:
                action: One of 'create', 'load', 'save', 'end', 'status'
                **kwargs: Additional parameters based on action
            """
            try:
                if action == "create":
                    candidate_name = kwargs.get("candidate_name", "Unknown")
                    job_title = kwargs.get("job_title", "Unknown Position")
                    session_id = self.session_manager.create_session(candidate_name, job_title)
                    return f"Created session {session_id} for {candidate_name}"
                
                elif action == "load":
                    session_id = kwargs.get("session_id")
                    if self.session_manager.load_session(session_id):
                        return f"Loaded session {session_id}"
                    return f"Failed to load session {session_id}"
                
                elif action == "save":
                    self.session_manager.save_session()
                    return "Session saved successfully"
                
                elif action == "end":
                    self.session_manager.end_session()
                    return "Session ended and files generated"
                
                elif action == "status":
                    summary = self.session_manager.get_session_summary()
                    return f"Session status: {summary}"
                
                else:
                    return f"Unknown action: {action}"
            
            except Exception as e:
                return f"Error in session management: {str(e)}"
        
        return FunctionTool.from_defaults(fn=manage_session)
    
    def _create_document_analysis_tool(self) -> FunctionTool:
        def analyze_documents(job_desc_path: str, resume_path: str) -> str:
            """
            Parse and analyze job description and resume documents.
            
            Args:
                job_desc_path: Path to job description file
                resume_path: Path to resume file
            """
            try:
                # Parse documents
                job_desc = self.document_parser.parse_job_description(job_desc_path)
                resume = self.document_parser.parse_resume(resume_path)
                skill_matching = self.document_parser.get_matching_skills(job_desc, resume)
                
                # Update shared state
                self.shared_state["job_description"] = job_desc
                self.shared_state["resume"] = resume
                self.shared_state["skill_matching"] = skill_matching
                
                # Generate focus areas for interview
                focus_areas = self._generate_focus_areas(job_desc, resume, skill_matching)
                self.shared_state["current_focus_areas"] = focus_areas
                
                analysis_summary = f"""
                Document Analysis Complete:
                - Job Title: {job_desc.title} at {job_desc.company}
                - Candidate: {resume.name}, {resume.title}
                - Skill Match: {skill_matching['match_percentage']:.1f}%
                - Focus Areas: {', '.join(focus_areas)}
                - Missing Skills: {', '.join(skill_matching['missing_skills'][:3])}
                """
                
                return analysis_summary
                
            except Exception as e:
                return f"Error analyzing documents: {str(e)}"
        
        return FunctionTool.from_defaults(fn=analyze_documents)
    
    def _create_state_management_tool(self) -> FunctionTool:
        def manage_state(action: str, key: str = None, value: Any = None) -> str:
            """
            Manage shared state between agents.
            
            Args:
                action: 'get', 'set', 'update', or 'list'
                key: State key name
                value: Value to set (for 'set' and 'update' actions)
            """
            try:
                if action == "get":
                    if key in self.shared_state:
                        return str(self.shared_state[key])
                    return f"Key '{key}' not found"
                
                elif action == "set":
                    self.shared_state[key] = value
                    return f"Set {key} = {value}"
                
                elif action == "update":
                    if key in self.shared_state and isinstance(self.shared_state[key], list):
                        self.shared_state[key].append(value)
                        return f"Added {value} to {key}"
                    return f"Cannot update {key}"
                
                elif action == "list":
                    return str(list(self.shared_state.keys()))
                
                else:
                    return f"Unknown action: {action}"
                    
            except Exception as e:
                return f"Error managing state: {str(e)}"
        
        return FunctionTool.from_defaults(fn=manage_state)
    
    def _create_coordination_tool(self) -> FunctionTool:
        def coordinate_agents(action: str, **kwargs) -> str:
            """
            Coordinate actions between different agents.
            
            Args:
                action: 'next_phase', 'set_topic', 'get_context', 'update_progress'
            """
            try:
                if action == "next_phase":
                    current_phase = self.session_manager.current_session.interview_phase if self.session_manager.current_session else "introduction"
                    
                    phase_progression = {
                        "introduction": "technical",
                        "technical": "behavioral", 
                        "behavioral": "conclusion",
                        "conclusion": "complete"
                    }
                    
                    next_phase = phase_progression.get(current_phase, "complete")
                    
                    if self.session_manager.current_session:
                        self.session_manager.set_phase(next_phase)
                    
                    return f"Moved from {current_phase} to {next_phase}"
                
                elif action == "set_topic":
                    topic = kwargs.get("topic", "")
                    if self.session_manager.current_session:
                        self.session_manager.set_topic(topic)
                        
                    # Update shared state
                    if topic and topic not in self.shared_state["completed_topics"]:
                        if self.shared_state["next_topic"]:
                            self.shared_state["completed_topics"].append(self.shared_state["next_topic"])
                        self.shared_state["next_topic"] = topic
                    
                    return f"Set current topic to: {topic}"
                
                elif action == "get_context":
                    context = {
                        "current_phase": self.session_manager.current_session.interview_phase if self.session_manager.current_session else "none",
                        "current_topic": self.shared_state.get("next_topic", ""),
                        "focus_areas": self.shared_state.get("current_focus_areas", []),
                        "completed_topics": self.shared_state.get("completed_topics", []),
                        "skill_match": self.shared_state.get("skill_matching", {}).get("match_percentage", 0) if self.shared_state.get("skill_matching") else 0
                    }
                    return str(context)
                
                elif action == "update_progress":
                    topic = kwargs.get("completed_topic")
                    if topic and topic not in self.shared_state["completed_topics"]:
                        self.shared_state["completed_topics"].append(topic)
                    return f"Marked {topic} as completed"
                
                else:
                    return f"Unknown coordination action: {action}"
                    
            except Exception as e:
                return f"Error in coordination: {str(e)}"
        
        return FunctionTool.from_defaults(fn=coordinate_agents)
    
    def _create_agent_management_tool(self) -> FunctionTool:
        def manage_agents(action: str, agent_name: str = "", **kwargs) -> str:
            """
            Manage sub-agents (TopicManager and Evaluator).
            
            Args:
                action: 'initialize', 'get_status', 'coordinate', 'sync_state'
                agent_name: Name of specific agent ('topic_manager', 'evaluator', 'all')
            """
            try:
                if action == "initialize":
                    self.initialize_agents()
                    
                    # Initialize topic management
                    topic_result = ""
                    if self.topic_manager:
                        topic_result = self.topic_manager.initialize_topic_management()
                    
                    # Initialize evaluation
                    eval_result = ""
                    if self.evaluator:
                        candidate_name = self.session_manager.current_session.candidate_name if self.session_manager.current_session else None
                        eval_result = self.evaluator.initialize_evaluation(candidate_name)
                    
                    return f"Agents initialized: {topic_result} | {eval_result}"
                
                elif action == "get_status":
                    status = {}
                    
                    if agent_name == "topic_manager" or agent_name == "all":
                        if self.topic_manager:
                            guidance = self.topic_manager.get_topic_guidance({})
                            status["topic_manager"] = f"Current topic: {guidance.get('current_topic', 'None')}, Depth: {guidance.get('current_depth', 'surface')}"
                        else:
                            status["topic_manager"] = "Not initialized"
                    
                    if agent_name == "evaluator" or agent_name == "all":
                        if self.evaluator:
                            assessment = self.evaluator.get_current_assessment()
                            status["evaluator"] = f"Overall score: {assessment.get('overall_score', 0):.1f}, Evaluations: {assessment.get('evaluation_count', 0)}"
                        else:
                            status["evaluator"] = "Not initialized"
                    
                    return str(status)
                
                elif action == "sync_state":
                    # Sync shared state with all agents
                    if self.topic_manager:
                        self.topic_manager.shared_state = self.shared_state
                    if self.evaluator:
                        self.evaluator.shared_state = self.shared_state
                    
                    return "Shared state synchronized with all agents"
                
                else:
                    return f"Unknown agent management action: {action}"
                    
            except Exception as e:
                return f"Error managing agents: {str(e)}"
        
        return FunctionTool.from_defaults(fn=manage_agents)
    
    def _create_multi_agent_coordination_tool(self) -> FunctionTool:
        def coordinate_multi_agents(
            scenario: str, 
            current_context: str = "",
            response_text: str = "",
            question: str = ""
        ) -> str:
            """
            Coordinate multiple agents for complex scenarios.
            
            Args:
                scenario: 'question_generation', 'response_evaluation', 'topic_transition', 'interview_guidance'
                current_context: Current interview context
                response_text: Candidate's response (for evaluation scenarios)
                question: Question asked (for evaluation scenarios)
            """
            try:
                if scenario == "question_generation":
                    # Get topic guidance from TopicManager
                    topic_guidance = {}
                    if self.topic_manager:
                        topic_guidance = self.topic_manager.get_topic_guidance({"context": current_context})
                    
                    # Update shared state with topic guidance
                    if "current_topic" in topic_guidance:
                        self.shared_state["next_topic"] = topic_guidance["current_topic"]
                        self.shared_state["suggested_depth"] = topic_guidance.get("suggested_depth", "medium")
                        self.shared_state["topic_category"] = topic_guidance.get("topic_category", "technical")
                    
                    return f"Question generation guidance: Topic: {topic_guidance.get('current_topic', 'General')}, Depth: {topic_guidance.get('suggested_depth', 'medium')}, Category: {topic_guidance.get('topic_category', 'technical')}"
                
                elif scenario == "response_evaluation":
                    # Evaluate response using EvaluatorAgent
                    if self.evaluator and response_text:
                        topic = self.shared_state.get("next_topic", "")
                        question_type = self.shared_state.get("topic_category", "technical")
                        
                        eval_result = self.evaluator.chat(
                            f"evaluate_response('{response_text}', '{question}', '{topic}', '{question_type}')"
                        )
                        
                        # Update topic manager with evaluation insights
                        if self.topic_manager:
                            # Extract response quality from evaluation (simplified)
                            quality = "medium"  # Default
                            if "excellent" in eval_result.lower() or "strong" in eval_result.lower():
                                quality = "high"
                            elif "needs" in eval_result.lower() or "weak" in eval_result.lower():
                                quality = "low"
                            
                            depth_result = self.topic_manager.chat(
                                f"evaluate_topic_depth('{topic}', '{quality}', {len(response_text.split())})"
                            )
                        
                        return f"Response evaluated: {eval_result} | Topic depth: {depth_result if 'depth_result' in locals() else 'N/A'}"
                    
                    return "Response evaluation requires EvaluatorAgent and response text"
                
                elif scenario == "topic_transition":
                    # Coordinate topic transition
                    if self.topic_manager:
                        current_topic = self.shared_state.get("next_topic", "")
                        coverage_status = "partial"  # Could be determined from evaluation data
                        
                        transition_result = self.topic_manager.chat(
                            f"suggest_next_topic('{current_topic}', '{coverage_status}')"
                        )
                        
                        # Update shared state with new topic
                        # Extract topic from result (simplified parsing)
                        if "Next topic:" in transition_result:
                            new_topic = transition_result.split("Next topic:")[1].split("(")[0].strip()
                            self.shared_state["next_topic"] = new_topic
                        
                        return f"Topic transition: {transition_result}"
                    
                    return "Topic transition requires TopicManagerAgent"
                
                elif scenario == "interview_guidance":
                    # Get comprehensive guidance from all agents
                    guidance = {}
                    
                    # Get topic guidance
                    if self.topic_manager:
                        topic_guidance = self.topic_manager.get_topic_guidance({})
                        guidance["topic"] = topic_guidance
                    
                    # Get evaluation guidance
                    if self.evaluator:
                        assessment = self.evaluator.get_current_assessment()
                        guidance["evaluation"] = assessment
                    
                    # Get coverage analysis
                    if self.topic_manager:
                        coverage = self.topic_manager.chat("analyze_coverage()")
                        guidance["coverage"] = coverage
                    
                    return f"Interview guidance: {str(guidance)}"
                
                else:
                    return f"Unknown multi-agent coordination scenario: {scenario}"
                    
            except Exception as e:
                return f"Error in multi-agent coordination: {str(e)}"
        
        return FunctionTool.from_defaults(fn=coordinate_multi_agents)
    
    def _generate_focus_areas(self, job_desc: ParsedJobDescription, resume: ParsedResume, skill_matching: Dict) -> List[str]:
        """Generate key focus areas for the interview based on job requirements and candidate profile."""
        focus_areas = []
        
        # Add areas based on job requirements
        for req in job_desc.requirements:
            if req.category == "technical_skill" and req.importance in ["high", "medium"]:
                focus_areas.append(req.requirement)
            elif req.category == "system_design":
                focus_areas.append("System Design")
            elif req.category == "leadership":
                focus_areas.append("Leadership Experience")
        
        # Add areas for missing critical skills
        for skill in skill_matching.get("missing_skills", [])[:2]:  # Top 2 missing skills
            focus_areas.append(f"Knowledge of {skill}")
        
        # Add general areas
        if any("experience" in req.requirement.lower() for req in job_desc.requirements):
            focus_areas.append("Professional Experience")
        
        return focus_areas[:5]  # Limit to 5 focus areas
    
    def initialize_interview(self, job_desc_path: str, resume_path: str, candidate_name: str = None) -> str:
        """Initialize a new interview session with document analysis and agent coordination."""
        try:
            # Parse documents first
            job_desc = self.document_parser.parse_job_description(job_desc_path)
            resume = self.document_parser.parse_resume(resume_path)
            
            # Use parsed name if not provided
            if not candidate_name:
                candidate_name = resume.name or "Unknown Candidate"
            
            # Create session
            session_id = self.session_manager.create_session(candidate_name, job_desc.title)
            
            # Analyze documents using the agent
            analysis_result = self.agent.chat(f"analyze_documents('{job_desc_path}', '{resume_path}')")
            
            # Initialize and coordinate sub-agents
            agent_init_result = self.agent.chat("manage_agents('initialize', 'all')")
            
            # Sync shared state with all agents
            sync_result = self.agent.chat("manage_agents('sync_state')")
            
            return f"Interview initialized successfully.\nSession ID: {session_id}\n{analysis_result}\nAgents: {agent_init_result}"
            
        except Exception as e:
            return f"Error initializing interview: {str(e)}"
    
    def get_shared_state(self) -> Dict:
        """Get current shared state for other agents."""
        return self.shared_state.copy()
    
    def chat(self, message: str) -> str:
        """Handle orchestrator-level queries and commands."""
        return str(self.agent.chat(message))
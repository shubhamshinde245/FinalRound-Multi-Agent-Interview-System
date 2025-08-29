import os
from typing import Dict, List, Optional, Any
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.core.base.llms.types import ChatMessage
from dotenv import load_dotenv

from core.session_manager import SessionManager
from core.document_parser import DocumentParser, ParsedJobDescription, ParsedResume


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
    
    def _create_agent(self) -> ReActAgent:
        tools = [
            self._create_session_tool(),
            self._create_document_analysis_tool(),
            self._create_state_management_tool(),
            self._create_coordination_tool()
        ]
        
        system_prompt = """
        You are the Orchestrator Agent for a multi-agent interview system. Your role is to:
        
        1. Coordinate the overall interview process
        2. Manage shared state between agents
        3. Parse and analyze job descriptions and resumes
        4. Determine interview flow and topic progression
        5. Ensure all agents have access to necessary context
        
        Key responsibilities:
        - Initialize interview sessions with candidate and job data
        - Analyze job requirements and candidate qualifications
        - Coordinate with InterviewerAgent for question generation
        - Maintain interview state and progress tracking
        - Decide when to transition between interview phases
        
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
        """Initialize a new interview session with document analysis."""
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
            
            return f"Interview initialized successfully.\nSession ID: {session_id}\n{analysis_result}"
            
        except Exception as e:
            return f"Error initializing interview: {str(e)}"
    
    def get_shared_state(self) -> Dict:
        """Get current shared state for other agents."""
        return self.shared_state.copy()
    
    def chat(self, message: str) -> str:
        """Handle orchestrator-level queries and commands."""
        return str(self.agent.chat(message))
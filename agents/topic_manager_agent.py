import os
from typing import Dict, List, Optional, Any, Tuple
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool, FunctionTool
from dotenv import load_dotenv
from dataclasses import dataclass
from datetime import datetime
import json

from core.session_manager import SessionManager
from core.document_parser import ParsedJobDescription, ParsedResume


load_dotenv()


@dataclass
class TopicNode:
    topic: str
    category: str  # "technical", "behavioral", "situational", "system_design"
    importance: str  # "high", "medium", "low"
    estimated_time: int  # minutes
    dependencies: List[str] = None  # topics that should be covered first
    depth_levels: List[str] = None  # ["surface", "medium", "deep"]
    covered: bool = False
    current_depth: str = "surface"
    questions_asked: int = 0
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.depth_levels is None:
            self.depth_levels = ["surface", "medium", "deep"]


@dataclass
class TopicFlow:
    sequence: List[str]  # ordered list of topics
    current_index: int = 0
    total_estimated_time: int = 0
    time_spent: int = 0
    coverage_score: float = 0.0


class TopicManagerAgent:
    def __init__(self, session_manager: SessionManager, shared_state: Dict = None):
        self.session_manager = session_manager
        self.shared_state = shared_state or {}
        self.llm = OpenAI(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.6
        )
        
        # Topic management state
        self.topic_nodes: Dict[str, TopicNode] = {}
        self.topic_flow: Optional[TopicFlow] = None
        self.current_topic: Optional[str] = None
        self.topic_start_time: Optional[datetime] = None
        
        # Configuration
        self.max_questions_per_topic = {
            "high": 4,
            "medium": 3,
            "low": 2
        }
        self.depth_progression_threshold = 2  # questions before considering deeper level
        
        self.agent = self._create_agent()
    
    def _create_agent(self) -> ReActAgent:
        tools = [
            self._create_topic_planning_tool(),
            self._create_depth_evaluation_tool(),
            self._create_transition_tool(),
            self._create_coverage_tool(),
            self._create_time_management_tool()
        ]
        
        system_prompt = """
        You are the Topic Manager Agent for a multi-agent interview system. Your role is to:
        
        1. Plan optimal topic sequence based on job requirements and candidate profile
        2. Control interview depth - when to go deeper vs. move to next topic
        3. Ensure comprehensive coverage of all critical areas
        4. Manage smooth transitions between topics
        5. Balance topic coverage within time constraints
        
        Key principles:
        - Prioritize high-importance topics from job requirements
        - Start with foundational topics before advanced ones
        - Allow deeper exploration for candidate's strong areas
        - Ensure balanced coverage across technical and behavioral aspects
        - Adapt flow based on time remaining and coverage progress
        
        Decision factors:
        - Topic importance and relevance to job
        - Candidate's expertise level in topic area
        - Time constraints and remaining topics
        - Quality and depth of previous responses
        - Interview phase and overall flow
        """
        
        return ReActAgent.from_tools(
            tools=tools,
            llm=self.llm,
            system_prompt=system_prompt,
            verbose=True
        )
    
    def _create_topic_planning_tool(self) -> FunctionTool:
        def plan_topic_sequence(
            job_requirements: List[str] = None,
            candidate_skills: List[str] = None,
            interview_duration: int = 45
        ) -> str:
            """
            Create an optimal topic sequence for the interview.
            
            Args:
                job_requirements: List of job requirements and skills
                candidate_skills: List of candidate's skills and experience
                interview_duration: Total interview time in minutes
            """
            try:
                # Get job description and resume from shared state
                job_desc = self.shared_state.get("job_description")
                resume = self.shared_state.get("resume")
                skill_matching = self.shared_state.get("skill_matching", {})
                
                # Initialize topic nodes based on job requirements
                self.topic_nodes = {}
                
                if job_desc and hasattr(job_desc, 'requirements'):
                    for req in job_desc.requirements:
                        topic_name = req.requirement
                        category = self._categorize_requirement(req.category)
                        importance = req.importance if hasattr(req, 'importance') else "medium"
                        
                        self.topic_nodes[topic_name] = TopicNode(
                            topic=topic_name,
                            category=category,
                            importance=importance,
                            estimated_time=self._estimate_topic_time(importance, category)
                        )
                
                # Add behavioral and general topics
                behavioral_topics = [
                    "Leadership Experience",
                    "Team Collaboration", 
                    "Problem Solving Approach",
                    "Professional Growth"
                ]
                
                for topic in behavioral_topics:
                    if topic not in self.topic_nodes:
                        self.topic_nodes[topic] = TopicNode(
                            topic=topic,
                            category="behavioral",
                            importance="medium",
                            estimated_time=5
                        )
                
                # Create optimized sequence
                sequence = self._optimize_topic_sequence(interview_duration)
                
                self.topic_flow = TopicFlow(
                    sequence=sequence,
                    total_estimated_time=sum(
                        self.topic_nodes[topic].estimated_time 
                        for topic in sequence
                    )
                )
                
                # Update shared state
                self.shared_state["topic_flow"] = {
                    "sequence": sequence,
                    "current_index": 0,
                    "topics": {name: {
                        "category": node.category,
                        "importance": node.importance,
                        "estimated_time": node.estimated_time
                    } for name, node in self.topic_nodes.items()}
                }
                
                return f"Topic sequence planned: {' → '.join(sequence[:5])}... (Total: {len(sequence)} topics, Est. time: {self.topic_flow.total_estimated_time}min)"
                
            except Exception as e:
                return f"Error planning topic sequence: {str(e)}"
        
        return FunctionTool.from_defaults(fn=plan_topic_sequence)
    
    def _create_depth_evaluation_tool(self) -> FunctionTool:
        def evaluate_topic_depth(
            topic: str,
            response_quality: str = "medium",
            response_length: int = 0
        ) -> str:
            """
            Evaluate if current topic needs deeper exploration.
            
            Args:
                topic: Current topic being discussed
                response_quality: Quality of candidate's response ("low", "medium", "high")
                response_length: Length of response in words
            """
            try:
                if topic not in self.topic_nodes:
                    return f"Topic '{topic}' not found in topic nodes"
                
                node = self.topic_nodes[topic]
                
                # Evaluate depth progression criteria
                should_go_deeper = False
                reasons = []
                
                # Check if candidate is performing well in this topic
                if response_quality == "high" and response_length > 50:
                    should_go_deeper = True
                    reasons.append("candidate showing strong expertise")
                
                # Check if topic is high importance and under-explored
                if node.importance == "high" and node.questions_asked < 3:
                    should_go_deeper = True
                    reasons.append("high importance topic needs more coverage")
                
                # Check if we haven't reached deeper levels yet
                if node.current_depth == "surface" and node.questions_asked >= self.depth_progression_threshold:
                    should_go_deeper = True
                    reasons.append("ready to progress to deeper level")
                
                # Check time constraints
                time_remaining = self._get_time_remaining()
                if time_remaining < 10:  # Less than 10 minutes remaining
                    should_go_deeper = False
                    reasons.append("time constraints")
                
                # Update topic state
                if should_go_deeper and node.current_depth == "surface":
                    node.current_depth = "medium"
                elif should_go_deeper and node.current_depth == "medium":
                    node.current_depth = "deep"
                
                node.questions_asked += 1
                
                return f"Depth evaluation for '{topic}': {'GO_DEEPER' if should_go_deeper else 'CONTINUE_CURRENT'} (Current: {node.current_depth}, Questions: {node.questions_asked}, Reasons: {', '.join(reasons)})"
                
            except Exception as e:
                return f"Error evaluating topic depth: {str(e)}"
        
        return FunctionTool.from_defaults(fn=evaluate_topic_depth)
    
    def _create_transition_tool(self) -> FunctionTool:
        def suggest_next_topic(
            current_topic: str = "",
            coverage_status: str = "partial",
            time_remaining: int = 0
        ) -> str:
            """
            Suggest the next topic to transition to.
            
            Args:
                current_topic: Topic currently being discussed
                coverage_status: How well current topic is covered ("minimal", "partial", "complete")
                time_remaining: Minutes remaining in interview
            """
            try:
                if not self.topic_flow:
                    return "Topic flow not initialized. Please plan topic sequence first."
                
                # Mark current topic as covered if status indicates completion
                if current_topic and coverage_status in ["complete", "partial"]:
                    if current_topic in self.topic_nodes:
                        self.topic_nodes[current_topic].covered = True
                
                # Find next uncovered topic
                next_topic = None
                
                # First, check if we should continue with planned sequence
                if self.topic_flow.current_index < len(self.topic_flow.sequence):
                    candidate_topic = self.topic_flow.sequence[self.topic_flow.current_index]
                    if not self.topic_nodes.get(candidate_topic, TopicNode("", "", "")).covered:
                        next_topic = candidate_topic
                
                # If planned topic is covered, find next uncovered high-priority topic
                if not next_topic:
                    for topic_name, node in self.topic_nodes.items():
                        if not node.covered and node.importance == "high":
                            next_topic = topic_name
                            break
                
                # If no high-priority topics, find medium priority
                if not next_topic:
                    for topic_name, node in self.topic_nodes.items():
                        if not node.covered and node.importance == "medium":
                            next_topic = topic_name
                            break
                
                # Update flow state
                if next_topic:
                    # Find index of next topic in sequence
                    try:
                        self.topic_flow.current_index = self.topic_flow.sequence.index(next_topic)
                    except ValueError:
                        # Topic not in original sequence, append it
                        self.topic_flow.sequence.append(next_topic)
                        self.topic_flow.current_index = len(self.topic_flow.sequence) - 1
                    
                    self.current_topic = next_topic
                    self.topic_start_time = datetime.now()
                    
                    # Update shared state
                    self.shared_state["next_topic"] = next_topic
                    self.shared_state["current_topic_category"] = self.topic_nodes[next_topic].category
                    
                    return f"Next topic: {next_topic} (Category: {self.topic_nodes[next_topic].category}, Importance: {self.topic_nodes[next_topic].importance})"
                
                else:
                    return "All topics covered or no suitable next topic found"
                
            except Exception as e:
                return f"Error suggesting next topic: {str(e)}"
        
        return FunctionTool.from_defaults(fn=suggest_next_topic)
    
    def _create_coverage_tool(self) -> FunctionTool:
        def analyze_coverage() -> str:
            """Analyze current topic coverage and provide recommendations."""
            try:
                if not self.topic_nodes:
                    return "No topics initialized. Please plan topic sequence first."
                
                total_topics = len(self.topic_nodes)
                covered_topics = sum(1 for node in self.topic_nodes.values() if node.covered)
                high_priority_covered = sum(1 for node in self.topic_nodes.values() 
                                          if node.covered and node.importance == "high")
                high_priority_total = sum(1 for node in self.topic_nodes.values() 
                                        if node.importance == "high")
                
                coverage_score = covered_topics / total_topics if total_topics > 0 else 0
                self.topic_flow.coverage_score = coverage_score
                
                # Identify gaps
                uncovered_high = [name for name, node in self.topic_nodes.items()
                                 if not node.covered and node.importance == "high"]
                uncovered_medium = [name for name, node in self.topic_nodes.items()
                                   if not node.covered and node.importance == "medium"]
                
                analysis = {
                    "total_coverage": f"{coverage_score:.1%}",
                    "topics_covered": f"{covered_topics}/{total_topics}",
                    "high_priority_coverage": f"{high_priority_covered}/{high_priority_total}",
                    "uncovered_high_priority": uncovered_high,
                    "uncovered_medium_priority": uncovered_medium[:3],  # Top 3
                    "time_utilization": f"{self.topic_flow.time_spent}/{self.topic_flow.total_estimated_time}min"
                }
                
                return f"Coverage Analysis: {analysis['total_coverage']} complete, {analysis['topics_covered']} topics, High-priority: {analysis['high_priority_coverage']}, Gaps: {', '.join(uncovered_high[:3])}"
                
            except Exception as e:
                return f"Error analyzing coverage: {str(e)}"
        
        return FunctionTool.from_defaults(fn=analyze_coverage)
    
    def _create_time_management_tool(self) -> FunctionTool:
        def manage_time_allocation(
            action: str,
            topic: str = "",
            time_spent: int = 0
        ) -> str:
            """
            Manage time allocation across topics.
            
            Args:
                action: 'start_topic', 'end_topic', 'check_time', 'adjust_plan'
                topic: Topic name
                time_spent: Time spent on topic in minutes
            """
            try:
                if action == "start_topic":
                    self.topic_start_time = datetime.now()
                    return f"Started timing for topic: {topic}"
                
                elif action == "end_topic":
                    if self.topic_start_time:
                        time_spent = (datetime.now() - self.topic_start_time).total_seconds() / 60
                        self.topic_flow.time_spent += time_spent
                        
                        if topic in self.topic_nodes:
                            self.topic_nodes[topic].covered = True
                        
                        return f"Topic '{topic}' completed in {time_spent:.1f} minutes"
                    
                elif action == "check_time":
                    time_remaining = self._get_time_remaining()
                    uncovered_count = sum(1 for node in self.topic_nodes.values() if not node.covered)
                    avg_time_per_topic = time_remaining / max(uncovered_count, 1)
                    
                    return f"Time remaining: {time_remaining}min, Uncovered topics: {uncovered_count}, Avg time available per topic: {avg_time_per_topic:.1f}min"
                
                elif action == "adjust_plan":
                    recommendations = self._adjust_time_plan()
                    return f"Time plan adjusted: {recommendations}"
                
                else:
                    return f"Unknown time management action: {action}"
                    
            except Exception as e:
                return f"Error managing time allocation: {str(e)}"
        
        return FunctionTool.from_defaults(fn=manage_time_allocation)
    
    def _categorize_requirement(self, category: str) -> str:
        """Map requirement categories to question types."""
        mapping = {
            "technical_skill": "technical",
            "system_design": "system_design",
            "leadership": "behavioral",
            "communication": "behavioral",
            "experience": "situational"
        }
        return mapping.get(category, "technical")
    
    def _estimate_topic_time(self, importance: str, category: str) -> int:
        """Estimate time needed for a topic based on importance and category."""
        base_times = {
            "technical": 6,
            "behavioral": 5,
            "situational": 4,
            "system_design": 8
        }
        
        multipliers = {
            "high": 1.5,
            "medium": 1.0,
            "low": 0.7
        }
        
        base_time = base_times.get(category, 5)
        multiplier = multipliers.get(importance, 1.0)
        
        return int(base_time * multiplier)
    
    def _optimize_topic_sequence(self, total_time: int) -> List[str]:
        """Create optimized topic sequence considering dependencies and importance."""
        # Sort topics by importance and category
        topics_by_priority = sorted(
            self.topic_nodes.items(),
            key=lambda x: (
                {"high": 3, "medium": 2, "low": 1}[x[1].importance],
                {"technical": 2, "system_design": 2, "behavioral": 1, "situational": 1}[x[1].category]
            ),
            reverse=True
        )
        
        # Build sequence considering time constraints
        sequence = []
        total_estimated_time = 0
        
        for topic_name, node in topics_by_priority:
            if total_estimated_time + node.estimated_time <= total_time:
                sequence.append(topic_name)
                total_estimated_time += node.estimated_time
            elif node.importance == "high":
                # Always include high-importance topics, but reduce estimated time
                sequence.append(topic_name)
                node.estimated_time = min(node.estimated_time, total_time - total_estimated_time)
                total_estimated_time += node.estimated_time
        
        return sequence
    
    def _get_time_remaining(self) -> int:
        """Get remaining interview time in minutes."""
        if self.session_manager.current_session:
            return max(0, self.session_manager.get_time_remaining() // 60)
        return 45  # Default 45 minutes
    
    def _adjust_time_plan(self) -> str:
        """Adjust time plan based on current progress."""
        time_remaining = self._get_time_remaining()
        uncovered_topics = [name for name, node in self.topic_nodes.items() if not node.covered]
        
        if len(uncovered_topics) == 0:
            return "All topics covered"
        
        # Prioritize high-importance uncovered topics
        high_priority_uncovered = [name for name in uncovered_topics 
                                  if self.topic_nodes[name].importance == "high"]
        
        if time_remaining < len(high_priority_uncovered) * 3:
            return f"Time critical: Focus only on {len(high_priority_uncovered)} high-priority topics"
        
        return f"Time sufficient: Continue with planned sequence"
    
    def initialize_topic_management(self, job_desc_path: str = None, resume_path: str = None) -> str:
        """Initialize topic management for a new interview."""
        try:
            # Plan topic sequence using available data
            result = self.agent.chat("plan_topic_sequence()")
            
            # Suggest first topic
            if self.topic_flow and self.topic_flow.sequence:
                first_topic_result = self.agent.chat("suggest_next_topic()")
                return f"Topic management initialized. {result}\n{first_topic_result}"
            
            return f"Topic management initialized. {result}"
            
        except Exception as e:
            return f"Error initializing topic management: {str(e)}"
    
    def get_topic_guidance(self, current_context: Dict) -> Dict:
        """Get guidance for current interview state."""
        try:
            guidance = {
                "current_topic": self.current_topic,
                "suggested_depth": "medium",
                "transition_recommendation": "continue",
                "time_status": "on_track"
            }
            
            if self.current_topic and self.current_topic in self.topic_nodes:
                node = self.topic_nodes[self.current_topic]
                guidance.update({
                    "current_topic": self.current_topic,
                    "topic_category": node.category,
                    "topic_importance": node.importance,
                    "current_depth": node.current_depth,
                    "questions_asked": node.questions_asked,
                    "suggested_depth": self._suggest_next_depth(node)
                })
            
            return guidance
            
        except Exception as e:
            return {"error": f"Error getting topic guidance: {str(e)}"}
    
    def _suggest_next_depth(self, node: TopicNode) -> str:
        """Suggest next depth level for a topic."""
        if node.questions_asked < self.depth_progression_threshold:
            return node.current_depth
        elif node.current_depth == "surface":
            return "medium"
        elif node.current_depth == "medium" and node.importance == "high":
            return "deep"
        else:
            return node.current_depth
    
    def chat(self, message: str) -> str:
        """Handle topic manager queries and commands."""
        return str(self.agent.chat(message))
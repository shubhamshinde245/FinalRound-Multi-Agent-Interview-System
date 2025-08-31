import os
from typing import Dict, List, Optional, Any
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool, FunctionTool
from dotenv import load_dotenv
import random

from core.session_manager import SessionManager


load_dotenv()


class InterviewerAgent:
    def __init__(self, session_manager: SessionManager, shared_state: Dict = None):
        self.session_manager = session_manager
        self.shared_state = shared_state or {}
        self.llm = OpenAI(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.8
        )
        
        # Streaming LLM for real-time question generation
        self.streaming_llm = OpenAI(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.8,
            streaming=True
        )
        
        self.question_templates = {
            "technical": [
                "Can you explain your experience with {skill}?",
                "How would you approach {scenario} using {skill}?",
                "What challenges have you faced when working with {skill}?",
                "Can you walk me through a project where you used {skill}?",
                "How do you stay updated with {skill} best practices?"
            ],
            "behavioral": [
                "Tell me about a time when you {situation}.",
                "Describe a challenging situation where you {context}.",
                "How do you handle {scenario} in your work?",
                "Can you give an example of when you {action}?",
                "What's your approach to {challenge}?"
            ],
            "situational": [
                "If you were asked to {scenario}, how would you approach it?",
                "How would you handle a situation where {challenge}?",
                "What would you do if {problem_scenario}?",
                "How would you prioritize {multiple_tasks}?",
                "What's your strategy for {goal_achievement}?"
            ],
            "system_design": [
                "How would you design a system for {use_case}?",
                "What considerations would you make when scaling {system_type}?",
                "How would you ensure {quality_attribute} in a {system_type}?",
                "What trade-offs would you consider for {design_decision}?",
                "How would you handle {system_challenge} in a distributed system?"
            ]
        }
        
        self.agent = self._create_agent()
    
    def _create_agent(self) -> ReActAgent:
        tools = [
            self._create_question_generation_tool(),
            self._create_follow_up_tool(),
            self._create_context_tool(),
            self._create_conversation_flow_tool(),
            self._create_agent_coordination_tool(),
            self._create_adaptive_questioning_tool()
        ]
        
        system_prompt = """
        You are the Interviewer Agent for a multi-agent interview system. Your role is to:
        
        1. Generate contextually relevant interview questions based on guidance from TopicManagerAgent
        2. Adapt questions based on candidate responses, job requirements, and evaluation feedback
        3. Maintain natural conversation flow with smooth topic transitions
        4. Ask appropriate follow-up questions guided by evaluation insights
        5. Work with other agents to ensure comprehensive interview coverage
        
        Multi-agent coordination:
        - Receive topic guidance from TopicManagerAgent (topic, depth, category)
        - Consider evaluation feedback from EvaluatorAgent for question difficulty adjustment
        - Coordinate with OrchestratorAgent for overall interview flow
        
        Question generation principles:
        - Base questions on job requirements and candidate background
        - Use topic manager guidance for optimal topic flow and depth
        - Adapt difficulty based on evaluation agent feedback about candidate performance
        - Ask follow-up questions when evaluator indicates need for deeper exploration
        - Maintain professional and engaging tone throughout
        - Integrate evaluation insights to personalize question approach
        
        Question types to generate:
        - Technical: Skills, technologies, problem-solving (with appropriate difficulty)
        - Behavioral: Past experiences, teamwork, leadership (based on evaluation patterns)
        - Situational: Hypothetical scenarios, decision-making (adapted to performance level)
        - System Design: Architecture, scalability, trade-offs (with complexity matching ability)
        """
        
        return ReActAgent.from_tools(
            tools=tools,
            llm=self.llm,
            system_prompt=system_prompt,
            verbose=True
        )
    
    def _create_question_generation_tool(self) -> FunctionTool:
        def generate_question(question_type: str, topic: str = "", context: str = "") -> str:
            """
            Generate an interview question based on type and topic.
            
            Args:
                question_type: Type of question ('technical', 'behavioral', 'situational', 'system_design')
                topic: Specific topic or skill to focus on
                context: Additional context from job description or candidate background
            """
            try:
                if question_type not in self.question_templates:
                    return f"Unknown question type: {question_type}"
                
                # Get job and candidate context
                job_desc = self.shared_state.get("job_description")
                resume = self.shared_state.get("resume")
                current_phase = self.session_manager.current_session.interview_phase if self.session_manager.current_session else "technical"
                
                # Get guidance from shared state (set by TopicManagerAgent and EvaluatorAgent)
                suggested_depth = self.shared_state.get("suggested_depth", "medium")
                evaluation_insights = self.shared_state.get("evaluation_insights", {})
                
                # Generate contextual question based on type and agent guidance
                if question_type == "technical":
                    question = self._generate_technical_question(topic, job_desc, resume, suggested_depth, evaluation_insights)
                elif question_type == "behavioral":
                    question = self._generate_behavioral_question(topic, job_desc, resume, suggested_depth, evaluation_insights)
                elif question_type == "situational":
                    question = self._generate_situational_question(topic, job_desc, resume, suggested_depth, evaluation_insights)
                elif question_type == "system_design":
                    question = self._generate_system_design_question(topic, job_desc, resume, suggested_depth, evaluation_insights)
                else:
                    template = random.choice(self.question_templates[question_type])
                    question = template.format(skill=topic, scenario=context, situation=topic)
                
                # Record the question
                if self.session_manager.current_session:
                    self.session_manager.add_question(question, question_type)
                
                return question
                
            except Exception as e:
                return f"Error generating question: {str(e)}"
        
        return FunctionTool.from_defaults(fn=generate_question)
    
    def _create_follow_up_tool(self) -> FunctionTool:
        def generate_follow_up(previous_response: str, original_question: str, depth_level: str = "medium") -> str:
            """
            Generate a follow-up question based on the candidate's response.
            
            Args:
                previous_response: The candidate's previous response
                original_question: The original question that was asked
                depth_level: How deep to go ('surface', 'medium', 'deep')
            """
            try:
                follow_up_prompts = {
                    "surface": [
                        "Can you elaborate on that?",
                        "What else can you tell me about this?",
                        "Are there any other aspects to consider?"
                    ],
                    "medium": [
                        "What challenges did you encounter in that situation?",
                        "How did you decide on that approach?",
                        "What would you do differently next time?",
                        "What was the outcome of that decision?"
                    ],
                    "deep": [
                        "Can you walk me through your thought process step by step?",
                        "What alternative approaches did you consider and why did you choose this one?",
                        "How did you measure the success of your approach?",
                        "What lessons did you learn that you apply in similar situations now?"
                    ]
                }
                
                # Analyze response to determine appropriate follow-up
                response_length = len(previous_response.split())
                
                if response_length < 20:  # Short response, encourage elaboration
                    follow_up = random.choice(follow_up_prompts["surface"])
                elif response_length < 50:  # Medium response, probe deeper
                    follow_up = random.choice(follow_up_prompts["medium"])
                else:  # Detailed response, ask for specific insights
                    follow_up = random.choice(follow_up_prompts["deep"])
                
                # Add context-specific follow-up if technical topic is detected
                technical_keywords = ['python', 'aws', 'system', 'design', 'architecture', 'database', 'api']
                if any(keyword in previous_response.lower() for keyword in technical_keywords):
                    technical_follow_ups = [
                        "What technologies would you choose differently today?",
                        "How would you scale this solution?",
                        "What performance considerations did you keep in mind?"
                    ]
                    follow_up = random.choice(technical_follow_ups)
                
                # Record the follow-up question
                if self.session_manager.current_session:
                    self.session_manager.add_question(follow_up, "follow-up")
                
                return follow_up
                
            except Exception as e:
                return f"Error generating follow-up: {str(e)}"
        
        return FunctionTool.from_defaults(fn=generate_follow_up)
    
    def _create_context_tool(self) -> FunctionTool:
        def get_interview_context() -> str:
            """Get current interview context and progress."""
            try:
                context = {
                    "session_active": self.session_manager.current_session is not None,
                    "current_phase": self.session_manager.current_session.interview_phase if self.session_manager.current_session else "none",
                    "questions_asked": len(self.session_manager.current_session.questions_asked) if self.session_manager.current_session else 0,
                    "current_topic": self.shared_state.get("next_topic", ""),
                    "focus_areas": self.shared_state.get("current_focus_areas", []),
                    "completed_topics": self.shared_state.get("completed_topics", []),
                    "time_remaining": self.session_manager.get_time_remaining()
                }
                
                return str(context)
                
            except Exception as e:
                return f"Error getting context: {str(e)}"
        
        return FunctionTool.from_defaults(fn=get_interview_context)
    
    def _create_conversation_flow_tool(self) -> FunctionTool:
        def manage_conversation_flow(action: str, **kwargs) -> str:
            """
            Manage the flow of conversation during the interview.
            
            Args:
                action: 'transition', 'wrap_up', 'introduce_topic', 'check_coverage'
            """
            try:
                if action == "transition":
                    new_topic = kwargs.get("topic", "")
                    transition_phrases = [
                        f"Great! Now let's move on to discuss {new_topic}.",
                        f"Thank you for that insight. I'd like to explore {new_topic} next.",
                        f"That's very helpful. Let's shift our focus to {new_topic}.",
                        f"Excellent. Now I'm curious about your experience with {new_topic}."
                    ]
                    return random.choice(transition_phrases)
                
                elif action == "wrap_up":
                    topic = kwargs.get("topic", "this topic")
                    wrap_up_phrases = [
                        f"Thank you for sharing your thoughts on {topic}.",
                        f"That gives me a good understanding of your experience with {topic}.",
                        f"I appreciate the detailed explanation about {topic}."
                    ]
                    return random.choice(wrap_up_phrases)
                
                elif action == "introduce_topic":
                    topic = kwargs.get("topic", "")
                    intro_phrases = [
                        f"I'd like to learn about your experience with {topic}.",
                        f"Let's discuss {topic} for a moment.",
                        f"Can we talk about {topic}?",
                        f"I'm interested in hearing about your work with {topic}."
                    ]
                    return random.choice(intro_phrases)
                
                elif action == "check_coverage":
                    focus_areas = self.shared_state.get("current_focus_areas", [])
                    completed = self.shared_state.get("completed_topics", [])
                    remaining = [area for area in focus_areas if area not in completed]
                    
                    return f"Remaining topics to cover: {', '.join(remaining)}"
                
                else:
                    return f"Unknown conversation action: {action}"
                    
            except Exception as e:
                return f"Error managing conversation flow: {str(e)}"
        
        return FunctionTool.from_defaults(fn=manage_conversation_flow)
    
    def _create_agent_coordination_tool(self) -> FunctionTool:
        def coordinate_with_agents(action: str, **kwargs) -> str:
            """
            Coordinate with other agents in the system.
            
            Args:
                action: 'get_topic_guidance', 'get_evaluation_insights', 'request_depth_change', 'sync_context'
            """
            try:
                if action == "get_topic_guidance":
                    # Get current topic guidance from shared state (updated by TopicManagerAgent)
                    topic_guidance = {
                        "current_topic": self.shared_state.get("next_topic", ""),
                        "suggested_depth": self.shared_state.get("suggested_depth", "medium"),
                        "topic_category": self.shared_state.get("topic_category", "technical"),
                        "transition_needed": self.shared_state.get("transition_needed", False)
                    }
                    return f"Topic guidance: {str(topic_guidance)}"
                
                elif action == "get_evaluation_insights":
                    # Get evaluation insights from shared state (updated by EvaluatorAgent)
                    evaluation_insights = {
                        "performance_level": self.shared_state.get("performance_level", "medium"),
                        "strong_areas": self.shared_state.get("strong_areas", []),
                        "weak_areas": self.shared_state.get("weak_areas", []),
                        "suggested_difficulty": self.shared_state.get("suggested_difficulty", "medium"),
                        "needs_follow_up": self.shared_state.get("needs_follow_up", False)
                    }
                    return f"Evaluation insights: {str(evaluation_insights)}"
                
                elif action == "sync_context":
                    # Update shared state with current interview context
                    current_context = {
                        "current_phase": self.session_manager.current_session.interview_phase if self.session_manager.current_session else "none",
                        "questions_asked_count": len(self.session_manager.current_session.questions_asked) if self.session_manager.current_session else 0,
                        "time_remaining": self.session_manager.get_time_remaining()
                    }
                    self.shared_state["interviewer_context"] = current_context
                    return f"Context synced: {str(current_context)}"
                
                else:
                    return f"Unknown coordination action: {action}"
                    
            except Exception as e:
                return f"Error coordinating with agents: {str(e)}"
        
        return FunctionTool.from_defaults(fn=coordinate_with_agents)
    
    def _create_adaptive_questioning_tool(self) -> FunctionTool:
        def adapt_questioning_strategy(
            performance_feedback: str = "",
            topic_guidance: str = "",
            candidate_response: str = ""
        ) -> str:
            """
            Adapt questioning strategy based on multi-agent feedback.
            
            Args:
                performance_feedback: Feedback from EvaluatorAgent
                topic_guidance: Guidance from TopicManagerAgent
                candidate_response: Recent candidate response for context
            """
            try:
                adaptations = []
                
                # Analyze performance feedback for difficulty adjustment
                if "strong" in performance_feedback.lower() or "excellent" in performance_feedback.lower():
                    adaptations.append("Increase question difficulty - candidate performing well")
                    self.shared_state["suggested_difficulty"] = "high"
                elif "weak" in performance_feedback.lower() or "struggling" in performance_feedback.lower():
                    adaptations.append("Reduce question difficulty - provide more support")
                    self.shared_state["suggested_difficulty"] = "low"
                
                # Analyze topic guidance for flow adjustments
                if "transition" in topic_guidance.lower():
                    adaptations.append("Prepare for topic transition")
                elif "deeper" in topic_guidance.lower():
                    adaptations.append("Ask more detailed follow-up questions")
                
                # Analyze candidate response patterns
                if candidate_response:
                    response_length = len(candidate_response.split())
                    if response_length < 20:
                        adaptations.append("Encourage more detailed responses")
                    elif response_length > 150:
                        adaptations.append("Guide toward more concise responses")
                    
                    # Check for uncertainty indicators
                    uncertainty_phrases = ["not sure", "i think", "maybe", "probably"]
                    if any(phrase in candidate_response.lower() for phrase in uncertainty_phrases):
                        adaptations.append("Provide supportive follow-up questions")
                
                return f"Questioning strategy adapted: {'; '.join(adaptations) if adaptations else 'No adaptations needed'}"
                
            except Exception as e:
                return f"Error adapting questioning strategy: {str(e)}"
        
        return FunctionTool.from_defaults(fn=adapt_questioning_strategy)
    
    def _generate_technical_question(self, topic: str, job_desc, resume, depth: str = "medium", insights: Dict = None) -> str:
        """Generate a technical question based on job requirements, candidate background, and agent guidance."""
        insights = insights or {}
        
        if not topic and job_desc:
            # Pick a technical requirement from job description
            tech_requirements = [req for req in job_desc.requirements if req.category == "technical_skill"]
            if tech_requirements:
                topic = random.choice(tech_requirements).requirement
        
        if not topic:
            topic = "your technical background"
        
        # Adapt question templates based on depth and performance insights
        if depth == "surface" or insights.get("suggested_difficulty") == "low":
            templates = [
                f"Can you tell me about your experience with {topic}?",
                f"How familiar are you with {topic}?",
                f"Have you worked with {topic} in any of your projects?",
                f"What do you know about {topic}?"
            ]
        elif depth == "deep" or insights.get("suggested_difficulty") == "high":
            templates = [
                f"Can you explain the internal architecture and optimization strategies you'd use when implementing {topic} at scale?",
                f"How would you debug performance issues in a {topic}-based system under high load?",
                f"What are the key trade-offs and design patterns you'd consider when architecting a system using {topic}?",
                f"Can you walk me through how you'd handle edge cases and error scenarios in a production {topic} implementation?",
                f"How would you approach migrating a legacy system to use {topic} while maintaining zero downtime?"
            ]
        else:  # medium depth
            templates = [
                f"Can you describe your hands-on experience with {topic} and any challenges you've overcome?",
                f"How have you used {topic} in your recent projects, and what results did you achieve?",
                f"What aspects of {topic} do you find most challenging, and how do you address them?",
                f"Can you walk me through a specific example where you implemented {topic} and the decisions you made?",
                f"How do you approach learning new features or best practices in {topic}?"
            ]
        
        return random.choice(templates)
    
    def _generate_behavioral_question(self, topic: str, job_desc, resume, depth: str = "medium", insights: Dict = None) -> str:
        """Generate a behavioral question based on job requirements and agent guidance."""
        insights = insights or {}
        
        behavioral_scenarios = [
            "had to work with a difficult team member",
            "faced a tight deadline with multiple competing priorities",
            "had to learn a new technology quickly for a project",
            "disagreed with a technical decision made by your team",
            "had to mentor or help a junior team member",
            "made a mistake that impacted a project",
            "had to present a technical solution to non-technical stakeholders"
        ]
        
        scenario = topic if topic else random.choice(behavioral_scenarios)
        
        # Adapt question format based on depth and insights
        if depth == "surface" or insights.get("needs_follow_up") == False:
            return f"Can you tell me about a time when you {scenario}?"
        elif depth == "deep" or insights.get("performance_level") == "high":
            return f"Tell me about a time when you {scenario}. I'm particularly interested in your thought process, the alternatives you considered, how you measured success, and what you learned that you now apply in similar situations."
        else:  # medium depth
            return f"Tell me about a time when you {scenario}. What was the situation, what did you do, and what was the outcome?"
    
    def _generate_situational_question(self, topic: str, job_desc, resume, depth: str = "medium", insights: Dict = None) -> str:
        """Generate a situational question based on job context and agent guidance."""
        insights = insights or {}
        
        if job_desc and job_desc.responsibilities and not topic:
            responsibility = random.choice(job_desc.responsibilities)
            scenario = f"you needed to {responsibility.lower()}"
        else:
            situational_scenarios = [
                "you inherited a legacy codebase with poor documentation",
                "you needed to optimize a slow-performing system",
                "you had to choose between two different architectural approaches",
                "you discovered a security vulnerability in production",
                "you needed to integrate with a third-party API that had limited documentation"
            ]
            scenario = topic if topic else random.choice(situational_scenarios)
        
        # Adapt question complexity based on depth and performance insights
        if depth == "surface" or insights.get("suggested_difficulty") == "low":
            return f"How would you handle a situation where {scenario}?"
        elif depth == "deep" or insights.get("suggested_difficulty") == "high":
            return f"Imagine {scenario}. Walk me through your complete approach including stakeholder communication, risk assessment, implementation strategy, monitoring, and how you'd handle potential complications."
        else:  # medium depth
            return f"Imagine {scenario}. How would you handle this situation? What steps would you take and what factors would you consider?"
    
    def _generate_system_design_question(self, topic: str, job_desc, resume, depth: str = "medium", insights: Dict = None) -> str:
        """Generate a system design question based on depth and performance insights."""
        insights = insights or {}
        
        if not topic:
            design_topics = [
                "a URL shortener service",
                "a chat messaging system",
                "a file storage system",
                "a notification service",
                "a caching layer for a web application",
                "a load balancing system",
                "a database backup system"
            ]
            topic = random.choice(design_topics)
        
        # Adapt question complexity based on depth and performance
        if depth == "surface" or insights.get("suggested_difficulty") == "low":
            return f"How would you approach designing {topic}? What are the main components you'd consider?"
        elif depth == "deep" or insights.get("suggested_difficulty") == "high":
            return f"Design {topic} for a company with 100M+ users. Address scalability, reliability, performance, security, monitoring, disaster recovery, cost optimization, and how you'd handle data consistency across multiple regions."
        else:  # medium depth
            return f"How would you design {topic}? Consider scalability, reliability, and performance in your approach, and explain your trade-offs."
    
    def start_interview(self) -> str:
        """Generate an opening question to start the interview."""
        opening_questions = [
            "Let's start with a brief introduction. Can you tell me about your current role and what drew you to apply for this position?",
            "I'd love to learn more about your background. Can you walk me through your professional journey and what interests you about this opportunity?",
            "To begin, could you share what you're currently working on and what aspects of this role excite you the most?",
            "Let's start by having you introduce yourself and tell me what you know about this position and why you're interested in it."
        ]
        
        question = random.choice(opening_questions)
        
        if self.session_manager.current_session:
            self.session_manager.add_question(question, "introduction")
            self.session_manager.set_phase("introduction")
        
        return question
    
    def generate_streaming_question(self, question_type: str, topic: str = "", context: str = "", callback=None):
        """Generate a question with streaming response."""
        try:
            # Get job and candidate context
            job_desc = self.shared_state.get("job_description")
            resume = self.shared_state.get("resume")
            
            # Create a detailed prompt for question generation
            prompt = self._create_streaming_prompt(question_type, topic, context, job_desc, resume)
            
            # Stream the response
            full_question = ""
            for chunk in self.streaming_llm.stream_complete(prompt):
                chunk_text = chunk.delta
                full_question += chunk_text
                if callback:
                    callback(chunk_text)
            
            # Record the complete question
            if self.session_manager.current_session:
                self.session_manager.add_question(full_question.strip(), question_type)
            
            return full_question.strip()
            
        except Exception as e:
            error_msg = f"Error generating streaming question: {str(e)}"
            if callback:
                callback(error_msg)
            return error_msg
    
    def _create_streaming_prompt(self, question_type: str, topic: str, context: str, job_desc, resume) -> str:
        """Create a detailed prompt for streaming question generation."""
        prompt_parts = [
            f"You are an experienced technical interviewer conducting a {question_type} interview question.",
            "Generate ONE high-quality, specific interview question."
        ]
        
        if job_desc:
            prompt_parts.append(f"Job Role: {getattr(job_desc, 'title', 'N/A')}")
            if hasattr(job_desc, 'requirements') and job_desc.requirements:
                key_requirements = [req.requirement for req in job_desc.requirements[:3]]
                prompt_parts.append(f"Key Requirements: {', '.join(key_requirements)}")
        
        if resume:
            prompt_parts.append(f"Candidate: {getattr(resume, 'name', 'N/A')}")
            if hasattr(resume, 'skills') and resume.skills:
                key_skills = [skill.skill_name for skill in resume.skills[:5]]
                prompt_parts.append(f"Key Skills: {', '.join(key_skills)}")
        
        if topic:
            prompt_parts.append(f"Focus Topic: {topic}")
        
        if context:
            prompt_parts.append(f"Additional Context: {context}")
        
        # Question type specific instructions
        type_instructions = {
            "technical": "Ask about specific technical experience, implementation details, or problem-solving approaches. Be specific and practical.",
            "behavioral": "Ask about past experiences using the STAR format (Situation, Task, Action, Result). Focus on leadership, teamwork, or challenges.",
            "situational": "Present a realistic workplace scenario and ask how they would handle it. Make it relevant to the role.",
            "system_design": "Ask them to design a system or architecture. Include scalability, reliability, and performance considerations."
        }
        
        prompt_parts.append(f"Question Style: {type_instructions.get(question_type, 'Ask a thoughtful, engaging question.')}")
        prompt_parts.append("Generate only the question - no additional text, explanations, or formatting.")
        
        return "\n".join(prompt_parts)
    
    def generate_next_question(self, context: str = "", previous_response: str = "") -> str:
        """Generate the next appropriate question based on current interview state and agent coordination."""
        try:
            # Get coordination data from other agents
            self.agent.chat("coordinate_with_agents('sync_context')")
            topic_guidance = self.agent.chat("coordinate_with_agents('get_topic_guidance')")
            evaluation_insights = self.agent.chat("coordinate_with_agents('get_evaluation_insights')")
            
            # Adapt questioning strategy based on multi-agent feedback
            if previous_response:
                adaptation_result = self.agent.chat(f"adapt_questioning_strategy('', '{topic_guidance}', '{previous_response}')")
            
            current_phase = self.session_manager.current_session.interview_phase if self.session_manager.current_session else "introduction"
            current_topic = self.shared_state.get("next_topic", "")
            suggested_depth = self.shared_state.get("suggested_depth", "medium")
            
            if current_phase == "introduction":
                return self.start_interview()
            elif current_phase == "technical":
                return self.agent.chat(f"generate_question('technical', '{current_topic}', '{context}')")
            elif current_phase == "behavioral":
                return self.agent.chat(f"generate_question('behavioral', '{current_topic}', '{context}')")
            else:
                # Default to contextual question with agent guidance
                question_type = self.shared_state.get("topic_category", "technical")
                return self.agent.chat(f"generate_question('{question_type}', '{current_topic}', '{context}')")
                
        except Exception as e:
            return f"Error generating next question: {str(e)}"
    
    def process_candidate_response(self, response: str, question: str, topic: str = "") -> str:
        """Process candidate response and coordinate with evaluation agent."""
        try:
            # Update shared state with response context
            self.shared_state["latest_response"] = response
            self.shared_state["latest_question"] = question
            
            # The actual evaluation will be handled by the orchestrator's coordination
            return f"Response processed for evaluation: {len(response.split())} words"
            
        except Exception as e:
            return f"Error processing response: {str(e)}"
    
    def chat(self, message: str) -> str:
        """Handle interviewer-level queries and commands."""
        return str(self.agent.chat(message))
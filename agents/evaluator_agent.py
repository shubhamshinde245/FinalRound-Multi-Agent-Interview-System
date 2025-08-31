import os
import re
from typing import Dict, List, Optional, Any, Tuple
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool, FunctionTool
from dotenv import load_dotenv
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import statistics

from core.session_manager import SessionManager


load_dotenv()


@dataclass
class ResponseEvaluation:
    response_id: str
    topic: str
    question_type: str
    response_text: str
    timestamp: datetime
    scores: Dict[str, float]  # technical, communication, depth, relevance, clarity
    feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    overall_score: float
    confidence_level: str  # "low", "medium", "high"
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class CandidateProfile:
    candidate_name: str
    running_scores: Dict[str, List[float]] = None
    topic_performance: Dict[str, Dict[str, float]] = None
    strengths_identified: List[str] = None
    improvement_areas: List[str] = None
    response_patterns: Dict[str, Any] = None
    overall_assessment: Dict[str, float] = None
    evaluation_history: List[ResponseEvaluation] = None
    
    def __post_init__(self):
        if not self.running_scores:
            self.running_scores = {
                "technical_knowledge": [],
                "communication_skills": [],
                "problem_solving": [],
                "depth_of_thinking": [],
                "relevance": [],
                "clarity": []
            }
        if not self.topic_performance:
            self.topic_performance = {}
        if not self.strengths_identified:
            self.strengths_identified = []
        if not self.improvement_areas:
            self.improvement_areas = []
        if not self.response_patterns:
            self.response_patterns = {
                "avg_response_length": 0,
                "technical_keyword_usage": 0,
                "confidence_indicators": 0,
                "question_asking_frequency": 0
            }
        if not self.overall_assessment:
            self.overall_assessment = {
                "technical_competency": 0.0,
                "communication_effectiveness": 0.0,
                "cultural_fit": 0.0,
                "growth_potential": 0.0,
                "overall_recommendation": 0.0
            }
        if not self.evaluation_history:
            self.evaluation_history = []


class EvaluatorAgent:
    def __init__(self, session_manager: SessionManager, shared_state: Dict = None):
        self.session_manager = session_manager
        self.shared_state = shared_state or {}
        self.llm = OpenAI(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.4  # Lower temperature for more consistent evaluations
        )
        
        # Evaluation state
        self.candidate_profile: Optional[CandidateProfile] = None
        self.evaluation_history: List[ResponseEvaluation] = []
        self.current_evaluation_context = {}
        
        # Scoring criteria and weights
        self.scoring_criteria = {
            "technical_knowledge": {
                "weight": 0.25,
                "indicators": ["accuracy", "depth", "best_practices", "problem_solving"],
                "keywords": ["algorithm", "architecture", "optimization", "design_pattern", "scalability"]
            },
            "communication_skills": {
                "weight": 0.20,
                "indicators": ["clarity", "structure", "conciseness", "articulation"],
                "keywords": ["explain", "clarify", "understand", "communicate", "present"]
            },
            "problem_solving": {
                "weight": 0.25,
                "indicators": ["approach", "methodology", "alternatives", "trade_offs"],
                "keywords": ["approach", "solution", "alternative", "trade-off", "consider"]
            },
            "depth_of_thinking": {
                "weight": 0.15,
                "indicators": ["analysis", "reasoning", "implications", "context"],
                "keywords": ["because", "therefore", "however", "consider", "impact"]
            },
            "relevance": {
                "weight": 0.10,
                "indicators": ["on_topic", "applicable", "practical", "job_relevant"],
                "keywords": []  # Context-dependent
            },
            "clarity": {
                "weight": 0.05,
                "indicators": ["coherent", "organized", "understandable", "logical"],
                "keywords": ["first", "second", "then", "finally", "specifically"]
            }
        }
        
        self.agent = self._create_agent()
    
    def _create_agent(self) -> ReActAgent:
        tools = [
            self._create_response_evaluation_tool(),
            self._create_scoring_tool(),
            self._create_pattern_analysis_tool(),
            self._create_feedback_generation_tool(),
            self._create_recommendation_tool()
        ]
        
        system_prompt = """
        You are the Evaluator Agent for a multi-agent interview system. Your role is to:
        
        1. Evaluate candidate responses in real-time across multiple dimensions
        2. Track performance patterns and trends throughout the interview
        3. Generate actionable feedback and insights
        4. Provide recommendations for question difficulty and topic transitions
        5. Create comprehensive candidate assessments
        
        Evaluation dimensions:
        - Technical Knowledge: Accuracy, depth, best practices, problem-solving ability
        - Communication Skills: Clarity, structure, articulation, presentation
        - Problem Solving: Methodology, approach, alternatives consideration
        - Depth of Thinking: Analysis, reasoning, implications understanding
        - Relevance: On-topic responses, practical applicability, job relevance
        - Clarity: Coherence, organization, logical flow
        
        Key principles:
        - Be objective and evidence-based in evaluations
        - Consider context (question difficulty, topic, interview stage)
        - Look for patterns across multiple responses
        - Provide constructive and specific feedback
        - Balance strengths identification with improvement areas
        - Adapt evaluation criteria based on role requirements
        """
        
        return ReActAgent.from_tools(
            tools=tools,
            llm=self.llm,
            system_prompt=system_prompt,
            verbose=True
        )
    
    def _create_response_evaluation_tool(self) -> FunctionTool:
        def evaluate_response(
            response_text: str,
            question: str = "",
            topic: str = "",
            question_type: str = "technical",
            expected_difficulty: str = "medium"
        ) -> str:
            """
            Evaluate a candidate's response across multiple dimensions.
            
            Args:
                response_text: The candidate's response to evaluate
                question: The question that was asked
                topic: Topic area of the question
                question_type: Type of question (technical, behavioral, etc.)
                expected_difficulty: Expected difficulty level
            """
            try:
                # Create evaluation ID
                eval_id = f"eval_{datetime.now().strftime('%H%M%S_%f')}"
                
                # Analyze response characteristics
                response_analysis = self._analyze_response_characteristics(response_text)
                
                # Calculate dimension scores
                scores = {}
                detailed_feedback = {}
                
                for dimension, criteria in self.scoring_criteria.items():
                    score, feedback = self._score_dimension(
                        response_text, question, dimension, criteria, question_type
                    )
                    scores[dimension] = score
                    detailed_feedback[dimension] = feedback
                
                # Calculate overall score
                overall_score = sum(
                    score * self.scoring_criteria[dim]["weight"] 
                    for dim, score in scores.items()
                )
                
                # Determine confidence level
                confidence = self._determine_confidence_level(response_analysis, scores)
                
                # Generate strengths and improvement areas
                strengths = self._identify_strengths(scores, detailed_feedback)
                improvements = self._identify_improvements(scores, detailed_feedback)
                
                # Create evaluation object
                evaluation = ResponseEvaluation(
                    response_id=eval_id,
                    topic=topic,
                    question_type=question_type,
                    response_text=response_text,
                    timestamp=datetime.now(),
                    scores=scores,
                    feedback=self._generate_comprehensive_feedback(scores, detailed_feedback),
                    strengths=strengths,
                    areas_for_improvement=improvements,
                    overall_score=overall_score,
                    confidence_level=confidence
                )
                
                # Update candidate profile
                self._update_candidate_profile(evaluation)
                
                # Store evaluation in session
                if self.session_manager.current_session:
                    self.session_manager.add_response(
                        response_text, 
                        evaluation.to_dict()
                    )
                
                return f"Response evaluated: Overall Score: {overall_score:.1f}/10, Confidence: {confidence}, Strengths: {', '.join(strengths[:2])}, Areas for Improvement: {', '.join(improvements[:2])}"
                
            except Exception as e:
                return f"Error evaluating response: {str(e)}"
        
        return FunctionTool.from_defaults(fn=evaluate_response)
    
    def _create_scoring_tool(self) -> FunctionTool:
        def calculate_running_scores() -> str:
            """Calculate and update running scores for the candidate."""
            try:
                if not self.candidate_profile:
                    return "No candidate profile initialized"
                
                # Calculate running averages
                running_averages = {}
                for dimension, scores in self.candidate_profile.running_scores.items():
                    if scores:
                        running_averages[dimension] = statistics.mean(scores)
                    else:
                        running_averages[dimension] = 0.0
                
                # Update session scores
                if self.session_manager.current_session:
                    score_mapping = {
                        "technical_knowledge": running_averages.get("technical_knowledge", 0),
                        "communication_skills": running_averages.get("communication_skills", 0),
                        "problem_solving": running_averages.get("problem_solving", 0),
                        "overall": statistics.mean(list(running_averages.values())) if running_averages else 0
                    }
                    self.session_manager.update_scores(score_mapping)
                
                # Calculate trends
                trends = self._calculate_performance_trends()
                
                return f"Running scores updated: Technical: {running_averages.get('technical_knowledge', 0):.1f}, Communication: {running_averages.get('communication_skills', 0):.1f}, Problem Solving: {running_averages.get('problem_solving', 0):.1f}, Trends: {trends}"
                
            except Exception as e:
                return f"Error calculating running scores: {str(e)}"
        
        return FunctionTool.from_defaults(fn=calculate_running_scores)
    
    def _create_pattern_analysis_tool(self) -> FunctionTool:
        def analyze_response_patterns() -> str:
            """Analyze patterns in candidate responses."""
            try:
                if not self.candidate_profile or not self.candidate_profile.evaluation_history:
                    return "No evaluation history available"
                
                evaluations = self.candidate_profile.evaluation_history
                
                # Analyze response length patterns
                response_lengths = [len(eval.response_text.split()) for eval in evaluations]
                avg_length = statistics.mean(response_lengths) if response_lengths else 0
                
                # Analyze technical keyword usage
                technical_keywords = []
                for criteria in self.scoring_criteria.values():
                    technical_keywords.extend(criteria.get("keywords", []))
                
                keyword_usage = 0
                total_responses = len(evaluations)
                
                for eval in evaluations:
                    response_lower = eval.response_text.lower()
                    keywords_found = sum(1 for keyword in technical_keywords if keyword in response_lower)
                    keyword_usage += keywords_found
                
                avg_keyword_usage = keyword_usage / max(total_responses, 1)
                
                # Analyze confidence indicators
                confidence_phrases = ["i think", "probably", "maybe", "not sure", "i believe"]
                uncertainty_phrases = ["i don't know", "not familiar", "haven't used"]
                
                confidence_score = 0
                for eval in evaluations:
                    response_lower = eval.response_text.lower()
                    confidence_indicators = sum(1 for phrase in confidence_phrases if phrase in response_lower)
                    uncertainty_indicators = sum(1 for phrase in uncertainty_phrases if phrase in response_lower)
                    confidence_score += max(0, confidence_indicators - uncertainty_indicators * 2)
                
                # Update patterns
                self.candidate_profile.response_patterns.update({
                    "avg_response_length": avg_length,
                    "technical_keyword_usage": avg_keyword_usage,
                    "confidence_indicators": confidence_score / max(total_responses, 1),
                    "question_asking_frequency": self._count_questions_asked(evaluations)
                })
                
                return f"Pattern analysis: Avg length: {avg_length:.1f} words, Technical keywords: {avg_keyword_usage:.1f}/response, Confidence: {confidence_score/max(total_responses, 1):.1f}"
                
            except Exception as e:
                return f"Error analyzing patterns: {str(e)}"
        
        return FunctionTool.from_defaults(fn=analyze_response_patterns)
    
    def _create_feedback_generation_tool(self) -> FunctionTool:
        def generate_detailed_feedback(focus_area: str = "overall") -> str:
            """
            Generate detailed feedback for the candidate.
            
            Args:
                focus_area: Area to focus feedback on ("overall", "technical", "communication", etc.)
            """
            try:
                if not self.candidate_profile:
                    return "No candidate profile available for feedback"
                
                feedback_sections = []
                
                if focus_area == "overall" or focus_area == "strengths":
                    strengths = self._generate_strengths_feedback()
                    feedback_sections.append(f"Strengths: {strengths}")
                
                if focus_area == "overall" or focus_area == "improvements":
                    improvements = self._generate_improvement_feedback()
                    feedback_sections.append(f"Areas for Development: {improvements}")
                
                if focus_area == "overall" or focus_area == "patterns":
                    patterns = self._generate_pattern_feedback()
                    feedback_sections.append(f"Response Patterns: {patterns}")
                
                if focus_area == "overall":
                    recommendations = self._generate_interview_recommendations()
                    feedback_sections.append(f"Interview Recommendations: {recommendations}")
                
                return " | ".join(feedback_sections)
                
            except Exception as e:
                return f"Error generating feedback: {str(e)}"
        
        return FunctionTool.from_defaults(fn=generate_detailed_feedback)
    
    def _create_recommendation_tool(self) -> FunctionTool:
        def get_interview_recommendations() -> str:
            """Get recommendations for interview continuation."""
            try:
                if not self.candidate_profile:
                    return "No candidate profile available for recommendations"
                
                # Analyze current performance
                avg_scores = {}
                for dimension, scores in self.candidate_profile.running_scores.items():
                    avg_scores[dimension] = statistics.mean(scores) if scores else 0
                
                overall_performance = statistics.mean(list(avg_scores.values())) if avg_scores else 0
                
                recommendations = []
                
                # Question difficulty recommendations
                if overall_performance >= 8:
                    recommendations.append("Increase question difficulty - candidate showing strong performance")
                elif overall_performance <= 4:
                    recommendations.append("Consider easier questions - candidate may be struggling")
                else:
                    recommendations.append("Maintain current difficulty level")
                
                # Topic recommendations
                weak_areas = [dim for dim, score in avg_scores.items() if score < 6]
                if weak_areas:
                    recommendations.append(f"Focus more on: {', '.join(weak_areas[:2])}")
                
                strong_areas = [dim for dim, score in avg_scores.items() if score >= 8]
                if strong_areas:
                    recommendations.append(f"Can reduce focus on: {', '.join(strong_areas[:2])}")
                
                # Interview continuation recommendations
                if overall_performance >= 7:
                    recommendations.append("Candidate showing good potential - continue with standard interview")
                elif overall_performance <= 3:
                    recommendations.append("Consider early conclusion - candidate may not meet requirements")
                else:
                    recommendations.append("Continue interview - need more data points")
                
                return " | ".join(recommendations)
                
            except Exception as e:
                return f"Error generating recommendations: {str(e)}"
        
        return FunctionTool.from_defaults(fn=get_interview_recommendations)
    
    def _analyze_response_characteristics(self, response_text: str) -> Dict:
        """Analyze basic characteristics of a response."""
        words = response_text.split()
        sentences = re.split(r'[.!?]+', response_text)
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "has_examples": "example" in response_text.lower() or "for instance" in response_text.lower(),
            "has_technical_terms": len([w for w in words if len(w) > 8]) > 2,
            "question_marks": response_text.count("?")
        }
    
    def _score_dimension(self, response: str, question: str, dimension: str, criteria: Dict, question_type: str) -> Tuple[float, str]:
        """Score a specific dimension of the response."""
        score = 5.0  # Base score
        feedback_points = []
        
        response_lower = response.lower()
        
        # Check for keyword presence
        keywords_found = sum(1 for keyword in criteria.get("keywords", []) if keyword in response_lower)
        if keywords_found > 0:
            score += min(keywords_found * 0.5, 2.0)
            feedback_points.append(f"Used relevant terminology ({keywords_found} keywords)")
        
        # Length-based scoring
        word_count = len(response.split())
        if dimension == "depth_of_thinking":
            if word_count > 100:
                score += 1.0
                feedback_points.append("Comprehensive response showing depth")
            elif word_count < 30:
                score -= 1.0
                feedback_points.append("Response could be more detailed")
        
        elif dimension == "clarity":
            if 50 <= word_count <= 150:
                score += 1.0
                feedback_points.append("Well-balanced response length")
            elif word_count > 200:
                score -= 0.5
                feedback_points.append("Response could be more concise")
        
        # Question type specific scoring
        if question_type == "technical" and dimension == "technical_knowledge":
            # Look for technical indicators
            technical_indicators = ["algorithm", "implement", "optimize", "design", "architecture"]
            if any(indicator in response_lower for indicator in technical_indicators):
                score += 1.0
                feedback_points.append("Demonstrated technical thinking")
        
        elif question_type == "behavioral" and dimension == "communication_skills":
            # Look for STAR format indicators
            star_indicators = ["situation", "task", "action", "result", "when", "what", "how"]
            if sum(1 for indicator in star_indicators if indicator in response_lower) >= 3:
                score += 1.5
                feedback_points.append("Used structured response format")
        
        # Ensure score is within bounds
        score = max(1.0, min(10.0, score))
        feedback = "; ".join(feedback_points) if feedback_points else "Standard response"
        
        return score, feedback
    
    def _determine_confidence_level(self, analysis: Dict, scores: Dict) -> str:
        """Determine confidence level of the evaluation."""
        avg_score = statistics.mean(scores.values())
        word_count = analysis["word_count"]
        
        if avg_score >= 7 and word_count >= 50:
            return "high"
        elif avg_score >= 5 and word_count >= 30:
            return "medium"
        else:
            return "low"
    
    def _identify_strengths(self, scores: Dict, feedback: Dict) -> List[str]:
        """Identify candidate strengths from scores."""
        strengths = []
        for dimension, score in scores.items():
            if score >= 7:
                dimension_name = dimension.replace("_", " ").title()
                strengths.append(dimension_name)
        return strengths[:3]  # Top 3 strengths
    
    def _identify_improvements(self, scores: Dict, feedback: Dict) -> List[str]:
        """Identify areas for improvement from scores."""
        improvements = []
        for dimension, score in scores.items():
            if score < 6:
                dimension_name = dimension.replace("_", " ").title()
                improvements.append(dimension_name)
        return improvements[:3]  # Top 3 improvement areas
    
    def _generate_comprehensive_feedback(self, scores: Dict, detailed_feedback: Dict) -> str:
        """Generate comprehensive feedback summary."""
        avg_score = statistics.mean(scores.values())
        
        if avg_score >= 8:
            overall = "Excellent response demonstrating strong capabilities"
        elif avg_score >= 6:
            overall = "Good response with solid understanding"
        elif avg_score >= 4:
            overall = "Adequate response with room for improvement"
        else:
            overall = "Response needs significant development"
        
        return f"{overall}. Key areas: {'; '.join(list(detailed_feedback.values())[:2])}"
    
    def _update_candidate_profile(self, evaluation: ResponseEvaluation):
        """Update the candidate profile with new evaluation."""
        if not self.candidate_profile:
            candidate_name = self.session_manager.current_session.candidate_name if self.session_manager.current_session else "Unknown"
            self.candidate_profile = CandidateProfile(candidate_name=candidate_name)
        
        # Add scores to running totals
        for dimension, score in evaluation.scores.items():
            self.candidate_profile.running_scores[dimension].append(score)
        
        # Update topic performance
        if evaluation.topic:
            if evaluation.topic not in self.candidate_profile.topic_performance:
                self.candidate_profile.topic_performance[evaluation.topic] = {}
            
            for dimension, score in evaluation.scores.items():
                self.candidate_profile.topic_performance[evaluation.topic][dimension] = score
        
        # Update strengths and improvement areas
        for strength in evaluation.strengths:
            if strength not in self.candidate_profile.strengths_identified:
                self.candidate_profile.strengths_identified.append(strength)
        
        for improvement in evaluation.areas_for_improvement:
            if improvement not in self.candidate_profile.improvement_areas:
                self.candidate_profile.improvement_areas.append(improvement)
        
        # Add to evaluation history
        self.candidate_profile.evaluation_history.append(evaluation)
    
    def _calculate_performance_trends(self) -> str:
        """Calculate performance trends over time."""
        if not self.candidate_profile or len(self.candidate_profile.evaluation_history) < 2:
            return "insufficient_data"
        
        recent_scores = [eval.overall_score for eval in self.candidate_profile.evaluation_history[-3:]]
        earlier_scores = [eval.overall_score for eval in self.candidate_profile.evaluation_history[:-3]]
        
        if not earlier_scores:
            return "improving" if len(recent_scores) > 1 and recent_scores[-1] > recent_scores[0] else "stable"
        
        recent_avg = statistics.mean(recent_scores)
        earlier_avg = statistics.mean(earlier_scores)
        
        if recent_avg > earlier_avg + 0.5:
            return "improving"
        elif recent_avg < earlier_avg - 0.5:
            return "declining"
        else:
            return "stable"
    
    def _count_questions_asked(self, evaluations: List[ResponseEvaluation]) -> float:
        """Count how many questions the candidate asks."""
        total_questions = 0
        for eval in evaluations:
            total_questions += eval.response_text.count("?")
        return total_questions / max(len(evaluations), 1)
    
    def _generate_strengths_feedback(self) -> str:
        """Generate feedback on candidate strengths."""
        if not self.candidate_profile.strengths_identified:
            return "Strengths still being assessed"
        
        top_strengths = list(set(self.candidate_profile.strengths_identified))[:3]
        return f"Demonstrating strong {', '.join(top_strengths).lower()}"
    
    def _generate_improvement_feedback(self) -> str:
        """Generate feedback on improvement areas."""
        if not self.candidate_profile.improvement_areas:
            return "No significant improvement areas identified"
        
        top_improvements = list(set(self.candidate_profile.improvement_areas))[:2]
        return f"Could strengthen {', '.join(top_improvements).lower()}"
    
    def _generate_pattern_feedback(self) -> str:
        """Generate feedback on response patterns."""
        patterns = self.candidate_profile.response_patterns
        feedback_items = []
        
        if patterns["avg_response_length"] > 80:
            feedback_items.append("provides detailed responses")
        elif patterns["avg_response_length"] < 30:
            feedback_items.append("responses could be more detailed")
        
        if patterns["technical_keyword_usage"] > 2:
            feedback_items.append("uses appropriate technical terminology")
        
        if patterns["confidence_indicators"] > 0:
            feedback_items.append("shows confidence in responses")
        
        return "; ".join(feedback_items) if feedback_items else "Standard response patterns"
    
    def _generate_interview_recommendations(self) -> str:
        """Generate recommendations for interview continuation."""
        if not self.candidate_profile:
            return "Continue with standard interview approach"
        
        avg_scores = {}
        for dimension, scores in self.candidate_profile.running_scores.items():
            avg_scores[dimension] = statistics.mean(scores) if scores else 0
        
        overall_avg = statistics.mean(list(avg_scores.values())) if avg_scores else 0
        
        if overall_avg >= 7:
            return "Strong candidate - consider advanced questions"
        elif overall_avg <= 4:
            return "Candidate struggling - consider supportive questioning"
        else:
            return "Continue with current interview approach"
    
    def initialize_evaluation(self, candidate_name: str = None) -> str:
        """Initialize evaluation for a new candidate."""
        try:
            if not candidate_name and self.session_manager.current_session:
                candidate_name = self.session_manager.current_session.candidate_name
            
            self.candidate_profile = CandidateProfile(
                candidate_name=candidate_name or "Unknown Candidate"
            )
            
            return f"Evaluation initialized for {candidate_name}"
            
        except Exception as e:
            return f"Error initializing evaluation: {str(e)}"
    
    def get_current_assessment(self) -> Dict:
        """Get current assessment summary."""
        if not self.candidate_profile:
            return {"error": "No evaluation data available"}
        
        # Calculate current averages
        current_scores = {}
        for dimension, scores in self.candidate_profile.running_scores.items():
            current_scores[dimension] = statistics.mean(scores) if scores else 0
        
        return {
            "overall_score": statistics.mean(list(current_scores.values())) if current_scores else 0,
            "dimension_scores": current_scores,
            "strengths": self.candidate_profile.strengths_identified[:3],
            "improvement_areas": self.candidate_profile.improvement_areas[:3],
            "evaluation_count": len(self.candidate_profile.evaluation_history),
            "performance_trend": self._calculate_performance_trends(),
            "recommendation": self._generate_interview_recommendations()
        }
    
    def chat(self, message: str) -> str:
        """Handle evaluator queries and commands."""
        return str(self.agent.chat(message))
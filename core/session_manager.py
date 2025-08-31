import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading


@dataclass
class InterviewState:
    session_id: str
    candidate_name: str
    job_title: str
    start_time: datetime
    current_topic: str = ""
    questions_asked: List[Dict] = None
    responses: List[Dict] = None
    evaluation_scores: Dict = None
    last_activity: datetime = None
    is_active: bool = True
    interview_phase: str = "introduction"  # introduction, technical, behavioral, conclusion
    # New fields for enhanced multi-agent support
    topic_progression: Dict = None  # Topic flow and coverage tracking
    detailed_evaluations: List[Dict] = None  # Detailed evaluation history from EvaluatorAgent
    agent_coordination_data: Dict = None  # Inter-agent coordination state
    
    def __post_init__(self):
        if self.questions_asked is None:
            self.questions_asked = []
        if self.responses is None:
            self.responses = []
        if self.evaluation_scores is None:
            self.evaluation_scores = {
                "technical_knowledge": 0,
                "communication_skills": 0,
                "problem_solving": 0,
                "depth_of_thinking": 0,
                "relevance": 0,
                "clarity": 0,
                "overall": 0
            }
        if self.last_activity is None:
            self.last_activity = datetime.now()
        # Initialize new fields
        if self.topic_progression is None:
            self.topic_progression = {
                "current_sequence": [],
                "completed_topics": [],
                "current_index": 0,
                "coverage_score": 0.0,
                "time_allocation": {}
            }
        if self.detailed_evaluations is None:
            self.detailed_evaluations = []
        if self.agent_coordination_data is None:
            self.agent_coordination_data = {
                "orchestrator_state": {},
                "topic_manager_state": {},
                "interviewer_state": {},
                "evaluator_state": {}
            }


class SessionManager:
    def __init__(self, session_dir: str = "data/sessions"):
        self.session_dir = session_dir
        self.current_session: Optional[InterviewState] = None
        self.session_timeout = 900  # 15 minutes in seconds
        self.auto_save_interval = 30  # 30 seconds
        self.is_auto_saving = False
        self._setup_directories()
        self._start_auto_save_thread()
    
    def _setup_directories(self):
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs("data/transcripts", exist_ok=True)
        os.makedirs("data/evaluations", exist_ok=True)
    
    def create_session(self, candidate_name: str, job_title: str) -> str:
        session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = InterviewState(
            session_id=session_id,
            candidate_name=candidate_name,
            job_title=job_title,
            start_time=datetime.now()
        )
        
        self.save_session()
        return session_id
    
    def load_session(self, session_id: str) -> bool:
        session_file = os.path.join(self.session_dir, f"{session_id}.json")
        
        if not os.path.exists(session_file):
            return False
        
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            # Convert datetime strings back to datetime objects
            data['start_time'] = datetime.fromisoformat(data['start_time'])
            data['last_activity'] = datetime.fromisoformat(data['last_activity'])
            
            self.current_session = InterviewState(**data)
            return True
        except Exception as e:
            print(f"Error loading session: {e}")
            return False
    
    def save_session(self):
        if not self.current_session:
            return
        
        session_data = asdict(self.current_session)
        
        # Convert datetime objects to strings for JSON serialization
        session_data['start_time'] = self.current_session.start_time.isoformat()
        session_data['last_activity'] = self.current_session.last_activity.isoformat()
        
        session_file = os.path.join(self.session_dir, f"{self.current_session.session_id}.json")
        
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def update_activity(self):
        if self.current_session:
            self.current_session.last_activity = datetime.now()
    
    def add_question(self, question: str, question_type: str = "general"):
        if not self.current_session:
            return
        
        question_data = {
            "question": question,
            "type": question_type,
            "timestamp": datetime.now().isoformat(),
            "topic": self.current_session.current_topic
        }
        
        self.current_session.questions_asked.append(question_data)
        self.update_activity()
    
    def add_response(self, response: str, evaluation: Dict = None):
        if not self.current_session:
            return
        
        response_data = {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "evaluation": evaluation or {}
        }
        
        self.current_session.responses.append(response_data)
        self.update_activity()
    
    def update_scores(self, scores: Dict):
        if not self.current_session:
            return
        
        self.current_session.evaluation_scores.update(scores)
        self.update_activity()
    
    def set_topic(self, topic: str):
        if self.current_session:
            self.current_session.current_topic = topic
            self.update_activity()
    
    def set_phase(self, phase: str):
        if self.current_session:
            self.current_session.interview_phase = phase
            self.update_activity()
    
    def update_topic_progression(self, progression_data: Dict):
        """Update topic progression data from TopicManagerAgent."""
        if self.current_session:
            self.current_session.topic_progression.update(progression_data)
            self.update_activity()
    
    def add_detailed_evaluation(self, evaluation_data: Dict):
        """Add detailed evaluation from EvaluatorAgent."""
        if self.current_session:
            # Add timestamp if not present
            if 'timestamp' not in evaluation_data:
                evaluation_data['timestamp'] = datetime.now().isoformat()
            
            self.current_session.detailed_evaluations.append(evaluation_data)
            self.update_activity()
    
    def update_agent_state(self, agent_name: str, state_data: Dict):
        """Update state data for a specific agent."""
        if self.current_session:
            agent_key = f"{agent_name}_state"
            if agent_key in self.current_session.agent_coordination_data:
                self.current_session.agent_coordination_data[agent_key].update(state_data)
            else:
                self.current_session.agent_coordination_data[agent_key] = state_data
            self.update_activity()
    
    def get_agent_state(self, agent_name: str) -> Dict:
        """Get state data for a specific agent."""
        if self.current_session:
            agent_key = f"{agent_name}_state"
            return self.current_session.agent_coordination_data.get(agent_key, {})
        return {}
    
    def get_topic_progression(self) -> Dict:
        """Get current topic progression data."""
        if self.current_session:
            return self.current_session.topic_progression
        return {}
    
    def get_detailed_evaluations(self) -> List[Dict]:
        """Get all detailed evaluations."""
        if self.current_session:
            return self.current_session.detailed_evaluations
        return []
    
    def check_timeout(self) -> bool:
        if not self.current_session or not self.current_session.is_active:
            return False
        
        time_elapsed = (datetime.now() - self.current_session.last_activity).total_seconds()
        return time_elapsed > self.session_timeout
    
    def get_time_remaining(self) -> int:
        if not self.current_session:
            return 0
        
        time_elapsed = (datetime.now() - self.current_session.last_activity).total_seconds()
        return max(0, self.session_timeout - int(time_elapsed))
    
    def end_session(self):
        if not self.current_session:
            return
        
        self.current_session.is_active = False
        self.save_session()
        
        # Generate final outputs
        self._generate_transcript()
        self._generate_evaluation()
    
    def _generate_transcript(self):
        if not self.current_session:
            return
        
        transcript_data = {
            "session_id": self.current_session.session_id,
            "candidate_name": self.current_session.candidate_name,
            "job_title": self.current_session.job_title,
            "start_time": self.current_session.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "conversation": []
        }
        
        # Merge questions and responses chronologically
        all_interactions = []
        
        for q in self.current_session.questions_asked:
            all_interactions.append({
                "type": "question",
                "timestamp": q["timestamp"],
                "content": q["question"],
                "topic": q.get("topic", ""),
                "question_type": q.get("type", "general")
            })
        
        for r in self.current_session.responses:
            all_interactions.append({
                "type": "response",
                "timestamp": r["timestamp"],
                "content": r["response"]
            })
        
        # Sort by timestamp
        all_interactions.sort(key=lambda x: x["timestamp"])
        transcript_data["conversation"] = all_interactions
        
        # Save transcript
        transcript_file = f"data/transcripts/{self.current_session.session_id}_transcript.json"
        with open(transcript_file, 'w') as f:
            json.dump(transcript_data, f, indent=2)
    
    def _generate_evaluation(self):
        if not self.current_session:
            return
        
        evaluation_data = {
            "session_id": self.current_session.session_id,
            "candidate_name": self.current_session.candidate_name,
            "job_title": self.current_session.job_title,
            "evaluation_date": datetime.now().isoformat(),
            "scores": self.current_session.evaluation_scores,
            "total_questions": len(self.current_session.questions_asked),
            "total_responses": len(self.current_session.responses),
            "interview_duration": str(datetime.now() - self.current_session.start_time),
            "phases_completed": self.current_session.interview_phase,
            "detailed_feedback": self._generate_detailed_feedback(),
            # Enhanced evaluation data
            "topic_coverage": self.current_session.topic_progression,
            "detailed_evaluations": self.current_session.detailed_evaluations,
            "agent_insights": self._generate_agent_insights(),
            "performance_trends": self._analyze_performance_trends()
        }
        
        # Save evaluation
        evaluation_file = f"data/evaluations/{self.current_session.session_id}_evaluation.json"
        with open(evaluation_file, 'w') as f:
            json.dump(evaluation_data, f, indent=2)
    
    def _generate_detailed_feedback(self) -> Dict:
        if not self.current_session:
            return {}
        
        scores = self.current_session.evaluation_scores
        
        feedback = {
            "strengths": [],
            "areas_for_improvement": [],
            "overall_assessment": "",
            "recommendation": ""
        }
        
        # Generate feedback based on scores
        if scores.get("technical_knowledge", 0) >= 7:
            feedback["strengths"].append("Strong technical knowledge and expertise")
        elif scores.get("technical_knowledge", 0) < 5:
            feedback["areas_for_improvement"].append("Technical knowledge needs improvement")
        
        if scores.get("communication_skills", 0) >= 7:
            feedback["strengths"].append("Excellent communication and articulation")
        elif scores.get("communication_skills", 0) < 5:
            feedback["areas_for_improvement"].append("Communication skills could be enhanced")
        
        if scores.get("problem_solving", 0) >= 7:
            feedback["strengths"].append("Strong problem-solving approach")
        elif scores.get("problem_solving", 0) < 5:
            feedback["areas_for_improvement"].append("Problem-solving methodology needs work")
        
        overall_score = scores.get("overall", 0)
        if overall_score >= 8:
            feedback["overall_assessment"] = "Excellent candidate with strong performance"
            feedback["recommendation"] = "Highly recommend for the position"
        elif overall_score >= 6:
            feedback["overall_assessment"] = "Good candidate with solid performance"
            feedback["recommendation"] = "Recommend for the position"
        elif overall_score >= 4:
            feedback["overall_assessment"] = "Average candidate with mixed performance"
            feedback["recommendation"] = "Consider with reservations"
        else:
            feedback["overall_assessment"] = "Below average performance"
            feedback["recommendation"] = "Do not recommend for the position"
        
        return feedback
    
    def _generate_agent_insights(self) -> Dict:
        """Generate insights from all agents for the final evaluation."""
        if not self.current_session:
            return {}
        
        insights = {
            "topic_management": {
                "coverage_achieved": self.current_session.topic_progression.get("coverage_score", 0),
                "topics_completed": len(self.current_session.topic_progression.get("completed_topics", [])),
                "time_utilization": "efficient" if self.current_session.topic_progression.get("coverage_score", 0) > 0.7 else "needs_improvement"
            },
            "evaluation_consistency": {
                "total_evaluations": len(self.current_session.detailed_evaluations),
                "evaluation_depth": "comprehensive" if len(self.current_session.detailed_evaluations) > 3 else "limited"
            }
        }
        
        return insights
    
    def _analyze_performance_trends(self) -> Dict:
        """Analyze candidate performance trends over the course of the interview."""
        if not self.current_session or not self.current_session.detailed_evaluations:
            return {}
        
        evaluations = self.current_session.detailed_evaluations
        
        if len(evaluations) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trend in overall scores
        scores = [eval.get("overall_score", 0) for eval in evaluations if "overall_score" in eval]
        
        if len(scores) < 2:
            return {"trend": "insufficient_score_data"}
        
        # Simple trend analysis
        first_half_avg = sum(scores[:len(scores)//2]) / max(len(scores)//2, 1)
        second_half_avg = sum(scores[len(scores)//2:]) / max(len(scores) - len(scores)//2, 1)
        
        trend = "stable"
        if second_half_avg > first_half_avg + 0.5:
            trend = "improving"
        elif second_half_avg < first_half_avg - 0.5:
            trend = "declining"
        
        return {
            "trend": trend,
            "first_half_average": first_half_avg,
            "second_half_average": second_half_avg,
            "total_evaluations": len(scores)
        }
    
    def _start_auto_save_thread(self):
        def auto_save():
            while True:
                time.sleep(self.auto_save_interval)
                if self.current_session and self.current_session.is_active:
                    self.save_session()
        
        if not self.is_auto_saving:
            self.is_auto_saving = True
            auto_save_thread = threading.Thread(target=auto_save, daemon=True)
            auto_save_thread.start()
    
    def get_session_summary(self) -> Dict:
        if not self.current_session:
            return {}
        
        return {
            "session_id": self.current_session.session_id,
            "candidate_name": self.current_session.candidate_name,
            "job_title": self.current_session.job_title,
            "current_phase": self.current_session.interview_phase,
            "current_topic": self.current_session.current_topic,
            "questions_asked": len(self.current_session.questions_asked),
            "time_remaining": self.get_time_remaining(),
            "is_active": self.current_session.is_active,
            "scores": self.current_session.evaluation_scores,
            # Enhanced summary data
            "topic_progression": {
                "completed_topics": len(self.current_session.topic_progression.get("completed_topics", [])),
                "coverage_score": self.current_session.topic_progression.get("coverage_score", 0)
            },
            "evaluation_summary": {
                "detailed_evaluations_count": len(self.current_session.detailed_evaluations),
                "latest_evaluation": self.current_session.detailed_evaluations[-1] if self.current_session.detailed_evaluations else None
            }
        }
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
                "overall": 0
            }
        if self.last_activity is None:
            self.last_activity = datetime.now()


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
            "detailed_feedback": self._generate_detailed_feedback()
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
            "scores": self.current_session.evaluation_scores
        }
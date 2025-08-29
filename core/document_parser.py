from typing import Dict, List, Optional
from dataclasses import dataclass
import re


@dataclass
class JobRequirement:
    category: str
    requirement: str
    importance: str = "medium"


@dataclass
class CandidateSkill:
    skill: str
    experience_level: str = "unknown"
    context: str = ""


@dataclass
class ParsedJobDescription:
    title: str
    company: str
    requirements: List[JobRequirement]
    responsibilities: List[str]
    raw_text: str


@dataclass
class ParsedResume:
    name: str
    title: str
    experience_years: str
    skills: List[CandidateSkill]
    experience: List[str]
    education: str
    raw_text: str


class DocumentParser:
    def __init__(self):
        self.skill_patterns = [
            r"Skills?:\s*([^\n]+)",
            r"Technical Skills:\s*([^\n]+)",
            r"Technologies?:\s*([^\n]+)"
        ]
        
    def parse_job_description(self, file_path: str) -> ParsedJobDescription:
        with open(file_path, 'r') as file:
            content = file.read()
        
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        title = ""
        company = ""
        requirements = []
        responsibilities = []
        
        current_section = None
        
        for line in lines:
            if not title and any(keyword in line.lower() for keyword in ['engineer', 'developer', 'manager', 'analyst']):
                title = line
            elif line.startswith('Company:'):
                company = line.replace('Company:', '').strip()
            elif line.lower().startswith('requirements'):
                current_section = 'requirements'
                continue
            elif line.lower().startswith('responsibilities'):
                current_section = 'responsibilities'
                continue
            elif line.startswith('- ') and current_section == 'requirements':
                req_text = line[2:]
                category = self._categorize_requirement(req_text)
                importance = self._assess_importance(req_text)
                requirements.append(JobRequirement(category, req_text, importance))
            elif line.startswith('- ') and current_section == 'responsibilities':
                responsibilities.append(line[2:])
        
        return ParsedJobDescription(title, company, requirements, responsibilities, content)
    
    def parse_resume(self, file_path: str) -> ParsedResume:
        with open(file_path, 'r') as file:
            content = file.read()
        
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        name = ""
        title = ""
        experience_years = ""
        skills = []
        experience = []
        education = ""
        
        for i, line in enumerate(lines):
            if i == 0 and not any(char.isdigit() for char in line):
                name = line
            elif i == 1 and any(keyword in line.lower() for keyword in ['engineer', 'developer', 'manager', 'analyst']):
                title = line
            elif 'years' in line.lower() and 'experience' in line.lower():
                experience_years = line
            elif any(pattern in line for pattern in ['Skills:', 'Technologies:']):
                skills_text = line.split(':', 1)[1] if ':' in line else line
                skill_list = [s.strip() for s in re.split(r'[,;]', skills_text) if s.strip()]
                skills = [CandidateSkill(skill) for skill in skill_list]
            elif line.startswith('- ') and any(keyword in line for keyword in ['Corp', 'Company', ':']):
                experience.append(line[2:])
            elif 'Education:' in line or 'University' in line or 'College' in line:
                education = line
        
        return ParsedResume(name, title, experience_years, skills, experience, education, content)
    
    def _categorize_requirement(self, requirement: str) -> str:
        req_lower = requirement.lower()
        
        if any(tech in req_lower for tech in ['python', 'java', 'javascript', 'c++', 'sql']):
            return "technical_skill"
        elif any(keyword in req_lower for keyword in ['years', 'experience']):
            return "experience"
        elif any(keyword in req_lower for keyword in ['aws', 'cloud', 'docker', 'kubernetes']):
            return "infrastructure"
        elif any(keyword in req_lower for keyword in ['design', 'architecture', 'system']):
            return "system_design"
        elif any(keyword in req_lower for keyword in ['leadership', 'mentor', 'manage']):
            return "leadership"
        else:
            return "general"
    
    def _assess_importance(self, requirement: str) -> str:
        req_lower = requirement.lower()
        
        if any(keyword in req_lower for keyword in ['required', 'must', 'essential']):
            return "high"
        elif any(keyword in req_lower for keyword in ['preferred', 'nice', 'bonus']):
            return "low"
        else:
            return "medium"
    
    def get_matching_skills(self, job_desc: ParsedJobDescription, resume: ParsedResume) -> Dict[str, any]:
        job_skills = set()
        resume_skills = set()
        
        for req in job_desc.requirements:
            if req.category == "technical_skill":
                job_skills.add(req.requirement.lower())
        
        for skill in resume.skills:
            resume_skills.add(skill.skill.lower())
        
        matching = job_skills.intersection(resume_skills)
        missing = job_skills - resume_skills
        additional = resume_skills - job_skills
        
        return {
            "matching_skills": list(matching),
            "missing_skills": list(missing),
            "additional_skills": list(additional),
            "match_percentage": len(matching) / len(job_skills) * 100 if job_skills else 0
        }
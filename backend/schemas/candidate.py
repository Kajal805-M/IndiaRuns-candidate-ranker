from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

class CandidateBase(BaseModel):
    candidate_id: str
    profile: Dict[str, Any]
    career_history: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[Dict[str, Any]]
    certifications: Optional[List[Dict[str, Any]]] = []
    languages: Optional[List[Dict[str, Any]]] = []
    redrob_signals: Dict[str, Any]

class CandidateCreate(CandidateBase):
    pass

class CandidateSchema(BaseModel):
    id: int
    candidate_id: str
    anonymized_name: str
    headline: str
    years_of_experience: float
    current_title: str
    current_company: str
    is_honeypot: bool
    github_activity_score: float
    recruiter_response_rate: float
    
    model_config = ConfigDict(from_attributes=True)

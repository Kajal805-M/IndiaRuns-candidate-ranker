from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from db.session import Base

class CandidateModel(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(String, unique=True, index=True)
    
    # Core Profile
    anonymized_name = Column(String)
    headline = Column(String)
    summary = Column(String)
    location = Column(String)
    country = Column(String)
    years_of_experience = Column(Float)
    current_title = Column(String)
    current_company = Column(String)
    
    # JSON stores for nested dynamic data
    career_history = Column(JSON)
    education = Column(JSON)
    skills = Column(JSON)
    certifications = Column(JSON)
    languages = Column(JSON)
    redrob_signals = Column(JSON)
    
    # Derived / Preprocessed features for fast structured filtering
    is_honeypot = Column(Boolean, default=False)
    is_title_chaser = Column(Boolean, default=False)
    consulting_only = Column(Boolean, default=False)
    
    # Redrob Signals flattened for fast querying without JSON parsing
    github_activity_score = Column(Float, default=-1.0)
    recruiter_response_rate = Column(Float, default=0.0)
    last_active_date = Column(String)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.session import get_db
from models.candidate import CandidateModel
from services.explainability_engine import generate_match_report, get_gemini_model

router = APIRouter()

DEFAULT_JD = "Senior AI Engineer. Production experience with embeddings, vector databases like FAISS, Pinecone. Python programming. Evaluation frameworks like NDCG. Needs product company experience."

class CopilotQuery(BaseModel):
    query: str

@router.post("/explain/{candidate_id}")
def explain_candidate(candidate_id: str, db: Session = Depends(get_db)):
    cand = db.query(CandidateModel).filter(CandidateModel.candidate_id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    cand_dict = {
        "title": cand.current_title,
        "experience": cand.years_of_experience,
        "history": cand.career_history
    }
    
    report = generate_match_report(cand_dict, DEFAULT_JD)
    return report

@router.post("/copilot")
def copilot_query(payload: CopilotQuery):
    model = get_gemini_model()
    
    prompt = f"You are an AI Recruiter Copilot. The recruiter asks: {payload.query}. Provide a concise, professional answer."
    
    try:
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API Error: {str(e)}")

@router.post("/interview/{candidate_id}")
def generate_interview_questions(candidate_id: str, db: Session = Depends(get_db)):
    cand = db.query(CandidateModel).filter(CandidateModel.candidate_id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    model = get_gemini_model()
    prompt = f"Based on this candidate ({cand.current_title}, {cand.years_of_experience} yrs exp) and the JD: {DEFAULT_JD}, generate 3 highly targeted interview questions to probe their technical weaknesses."
    
    try:
        response = model.generate_content(prompt)
        return {"questions": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API Error: {str(e)}")


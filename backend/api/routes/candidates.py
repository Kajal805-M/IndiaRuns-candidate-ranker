from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.ranking_engine import rank_candidates
from models.candidate import CandidateModel

router = APIRouter()

# Default JD loaded from the txt file ideally. For now, a quick summary string.
DEFAULT_JD = "Senior AI Engineer. Production experience with embeddings, vector databases like FAISS, Pinecone. Python programming. Evaluation frameworks like NDCG. Needs product company experience."

@router.get("/")
def get_ranked_candidates(db: Session = Depends(get_db)):
    results = rank_candidates(db, DEFAULT_JD, top_n=100)
    
    formatted = []
    for idx, res in enumerate(results):
        cand = res["candidate"]
        formatted.append({
            "rank": idx + 1,
            "candidate_id": cand.candidate_id,
            "anonymized_name": cand.anonymized_name,
            "current_title": cand.current_title,
            "years_of_experience": cand.years_of_experience,
            "score": round(res["score"], 4),
            "github_activity_score": cand.github_activity_score,
            "recruiter_response_rate": cand.recruiter_response_rate
        })
    return formatted

@router.get("/{candidate_id}")
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    cand = db.query(CandidateModel).filter(CandidateModel.candidate_id == candidate_id).first()
    if not cand:
        return {"error": "Candidate not found"}
    return cand

from sqlalchemy.orm import Session
from models.candidate import CandidateModel
from services.faiss_service import faiss_service
from services.job_engine import job_engine
from services.signal_engine import apply_behavioral_signals

def rank_candidates(db: Session, jd_text: str, top_n: int = 100):
    jd_embedding = job_engine.embed_job_description(jd_text)
    
    # 1. Semantic Retrieval (Top 2000)
    faiss_results = faiss_service.search(jd_embedding, k=2000)
    
    # 2. Re-ranking with behavioral signals
    ranked_results = []
    
    for res in faiss_results:
        cand_id = res["candidate_id"]
        base_score = res["semantic_score"]
        
        # Load from DB (Using simple query loop for PoC clarity; can be bulk optimized)
        candidate = db.query(CandidateModel).filter(CandidateModel.candidate_id == cand_id).first()
        if not candidate:
            continue
            
        final_score = apply_behavioral_signals(base_score, candidate)
        
        ranked_results.append({
            "candidate": candidate,
            "score": final_score
        })
        
    # Sort by descending score
    ranked_results.sort(key=lambda x: x["score"], reverse=True)
    
    return ranked_results[:top_n]

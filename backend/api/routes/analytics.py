from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import get_db
from models.candidate import CandidateModel

router = APIRouter()

@router.get("/")
def get_analytics(db: Session = Depends(get_db)):
    """
    Returns aggregated analytics for the React Dashboard.
    Uses limited query samples for fast PoC load times.
    """
    total_cands = db.query(CandidateModel).count()
    honeypots = db.query(CandidateModel).filter(CandidateModel.is_honeypot == True).count()
    
    # 1. Experience Distribution (Sampling 2000 for fast agg)
    exp_dist = db.query(CandidateModel.years_of_experience).limit(2000).all()
    exp_buckets = {"0-2 yrs": 0, "3-5 yrs": 0, "6-10 yrs": 0, "11+ yrs": 0}
    
    total_exp = 0
    for (exp,) in exp_dist:
        total_exp += exp
        if exp <= 2: exp_buckets["0-2 yrs"] += 1
        elif exp <= 5: exp_buckets["3-5 yrs"] += 1
        elif exp <= 10: exp_buckets["6-10 yrs"] += 1
        else: exp_buckets["11+ yrs"] += 1
        
    avg_exp = round(total_exp / max(len(exp_dist), 1), 1)

    # 2. GitHub Activity Distribution
    gh_dist = db.query(CandidateModel.github_activity_score).limit(2000).all()
    gh_buckets = {"No GitHub": 0, "Low (0-20)": 0, "Medium (21-50)": 0, "High (50+)": 0}
    for (gh,) in gh_dist:
        if gh < 0: gh_buckets["No GitHub"] += 1
        elif gh <= 20: gh_buckets["Low (0-20)"] += 1
        elif gh <= 50: gh_buckets["Medium (21-50)"] += 1
        else: gh_buckets["High (50+)"] += 1

    # 3. Recruiter Response Distribution
    rr_dist = db.query(CandidateModel.recruiter_response_rate).limit(2000).all()
    rr_buckets = {"Ghost (0%)": 0, "Low (<30%)": 0, "Medium (30-70%)": 0, "High (>70%)": 0}
    for (rr,) in rr_dist:
        if rr == 0: rr_buckets["Ghost (0%)"] += 1
        elif rr < 0.3: rr_buckets["Low (<30%)"] += 1
        elif rr <= 0.7: rr_buckets["Medium (30-70%)"] += 1
        else: rr_buckets["High (>70%)"] += 1

    # 4. Match Score Mock Distribution for UI (Normal distribution curve)
    match_curve = [
        {"range": "0-20%", "count": 15},
        {"range": "21-40%", "count": 45},
        {"range": "41-60%", "count": 120},
        {"range": "61-80%", "count": 210},
        {"range": "81-100%", "count": 55},
    ]
        
    return {
        "summary": {
            "total_candidates": total_cands,
            "avg_experience": avg_exp,
            "honeypots_caught": honeypots,
            "active_pool": total_cands - honeypots
        },
        "experience": [{"name": k, "value": v} for k, v in exp_buckets.items()],
        "github": [{"name": k, "value": v} for k, v in gh_buckets.items()],
        "response": [{"name": k, "value": v} for k, v in rr_buckets.items()],
        "matchCurve": match_curve
    }

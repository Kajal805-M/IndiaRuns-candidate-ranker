def apply_behavioral_signals(base_score: float, candidate) -> float:
    """
    Applies behavioral modifiers to the base semantic score.
    """
    score = base_score
    
    # Positive signals
    if candidate.github_activity_score > 50:
        score += 0.05
    elif candidate.github_activity_score > 0:
        score += 0.02
        
    if candidate.recruiter_response_rate > 0.7:
        score += 0.05
    elif candidate.recruiter_response_rate < 0.2:
        score -= 0.1
        
    # Traps & Penalties
    if candidate.is_honeypot:
        score = 0.0
        
    if candidate.consulting_only:
        score -= 0.15 # Per JD, no pure consulting without product experience
        
    if candidate.is_title_chaser:
        score -= 0.10
        
    # Notice period penalty
    notice = candidate.redrob_signals.get("notice_period_days", 0) if isinstance(candidate.redrob_signals, dict) else 0
    if notice > 60:
        score -= 0.1
    elif notice > 30:
        score -= 0.05
        
    return max(0.0, min(1.0, score))

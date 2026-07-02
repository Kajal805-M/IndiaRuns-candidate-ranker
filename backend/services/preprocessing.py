def format_candidate_for_embedding(candidate) -> str:
    """
    Constructs a textual narrative of the candidate's career.
    We purposely omit raw skill lists to avoid keyword-stuffing traps.
    """
    text = f"{candidate.current_title} with {candidate.years_of_experience} years of experience.\n"
    if candidate.headline:
        text += f"Headline: {candidate.headline}\n"
    if candidate.summary:
        text += f"Summary: {candidate.summary}\n"
    
    if candidate.career_history:
        text += "Career History:\n"
        for job in candidate.career_history:
            text += f"- {job.get('title', '')} at {job.get('company', '')}: {job.get('description', '')}\n"
            
    return text

from typing import Dict, Any, List

def clean_missing_values(data: Any) -> Any:
    """
    Recursively navigates the candidate JSON schema to convert None 
    or empty string variants to appropriate defaults, preventing DB null constraint errors.
    """
    if isinstance(data, dict):
        cleaned_dict = {}
        for k, v in data.items():
            if v is None or v in ["", "null", "None", "N/A"]:
                if k in ["years_of_experience", "github_activity_score", "recruiter_response_rate"]:
                    cleaned_dict[k] = 0.0
                elif isinstance(v, list):
                    cleaned_dict[k] = []
                elif isinstance(v, dict):
                    cleaned_dict[k] = {}
                else:
                    cleaned_dict[k] = ""
            elif isinstance(v, (dict, list)):
                cleaned_dict[k] = clean_missing_values(v)
            else:
                cleaned_dict[k] = v
        return cleaned_dict
    elif isinstance(data, list):
        return [clean_missing_values(item) for item in data]
    return data

def normalize_fields(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes textual fields (casing/stripping) and mathematically coerces metrics.
    """
    profile = candidate.get("profile", {})
    
    # Normalize Title
    title = profile.get("current_title", "")
    profile["current_title"] = title.strip().title() if title else "Unknown Title"
    
    # Normalize Experience safely
    try:
        exp = float(profile.get("years_of_experience", 0.0))
    except (ValueError, TypeError):
        exp = 0.0
    profile["years_of_experience"] = max(0.0, exp)
    
    # Clean Redrob Signals
    signals = candidate.get("redrob_signals", {})
    if not isinstance(signals, dict):
        signals = {}
        
    try:
        gh = float(signals.get("github_activity_score", -1))
    except (ValueError, TypeError):
        gh = -1.0
    signals["github_activity_score"] = gh
    
    try:
        rr = float(signals.get("recruiter_response_rate", 0.0))
    except (ValueError, TypeError):
        rr = 0.0
    signals["recruiter_response_rate"] = rr
    
    candidate["profile"] = profile
    candidate["redrob_signals"] = signals
    return candidate

def validate_candidate(candidate_raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master preprocessing utility. Chains cleaning and normalization.
    """
    cleaned = clean_missing_values(candidate_raw)
    normalized = normalize_fields(cleaned)
    return normalized

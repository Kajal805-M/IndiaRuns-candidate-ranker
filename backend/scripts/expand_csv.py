import json
import pandas as pd

csv_path = "/Users/kamal/India_runs/platform/NeuralNetwork.csv"
jsonl_path = "/Users/kamal/India_runs/dataset/India_runs_data_and_ai_challenge/candidates.jsonl"
out_path = "/Users/kamal/India_runs/platform/backend/data/top_100_candidates.json"

# Read top 100 IDs and scores
df = pd.read_csv(csv_path)
top_ids = {row['candidate_id']: float(row['score']) for _, row in df.iterrows()}

print(f"Loaded {len(top_ids)} IDs from CSV.")

# Find them in the giant JSONL
expanded = {}
with open(jsonl_path, 'r') as f:
    for line in f:
        if not line.strip(): continue
        try:
            cand = json.loads(line)
            cid = cand.get('candidate_id')
            if cid in top_ids:
                # Format to match what the frontend expects
                profile = cand.get("profile", {})
                signals = cand.get("redrob_signals", {})
                
                formatted = {
                    "candidate_id": cid,
                    "anonymized_name": profile.get("anonymized_name", ""),
                    "current_title": profile.get("current_title", ""),
                    "years_of_experience": profile.get("years_of_experience", 0.0),
                    "github_activity_score": signals.get("github_activity_score", -1.0),
                    "recruiter_response_rate": signals.get("recruiter_response_rate", 0.0),
                    
                    # Also include the extra fields for candidate detail page
                    "summary": profile.get("summary", ""),
                    "location": profile.get("location", ""),
                    "country": profile.get("country", ""),
                    "career_history": cand.get("career_history", []),
                    "education": cand.get("education", []),
                    "skills": cand.get("skills", []),
                    "certifications": cand.get("certifications", []),
                    "languages": cand.get("languages", []),
                    "redrob_signals": signals
                }
                expanded[cid] = formatted
                
                if len(expanded) == len(top_ids):
                    break # Found them all
        except Exception as e:
            print("Error parsing line", e)
            pass

print(f"Found {len(expanded)} candidates in JSONL.")

# Build the final ordered list
final_list = []
for cid in df['candidate_id']:
    if cid in expanded:
        final_list.append({
            "candidate": expanded[cid],
            "score": top_ids[cid]
        })

with open(out_path, 'w') as f:
    json.dump(final_list, f)

print(f"Wrote {len(final_list)} complete records to {out_path}.")

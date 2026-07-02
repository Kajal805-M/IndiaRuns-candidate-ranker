import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.candidate import CandidateModel
from services.preprocessing import format_candidate_for_embedding
import json

def generate_embeddings():
    print("Loading model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    db: Session = SessionLocal()
    candidates = db.query(CandidateModel).all()
    
    if not candidates:
        print("No candidates found in DB. Run load_data.py first.")
        return

    print(f"Generating embeddings for {len(candidates)} candidates...")
    
    texts = [format_candidate_for_embedding(c) for c in candidates]
    candidate_ids = [c.candidate_id for c in candidates]
    
    # Batch encode
    embeddings = model.encode(texts, batch_size=128, show_progress_bar=True)
    
    os.makedirs("data", exist_ok=True)
    np.save("data/embeddings.npy", embeddings)
    
    with open("data/candidate_ids.json", "w") as f:
        json.dump(candidate_ids, f)
        
    print("Saved embeddings and IDs to data/")
    db.close()

if __name__ == "__main__":
    generate_embeddings()

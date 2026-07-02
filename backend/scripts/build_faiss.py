import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import faiss
import numpy as np

def build_index():
    if not os.path.exists("data/embeddings.npy"):
        print("Embeddings not found. Run generate_embeddings.py first.")
        return
        
    print("Loading embeddings...")
    embeddings = np.load("data/embeddings.npy").astype('float32')
    
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    
    print(f"Building FAISS index for {len(embeddings)} vectors of dimension {d}...")
    index.add(embeddings)
    
    faiss.write_index(index, "data/faiss.index")
    print("Saved index to data/faiss.index")

if __name__ == "__main__":
    build_index()

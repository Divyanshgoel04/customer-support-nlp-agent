import os
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def build_knowledge_base():
    # Load the full dataset
    df = pd.read_csv(os.path.join(BASE_DIR, "data", "raw", "bitext_support.csv"))
    
    print(f"Loaded {len(df)} entries")
    
    # Drop duplicates on response to avoid redundant embeddings
    df_unique = df.drop_duplicates(subset=['response']).reset_index(drop=True)
    print(f"Unique responses: {len(df_unique)}")
    
    # Initialize ChromaDB
    chroma_path = os.path.join(BASE_DIR, "data", "knowledge_base")
    client = chromadb.PersistentClient(path=chroma_path)
    
    # Delete collection if it already exists (clean rebuild)
    try:
        client.delete_collection("support_responses")
        print("Deleted existing collection")
    except:
        pass
    
    collection = client.create_collection(
        name="support_responses",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Load sentence transformer for embeddings
    print("Loading embedding model...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Embed in batches
    batch_size = 500
    total = len(df_unique)
    
    for i in range(0, total, batch_size):
        batch = df_unique.iloc[i:i+batch_size]
        
        responses = batch['response'].tolist()
        intents = batch['intent'].tolist()
        categories = batch['category'].tolist()
        instructions = batch['instruction'].tolist()
        
        embeddings = embedder.encode(responses, show_progress_bar=False).tolist()
        
        ids = [f"resp_{i+j}" for j in range(len(batch))]
        
        metadatas = [
            {
                "intent": intents[j],
                "category": categories[j],
                "instruction": instructions[j]
            }
            for j in range(len(batch))
        ]
        
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=responses,
            metadatas=metadatas
        )
        
        print(f"Embedded {min(i+batch_size, total)}/{total} responses")
    
    print(f"\nKnowledge base built successfully!")
    print(f"Total entries in ChromaDB: {collection.count()}")
    return collection

if __name__ == "__main__":
    build_knowledge_base()
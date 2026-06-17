import os
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load once at module level
_client = None
_collection = None
_embedder = None

def get_collection():
    global _client, _collection
    if _collection is None:
        chroma_path = os.path.join(BASE_DIR, "data", "knowledge_base")
        _client = chromadb.PersistentClient(path=chroma_path)
        _collection = _client.get_collection("support_responses")
    return _collection

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedder

def search_knowledge_base(query: str, intent: str = None, n_results: int = 3):
    """
    Search for relevant responses given a customer query.
    Optionally filter by intent for more precise results.
    """
    collection = get_collection()
    embedder = get_embedder()
    
    query_embedding = embedder.encode(query).tolist()
    
    # Build filter if intent provided
    where_filter = {"intent": intent} if intent else None
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )
    
    output = []
    for i in range(len(results['documents'][0])):
        output.append({
            "response": results['documents'][0][i],
            "intent": results['metadatas'][0][i]['intent'],
            "category": results['metadatas'][0][i]['category'],
            "similarity_score": 1 - results['distances'][0][i]
        })
    
    return output

def search_by_intent(intent: str, n_results: int = 1):
    """
    Get the best response for a specific intent directly.
    Used by agent when intent is known with high confidence.
    """
    collection = get_collection()
    embedder = get_embedder()
    
    # Use intent name as query to find most representative response
    query_embedding = embedder.encode(intent.replace('_', ' ')).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"intent": intent},
        include=["documents", "metadatas"]
    )
    
    if results['documents'][0]:
        return {
            "response": results['documents'][0][0],
            "intent": results['metadatas'][0][0]['intent'],
            "category": results['metadatas'][0][0]['category']
        }
    return None
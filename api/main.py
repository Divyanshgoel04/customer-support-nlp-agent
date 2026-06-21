import os
import sys
import json
from datetime import datetime
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from src.agent.agent import handle_ticket
from src.agent.router import route_ticket
from src.database.queries import get_order_details, get_customer_details, log_ticket

# Initialize FastAPI app
app = FastAPI(
    title="Customer Support NLP Agent API",
    description="AI-powered customer support ticket classification and automated response system",
    version="1.0.0"
)

# Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load classifier once at startup
classifier = None
tokenizer_obj = None
label2id = None
id2label = None

@app.on_event("startup")
async def load_classifier():
    global classifier, tokenizer_obj, label2id, id2label
    try:
        import torch
        from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast
        
        model_path = os.path.join(BASE_DIR, "models", "distilbert_intent_model")
        
        classifier = DistilBertForSequenceClassification.from_pretrained(model_path)
        tokenizer_obj = DistilBertTokenizerFast.from_pretrained(model_path)
        classifier.eval()
        
        with open(os.path.join(model_path, "label2id.json")) as f:
            label2id = json.load(f)
        with open(os.path.join(model_path, "id2label.json")) as f:
            id2label = json.load(f)
        
        print("DistilBERT classifier loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load DistilBERT model: {e}")
        print("Falling back to SVM classifier")


def classify_with_distilbert(text: str) -> dict:
    """Classify text using DistilBERT model."""
    import torch
    import re
    
    # Light cleaning
    clean_text = re.sub(r'\{\{.*?\}\}', '', text).strip()
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    inputs = tokenizer_obj(
        clean_text,
        return_tensors="pt",
        truncation=True,
        max_length=64,
        padding=True
    )
    
    with torch.no_grad():
        outputs = classifier(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=1)
        confidence, predicted_id = torch.max(probabilities, dim=1)
    
    intent = id2label[str(predicted_id.item())]
    confidence_score = confidence.item()
    
    return {
        "intent": intent,
        "confidence": confidence_score
    }


def classify_with_svm(text: str) -> dict:
    """Fallback SVM classifier."""
    import joblib
    import re
    import spacy
    from nltk.corpus import stopwords
    
    nlp = spacy.load("en_core_web_sm")
    stop_words = set(stopwords.words('english'))
    
    vectorizer = joblib.load(os.path.join(BASE_DIR, "models", "tfidf_vectorizer.pkl"))
    svm = joblib.load(os.path.join(BASE_DIR, "models", "svm_tfidf.pkl"))
    
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    doc = nlp(text)
    tokens = [t.lemma_ for t in doc if t.text not in stop_words and len(t.text) > 1]
    clean = " ".join(tokens)
    
    X = vectorizer.transform([clean])
    intent = svm.predict(X)[0]
    
    decision = svm.decision_function(X)
    confidence = float(max(decision[0]) / sum(abs(d) for d in decision[0]))
    
    return {"intent": intent, "confidence": min(abs(confidence), 0.99)}


# ─── Request/Response Models ───────────────────────────────────────────────────

class ClassifyRequest(BaseModel):
    text: str

class ClassifyResponse(BaseModel):
    intent: str
    confidence: float
    category: str

class TicketRequest(BaseModel):
    text: str
    customer_id: Optional[str] = None
    order_id: Optional[str] = None

class TicketResponse(BaseModel):
    intent: str
    confidence: float
    routing_action: str
    escalated: bool
    response: str
    timestamp: str

class OrderResponse(BaseModel):
    order_id: str
    product_name: str
    order_date: str
    status: str
    estimated_delivery: Optional[str]
    amount: float
    refund_status: str

# Intent to category mapping
INTENT_CATEGORY_MAP = {
    "cancel_order": "ORDER", "change_order": "ORDER",
    "track_order": "ORDER", "place_order": "ORDER",
    "track_refund": "REFUND", "get_refund": "REFUND",
    "check_refund_policy": "REFUND",
    "change_shipping_address": "SHIPPING",
    "set_up_shipping_address": "SHIPPING",
    "delivery_options": "DELIVERY", "delivery_period": "DELIVERY",
    "check_invoice": "INVOICE", "get_invoice": "INVOICE",
    "check_payment_methods": "PAYMENT", "payment_issue": "PAYMENT",
    "check_cancellation_fee": "CANCEL",
    "complaint": "FEEDBACK", "review": "FEEDBACK",
    "contact_customer_service": "CONTACT",
    "contact_human_agent": "CONTACT",
    "create_account": "ACCOUNT", "delete_account": "ACCOUNT",
    "edit_account": "ACCOUNT", "switch_account": "ACCOUNT",
    "recover_password": "ACCOUNT", "registration_problems": "ACCOUNT",
    "newsletter_subscription": "SUBSCRIPTION"
}

# ─── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Customer Support NLP Agent API",
        "version": "1.0.0",
        "endpoints": [
            "POST /classify",
            "POST /agent/handle",
            "GET /orders/{order_id}",
            "GET /customers/{customer_id}",
            "GET /health",
            "GET /metrics"
        ]
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "classifier_loaded": classifier is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/classify", response_model=ClassifyResponse)
def classify_ticket(request: ClassifyRequest):
    """
    Classify a customer support ticket into an intent.
    Uses DistilBERT if available, falls back to SVM.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        if classifier is not None:
            result = classify_with_distilbert(request.text)
        else:
            result = classify_with_svm(request.text)
        
        category = INTENT_CATEGORY_MAP.get(result['intent'], "GENERAL")
        
        return ClassifyResponse(
            intent=result['intent'],
            confidence=result['confidence'],
            category=category
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/handle", response_model=TicketResponse)
def handle_ticket_endpoint(request: TicketRequest):
    """
    Full pipeline: classify ticket → route → agent handles → return response.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Step 1 - Classify
        if classifier is not None:
            classification = classify_with_distilbert(request.text)
        else:
            classification = classify_with_svm(request.text)
        
        intent = classification['intent']
        confidence = classification['confidence']
        
        # Step 2 - Handle with agent
        result = handle_ticket(
            ticket_text=request.text,
            intent=intent,
            confidence=confidence,
            customer_id=request.customer_id,
            order_id=request.order_id
        )
        
        # Step 3 - Log to database
        try:
            log_ticket({
                "ticket_id": f"T{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "customer_id": request.customer_id,
                "order_id": request.order_id,
                "raw_text": request.text,
                "intent": intent,
                "category": INTENT_CATEGORY_MAP.get(intent, "GENERAL"),
                "confidence_score": confidence,
                "agent_response": result.get('response', ''),
                "escalated": result.get('escalated', False),
                "resolved": not result.get('escalated', False),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as log_error:
            print(f"Logging error (non-critical): {log_error}")
        
        return TicketResponse(
            intent=intent,
            confidence=confidence,
            routing_action=result.get('routing_action', 'unknown'),
            escalated=result.get('escalated', False),
            response=result.get('response', ''),
            timestamp=result.get('timestamp', datetime.now().isoformat())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    """Get order details by order ID."""
    result = get_order_details(order_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return OrderResponse(**result)


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    """Get customer details by customer ID."""
    result = get_customer_details(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return result


@app.get("/metrics")
def get_metrics():
    """Get system metrics for dashboard."""
    try:
        from src.database.models import get_session, Ticket
        session = get_session()
        
        total_tickets = session.query(Ticket).count()
        escalated = session.query(Ticket).filter(Ticket.escalated == True).count()
        resolved = session.query(Ticket).filter(Ticket.resolved == True).count()
        
        # Intent distribution
        from sqlalchemy import func
        intent_counts = session.query(
            Ticket.intent,
            func.count(Ticket.intent)
        ).group_by(Ticket.intent).all()
        
        session.close()
        
        return {
            "total_tickets": total_tickets,
            "escalated": escalated,
            "resolved": resolved,
            "auto_resolved": resolved,
            "escalation_rate": round(escalated / total_tickets * 100, 2) if total_tickets > 0 else 0,
            "intent_distribution": {intent: count for intent, count in intent_counts},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "total_tickets": 0,
            "escalated": 0,
            "resolved": 0,
            "auto_resolved": 0,
            "escalation_rate": 0,
            "intent_distribution": {},
            "timestamp": datetime.now().isoformat(),
            "note": "No tickets processed yet"
        }
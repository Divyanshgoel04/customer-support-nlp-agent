import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.agent.agent import handle_ticket
from src.agent.router import route_ticket

print("="*60)
print("Testing Router")
print("="*60)

# Test routing logic (no API calls)
test_cases = [
    ("cancel_order", 0.95),
    ("complaint", 0.91),
    ("check_refund_policy", 0.88),
    ("track_order", 0.72),  # low confidence
    ("get_refund", 0.96),
]

for intent, confidence in test_cases:
    result = route_ticket(intent, confidence)
    print(f"Intent: {intent:30s} Confidence: {confidence} → {result['action']}")

print("\n" + "="*60)
print("Testing Full Agent Pipeline")
print("="*60)

# Test 1 - Simple policy question (no DB needed)
print("\nTest 1: Policy question")
result = handle_ticket(
    ticket_text="What is your refund policy?",
    intent="check_refund_policy",
    confidence=0.97
)
print(f"Action: {result['routing_action']}")
print(f"Response: {result['response'][:300]}")

print("\n" + "-"*60)

# Test 2 - Order lookup
print("\nTest 2: Order tracking")
result = handle_ticket(
    ticket_text="Where is my order ORD00001? It hasn't arrived yet.",
    intent="track_order",
    confidence=0.94,
    customer_id="C0001",
    order_id="ORD00001"
)
print(f"Action: {result['routing_action']}")
print(f"Escalated: {result['escalated']}")
print(f"Response: {result['response'][:400]}")

print("\n" + "-"*60)

# Test 3 - Complaint (should escalate)
print("\nTest 3: Complaint - should escalate to human")
result = handle_ticket(
    ticket_text="This is absolutely terrible service I want to speak to a manager NOW",
    intent="complaint",
    confidence=0.93
)
print(f"Action: {result['routing_action']}")
print(f"Escalated: {result['escalated']}")
print(f"Response: {result['response']}")

print("\n" + "-"*60)

# Test 4 - Refund request
print("\nTest 4: Refund request")
result = handle_ticket(
    ticket_text="I want a refund for my order ORD00001",
    intent="get_refund",
    confidence=0.96,
    customer_id="C0001",
    order_id="ORD00001"
)
print(f"Action: {result['routing_action']}")
print(f"Escalated: {result['escalated']}")
print(f"Response: {result['response'][:400]}")
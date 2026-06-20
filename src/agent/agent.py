import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent

from src.agent.tools import (
    lookup_order,
    lookup_customer,
    get_order_history,
    search_policy,
    get_response_template,
    check_refund_eligibility,
    escalate_to_human
)
from src.agent.prompts import SYSTEM_PROMPT
from src.agent.router import route_ticket

TOOLS = [
    lookup_order,
    lookup_customer,
    get_order_history,
    search_policy,
    get_response_template,
    check_refund_eligibility,
    escalate_to_human
]

from langchain_groq import ChatGroq

def create_agent():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=1000
    )
    
    agent = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT
    )
    
    return agent


def handle_ticket(ticket_text: str, intent: str, confidence: float,
                  customer_id: str = None, order_id: str = None) -> dict:
    """
    Main entry point for handling a customer ticket.
    """
    
    # Step 1 — Route the ticket
    routing = route_ticket(intent, confidence)
    action = routing['action']
    
    result = {
        'ticket_text': ticket_text,
        'intent': intent,
        'confidence': confidence,
        'routing_action': action,
        'routing_reason': routing['reason'],
        'escalated': action == 'human',
        'response': None,
        'timestamp': datetime.now().isoformat()
    }
    
    # Step 2 — If routing to human, return immediately
    if action == 'human':
        result['response'] = (
            f"Thank you for contacting us. Your request has been forwarded "
            f"to one of our human agents who will assist you shortly. "
            f"Reason: {routing['reason']}"
        )
        return result
    
    # Step 3 — Build context for agent
    context_parts = [f"Customer ticket: {ticket_text}"]
    context_parts.append(f"Detected intent: {intent}")
    
    if customer_id:
        context_parts.append(f"Customer ID: {customer_id}")
    if order_id:
        context_parts.append(f"Order ID mentioned: {order_id}")
    
    context = "\n".join(context_parts)
    
    # Step 4 — Run agent
    try:
        agent = create_agent()
        
        response = agent.invoke({
            "messages": [{"role": "user", "content": context}]
        })
        
        # Extract final message from response
        final_message = response["messages"][-1].content
        result['response'] = final_message
        
    except Exception as e:
        result['response'] = (
            "We apologize for the inconvenience. Your request is being "
            "forwarded to a human agent for assistance."
        )
        result['escalated'] = True
        result['error'] = str(e)
        print(f"Agent error: {e}")
    
    return result
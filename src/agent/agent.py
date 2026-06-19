import os
import sys
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage

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

# All tools available to the agent
TOOLS = [
    lookup_order,
    lookup_customer,
    get_order_history,
    search_policy,
    get_response_template,
    check_refund_eligibility,
    escalate_to_human
]

def create_agent():
    """Create and return the LangChain agent executor."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=1000
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    agent = create_openai_tools_agent(llm, TOOLS, prompt)
    
    executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        max_iterations=6,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return executor


def handle_ticket(ticket_text: str, intent: str, confidence: float, 
                  customer_id: str = None, order_id: str = None) -> dict:
    """
    Main entry point for handling a customer ticket.
    
    Args:
        ticket_text: Raw customer message
        intent: Predicted intent from classifier
        confidence: Classifier confidence score
        customer_id: Optional customer ID if known
        order_id: Optional order ID if mentioned
    
    Returns:
        dict with response, action_taken, escalated, tools_used
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
        agent_executor = create_agent()
        response = agent_executor.invoke({"input": context})
        result['response'] = response['output']
        
    except Exception as e:
        # If agent fails, escalate to human
        result['response'] = (
            "We apologize for the inconvenience. Your request is being "
            "forwarded to a human agent for assistance."
        )
        result['escalated'] = True
        result['error'] = str(e)
    
    return result
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv()

# Intents that are safe for full automation
SIMPLE_INTENTS = {
    'check_refund_policy',
    'check_cancellation_fee', 
    'check_payment_methods',
    'delivery_options',
    'delivery_period',
    'newsletter_subscription',
    'contact_customer_service',
    'review',
    'place_order'
}

# Intents that need DB lookups but are still automatable
DB_INTENTS = {
    'cancel_order',
    'change_order',
    'track_order',
    'track_refund',
    'get_refund',
    'check_invoice',
    'get_invoice',
    'change_shipping_address',
    'set_up_shipping_address',
    'payment_issue'
}

# Intents that should go to human
SENSITIVE_INTENTS = {
    'complaint',
    'contact_human_agent'
}

# Account intents - need account verification
ACCOUNT_INTENTS = {
    'create_account',
    'delete_account',
    'edit_account',
    'switch_account',
    'recover_password',
    'registration_problems'
}

CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.85))

def route_ticket(intent: str, confidence: float) -> dict:
    """
    Decide how to handle a ticket based on intent and confidence.
    
    Returns:
        dict with 'action' and 'reason'
        action: 'agent_simple', 'agent_db', 'agent_account', 'human'
    """
    # Low confidence always goes to human
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            'action': 'human',
            'reason': f'Low confidence score: {confidence:.2f} (threshold: {CONFIDENCE_THRESHOLD})'
        }
    
    if intent in SENSITIVE_INTENTS:
        return {
            'action': 'human',
            'reason': f'Sensitive intent: {intent}'
        }
    
    if intent in SIMPLE_INTENTS:
        return {
            'action': 'agent_simple',
            'reason': f'Simple policy question: {intent}'
        }
    
    if intent in DB_INTENTS:
        return {
            'action': 'agent_db',
            'reason': f'Requires database lookup: {intent}'
        }
    
    if intent in ACCOUNT_INTENTS:
        return {
            'action': 'agent_account',
            'reason': f'Account management: {intent}'
        }
    
    # Unknown intent - escalate
    return {
        'action': 'human',
        'reason': f'Unknown intent: {intent}'
    }
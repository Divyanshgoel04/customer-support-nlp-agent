import os
import sys
import json
from datetime import datetime

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from src.database.queries import (
    get_order_details,
    get_customer_details,
    get_customer_orders,
    log_ticket
)
from src.knowledge_base.search import search_knowledge_base, search_by_intent
from langchain.tools import tool


@tool
def lookup_order(order_id: str) -> str:
    """
    Look up order details by order ID.
    Use this when customer mentions an order number or asks about order status.
    Input: order ID string (e.g. 'ORD00001')
    """
    result = get_order_details(order_id)
    if not result:
        return f"No order found with ID {order_id}. Please verify the order number."
    
    return (
        f"Order {result['order_id']}:\n"
        f"  Product: {result['product_name']}\n"
        f"  Order Date: {result['order_date']}\n"
        f"  Status: {result['status']}\n"
        f"  Estimated Delivery: {result['estimated_delivery']}\n"
        f"  Amount: ${result['amount']}\n"
        f"  Refund Status: {result['refund_status']}"
    )


@tool
def lookup_customer(customer_id: str) -> str:
    """
    Look up customer account details by customer ID.
    Use this to verify customer identity and account status.
    Input: customer ID string (e.g. 'C0001')
    """
    result = get_customer_details(customer_id)
    if not result:
        return f"No customer found with ID {customer_id}."
    
    return (
        f"Customer {result['customer_id']}:\n"
        f"  Name: {result['name']}\n"
        f"  Email: {result['email']}\n"
        f"  Account Status: {result['account_status']}"
    )


@tool
def get_order_history(customer_id: str) -> str:
    """
    Get all orders for a customer.
    Use this when customer asks about their purchase history or 
    when you need to find an order but don't have the order ID.
    Input: customer ID string (e.g. 'C0001')
    """
    orders = get_customer_orders(customer_id)
    if not orders:
        return f"No orders found for customer {customer_id}."
    
    result = f"Orders for customer {customer_id}:\n"
    for o in orders:
        result += (
            f"  - {o['order_id']}: {o['product_name']} | "
            f"{o['order_date']} | {o['status']} | ${o['amount']}\n"
        )
    return result


@tool
def search_policy(query: str) -> str:
    """
    Search the knowledge base for relevant policy information and response templates.
    Use this to find how to respond to specific customer issues.
    Input: a description of the customer's issue or intent
    """
    results = search_knowledge_base(query, n_results=2)
    if not results:
        return "No relevant policy information found."
    
    output = "Relevant response templates found:\n\n"
    for i, r in enumerate(results, 1):
        output += f"Template {i} (Intent: {r['intent']}, Score: {r['similarity_score']:.2f}):\n"
        output += f"{r['response'][:300]}...\n\n"
    
    return output


@tool
def get_response_template(intent: str) -> str:
    """
    Get the best response template for a specific intent.
    Use this when you know exactly what the customer wants.
    Input: intent name (e.g. 'cancel_order', 'track_refund', 'get_refund')
    Valid intents: cancel_order, change_order, change_shipping_address,
    check_cancellation_fee, check_invoice, check_payment_methods,
    check_refund_policy, complaint, contact_customer_service,
    contact_human_agent, create_account, delete_account,
    delivery_options, delivery_period, edit_account, get_invoice,
    get_refund, newsletter_subscription, payment_issue, place_order,
    recover_password, registration_problems, review,
    set_up_shipping_address, switch_account, track_order, track_refund
    """
    result = search_by_intent(intent)
    if not result:
        return f"No template found for intent '{intent}'."
    
    return (
        f"Response template for '{intent}':\n"
        f"{result['response']}"
    )


@tool
def escalate_to_human(reason: str) -> str:
    """
    Escalate the ticket to a human agent.
    Use this when:
    - The issue is too complex for automated handling
    - Customer is very frustrated or angry
    - The intent involves legal, fraud, or sensitive matters
    - You cannot find the required information
    Input: reason for escalation
    """
    return (
        f"ESCALATED TO HUMAN AGENT\n"
        f"Reason: {reason}\n"
        f"The customer will be connected to a human agent shortly.\n"
        f"Estimated wait time: 5-10 minutes."
    )


@tool  
def check_refund_eligibility(order_id: str) -> str:
    """
    Check if an order is eligible for a refund based on its status and date.
    Use this when customer asks for a refund.
    Input: order ID string
    """
    result = get_order_details(order_id)
    if not result:
        return f"Cannot check refund eligibility - order {order_id} not found."
    
    status = result['status']
    refund_status = result['refund_status']
    
    if refund_status == 'completed':
        return f"Order {order_id} has already been refunded."
    
    if refund_status == 'approved':
        return f"Refund for order {order_id} is already approved and being processed."
    
    if status == 'Cancelled':
        return f"Order {order_id} is already cancelled. Refund will be processed within 5-7 business days."
    
    if status == 'Delivered':
        return (
            f"Order {order_id} was delivered. "
            f"Eligible for refund within 30 days of delivery. "
            f"Customer needs to return the item first."
        )
    
    if status in ['Processing', 'Shipped']:
        return (
            f"Order {order_id} is currently {status}. "
            f"Can be cancelled and refunded. "
            f"Full refund will be issued within 3-5 business days."
        )
    
    return f"Order {order_id} status: {status}. Please contact support for refund options."
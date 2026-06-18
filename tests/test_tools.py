import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.agent.tools import (
    lookup_order,
    lookup_customer,
    get_order_history,
    search_policy,
    get_response_template,
    escalate_to_human,
    check_refund_eligibility
)

print("="*50)
print("Testing Agent Tools")
print("="*50)

# Test 1
print("\n1. lookup_order:")
print(lookup_order.invoke("ORD00001"))

# Test 2
print("\n2. lookup_customer:")
print(lookup_customer.invoke("C0001"))

# Test 3
print("\n3. get_order_history:")
print(get_order_history.invoke("C0001"))

# Test 4
print("\n4. search_policy:")
print(search_policy.invoke("customer wants to cancel their order"))

# Test 5
print("\n5. get_response_template:")
print(get_response_template.invoke("cancel_order"))

# Test 6
print("\n6. check_refund_eligibility:")
print(check_refund_eligibility.invoke("ORD00001"))

# Test 7
print("\n7. escalate_to_human:")
print(escalate_to_human.invoke("Customer is extremely frustrated and requesting manager"))

print("\n" + "="*50)
print("All tools tested successfully!")
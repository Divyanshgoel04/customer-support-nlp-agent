import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import Customer, Order, Ticket, get_session, create_tables
import random
from datetime import datetime, timedelta
import uuid

# Products from the Bitext dataset's domain
PRODUCTS = [
    "GoPro Hero", "LG Smart TV", "Dell XPS", "Microsoft Office",
    "Autodesk AutoCAD", "Apple iPhone", "Samsung Galaxy",
    "Sony PlayStation", "Amazon Echo", "Google Pixel",
    "MacBook Pro", "iPad Air", "Nintendo Switch", "Fitbit Charge",
    "Bose Headphones"
]

STATUSES = ["Processing", "Shipped", "Delivered", "Cancelled"]

def random_date(start_days_ago=90, end_days_ago=1):
    days = random.randint(end_days_ago, start_days_ago)
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

def seed_customers(session, n=100):
    first_names = ["James", "Mary", "John", "Patricia", "Robert",
                   "Jennifer", "Michael", "Linda", "William", "Barbara",
                   "Priya", "Rahul", "Aisha", "Carlos", "Emma"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones",
                  "Garcia", "Miller", "Davis", "Wilson", "Taylor",
                  "Sharma", "Patel", "Khan", "Lopez", "Chen"]
    
    customers = []
    for i in range(n):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        customer = Customer(
            customer_id=f"C{str(i+1).zfill(4)}",
            name=name,
            email=f"user{i+1}@example.com",
            account_status=random.choice(["active", "active", "active", "suspended"]),
            created_date=random_date(365, 90)
        )
        customers.append(customer)
    
    session.add_all(customers)
    session.commit()
    print(f"Seeded {n} customers")
    return customers

def seed_orders(session, customers, n=200):
    orders = []
    for i in range(n):
        customer = random.choice(customers)
        order_date = random_date(60, 1)
        status = random.choice(STATUSES)
        
        order = Order(
            order_id=f"ORD{str(i+1).zfill(5)}",
            customer_id=customer.customer_id,
            product_name=random.choice(PRODUCTS),
            order_date=order_date,
            status=status,
            estimated_delivery=random_date(10, 1),
            actual_delivery=random_date(5, 1) if status == "Delivered" else None,
            amount=round(random.uniform(29.99, 1299.99), 2),
            refund_status=random.choice(["none", "none", "none", "requested", "approved"])
        )
        orders.append(order)
    
    session.add_all(orders)
    session.commit()
    print(f"Seeded {n} orders")
    return orders

if __name__ == "__main__":
    create_tables()
    session = get_session()
    customers = seed_customers(session, n=100)
    orders = seed_orders(session, customers, n=200)
    print("Database seeded successfully!")
    session.close()
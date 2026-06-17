from models import Customer, Order, Ticket, get_session

def get_order_details(order_id: str):
    session = get_session()
    try:
        order = session.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return None
        return {
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "product_name": order.product_name,
            "order_date": order.order_date,
            "status": order.status,
            "estimated_delivery": order.estimated_delivery,
            "amount": order.amount,
            "refund_status": order.refund_status
        }
    finally:
        session.close()

def get_customer_details(customer_id: str):
    session = get_session()
    try:
        customer = session.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()
        if not customer:
            return None
        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "email": customer.email,
            "account_status": customer.account_status
        }
    finally:
        session.close()

def get_customer_orders(customer_id: str):
    session = get_session()
    try:
        orders = session.query(Order).filter(
            Order.customer_id == customer_id
        ).all()
        return [
            {
                "order_id": o.order_id,
                "product_name": o.product_name,
                "order_date": o.order_date,
                "status": o.status,
                "amount": o.amount
            }
            for o in orders
        ]
    finally:
        session.close()

def log_ticket(ticket_data: dict):
    session = get_session()
    try:
        ticket = Ticket(**ticket_data)
        session.add(ticket)
        session.commit()
        return ticket.ticket_id
    finally:
        session.close()
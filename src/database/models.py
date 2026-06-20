from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    customer_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    account_status = Column(String, default='active')  # active/suspended/closed
    created_date = Column(String)

class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    order_date = Column(String, nullable=False)
    status = Column(String, nullable=False)  # Processing/Shipped/Delivered/Cancelled
    estimated_delivery = Column(String)
    actual_delivery = Column(String)
    amount = Column(Float)
    refund_status = Column(String, default='none')  # none/requested/approved/completed

class Ticket(Base):
    __tablename__ = 'tickets'
    
    ticket_id = Column(String, primary_key=True)
    customer_id = Column(String)
    order_id = Column(String)
    raw_text = Column(Text)
    intent = Column(String)
    category = Column(String)
    confidence_score = Column(Float)
    agent_response = Column(Text)
    escalated = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)
    timestamp = Column(String)

def get_engine():
    # Load .env from project root
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    load_dotenv(env_path)
    database_url = os.getenv('DATABASE_URL')
    return create_engine(database_url)

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Tables created successfully")
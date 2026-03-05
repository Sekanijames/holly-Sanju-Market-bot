from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    referred_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    balance = Column(Float, default=0.0)
    referral_count = Column(Integer, default=0)
    referral_commission = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    referrals = relationship("User", remote_side=[referred_by])
    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    service_name = Column(String, nullable=False)
    service_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")

class AdminConfig(Base):
    __tablename__ = 'admin_config'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, nullable=False)
    channel_username = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    flutterwave_secret = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Referral(Base):
    __tablename__ = 'referrals'
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    referred_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    payment_made = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
Base.metadata.create_all(engine)

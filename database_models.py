from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
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
    virtual_numbers = relationship("VirtualNumber", back_populates="user")

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

class VirtualNumber(Base):
    """Store purchased virtual numbers"""
    __tablename__ = 'virtual_numbers'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    service_name = Column(String, nullable=False)  # WhatsApp, Instagram, etc.
    service_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="virtual_numbers")
    otps = relationship("OTP", back_populates="virtual_number", cascade="all, delete-orphan")

class OTP(Base):
    """Store OTPs for virtual numbers"""
    __tablename__ = 'otps'
    
    id = Column(Integer, primary_key=True)
    virtual_number_id = Column(Integer, ForeignKey('virtual_numbers.id'), nullable=False)
    otp_code = Column(String(6), nullable=False)
    status = Column(String, default="pending")  # pending, used, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    virtual_number = relationship("VirtualNumber", back_populates="otps")

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

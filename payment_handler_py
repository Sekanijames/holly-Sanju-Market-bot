import requests
from config import BITRAHQ_API_KEY, BITRAHQ_API_URL
from database_models import Session, User, Order, Referral
from datetime import datetime

class PaymentHandler:
    def __init__(self):
        self.session = Session()
        self.api_key = BITRAHQ_API_KEY
        self.api_url = BITRAHQ_API_URL
    
    def get_services(self):
        """Fetch available services from BitRaHQ API"""
        try:
            params = {"api_key": self.api_key}
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching services: {e}")
            return None
    
    def purchase_service(self, user_id, service_id, quantity):
        """Purchase a virtual number service"""
        try:
            user = self.session.query(User).filter_by(telegram_id=user_id).first()
            if not user:
                return {"status": "error", "message": "User not found"}
            
            # Get service details
            services = self.get_services()
            service = next((s for s in services.get("data", []) if s["id"] == service_id), None)
            
            if not service:
                return {"status": "error", "message": "Service not found"}
            
            price = float(service["price"]) * quantity
            
            # Check balance (you'll implement actual payment later)
            if user.balance < price:
                return {"status": "error", "message": f"Insufficient balance. Need ${price}, have ${user.balance}"}
            
            # Create order
            order = Order(
                user_id=user.id,
                service_name=service["name"],
                service_id=service_id,
                quantity=quantity,
                price=price,
                status="pending"
            )
            self.session.add(order)
            self.session.commit()
            
            # Update balance
            user.balance -= price
            self.session.commit()
            
            return {
                "status": "success",
                "message": f"Order created successfully",
                "order_id": order.id,
                "remaining_balance": user.balance
            }
        except Exception as e:
            print(f"Error purchasing service: {e}")
            return {"status": "error", "message": str(e)}
    
    def process_referral_payment(self, user_id):
        """Handle referral commission after user's first payment"""
        try:
            user = self.session.query(User).filter_by(telegram_id=user_id).first()
            if not user or not user.referred_by:
                return False
            
            # Find referrer
            referrer = self.session.query(User).filter_by(id=user.referred_by).first()
            if not referrer:
                return False
            
            # Increment referral count
            referrer.referral_count += 1
            
            # Update referral record
            referral = self.session.query(Referral).filter_by(
                referrer_id=referrer.id,
                referred_user_id=user.id
            ).first()
            
            if referral:
                referral.payment_made = True
            
            # Check if referrer has reached 10 referrals
            if referrer.referral_count % 10 == 0:
                # Calculate commission from 10 referrals (you'll calculate actual amount)
                commission = 5.0  # Placeholder, calculate based on actual payments
                referrer.referral_commission += commission
                self.session.commit()
                return True
            
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error processing referral payment: {e}")
            return False
    
    def update_api_key(self, new_api_key):
        """Update BitRaHQ API key"""
        try:
            self.api_key = new_api_key
            # You can also update in database
            return True
        except Exception as e:
            print(f"Error updating API key: {e}")
            return False

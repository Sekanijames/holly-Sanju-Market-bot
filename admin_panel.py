from database_models import Session, User, AdminConfig, Order
from config import ADMIN_CHAT_ID
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from datetime import datetime

class AdminPanel:
    def __init__(self):
        self.session = Session()
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return user_id == ADMIN_CHAT_ID
    
    def set_channel_username(self, channel_username):
        """Set the channel username that users must follow"""
        try:
            config = self.session.query(AdminConfig).first()
            if not config:
                config = AdminConfig(admin_id=ADMIN_CHAT_ID, channel_username=channel_username)
                self.session.add(config)
            else:
                config.channel_username = channel_username
            
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error setting channel: {e}")
            return False
    
    def set_api_key(self, api_key):
        """Update BitRaHQ API key"""
        try:
            config = self.session.query(AdminConfig).first()
            if not config:
                config = AdminConfig(admin_id=ADMIN_CHAT_ID, api_key=api_key)
                self.session.add(config)
            else:
                config.api_key = api_key
            
            config.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error setting API key: {e}")
            return False
    
    def set_payment_details(self, method, details):
        """Update payment method details"""
        try:
            config = self.session.query(AdminConfig).first()
            if not config:
                config = AdminConfig(admin_id=ADMIN_CHAT_ID, payment_method=method)
                self.session.add(config)
            else:
                config.payment_method = method
            
            if method == "flutterwave":
                config.flutterwave_secret = details
            
            config.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error setting payment details: {e}")
            return False
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        try:
            total_users = self.session.query(User).count()
            verified_users = self.session.query(User).filter_by(is_verified=True).count()
            total_orders = self.session.query(Order).count()
            pending_orders = self.session.query(Order).filter_by(status="pending").count()
            
            return {
                "total_users": total_users,
                "verified_users": verified_users,
                "total_orders": total_orders,
                "pending_orders": pending_orders
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return None
    
    def get_pending_orders(self):
        """Get all pending orders"""
        try:
            orders = self.session.query(Order).filter_by(status="pending").all()
            return orders
        except Exception as e:
            print(f"Error getting pending orders: {e}")
            return []
    
    def update_order_status(self, order_id, status):
        """Update order status"""
        try:
            order = self.session.query(Order).filter_by(id=order_id).first()
            if not order:
                return False
            
            order.status = status
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error updating order: {e}")
            return False

def admin_menu_keyboard():
    """Generate admin menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📊 Dashboard", callback_data="admin_dashboard")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("📋 Orders", callback_data="admin_orders")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("🔑 API Keys", callback_data="admin_apikeys")],
        [InlineKeyboardButton("💳 Payment Methods", callback_data="admin_payments")],
        [InlineKeyboardButton("📢 Channel Link", callback_data="admin_channel")],
    ]
    return InlineKeyboardMarkup(keyboard)

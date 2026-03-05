from database_models import Session, User, Referral
from datetime import datetime
import uuid

class ReferralSystem:
    def __init__(self):
        self.session = Session()
    
    def generate_referral_link(self, user_id):
        """Generate a unique referral link for a user"""
        try:
            user = self.session.query(User).filter_by(telegram_id=user_id).first()
            if not user:
                return None
            
            # You can use base62 encoding or just the user ID
            referral_code = f"ref_{user.id}_{uuid.uuid4().hex[:6]}"
            return referral_code
        except Exception as e:
            print(f"Error generating referral link: {e}")
            return None
    
    def add_referral(self, referrer_telegram_id, new_user_telegram_id):
        """Add a new referral relationship"""
        try:
            referrer = self.session.query(User).filter_by(telegram_id=referrer_telegram_id).first()
            new_user = self.session.query(User).filter_by(telegram_id=new_user_telegram_id).first()
            
            if not referrer or not new_user:
                return False
            
            # Check if already referred
            existing = self.session.query(Referral).filter_by(
                referrer_id=referrer.id,
                referred_user_id=new_user.id
            ).first()
            
            if existing:
                return False
            
            # Create referral
            referral = Referral(
                referrer_id=referrer.id,
                referred_user_id=new_user.id
            )
            new_user.referred_by = referrer.id
            
            self.session.add(referral)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error adding referral: {e}")
            return False
    
    def get_referral_stats(self, user_id):
        """Get referral statistics for a user"""
        try:
            user = self.session.query(User).filter_by(telegram_id=user_id).first()
            if not user:
                return None
            
            total_referrals = self.session.query(Referral).filter_by(referrer_id=user.id).count()
            paid_referrals = self.session.query(Referral).filter_by(
                referrer_id=user.id,
                payment_made=True
            ).count()
            
            return {
                "total_referrals": total_referrals,
                "paid_referrals": paid_referrals,
                "pending": 10 - (paid_referrals % 10) if paid_referrals < 10 else 0,
                "commission_balance": user.referral_commission,
                "next_reward_at": 10 - (paid_referrals % 10) if paid_referrals < 10 else 0
            }
        except Exception as e:
            print(f"Error getting referral stats: {e}")
            return None
    
    def claim_referral_reward(self, user_id):
        """Claim referral reward if conditions are met"""
        try:
            user = self.session.query(User).filter_by(telegram_id=user_id).first()
            if not user or user.referral_commission <= 0:
                return False
            
            # Add commission to balance
            user.balance += user.referral_commission
            user.referral_commission = 0
            self.session.commit()
            return True
        except Exception as e:
            print(f"Error claiming reward: {e}")
            return False

import requests
from datetime import datetime, timedelta
from config import BITRAHQ_API_KEY, BITRAHQ_API_URL
from database_models import Session, VirtualNumber, OTP
import logging

logger = logging.getLogger(__name__)

class OTPHandler:
    def __init__(self):
        self.session = Session()
        self.api_key = BITRAHQ_API_KEY
        self.api_url = BITRAHQ_API_URL
        self.otp_lifetime = 300  # OTP valid for 5 minutes
    
    def request_code(self, virtual_number_id):
        """Request OTP code from BitRaHQ API for a virtual number"""
        try:
            virtual_number = self.session.query(VirtualNumber).filter_by(
                id=virtual_number_id
            ).first()
            
            if not virtual_number:
                return {
                    "status": "error",
                    "message": "Virtual number not found"
                }
            
            if not virtual_number.is_active:
                return {
                    "status": "error",
                    "message": "This virtual number is no longer active"
                }
            
            # Call BitRaHQ API to request OTP
            params = {
                "api_key": self.api_key,
                "action": "getOTP",
                "number": virtual_number.phone_number,
                "service": virtual_number.service_id
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                otp_code = data.get("otp")
                
                # Delete any previous pending OTPs for this number
                self.session.query(OTP).filter_by(
                    virtual_number_id=virtual_number_id,
                    status="pending"
                ).delete()
                
                # Store OTP in database
                otp = OTP(
                    virtual_number_id=virtual_number_id,
                    otp_code=otp_code,
                    status="pending",
                    expires_at=datetime.utcnow() + timedelta(seconds=self.otp_lifetime)
                )
                self.session.add(otp)
                self.session.commit()
                
                return {
                    "status": "success",
                    "message": "OTP sent successfully",
                    "otp": otp_code,
                    "expires_in": self.otp_lifetime
                }
            else:
                return {
                    "status": "error",
                    "message": data.get("message", "Failed to get OTP from API")
                }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error requesting OTP: {e}")
            return {
                "status": "error",
                "message": f"API Error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in request_code: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def refresh_otp(self, virtual_number_id):
        """Refresh/get the latest OTP for a virtual number"""
        try:
            # Get the latest pending OTP
            otp = self.session.query(OTP).filter_by(
                virtual_number_id=virtual_number_id,
                status="pending"
            ).order_by(OTP.created_at.desc()).first()
            
            if not otp:
                return {
                    "status": "error",
                    "message": "No active OTP found. Please request a code first."
                }
            
            # Check if OTP has expired
            if datetime.utcnow() > otp.expires_at:
                otp.status = "expired"
                self.session.commit()
                return {
                    "status": "error",
                    "message": "OTP has expired. Please request a new code."
                }
            
            # Calculate remaining time
            remaining_time = int((otp.expires_at - datetime.utcnow()).total_seconds())
            
            return {
                "status": "success",
                "otp": otp.otp_code,
                "expires_in": remaining_time,
                "created_at": otp.created_at.isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error in refresh_otp: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_user_numbers(self, user_id):
        """Get all virtual numbers for a user"""
        try:
            numbers = self.session.query(VirtualNumber).filter_by(
                user_id=user_id,
                is_active=True
            ).all()
            
            return {
                "status": "success",
                "numbers": [
                    {
                        "id": num.id,
                        "number": num.phone_number,
                        "service": num.service_name,
                        "created_at": num.created_at.isoformat()
                    }
                    for num in numbers
                ]
            }
        except Exception as e:
            logger.error(f"Error getting user numbers: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def mark_otp_as_used(self, virtual_number_id):
        """Mark OTP as used after verification"""
        try:
            otp = self.session.query(OTP).filter_by(
                virtual_number_id=virtual_number_id,
                status="pending"
            ).order_by(OTP.created_at.desc()).first()
            
            if otp:
                otp.status = "used"
                otp.used_at = datetime.utcnow()
                self.session.commit()
                return {"status": "success"}
            
            return {"status": "error", "message": "OTP not found"}
        except Exception as e:
            logger.error(f"Error marking OTP as used: {e}")
            return {"status": "error", "message": str(e)}

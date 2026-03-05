import random
import string
import time

class OTPManager:
    def __init__(self, length=6, lifetime=300):
        self.length = length  # Length of the OTP
        self.lifetime = lifetime  # Lifetime of the OTP in seconds
        self.otps = {}  # Dictionary to store OTPs and their expiration times

    def generate_otp(self):
        otp = ''.join(random.choices(string.digits, k=self.length))
        expiration_time = time.time() + self.lifetime
        self.otps[otp] = expiration_time
        return otp

    def validate_otp(self, otp):
        current_time = time.time()
        if otp in self.otps:
            if current_time < self.otps[otp]:
                del self.otps[otp]  # Delete OTP after validation
                return True
            else:
                del self.otps[otp]  # Delete expired OTP
                return False
        return False

# Example usage:
# otp_manager = OTPManager()
# new_otp = otp_manager.generate_otp()
# print(new_otp)
# print(otp_manager.validate_otp(new_otp))

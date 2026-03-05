# Configuration file for the bot
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# BitRaHQ API Configuration
BITRAHQ_API_KEY = os.getenv("BITRAHQ_API_KEY", "ef209f45e59848126a807ef654d36e9c")
BITRAHQ_API_URL = "https://bitrahq.com/api/v1/services.php"

# Admin Configuration
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))  # Will be set by admin in bot

# Channel Configuration
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@DENKI_CRASHER")  # Will be set by admin

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_database.db")

# Referral Configuration
REFERRAL_THRESHOLD = 10  # Users need to refer 10 people
REFERRAL_COMMISSION = 0.10  # 10% commission from first payment

# Payment Configuration
PAYMENT_METHODS = {
    "flutterwave": "Your Flutterwave Public Key",
    "stripe": "Your Stripe Public Key",
}

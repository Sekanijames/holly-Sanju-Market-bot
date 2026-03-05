import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, CallbackQueryHandler, 
    Filters, CallbackContext, ConversationHandler
)
from config import BOT_TOKEN, ADMIN_CHAT_ID
from database_models import Session, User
from admin_panel import AdminPanel, admin_menu_keyboard
from payment_handler import PaymentHandler
from referral_system import ReferralSystem

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversations
REFERRAL_CODE, CONFIRM_CHANNEL, SET_CHANNEL, SET_API_KEY, SET_PAYMENT = range(5)

class TelegramBot:
    def __init__(self):
        self.admin = AdminPanel()
        self.payment = PaymentHandler()
        self.referral = ReferralSystem()
        self.session = Session()
    
    def start(self, update: Update, context: CallbackContext) -> None:
        """Start command handler"""
        user = update.effective_user
        
        # Check if user exists
        db_user = self.session.query(User).filter_by(telegram_id=user.id).first()
        if not db_user:
            db_user = User(
                telegram_id=user.id,
                username=user.username or "Unknown"
            )
            self.session.add(db_user)
            self.session.commit()
        
        # Check if coming from referral link
        if context.args:
            referral_code = context.args[0]
            # Parse referral code and add relationship
            if referral_code.startswith("ref_"):
                try:
                    referrer_id = int(referral_code.split("_")[1])
                    referrer = self.session.query(User).filter_by(id=referrer_id).first()
                    if referrer and db_user.referred_by is None:
                        self.referral.add_referral(referrer.telegram_id, user.id)
                        update.message.reply_text(
                            f"✅ You've been referred by {referrer.username}!\n\n"
                            "Now please verify by following the channel below."
                        )
                except:
                    pass
        
        # Show welcome message
        welcome_text = """
🤖 Welcome to Social Media Boost Bot!

This bot helps you:
✅ Boost social media accounts
✅ Purchase virtual numbers
✅ Earn through referrals

Please verify by following our channel first, then click confirm below.
"""
        update.message.reply_text(welcome_text)
        
        # Show channel verification
        self.show_channel_verification(update, context)
        
        return CONFIRM_CHANNEL
    
    def show_channel_verification(self, update: Update, context: CallbackContext) -> None:
        """Show channel verification button"""
        admin_config = self.admin.session.query(self.admin.session.query(User).filter_by(id=1).first().__class__.__bases__[0]).first()
        
        channel_username = "@your_channel"  # Default, should be set by admin
        
        keyboard = [
            [InlineKeyboardButton("👉 Join Channel", url=f"https://t.me/{channel_username[1:]}")],
            [InlineKeyboardButton("✅ I've Joined", callback_data="verify_channel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            "Please join our channel to proceed:",
            reply_markup=reply_markup
        )
    
    def verify_channel(self, update: Update, context: CallbackContext) -> None:
        """Verify if user has joined the channel"""
        query = update.callback_query
        user = update.effective_user
        
        # Get channel from config (you'll need to implement this properly)
        channel_username = "your_channel"  # Replace with actual channel
        
        try:
            # Check if user is member of channel
            member = context.bot.get_chat_member(f"@{channel_username}", user.id)
            
            if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR]:
                # Mark user as verified
                db_user = self.session.query(User).filter_by(telegram_id=user.id).first()
                db_user.is_verified = True
                self.session.commit()
                
                query.edit_message_text(
                    "✅ Channel verification successful!\n\n"
                    "Now you can use the bot. What would you like to do?"
                )
                self.show_main_menu(update, context)
            else:
                query.answer("❌ Please join the channel first!", show_alert=True)
        except Exception as e:
            query.answer(f"Error verifying: {str(e)}", show_alert=True)
    
    def show_main_menu(self, update: Update, context: CallbackContext) -> None:
        """Show main menu"""
        keyboard = [
            [InlineKeyboardButton("🛒 Buy Numbers", callback_data="buy_numbers")],
            [InlineKeyboardButton("👥 Referral System", callback_data="referrals")],
            [InlineKeyboardButton("💰 My Balance", callback_data="balance")],
            [InlineKeyboardButton("📋 My Orders", callback_data="orders")],
        ]
        
        if update.effective_user.id == ADMIN_CHAT_ID:
            keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text(
            "📱 Main Menu - Choose an option:",
            reply_markup=reply_markup
        )
    
    def referrals_menu(self, update: Update, context: CallbackContext) -> None:
        """Show referral menu"""
        query = update.callback_query
        user = update.effective_user
        
        # Get referral link
        referral_code = self.referral.generate_referral_link(user.id)
        referral_link = f"https://t.me/your_bot?start={referral_code}"
        
        # Get stats
        stats = self.referral.get_referral_stats(user.id)
        
        text = f"""
👥 Referral System

Your Referral Link:
<code>{referral_link}</code>

📊 Statistics:
• Total Referrals: {stats['total_referrals']}
• Referrals with Payment: {stats['paid_referrals']}
• Pending for Reward: {stats['pending']}
• Commission Balance: ${stats['commission_balance']:.2f}

🎁 How it works:
1. Share your link with friends
2. They must make their first payment
3. After 10 referrals make payment, you get 10% commission
4. Use commission to buy numbers!
"""
        
        keyboard = [
            [InlineKeyboardButton("🎯 Copy Link", callback_data="copy_referral")],
            [InlineKeyboardButton("💵 Claim Reward", callback_data="claim_reward")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
    
    def admin_panel_menu(self, update: Update, context: CallbackContext) -> None:
        """Show admin panel"""
        query = update.callback_query
        user = update.effective_user
        
        if not self.admin.is_admin(user.id):
            query.answer("❌ You are not authorized!", show_alert=True)
            return
        
        query.edit_message_text(
            "⚙️ Admin Panel",
            reply_markup=admin_menu_keyboard()
        )
    
    def admin_dashboard(self, update: Update, context: CallbackContext) -> None:
        """Show admin dashboard"""
        query = update.callback_query
        stats = self.admin.get_dashboard_stats()
        
        text = f"""
📊 Dashboard Statistics

👥 Users: {stats['total_users']}
✅ Verified Users: {stats['verified_users']}

📋 Orders:
• Total Orders: {stats['total_orders']}
• Pending Orders: {stats['pending_orders']}
"""
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(text, reply_markup=reply_markup)
    
    def set_channel_handler(self, update: Update, context: CallbackContext) -> int:
        """Handle setting channel username"""
        query = update.callback_query
        query.edit_message_text("Please send the channel username (e.g., @mychannel):")
        return SET_CHANNEL
    
    def save_channel(self, update: Update, context: CallbackContext) -> None:
        """Save channel username"""
        channel = update.message.text
        if not channel.startswith("@"):
            update.message.reply_text("❌ Please include @ symbol")
            return SET_CHANNEL
        
        if self.admin.set_channel_username(channel):
            update.message.reply_text(f"✅ Channel set to {channel}")
        else:
            update.message.reply_text("❌ Error setting channel")
        
        return ConversationHandler.END
    
    def set_api_key_handler(self, update: Update, context: CallbackContext) -> int:
        """Handle setting API key"""
        query = update.callback_query
        query.edit_message_text("Please send the BitRaHQ API key:")
        return SET_API_KEY
    
    def save_api_key(self, update: Update, context: CallbackContext) -> None:
        """Save API key"""
        api_key = update.message.text.strip()
        
        if self.admin.set_api_key(api_key):
            update.message.reply_text("✅ API key updated successfully")
        else:
            update.message.reply_text("❌ Error updating API key")
        
        return ConversationHandler.END
    
    def error_handler(self, update: Update, context: CallbackContext) -> None:
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    bot = TelegramBot()
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Command handlers
    dispatcher.add_handler(CommandHandler("start", bot.start))
    
    # Callback handlers
    dispatcher.add_handler(CallbackQueryHandler(bot.verify_channel, pattern="verify_channel"))
    dispatcher.add_handler(CallbackQueryHandler(bot.show_main_menu, pattern="main_menu"))
    dispatcher.add_handler(CallbackQueryHandler(bot.referrals_menu, pattern="referrals"))
    dispatcher.add_handler(CallbackQueryHandler(bot.admin_panel_menu, pattern="admin_panel"))
    dispatcher.add_handler(CallbackQueryHandler(bot.admin_dashboard, pattern="admin_dashboard"))
    dispatcher.add_handler(CallbackQueryHandler(bot.set_channel_handler, pattern="admin_channel"))
    dispatcher.add_handler(CallbackQueryHandler(bot.set_api_key_handler, pattern="admin_apikeys"))
    
    # Conversation handlers
    channel_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(bot.set_channel_handler, pattern="admin_channel")],
        states={
            SET_CHANNEL: [MessageHandler(Filters.text & ~Filters.command, bot.save_channel)],
        },
        fallbacks=[CommandHandler("start", bot.start)],
    )
    
    apikey_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(bot.set_api_key_handler, pattern="admin_apikeys")],
        states={
            SET_API_KEY: [MessageHandler(Filters.text & ~Filters.command, bot.save_api_key)],
        },
        fallbacks=[CommandHandler("start", bot.start)],
    )
    
    dispatcher.add_handler(channel_conv)
    dispatcher.add_handler(apikey_conv)
    
    # Error handler
    dispatcher.add_error_handler(bot.error_handler)
    
    # Start polling
    updater.start_polling()
    logger.info("Bot started polling...")
    updater.idle()

if __name__ == '__main__':
    main()

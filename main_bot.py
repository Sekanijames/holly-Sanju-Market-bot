# Add to imports at the top
from otp_handler import OTPHandler

# Add to TelegramBot.__init__:
self.otp = OTPHandler()

# Add these new states to the range at the top
BUY_NUMBERS, SELECT_SERVICE, REQUEST_CODE = range(5, 8)

# Add these new methods to TelegramBot class:

def buy_numbers_handler(self, update: Update, context: CallbackContext) -> int:
    """Show available services to buy numbers"""
    query = update.callback_query
    user = update.effective_user
    
    try:
        services = self.payment.get_services()
        if not services or "data" not in services:
            query.answer("❌ Failed to load services", show_alert=True)
            return
        
        keyboard = []
        for service in services.get("data", [])[:10]:  # Limit to 10 services
            keyboard.append([
                InlineKeyboardButton(
                    f"📱 {service['name']} - ${service['price']}", 
                    callback_data=f"select_service_{service['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "🛒 Select a service to purchase a virtual number:",
            reply_markup=reply_markup
        )
    except Exception as e:
        query.answer(f"❌ Error: {str(e)}", show_alert=True)

def select_service_handler(self, update: Update, context: CallbackContext) -> int:
    """Handle service selection and show purchase prompt"""
    query = update.callback_query
    user = update.effective_user
    
    try:
        # Extract service_id from callback_data
        service_id = int(query.data.split("_")[-1])
        
        # Store in context for later use
        context.user_data['selected_service_id'] = service_id
        
        # Get service details
        services = self.payment.get_services()
        service = next((s for s in services.get("data", []) if s["id"] == service_id), None)
        
        if not service:
            query.answer("❌ Service not found", show_alert=True)
            return
        
        text = f"""
📱 Service: {service['name']}
💰 Price: ${service['price']}

Click below to complete the purchase.
"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirm Purchase", callback_data=f"confirm_purchase_{service_id}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="buy_numbers")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        query.answer(f"❌ Error: {str(e)}", show_alert=True)

def confirm_purchase_handler(self, update: Update, context: CallbackContext) -> None:
    """Confirm purchase and assign virtual number"""
    query = update.callback_query
    user = update.effective_user
    
    try:
        service_id = int(query.data.split("_")[-1])
        
        # Purchase the service
        result = self.payment.purchase_service(user.id, service_id, 1)
        
        if result["status"] == "error":
            query.answer(f"❌ {result['message']}", show_alert=True)
            return
        
        # Create virtual number record
        # Note: You'll need to implement the actual number assignment from BitRaHQ
        # For now, we'll use a placeholder
        services = self.payment.get_services()
        service = next((s for s in services.get("data", []) if s["id"] == service_id), None)
        
        from database_models import VirtualNumber
        virtual_num = VirtualNumber(
            user_id=self.session.query(User).filter_by(telegram_id=user.id).first().id,
            phone_number=f"+1234567890",  # Replace with actual number from API
            service_name=service['name'] if service else "Unknown",
            service_id=service_id
        )
        self.session.add(virtual_num)
        self.session.commit()
        
        text = f"""
✅ Purchase Successful!

🎉 Virtual Number Purchased: {virtual_num.phone_number}
📱 Service: {service['name'] if service else 'Service'}
💰 Balance: ${result.get('remaining_balance', 0):.2f}

Now you can request the code for this number.
"""
        
        keyboard = [
            [InlineKeyboardButton("🔐 Request Code", callback_data=f"request_code_{virtual_num.id}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in confirm_purchase: {e}")
        query.answer(f"❌ Error: {str(e)}", show_alert=True)

def request_code_handler(self, update: Update, context: CallbackContext) -> None:
    """Request OTP code for virtual number"""
    query = update.callback_query
    user = update.effective_user
    
    try:
        virtual_number_id = int(query.data.split("_")[-1])
        
        # Request OTP from API
        result = self.otp.request_code(virtual_number_id)
        
        if result["status"] == "error":
            query.answer(f"❌ {result['message']}", show_alert=True)
            return
        
        text = f"""
🔐 OTP Code Request Sent!

⏱️ OTP Valid for: {result['expires_in']} seconds

The code will be displayed below. Click refresh to get the latest OTP.
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh OTP", callback_data=f"refresh_otp_{virtual_number_id}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in request_code: {e}")
        query.answer(f"❌ Error: {str(e)}", show_alert=True)

def refresh_otp_handler(self, update: Update, context: CallbackContext) -> None:
    """Refresh and show the latest OTP"""
    query = update.callback_query
    
    try:
        virtual_number_id = int(query.data.split("_")[-1])
        
        # Get latest OTP
        result = self.otp.refresh_otp(virtual_number_id)
        
        if result["status"] == "error":
            query.answer(f"❌ {result['message']}", show_alert=True)
            return
        
        text = f"""
🔐 Your OTP Code:

<code>{result['otp']}</code>

⏱️ Expires in: {result['expires_in']} seconds

Use this code to verify your account on the platform.
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh OTP", callback_data=f"refresh_otp_{virtual_number_id}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in refresh_otp: {e}")
        query.answer(f"❌ Error: {str(e)}", show_alert=True)

# Add to main() dispatcher.add_handler calls:
dispatcher.add_handler(CallbackQueryHandler(bot.buy_numbers_handler, pattern="buy_numbers"))
dispatcher.add_handler(CallbackQueryHandler(bot.select_service_handler, pattern="^select_service_"))
dispatcher.add_handler(CallbackQueryHandler(bot.confirm_purchase_handler, pattern="^confirm_purchase_"))
dispatcher.add_handler(CallbackQueryHandler(bot.request_code_handler, pattern="^request_code_"))
dispatcher.add_handler(CallbackQueryHandler(bot.refresh_otp_handler, pattern="^refresh_otp_"))

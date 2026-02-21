from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ContextTypes, ConversationHandler
)
from telegram.constants import ChatAction, ParseMode
import json
from v2ray_converter import V2RayConverter
from logger import setup_logger
from config import TELEGRAM_BOT_TOKEN, API_REQUEST_TIMEOUT

logger = setup_logger(__name__)

# Conversation states
WAITING_FOR_JSON = 1
WAITING_FOR_NAME = 2


class V2RayTelegramBot:
    """Telegram bot for V2Ray configuration conversion"""
    
    def __init__(self, token: str):
        self.token = token
        self.converter = V2RayConverter()
        self.app = None
        self.user_configs = {}  # Temporary storage for JSON during conversation
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        try:
            welcome_text = (
                "🚀 <b>Welcome to V2Ray Converter Bot!</b>\n\n"
                "I can convert JSON V2Ray configurations to shareable links.\n\n"
                "<b>Supported Protocols:</b>\n"
                "✅ VLESS\n"
                "✅ VMess\n"
                "✅ Trojan\n"
                "✅ Shadowsocks\n"
                "✅ Hysteria 1\n"
                "✅ Hysteria 2\n\n"
                "<b>How to use:</b>\n"
                "Send /convert to start converting a configuration.\n"
                "Or send /help for more information."
            )
            
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.HTML
            )
            logger.info(f"User {update.effective_user.id} started the bot")
        except Exception as e:
            logger.error(f"Error in start command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred while processing your request."
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        try:
            help_text = (
                "<b>📖 Help & Instructions</b>\n\n"
                "<b>Commands:</b>\n"
                "/start - Show welcome message\n"
                "/help - Show this help message\n"
                "/convert - Start configuration conversion\n\n"
                "<b>How to Convert:</b>\n"
                "1️⃣ Use /convert command\n"
                "2️⃣ Send your JSON configuration\n"
                "3️⃣ Enter a name/remark for the server\n"
                "4️⃣ Get your V2Ray link!\n\n"
                "<b>JSON Format Example:</b>\n"
                "<code>{\n"
                '  "protocol": "vless",\n'
                '  "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",\n'
                '  "address": "example.com",\n'
                '  "port": 443\n'
                "}</code>\n\n"
                "<b>Required Fields by Protocol:</b>\n"
                "🔹 <b>VLESS:</b> protocol, uuid, address, port\n"
                "🔹 <b>VMess:</b> protocol, uuid, address, port\n"
                "🔹 <b>Trojan:</b> protocol, password, address, port\n"
                "🔹 <b>SS:</b> protocol, method, password, address, port\n"
                "🔹 <b>Hysteria:</b> protocol, authString, address, port\n"
                "🔹 <b>Hysteria2:</b> protocol, password, address, port\n\n"
                "<b>Optional Fields:</b>\n"
                "tls, sni, alpn, path, host, network, and more...\n\n"
                "For more details, visit the documentation."
            )
            
            await update.message.reply_text(
                help_text,
                parse_mode=ParseMode.HTML
            )
            logger.info(f"User {update.effective_user.id} requested help")
        except Exception as e:
            logger.error(f"Error in help command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred while processing your request."
            )
    
    async def convert_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the conversion process"""
        try:
            user_id = update.effective_user.id
            
            message_text = (
                "📝 <b>Send your JSON configuration</b>\n\n"
                "Please paste the JSON configuration for your V2Ray server.\n\n"
                "Example:\n"
                "<code>{\n"
                '  "protocol": "vless",\n'
                '  "uuid": "uuid-here",\n'
                '  "address": "server.com",\n'
                '  "port": 443\n'
                "}</code>\n\n"
                "Or use /cancel to exit."
            )
            
            await update.message.reply_text(
                message_text,
                parse_mode=ParseMode.HTML
            )
            logger.info(f"User {user_id} started conversion process")
            
            return WAITING_FOR_JSON
        except Exception as e:
            logger.error(f"Error in convert_start: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred. Please try again with /convert"
            )
            return ConversationHandler.END
    
    async def receive_json(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive and validate JSON configuration"""
        try:
            user_id = update.effective_user.id
            json_text = update.message.text.strip()
            
            # Try to parse JSON
            try:
                config = json.loads(json_text)
            except json.JSONDecodeError as e:
                await update.message.reply_text(
                    f"❌ <b>Invalid JSON Format</b>\n\n"
                    f"Error: {str(e)}\n\n"
                    f"Please send valid JSON or use /cancel to exit.",
                    parse_mode=ParseMode.HTML
                )
                logger.warning(f"User {user_id} sent invalid JSON: {e}")
                return WAITING_FOR_JSON
            
            # Check if protocol is present
            if "protocol" not in config:
                await update.message.reply_text(
                    "❌ <b>Missing Protocol Field</b>\n\n"
                    "Your JSON must include a 'protocol' field.\n\n"
                    "Supported protocols: vless, vmess, trojan, ss, hysteria, hy2",
                    parse_mode=ParseMode.HTML
                )
                return WAITING_FOR_JSON
            
            # Store the JSON temporarily
            self.user_configs[user_id] = json_text
            
            await update.message.reply_text(
                "✅ JSON configuration received!\n\n"
                "Now, please enter a <b>name/remark</b> for this server.\n"
                "(e.g., 'My VPN Server', 'Fast Server', etc.)"
                "\n\nOr use /cancel to exit.",
                parse_mode=ParseMode.HTML
            )
            logger.info(f"User {user_id} submitted valid JSON")
            
            return WAITING_FOR_NAME
        except Exception as e:
            logger.error(f"Error in receive_json: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred while processing your JSON. Please try again."
            )
            return WAITING_FOR_JSON
    
    async def receive_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive server name and generate conversion"""
        try:
            user_id = update.effective_user.id
            server_name = update.message.text.strip()
            
            # Validate name
            if not server_name or len(server_name) < 1:
                await update.message.reply_text(
                    "❌ Please enter a valid name for the server."
                )
                return WAITING_FOR_NAME
            
            if len(server_name) > 100:
                await update.message.reply_text(
                    "❌ Server name is too long (max 100 characters)."
                )
                return WAITING_FOR_NAME
            
            # Get stored JSON
            json_config = self.user_configs.get(user_id)
            if not json_config:
                await update.message.reply_text(
                    "❌ Configuration not found. Please start over with /convert"
                )
                return ConversationHandler.END
            
            # Show typing indicator
            await update.message.chat.send_action(ChatAction.TYPING)
            
            # Convert
            try:
                result_url = self.converter.convert(json_config, server_name)
                
                # Clean up
                del self.user_configs[user_id]
                
                # Prepare response
                response_text = (
                    "✅ <b>Conversion Successful!</b>\n\n"
                    "<b>Server Name:</b> {}\n\n"
                    "<b>V2Ray Link:</b>\n"
                    "<code>{}</code>\n\n"
                    "You can share this link or use it in V2Ray clients."
                ).format(server_name, result_url)
                
                # Create inline keyboard
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "📋 Copy Link",
                            callback_data=f"copy_{result_url}"
                        ),
                        InlineKeyboardButton(
                            "🔄 Convert Another",
                            callback_data="convert_new"
                        )
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    response_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
                logger.info(f"User {user_id} successfully converted config to {server_name}")
                
                return ConversationHandler.END
            
            except ValueError as e:
                await update.message.reply_text(
                    f"❌ <b>Conversion Error</b>\n\n"
                    f"{str(e)}\n\n"
                    f"Please check your JSON configuration and try again.",
                    parse_mode=ParseMode.HTML
                )
                logger.warning(f"User {user_id} conversion failed: {e}")
                
                # Ask to retry
                await update.message.reply_text(
                    "Would you like to:\n"
                    "/convert - Try again with different config\n"
                    "/cancel - Exit"
                )
                return ConversationHandler.END
        
        except Exception as e:
            logger.error(f"Error in receive_name: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An unexpected error occurred. Please try again with /convert"
            )
            return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the conversion process"""
        try:
            user_id = update.effective_user.id
            
            # Clean up
            if user_id in self.user_configs:
                del self.user_configs[user_id]
            
            await update.message.reply_text(
                "❌ Conversion cancelled.\n\n"
                "Use /convert to start again or /help for more information."
            )
            logger.info(f"User {user_id} cancelled the conversion")
            
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Error in cancel: {e}", exc_info=True)
            return ConversationHandler.END
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors in the application"""
        logger.error(
            f"Exception while handling an update: {context.error}",
            exc_info=context.error
        )
        
        if isinstance(update, Update) and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ <b>An Unexpected Error Occurred</b>\n\n"
                    "Our developers have been notified. Please try again later.\n"
                    "Use /help for assistance.",
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")
    
    def build_application(self) -> Application:
        """Build the Telegram application with all handlers"""
        self.app = (
            Application.builder()
            .token(self.token)
            .connect_timeout(API_REQUEST_TIMEOUT)
            .pool_timeout(API_REQUEST_TIMEOUT)
            .build()
        )
        
        # Create conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("convert", self.convert_start)],
            states={
                WAITING_FOR_JSON: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_json)
                ],
                WAITING_FOR_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_name)
                ]
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel),
                CommandHandler("start", self.start),
                CommandHandler("help", self.help_command),
                CommandHandler("convert", self.convert_start)
            ],
            allow_reentry=True
        )
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(conv_handler)
        
        # Error handler
        self.app.add_error_handler(self.error_handler)
        
        logger.info("Telegram application built successfully")
        return self.app
    
    async def run(self) -> None:
        """Run the bot with polling"""
        if not self.app:
            self.build_application()
        
        logger.info("Starting bot polling...")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        # Keep running
        await self.app.updater.idle()
    
    async def stop(self) -> None:
        """Stop the bot gracefully"""
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            logger.info("Bot stopped gracefully")
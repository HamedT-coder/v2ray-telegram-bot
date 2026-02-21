import asyncio
import signal
import sys
from telegram_bot import V2RayTelegramBot
from config import TELEGRAM_BOT_TOKEN
from logger import setup_logger

logger = setup_logger(__name__)


class BotApplication:
    """Main application wrapper for V2Ray Telegram Bot"""
    
    def __init__(self):
        self.bot = None
        self.running = False
    
    async def start(self) -> None:
        """Start the bot application"""
        try:
            logger.info("=" * 50)
            logger.info("V2Ray Telegram Bot Starting...")
            logger.info("=" * 50)
            
            # Validate token
            if not TELEGRAM_BOT_TOKEN:
                raise ValueError("TELEGRAM_BOT_TOKEN is not set!")
            
            logger.info(f"Bot token loaded (length: {len(TELEGRAM_BOT_TOKEN)})")
            
            # Initialize bot
            self.bot = V2RayTelegramBot(TELEGRAM_BOT_TOKEN)
            self.bot.build_application()
            
            logger.info("Bot application built successfully")
            logger.info("Bot polling started...")
            logger.info("=" * 50)
            
            self.running = True
            
            # Run the bot
            await self.bot.run()
        
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Bot interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)
    
    async def stop(self) -> None:
        """Stop the bot application gracefully"""
        if self.bot and self.running:
            logger.info("Stopping bot...")
            await self.bot.stop()
            self.running = False
            logger.info("Bot stopped successfully")


def handle_signal(signum, frame):
    """Handle system signals for graceful shutdown"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)


async def main():
    """Main entry point"""
    app = BotApplication()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await app.stop()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
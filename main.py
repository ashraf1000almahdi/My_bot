from app import app
import threading
import logging
import atexit
from telegram_bot import run_bot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global bot thread
bot_thread = None

def start_bot():
    """Start the bot in a separate thread"""
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        logger.info("Starting Telegram bot thread...")
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("Telegram bot thread started successfully")

def stop_bot():
    """Stop the bot gracefully"""
    from telegram_bot import bot_instance
    if bot_instance:
        bot_instance.stop()
        logger.info("Bot stopped")

# Register cleanup function
atexit.register(stop_bot)

# Start the bot when the module is imported (for Gunicorn)
start_bot()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

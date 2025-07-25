import logging
from telegram import Bot
from telegram.error import TelegramError
from config import Config

class SubscriptionChecker:
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
        self.channel_username = Config.CHANNEL_USERNAME
        self.channel_id = Config.CHANNEL_ID
        
    async def check_subscription(self, user_id):
        """Check if user is subscribed to the required channel"""
        try:
            # Get chat member info
            member = await self.bot.get_chat_member(
                chat_id=self.channel_id,
                user_id=user_id
            )
            
            # Check if user is subscribed (member, administrator, or creator)
            if member.status in ['member', 'administrator', 'creator']:
                return True
            else:
                return False
                
        except TelegramError as e:
            logging.error(f"Error checking subscription for user {user_id}: {e}")
            return False
    
    async def get_channel_info(self):
        """Get channel information"""
        try:
            chat = await self.bot.get_chat(chat_id=self.channel_id)
            return {
                'title': chat.title,
                'username': chat.username,
                'description': chat.description,
                'member_count': await self.bot.get_chat_member_count(chat_id=self.channel_id)
            }
        except TelegramError as e:
            logging.error(f"Error getting channel info: {e}")
            return None

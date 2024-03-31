import os
import requests
from enum import StrEnum

class MessageFormat(StrEnum):
    MARKDOWN_V2 = 'MarkdownV2'
    HTML = 'HTML'
    MARKDOWN_LEGACY = 'Markdown'

class TelegramAPIService:
    API_TOKEN_ENV = 'TELEGRAM_API_TOKEN'
    CHAT_ID_ENV = 'TELEGRAM_CHAT_ID'
    BOT_URL = "https://api.telegram.org/bot{token}"

    def __init__(self):
        self.api_token = os.getenv(self.API_TOKEN_ENV)
        self.chat_id = os.getenv(self.CHAT_ID_ENV)

        if not self.api_token:
            raise Exception('Telegram API Token env var not set')
        
        if not self.chat_id:
            raise Exception('Telegram Chat ID env var not set')

    def get_api_url(self):
        return self.BOT_URL.format(token=self.api_token)

    def send_message_to_me(self, message: str, format: MessageFormat | None = None):
        params = {"chat_id": self.chat_id, "text": message, "parse_mode": format}

        resp = requests.get(self.get_api_url() + "/sendMessage", params=params)
        return resp.json()
